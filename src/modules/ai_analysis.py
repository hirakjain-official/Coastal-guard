"""
AI Analysis Service
Handles hazard classification using DeepSeek API for relevance, hazard type, urgency, and confidence scoring.
"""

import os
import json
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from loguru import logger

class AIAnalysisService:
    """Handles AI-powered analysis of social media posts for hazard detection."""
    
    def __init__(self):
        """Initialize the AI analysis service."""
        self.deepseek_api_key = os.getenv('DEEPSEEK_API_KEY')
        self.deepseek_base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://api.deepseek.com')
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', 0.75))
        
        # Classification prompts
        self.system_prompt = """You are an expert disaster response analyst specializing in social media monitoring for natural hazards in India. Your task is to analyze social media posts and classify them for potential flood, tsunami, high wave, and cyclone threats.

You must respond with ONLY a valid JSON object containing the following fields:
- "relevance": "hazard" or "non-hazard" 
- "hazard_type": "Flood", "Tsunami", "High Wave", "Storm Surge", "Cyclone", or "Other" (only if relevance is "hazard")
- "urgency": "Low", "Medium", or "High"
- "confidence": a decimal between 0.0 and 1.0
- "reasoning": brief explanation of your classification

Guidelines:
- "hazard": Posts describing actual water-related emergencies, flooding, tsunamis, high waves, storm surges, cyclones
- "non-hazard": News articles, weather forecasts, historical events, jokes, unrelated content
- Urgency "High": Immediate danger, calls for help, evacuation needs
- Urgency "Medium": Developing situation, warnings, preparation advice  
- Urgency "Low": Minor flooding, past events, general concerns
- Confidence: How certain you are (0.8+ for clear cases, 0.5-0.7 for uncertain, <0.5 for very unclear)

Focus on content indicating real-time hazardous conditions in India."""

        if not self.deepseek_api_key:
            logger.warning("DeepSeek API key not found. AI analysis will be unavailable.")
        
        logger.info("AI analysis service initialized")
    
    async def analyze_posts(self, processed_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Analyze processed posts for hazard classification.
        
        Args:
            processed_posts: List of preprocessed posts
            
        Returns:
            List of posts with AI analysis results
        """
        if not self.deepseek_api_key:
            logger.error("Cannot perform AI analysis: DeepSeek API key not configured")
            return processed_posts
        
        logger.info(f"Starting AI analysis of {len(processed_posts)} posts")
        
        analyzed_posts = []
        batch_size = 10  # Process in batches to avoid rate limits
        
        for i in range(0, len(processed_posts), batch_size):
            batch = processed_posts[i:i + batch_size]
            batch_results = await self._analyze_batch(batch)
            analyzed_posts.extend(batch_results)
            
            # Small delay between batches to respect rate limits
            if i + batch_size < len(processed_posts):
                await asyncio.sleep(1)
        
        # Filter by confidence threshold
        high_confidence_posts = [
            post for post in analyzed_posts 
            if post.get('ai_analysis', {}).get('confidence', 0) >= self.confidence_threshold
        ]
        
        logger.info(f"AI analysis complete. {len(high_confidence_posts)} posts above confidence threshold")
        return analyzed_posts
    
    async def _analyze_batch(self, posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Analyze a batch of posts."""
        tasks = [self._analyze_single_post(post) for post in posts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        analyzed_posts = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Error analyzing post {posts[i].get('id')}: {str(result)}")
                # Add default analysis for failed posts
                posts[i]['ai_analysis'] = self._get_default_analysis()
                analyzed_posts.append(posts[i])
            else:
                analyzed_posts.append(result)
        
        return analyzed_posts
    
    async def _analyze_single_post(self, post: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single post using DeepSeek API."""
        text = post.get('cleaned_text', post.get('text', ''))
        location_info = post.get('inferred_location', {})
        
        # Build analysis prompt
        user_prompt = self._build_analysis_prompt(text, location_info)
        
        try:
            analysis_result = await self._call_deepseek_api(user_prompt)
            post['ai_analysis'] = analysis_result
            
            # Add derived fields for easier filtering
            post['is_hazard'] = analysis_result.get('relevance') == 'hazard'
            post['meets_confidence_threshold'] = analysis_result.get('confidence', 0) >= self.confidence_threshold
            
        except Exception as e:
            logger.error(f"Error in AI analysis for post {post.get('id')}: {str(e)}")
            post['ai_analysis'] = self._get_default_analysis()
            post['is_hazard'] = False
            post['meets_confidence_threshold'] = False
        
        return post
    
    def _build_analysis_prompt(self, text: str, location_info: Dict) -> str:
        """Build the analysis prompt for a specific post."""
        location_context = ""
        if location_info:
            city = location_info.get('city', 'Unknown')
            state = location_info.get('state', 'Unknown')
            location_context = f"\nLocation context: {city}, {state}, India"
        
        prompt = f"""Analyze this social media post for water-related hazards in India:

Text: "{text}"{location_context}

Classify this post according to the guidelines provided."""
        
        return prompt
    
    async def _call_deepseek_api(self, user_prompt: str) -> Dict[str, Any]:
        """Make API call to DeepSeek for analysis."""
        url = f"{self.deepseek_base_url}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.deepseek_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': 'deepseek-chat',
            'messages': [
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': 0.1,  # Low temperature for consistent classification
            'max_tokens': 200
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result['choices'][0]['message']['content'].strip()
                    
                    try:
                        # Parse JSON response
                        analysis = json.loads(content)
                        return self._validate_analysis_result(analysis)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse AI response as JSON: {content}")
                        return self._get_default_analysis()
                else:
                    error_text = await response.text()
                    logger.error(f"DeepSeek API error {response.status}: {error_text}")
                    raise Exception(f"API error: {response.status}")
    
    def _validate_analysis_result(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and normalize the analysis result."""
        # Set defaults for missing fields
        validated = {
            'relevance': analysis.get('relevance', 'non-hazard'),
            'hazard_type': analysis.get('hazard_type', 'Other'),
            'urgency': analysis.get('urgency', 'Low'),
            'confidence': float(analysis.get('confidence', 0.0)),
            'reasoning': analysis.get('reasoning', 'No reasoning provided')
        }
        
        # Validate relevance
        if validated['relevance'] not in ['hazard', 'non-hazard']:
            validated['relevance'] = 'non-hazard'
        
        # Validate hazard_type
        valid_hazard_types = ['Flood', 'Tsunami', 'High Wave', 'Storm Surge', 'Cyclone', 'Other']
        if validated['hazard_type'] not in valid_hazard_types:
            validated['hazard_type'] = 'Other'
        
        # Validate urgency
        if validated['urgency'] not in ['Low', 'Medium', 'High']:
            validated['urgency'] = 'Low'
        
        # Validate confidence
        if not (0.0 <= validated['confidence'] <= 1.0):
            validated['confidence'] = 0.0
        
        # If non-hazard, set hazard_type to None
        if validated['relevance'] == 'non-hazard':
            validated['hazard_type'] = None
        
        return validated
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Get default analysis for failed cases."""
        return {
            'relevance': 'non-hazard',
            'hazard_type': None,
            'urgency': 'Low',
            'confidence': 0.0,
            'reasoning': 'Analysis failed - default classification applied'
        }
    
    def get_hazard_posts(self, analyzed_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter posts that are classified as hazards with sufficient confidence."""
        return [
            post for post in analyzed_posts
            if (post.get('is_hazard', False) and 
                post.get('meets_confidence_threshold', False))
        ]
    
    def get_posts_by_hazard_type(self, analyzed_posts: List[Dict[str, Any]], hazard_type: str) -> List[Dict[str, Any]]:
        """Filter posts by specific hazard type."""
        return [
            post for post in analyzed_posts
            if (post.get('ai_analysis', {}).get('hazard_type') == hazard_type and
                post.get('meets_confidence_threshold', False))
        ]
    
    def get_urgent_posts(self, analyzed_posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter posts with high urgency classification."""
        return [
            post for post in analyzed_posts
            if (post.get('ai_analysis', {}).get('urgency') == 'High' and
                post.get('meets_confidence_threshold', False))
        ]
    
    def get_analysis_summary(self, analyzed_posts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary statistics of the analysis results."""
        total_posts = len(analyzed_posts)
        hazard_posts = len(self.get_hazard_posts(analyzed_posts))
        high_confidence = len([p for p in analyzed_posts if p.get('meets_confidence_threshold', False)])
        urgent_posts = len(self.get_urgent_posts(analyzed_posts))
        
        hazard_type_counts = {}
        urgency_counts = {'Low': 0, 'Medium': 0, 'High': 0}
        
        for post in analyzed_posts:
            analysis = post.get('ai_analysis', {})
            hazard_type = analysis.get('hazard_type')
            urgency = analysis.get('urgency', 'Low')
            
            if hazard_type and post.get('meets_confidence_threshold', False):
                hazard_type_counts[hazard_type] = hazard_type_counts.get(hazard_type, 0) + 1
            
            if post.get('meets_confidence_threshold', False):
                urgency_counts[urgency] += 1
        
        return {
            'total_posts_analyzed': total_posts,
            'hazard_posts_detected': hazard_posts,
            'high_confidence_posts': high_confidence,
            'urgent_posts': urgent_posts,
            'hazard_type_breakdown': hazard_type_counts,
            'urgency_breakdown': urgency_counts,
            'confidence_threshold': self.confidence_threshold
        }
