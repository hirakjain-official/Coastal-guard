"""
Preprocessing Service
Handles deduplication, text cleaning, language normalization, and location inference.
"""

import re
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import pandas as pd
from langdetect import detect, LangDetectError
from geopy.geocoders import Nominatim
from loguru import logger

class PreprocessingService:
    """Handles preprocessing of raw social media posts."""
    
    def __init__(self):
        """Initialize the preprocessing service."""
        self.geolocator = Nominatim(user_agent="social-media-analytics-agent")
        
        # Common Indian city name mappings
        self.city_mappings = {
            # Common variations and abbreviations
            'vizag': 'Visakhapatnam',
            'hyd': 'Hyderabad', 
            'blr': 'Bangalore',
            'bangalore': 'Bengaluru',
            'bombay': 'Mumbai',
            'calcutta': 'Kolkata',
            'madras': 'Chennai',
            'trivandrum': 'Thiruvananthapuram',
            'cochin': 'Kochi',
            'panjim': 'Panaji',
            
            # Regional names
            'दिल्ली': 'Delhi',
            'मुंबई': 'Mumbai',
            'কলকাতা': 'Kolkata',
            'চেন্নাই': 'Chennai',
            'ചെന്നൈ': 'Chennai',
            'சென்னை': 'Chennai',
            'ముంబై': 'Mumbai',
            'హైదరాబాద్': 'Hyderabad',
            'बेंगलुरु': 'Bengaluru',
            'பெங்களூரு': 'Bengaluru'
        }
        
        # State name mappings
        self.state_mappings = {
            'UP': 'Uttar Pradesh',
            'MP': 'Madhya Pradesh',
            'HP': 'Himachal Pradesh',
            'AP': 'Andhra Pradesh',
            'TN': 'Tamil Nadu',
            'WB': 'West Bengal',
            'KA': 'Karnataka',
            'MH': 'Maharashtra',
            'GJ': 'Gujarat',
            'RJ': 'Rajasthan',
            'OR': 'Odisha',
            'AS': 'Assam',
            'JK': 'Jammu and Kashmir',
            'PB': 'Punjab',
            'HR': 'Haryana',
            'TS': 'Telangana',
            'KL': 'Kerala'
        }
        
        logger.info("Preprocessing service initialized")
    
    async def process_posts(self, raw_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process raw posts through the complete preprocessing pipeline.
        
        Args:
            raw_posts: List of raw social media posts
            
        Returns:
            List of processed posts
        """
        logger.info(f"Starting preprocessing of {len(raw_posts)} raw posts")
        
        # Step 1: Deduplicate posts
        deduplicated_posts = self._deduplicate_posts(raw_posts)
        logger.info(f"After deduplication: {len(deduplicated_posts)} posts")
        
        # Step 2: Clean and normalize text
        cleaned_posts = []
        for post in deduplicated_posts:
            cleaned_post = await self._clean_and_normalize_post(post)
            if cleaned_post:  # Only keep posts that pass cleaning
                cleaned_posts.append(cleaned_post)
        
        logger.info(f"After cleaning: {len(cleaned_posts)} posts")
        
        # Step 3: Infer locations
        located_posts = []
        for post in cleaned_posts:
            located_post = await self._infer_location(post)
            located_posts.append(located_post)
        
        logger.info(f"Preprocessing complete: {len(located_posts)} posts")
        return located_posts
    
    def _deduplicate_posts(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate and near-duplicate posts.
        
        Args:
            posts: List of raw posts
            
        Returns:
            List of deduplicated posts
        """
        # Create DataFrame for easier deduplication
        df = pd.DataFrame(posts)
        
        # Remove exact text duplicates
        df = df.drop_duplicates(subset=['text'], keep='first')
        
        # Remove retweets and quoted tweets (basic detection)
        df = df[~df['text'].str.startswith('RT @', na=False)]
        df = df[~df['text'].str.contains(r'^".*" — @\w+', na=False, regex=True)]
        
        # Remove posts that are too short (likely not informative)
        df = df[df['text'].str.len() >= 10]
        
        # Remove posts that are mostly URLs or mentions
        def is_mostly_links_or_mentions(text):
            if not isinstance(text, str):
                return True
            
            # Count URLs and mentions
            url_count = len(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text))
            mention_count = len(re.findall(r'@\w+', text))
            
            # Remove @ and URLs from text to count meaningful content
            clean_text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            clean_text = re.sub(r'@\w+', '', clean_text)
            clean_text = clean_text.strip()
            
            # If more than 50% is URLs/mentions, filter out
            return len(clean_text) < len(text) * 0.5
        
        df = df[~df['text'].apply(is_mostly_links_or_mentions)]
        
        return df.to_dict('records')
    
    async def _clean_and_normalize_post(self, post: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Clean and normalize a single post.
        
        Args:
            post: Raw post dictionary
            
        Returns:
            Cleaned post dictionary or None if post should be filtered out
        """
        try:
            text = post.get('text', '')
            if not text:
                return None
            
            # Store original text
            post['original_text'] = text
            
            # Remove URLs
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
            
            # Remove excessive whitespace
            text = re.sub(r'\s+', ' ', text).strip()
            
            # Remove or normalize emojis (keep some flood/water related ones)
            water_emojis = ['🌊', '💧', '🌧️', '⛈️', '🌀', '⚠️', '🚨', '🆘']
            
            # Extract water/disaster related emojis
            found_emojis = []
            for emoji in water_emojis:
                if emoji in text:
                    found_emojis.append(emoji)
            
            # Remove all emojis except disaster-related ones
            text = re.sub(r'[^\w\s\u0900-\u097F\u0980-\u09FF\u0A00-\u0A7F\u0A80-\u0AFF\u0B00-\u0B7F\u0B80-\u0BFF\u0C00-\u0C7F\u0C80-\u0CFF\u0D00-\u0D7F#@.,!?:;()-]', '', text)
            
            # Add back important emojis
            if found_emojis:
                text += ' ' + ' '.join(found_emojis)
            
            # Normalize common abbreviations
            text = self._normalize_abbreviations(text)
            
            # Detect language
            try:
                detected_lang = detect(text)
                post['detected_language'] = detected_lang
            except LangDetectError:
                post['detected_language'] = 'unknown'
            
            # Update cleaned text
            post['cleaned_text'] = text
            
            # Filter out posts that are too short after cleaning
            if len(text.strip()) < 5:
                return None
            
            # Filter out obvious spam or promotional content
            if self._is_spam_or_promotional(text):
                return None
            
            return post
            
        except Exception as e:
            logger.error(f"Error cleaning post {post.get('id')}: {str(e)}")
            return None
    
    def _normalize_abbreviations(self, text: str) -> str:
        """Normalize common abbreviations and shorthand."""
        # Common text speak normalizations
        normalizations = {
            r'\bu\b': 'you',
            r'\bur\b': 'your',
            r'\br\b': 'are',
            r'\bn\b': 'and',
            r'\bw/\b': 'with',
            r'\bw/o\b': 'without',
            r'\btho\b': 'though',
            r'\bthru\b': 'through',
            r'\bcoz\b': 'because',
            r'\bbcoz\b': 'because',
        }
        
        for pattern, replacement in normalizations.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _is_spam_or_promotional(self, text: str) -> bool:
        """Check if text appears to be spam or promotional content."""
        spam_indicators = [
            r'buy now',
            r'click here',
            r'limited time',
            r'call now',
            r'visit our website',
            r'download app',
            r'free download',
            r'get \d+% off',
            r'subscribe to',
            r'follow us',
            r'like and share',
            r'dm for'
        ]
        
        text_lower = text.lower()
        spam_count = sum(1 for pattern in spam_indicators if re.search(pattern, text_lower))
        
        # If more than 2 spam indicators, likely spam
        return spam_count >= 2
    
    async def _infer_location(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """
        Infer location from post content and geotag.
        
        Args:
            post: Cleaned post dictionary
            
        Returns:
            Post dictionary with inferred location
        """
        inferred_location = None
        confidence = 0.0
        
        # Priority 1: Use existing geotag if available
        if post.get('geo') and isinstance(post['geo'], dict):
            geo = post['geo']
            if 'coordinates' in geo:
                try:
                    lat, lon = geo['coordinates'][1], geo['coordinates'][0]  # lat, lon order
                    location = self.geolocator.reverse((lat, lon), timeout=5)
                    if location:
                        inferred_location = {
                            'latitude': lat,
                            'longitude': lon,
                            'address': location.address,
                            'city': self._extract_city_from_address(location.address),
                            'state': self._extract_state_from_address(location.address),
                            'country': 'India'
                        }
                        confidence = 1.0
                except Exception as e:
                    logger.debug(f"Error processing geotag: {str(e)}")
        
        # Priority 2: Extract from text content
        if not inferred_location:
            location_info = self._extract_location_from_text(post.get('cleaned_text', ''))
            if location_info:
                inferred_location = location_info
                confidence = 0.7
        
        # Store location information
        post['inferred_location'] = inferred_location
        post['location_confidence'] = confidence
        
        return post
    
    def _extract_city_from_address(self, address: str) -> Optional[str]:
        """Extract city name from geocoded address."""
        if not address:
            return None
        
        # Simple extraction - this could be enhanced with more sophisticated parsing
        parts = address.split(', ')
        for part in parts:
            part = part.strip()
            if part in self.city_mappings.values() or part in self.city_mappings.keys():
                return self.city_mappings.get(part, part)
        
        return parts[0] if parts else None
    
    def _extract_state_from_address(self, address: str) -> Optional[str]:
        """Extract state name from geocoded address."""
        if not address:
            return None
        
        parts = address.split(', ')
        for part in parts:
            part = part.strip()
            if part in self.state_mappings.values() or part in self.state_mappings.keys():
                return self.state_mappings.get(part, part)
        
        return None
    
    def _extract_location_from_text(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract location information from text content."""
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Look for city mentions
        found_city = None
        found_state = None
        
        # Check for city names (including variations)
        for variation, standard_name in self.city_mappings.items():
            if variation.lower() in text_lower:
                found_city = standard_name
                break
        
        # If no variation found, check standard names
        if not found_city:
            for city in self.city_mappings.values():
                if city.lower() in text_lower:
                    found_city = city
                    break
        
        # Check for state names
        for variation, standard_name in self.state_mappings.items():
            if variation.lower() in text_lower:
                found_state = standard_name
                break
        
        # If no variation found, check standard names
        if not found_state:
            for state in self.state_mappings.values():
                if state.lower() in text_lower:
                    found_state = state
                    break
        
        if found_city or found_state:
            return {
                'city': found_city,
                'state': found_state,
                'country': 'India',
                'extraction_method': 'text_analysis'
            }
        
        return None
