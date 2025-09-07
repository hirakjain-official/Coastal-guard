"""
Aggregation Service
Handles grouping of analyzed posts by location and time, and hotspot detection.
"""

import os
import math
from typing import List, Dict, Any, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict
from loguru import logger

class AggregationService:
    """Handles aggregation and hotspot detection of analyzed posts."""
    
    def __init__(self):
        """Initialize the aggregation service."""
        self.hotspot_post_threshold = int(os.getenv('HOTSPOT_POST_THRESHOLD', 20))
        self.hotspot_radius_km = float(os.getenv('HOTSPOT_RADIUS_KM', 10))
        
        logger.info(f"Aggregation service initialized - threshold: {self.hotspot_post_threshold} posts, radius: {self.hotspot_radius_km}km")
    
    async def detect_hotspots(self, analyzed_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect hotspots from analyzed posts based on spatial and temporal clustering.
        
        Args:
            analyzed_posts: List of posts with AI analysis
            
        Returns:
            List of detected hotspots
        """
        # Filter high-confidence hazard posts
        hazard_posts = [
            post for post in analyzed_posts
            if (post.get('is_hazard', False) and 
                post.get('meets_confidence_threshold', False))
        ]
        
        logger.info(f"Processing {len(hazard_posts)} high-confidence hazard posts for hotspot detection")
        
        if not hazard_posts:
            return []
        
        # Group posts by location and hazard type
        location_groups = self._group_posts_by_location(hazard_posts)
        
        # Detect hotspots within each location group
        hotspots = []
        for location_key, posts in location_groups.items():
            location_hotspots = await self._detect_location_hotspots(location_key, posts)
            hotspots.extend(location_hotspots)
        
        logger.info(f"Detected {len(hotspots)} hotspots")
        return hotspots
    
    def _group_posts_by_location(self, posts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group posts by general location (city/state level)."""
        location_groups = defaultdict(list)
        
        for post in posts:
            location = post.get('inferred_location', {})
            
            # Create location key
            if location:
                city = location.get('city', 'Unknown')
                state = location.get('state', 'Unknown') 
                location_key = f"{city}, {state}"
            else:
                location_key = "Unknown Location"
            
            location_groups[location_key].append(post)
        
        return dict(location_groups)
    
    async def _detect_location_hotspots(
        self, 
        location_key: str, 
        posts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Detect hotspots within a specific location."""
        if len(posts) < self.hotspot_post_threshold:
            return []
        
        hotspots = []
        
        # Group by hazard type within location
        hazard_groups = defaultdict(list)
        for post in posts:
            hazard_type = post.get('ai_analysis', {}).get('hazard_type', 'Other')
            hazard_groups[hazard_type].append(post)
        
        # Check each hazard type group
        for hazard_type, hazard_posts in hazard_groups.items():
            if len(hazard_posts) >= self.hotspot_post_threshold:
                hotspot = await self._create_hotspot(location_key, hazard_type, hazard_posts)
                hotspots.append(hotspot)
        
        return hotspots
    
    async def _create_hotspot(
        self, 
        location_key: str, 
        hazard_type: str, 
        posts: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create a hotspot from grouped posts."""
        # Calculate hotspot metadata
        post_count = len(posts)
        urgency_counts = {'Low': 0, 'Medium': 0, 'High': 0}
        confidence_scores = []
        timestamps = []
        
        for post in posts:
            analysis = post.get('ai_analysis', {})
            urgency = analysis.get('urgency', 'Low')
            confidence = analysis.get('confidence', 0.0)
            
            urgency_counts[urgency] += 1
            confidence_scores.append(confidence)
            
            # Parse timestamp
            created_at = post.get('created_at')
            if created_at:
                if isinstance(created_at, str):
                    try:
                        timestamp = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        timestamps.append(timestamp)
                    except:
                        pass
                elif isinstance(created_at, datetime):
                    timestamps.append(created_at)
        
        # Calculate averages and statistics
        avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
        
        # Determine overall urgency (highest urgency with significant representation)
        overall_urgency = 'Low'
        if urgency_counts['High'] >= post_count * 0.3:  # 30% high urgency
            overall_urgency = 'High'
        elif urgency_counts['Medium'] >= post_count * 0.4:  # 40% medium urgency  
            overall_urgency = 'Medium'
        
        # Time range
        time_range = None
        if timestamps:
            earliest = min(timestamps)
            latest = max(timestamps)
            time_range = {
                'start': earliest.isoformat(),
                'end': latest.isoformat(),
                'duration_minutes': (latest - earliest).total_seconds() / 60
            }
        
        # Extract location information
        location_info = self._extract_location_info(posts)
        
        hotspot = {
            'id': f"hotspot_{location_key.replace(', ', '_')}_{hazard_type}_{int(datetime.now().timestamp())}",
            'location': location_key,
            'location_details': location_info,
            'hazard_type': hazard_type,
            'post_count': post_count,
            'urgency_breakdown': urgency_counts,
            'overall_urgency': overall_urgency,
            'average_confidence': round(avg_confidence, 3),
            'time_range': time_range,
            'detection_time': datetime.now().isoformat(),
            'status': 'pending_validation',
            'contributing_posts': [
                {
                    'id': post.get('id'),
                    'text_preview': post.get('cleaned_text', '')[:100] + '...',
                    'confidence': post.get('ai_analysis', {}).get('confidence', 0.0),
                    'urgency': post.get('ai_analysis', {}).get('urgency', 'Low'),
                    'created_at': post.get('created_at')
                }
                for post in posts[:10]  # Include first 10 posts as examples
            ]
        }
        
        return hotspot
    
    def _extract_location_info(self, posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Extract comprehensive location information from posts."""
        locations = []
        coordinates = []
        
        for post in posts:
            location = post.get('inferred_location')
            if location:
                locations.append(location)
                
                if 'latitude' in location and 'longitude' in location:
                    coordinates.append((location['latitude'], location['longitude']))
        
        if not locations:
            return {}
        
        # Find most common city and state
        cities = [loc.get('city') for loc in locations if loc.get('city')]
        states = [loc.get('state') for loc in locations if loc.get('state')]
        
        most_common_city = max(set(cities), key=cities.count) if cities else None
        most_common_state = max(set(states), key=states.count) if states else None
        
        # Calculate centroid if coordinates available
        centroid = None
        if coordinates:
            avg_lat = sum(coord[0] for coord in coordinates) / len(coordinates)
            avg_lon = sum(coord[1] for coord in coordinates) / len(coordinates)
            centroid = {'latitude': avg_lat, 'longitude': avg_lon}
        
        return {
            'city': most_common_city,
            'state': most_common_state,
            'country': 'India',
            'centroid': centroid,
            'coordinate_count': len(coordinates),
            'total_location_references': len(locations)
        }
    
    def _haversine_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate the Haversine distance between two points in kilometers."""
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c
    
    def get_hotspots_by_urgency(self, hotspots: List[Dict[str, Any]], urgency: str) -> List[Dict[str, Any]]:
        """Filter hotspots by urgency level."""
        return [h for h in hotspots if h.get('overall_urgency') == urgency]
    
    def get_hotspots_by_hazard_type(self, hotspots: List[Dict[str, Any]], hazard_type: str) -> List[Dict[str, Any]]:
        """Filter hotspots by hazard type."""
        return [h for h in hotspots if h.get('hazard_type') == hazard_type]
    
    def get_aggregation_summary(self, hotspots: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics for detected hotspots."""
        if not hotspots:
            return {
                'total_hotspots': 0,
                'urgency_breakdown': {'High': 0, 'Medium': 0, 'Low': 0},
                'hazard_type_breakdown': {},
                'total_posts_in_hotspots': 0
            }
        
        urgency_counts = {'High': 0, 'Medium': 0, 'Low': 0}
        hazard_type_counts = defaultdict(int)
        total_posts = 0
        
        for hotspot in hotspots:
            urgency = hotspot.get('overall_urgency', 'Low')
            hazard_type = hotspot.get('hazard_type', 'Other')
            post_count = hotspot.get('post_count', 0)
            
            urgency_counts[urgency] += 1
            hazard_type_counts[hazard_type] += 1
            total_posts += post_count
        
        return {
            'total_hotspots': len(hotspots),
            'urgency_breakdown': urgency_counts,
            'hazard_type_breakdown': dict(hazard_type_counts),
            'total_posts_in_hotspots': total_posts,
            'average_posts_per_hotspot': round(total_posts / len(hotspots), 1) if hotspots else 0
        }
