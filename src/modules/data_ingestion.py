"""
Data Ingestion Service
Handles fetching social media posts from Twitter/X API via RapidAPI and other sources.
"""

import os
import asyncio
import aiohttp
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from loguru import logger
import tweepy
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DataIngestionService:
    """Handles data ingestion from social media platforms."""
    
    def __init__(self):
        """Initialize the data ingestion service with API credentials."""
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        self.rapidapi_host = os.getenv('RAPIDAPI_HOST', 'twitter-api47.p.rapidapi.com')
        self.twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        
        # Initialize Twitter API client
        if self.twitter_bearer_token:
            self.twitter_client = tweepy.Client(bearer_token=self.twitter_bearer_token)
        else:
            self.twitter_client = None
            logger.warning("Twitter Bearer Token not found. Twitter API will be unavailable.")
        
        # Hazard-related hashtags and keywords for India
        self.hashtags = [
            # English hashtags
            '#flood', '#tsunami', '#highwaves', '#cyclone', '#storm', 
            '#flooding', '#heavyrain', '#waterlogging', '#surge',
            
            # Regional language hashtags
            '#बाढ़', '#baadh', '#सुनामी', '#tsunami', '#तूफान', '#toofan',
            '#समुद्री_लहरें', '#samudra', '#samudrabay', '#चक्रवात',
            
            # Tamil
            '#வெள்ளம்', '#சுனामி', '#புயல்',
            
            # Telugu  
            '#వరద', '#సునామి', '#తుఫాను',
            
            # Bengali
            '#বন্যা', '#সুনামি', '#ঝড়'
        ]
        
        self.keywords = [
            'flood', 'flooding', 'waterlogged', 'tsunami', 'high waves', 
            'cyclone', 'storm surge', 'heavy rain', 'water level rising',
            'coastal flooding', 'sea level', 'waves hitting', 'evacuation',
            'emergency', 'rescue', 'disaster',
            
            # Regional keywords
            'बाढ़', 'पानी', 'तूफान', 'लहरें', 'आपातकाल',
            'வெள்ளம்', 'நீர்', 'புயல்', 'அலைகள்',
            'వరద', 'నీరు', 'తుఫాను', 'అలలు',
            'বন্যা', 'পানি', 'ঝড়', 'ঢেউ'
        ]
        
        # India bounding box coordinates (approximate)
        self.india_bbox = {
            'south': 6.4627,
            'west': 68.1097,  
            'north': 35.5044,
            'east': 97.3953
        }
        
        logger.info("Data ingestion service initialized")
    
    async def fetch_social_media_posts(
        self, 
        start_time: datetime, 
        end_time: datetime,
        geo_filter: str = 'India'
    ) -> List[Dict[str, Any]]:
        """
        Fetch social media posts from multiple sources within the specified time window.
        
        Args:
            start_time: Start of the time window
            end_time: End of the time window
            geo_filter: Geographic filter (default: 'India')
            
        Returns:
            List of raw social media posts
        """
        all_posts = []
        
        logger.info(f"Fetching posts from {start_time} to {end_time}")
        
        # Fetch from Twitter via RapidAPI
        if self.rapidapi_key:
            rapidapi_posts = await self._fetch_from_rapidapi(start_time, end_time)
            all_posts.extend(rapidapi_posts)
            logger.info(f"Fetched {len(rapidapi_posts)} posts from RapidAPI")
        
        # Fetch from Twitter API v2 directly
        if self.twitter_client:
            twitter_posts = await self._fetch_from_twitter_api(start_time, end_time)
            all_posts.extend(twitter_posts)
            logger.info(f"Fetched {len(twitter_posts)} posts from Twitter API")
        
        # If no posts were fetched from any API, log the issue
        if len(all_posts) == 0:
            if not self.rapidapi_key and not self.twitter_client:
                logger.warning("No API credentials configured - no posts can be fetched")
            else:
                logger.warning(f"No posts fetched despite having API credentials - RapidAPI: {'Yes' if self.rapidapi_key else 'No'}, Twitter: {'Yes' if self.twitter_client else 'No'}")
        
        logger.info(f"Total posts fetched: {len(all_posts)}")
        return all_posts
    
    async def _fetch_from_rapidapi(
        self, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch posts from Twitter via RapidAPI."""
        posts = []
        
        headers = {
            'X-RapidAPI-Key': self.rapidapi_key,
            'X-RapidAPI-Host': self.rapidapi_host
        }
        
        url = f"https://{self.rapidapi_host}/v2/search"
        
        params = {
            "query": '#flood OR #tsunami OR #highwaves OR #cyclone OR #storm OR #flooding OR #heavyrain OR #waterlogging OR #surge OR #बाढ़ OR "flood" OR "flooding" OR "waterlogged" OR "tsunami" OR "high waves" OR "cyclone" OR "storm surge" OR "heavy rain" OR "water level rising" OR "coastal flooding"',
            "type": "Latest",
            "max_results": "100"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'tweets' in data:
                            for tweet in data['tweets']:
                                post = self._format_rapidapi_post(tweet)
                                if self._is_india_relevant(post):
                                    posts.append(post)
                    else:
                        error_text = await response.text()
                        logger.error(f"RapidAPI request failed: {response.status} - {error_text}")
                        logger.error(f"Request URL: {url}")
                        logger.error(f"Request params: {params}")
                        
        except Exception as e:
            logger.error(f"Error fetching from RapidAPI: {str(e)}")
        
        return posts
    
    async def _fetch_from_twitter_api(
        self, 
        start_time: datetime, 
        end_time: datetime
    ) -> List[Dict[str, Any]]:
        """Fetch posts from Twitter API v2."""
        posts = []
        
        # Build search query
        hashtag_query = ' OR '.join(self.hashtags[:10])
        keyword_query = ' OR '.join([f'"{kw}"' for kw in self.keywords[:10]])
        full_query = f"({hashtag_query}) OR ({keyword_query}) lang:en -is:retweet"
        
        try:
            tweets = tweepy.Paginator(
                self.twitter_client.search_recent_tweets,
                query=full_query,
                start_time=start_time,
                end_time=end_time,
                max_results=100,
                tweet_fields=['created_at', 'author_id', 'public_metrics', 'geo', 'lang', 'context_annotations']
            ).flatten(limit=1000)
            
            for tweet in tweets:
                post = self._format_twitter_post(tweet)
                if self._is_india_relevant(post):
                    posts.append(post)
                    
        except Exception as e:
            logger.error(f"Error fetching from Twitter API: {str(e)}")
        
        return posts
    
    def _format_rapidapi_post(self, tweet_data: Dict) -> Dict[str, Any]:
        """Format a RapidAPI tweet into our standard post format."""
        try:
            # Extract tweet data from nested structure
            content = tweet_data.get('content', {})
            item_content = content.get('itemContent', {})
            tweet_results = item_content.get('tweet_results', {})
            result = tweet_results.get('result', {})
            
            # Get tweet text from legacy field
            tweet_text = result.get('legacy', {}).get('full_text', '') or result.get('legacy', {}).get('text', '')
            
            # Get user info
            user_results = result.get('core', {}).get('user_results', {})
            user_result = user_results.get('result', {})
            user_legacy = user_result.get('legacy', {})
            
            # Get metrics
            legacy = result.get('legacy', {})
            
            return {
                'id': tweet_data.get('entryId', ''),
                'text': tweet_text,
                'created_at': legacy.get('created_at', ''),
                'author_id': user_result.get('rest_id', ''),
                'author_username': user_legacy.get('screen_name', ''),
                'retweet_count': legacy.get('retweet_count', 0),
                'like_count': legacy.get('favorite_count', 0),
                'geo': legacy.get('geo'),
                'language': legacy.get('lang', 'unknown'),
                'source': 'rapidapi_twitter',
                'raw_data': tweet_data
            }
        except Exception as e:
            logger.error(f"Error formatting RapidAPI post: {str(e)} - Data: {tweet_data}")
            # Return basic structure with fallback values
            return {
                'id': tweet_data.get('entryId', 'unknown'),
                'text': str(tweet_data.get('content', '')),
                'created_at': '',
                'author_id': '',
                'author_username': '',
                'retweet_count': 0,
                'like_count': 0,
                'geo': None,
                'language': 'unknown',
                'source': 'rapidapi_twitter',
                'raw_data': tweet_data
            }
    
    def _format_twitter_post(self, tweet) -> Dict[str, Any]:
        """Format a Twitter API v2 tweet into our standard post format."""
        metrics = tweet.public_metrics or {}
        
        return {
            'id': str(tweet.id),
            'text': tweet.text,
            'created_at': tweet.created_at.isoformat() if tweet.created_at else None,
            'author_id': str(tweet.author_id),
            'author_username': None,  # Would need user lookup
            'retweet_count': metrics.get('retweet_count', 0),
            'like_count': metrics.get('like_count', 0),
            'geo': tweet.geo,
            'language': tweet.lang,
            'source': 'twitter_api_v2',
            'raw_data': tweet.data
        }
    
    def _is_india_relevant(self, post: Dict[str, Any]) -> bool:
        """
        Check if a post is relevant to India based on geo-location or text content.
        
        Args:
            post: Formatted post dictionary
            
        Returns:
            True if post is India-relevant
        """
        try:
            # Check geo-location if available
            if post.get('geo'):
                geo = post['geo']
                if isinstance(geo, dict) and 'coordinates' in geo:
                    coords = geo['coordinates']
                    if isinstance(coords, (list, tuple)) and len(coords) >= 2:
                        if (self.india_bbox['south'] <= coords[1] <= self.india_bbox['north'] and
                            self.india_bbox['west'] <= coords[0] <= self.india_bbox['east']):
                            return True
            
            # Check text content for Indian city/state mentions
            text_value = post.get('text', '')
            # Ensure text is a string before calling .lower()
            if not isinstance(text_value, str):
                logger.warning(f"Post text is not a string: {type(text_value)} - {text_value}")
                return False
            
            text = text_value.lower()
            indian_locations = [
                'mumbai', 'delhi', 'bangalore', 'hyderabad', 'ahmedabad', 'chennai',
                'kolkata', 'pune', 'jaipur', 'lucknow', 'kanpur', 'nagpur',
                'visakhapatnam', 'vizag', 'bhubaneswar', 'kochi', 'kozhikode',
                'thiruvananthapuram', 'goa', 'panaji', 'gujarat', 'maharashtra',
                'karnataka', 'tamil nadu', 'kerala', 'andhra pradesh', 'telangana',
                'west bengal', 'odisha', 'rajasthan', 'uttar pradesh', 'bihar',
                'jharkhand', 'chhattisgarh', 'madhya pradesh', 'haryana', 'punjab',
                'himachal pradesh', 'uttarakhand', 'jammu', 'kashmir', 'assam',
                'manipur', 'meghalaya', 'tripura', 'mizoram', 'nagaland', 'arunachal pradesh',
                'india', 'indian', 'भारत', 'हिन्दुस्तान'
            ]
            
            for location in indian_locations:
                if location in text:
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error in _is_india_relevant: {str(e)} - Post: {post}")
            return False
