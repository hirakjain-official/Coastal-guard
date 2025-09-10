"""
Internet Verification Service
Searches Reddit, Google News, and other sources to verify the seriousness of detected hazard situations.
"""

import os
import re
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import json


class InternetVerificationService:
    """Handles internet search verification of detected hazard situations."""
    
    def __init__(self):
        """Initialize the internet verification service."""
        self.reddit_search_enabled = True
        self.news_search_enabled = True
        self.max_search_results = 10
        
        # Reddit API endpoints (using public API without authentication for basic search)
        self.reddit_search_url = "https://www.reddit.com/search.json"
        
        # News search using RSS feeds and public APIs
        self.news_sources = [
            "https://news.google.com/rss/search",
            "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
            "https://feeds.feedburner.com/ndtvnews-top-stories",
            "https://www.thehindu.com/news/national/?service=rss"
        ]
        
        logger.info("Internet verification service initialized")
    
    async def verify_situation(self, hazard_posts: List[Dict[str, Any]], location: str, hazard_type: str) -> Dict[str, Any]:
        """
        Verify a detected hazard situation by searching internet sources.
        
        Args:
            hazard_posts: List of X posts that triggered the detection
            location: Location of the detected situation
            hazard_type: Type of hazard detected
            
        Returns:
            Verification results with seriousness assessment
        """
        logger.info(f"Starting internet verification for {hazard_type} in {location}")
        
        # Generate search terms based on posts and location
        search_terms = self._generate_search_terms(hazard_posts, location, hazard_type)
        
        verification_results = {
            'verification_timestamp': datetime.now().isoformat(),
            'location': location,
            'hazard_type': hazard_type,
            'search_terms_used': search_terms,
            'reddit_results': [],
            'news_results': [],
            'verification_summary': {},
            'seriousness_assessment': 'unknown'
        }
        
        # Search Reddit
        if self.reddit_search_enabled:
            reddit_results = await self._search_reddit(search_terms)
            verification_results['reddit_results'] = reddit_results
        
        # Search news sources
        if self.news_search_enabled:
            news_results = await self._search_news_sources(search_terms)
            verification_results['news_results'] = news_results
        
        # Analyze verification results
        verification_results['verification_summary'] = self._analyze_verification_results(
            verification_results['reddit_results'],
            verification_results['news_results']
        )
        
        # Assess overall seriousness
        verification_results['seriousness_assessment'] = self._assess_seriousness(
            hazard_posts, 
            verification_results['verification_summary']
        )
        
        logger.info(f"Internet verification completed - Assessment: {verification_results['seriousness_assessment']}")
        return verification_results
    
    def _generate_search_terms(self, posts: List[Dict[str, Any]], location: str, hazard_type: str) -> List[str]:
        """Generate relevant search terms from posts and situation context."""
        search_terms = []
        
        # Add location-based terms
        if location and location != "Unknown Location":
            location_parts = location.split(', ')
            search_terms.extend(location_parts)
        
        # Add hazard type terms
        hazard_keywords = {
            'Flood': ['flood', 'flooding', 'waterlogged', 'inundation'],
            'Tsunami': ['tsunami', 'sea waves', 'tidal waves'],
            'High Wave': ['high waves', 'rough seas', 'wave surge'],
            'Storm Surge': ['storm surge', 'sea level rise', 'coastal flooding'],
            'Cyclone': ['cyclone', 'hurricane', 'typhoon', 'storm']
        }
        
        if hazard_type in hazard_keywords:
            search_terms.extend(hazard_keywords[hazard_type])
        
        # Extract key terms from post content
        for post in posts[:5]:  # Analyze first 5 posts
            text = post.get('cleaned_text', '')
            # Extract hashtags
            hashtags = re.findall(r'#\w+', text.lower())
            search_terms.extend([tag.replace('#', '') for tag in hashtags])
            
            # Extract urgent keywords
            urgent_keywords = ['emergency', 'rescue', 'evacuation', 'disaster', 'urgent', 'help']
            for keyword in urgent_keywords:
                if keyword in text.lower():
                    search_terms.append(keyword)
        
        # Remove duplicates and limit
        unique_terms = list(set(search_terms))
        return unique_terms[:10]  # Limit to 10 most relevant terms
    
    async def _search_reddit(self, search_terms: List[str]) -> List[Dict[str, Any]]:
        """Search Reddit for relevant discussions."""
        reddit_results = []
        
        try:
            # Combine search terms for Reddit query
            query = " OR ".join(search_terms[:5])  # Limit to avoid too broad search
            
            params = {
                'q': query,
                'limit': self.max_search_results,
                'sort': 'new',
                'type': 'link',
                't': 'day'  # Last day
            }
            
            async with aiohttp.ClientSession() as session:
                # Add user agent to avoid blocking
                headers = {
                    'User-Agent': 'SocialMediaAnalyticsAgent/1.0 (Disaster Response Research)'
                }
                
                async with session.get(self.reddit_search_url, params=params, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if 'data' in data and 'children' in data['data']:
                            for item in data['data']['children'][:self.max_search_results]:
                                post_data = item.get('data', {})
                                
                                reddit_result = {
                                    'title': post_data.get('title', ''),
                                    'url': post_data.get('url', ''),
                                    'score': post_data.get('score', 0),
                                    'num_comments': post_data.get('num_comments', 0),
                                    'created_utc': post_data.get('created_utc', 0),
                                    'subreddit': post_data.get('subreddit', ''),
                                    'author': post_data.get('author', ''),
                                    'selftext': post_data.get('selftext', '')[:200],  # First 200 chars
                                    'relevance_score': self._calculate_relevance_score(
                                        post_data.get('title', '') + ' ' + post_data.get('selftext', ''),
                                        search_terms
                                    )
                                }
                                
                                reddit_results.append(reddit_result)
                    else:
                        logger.warning(f"Reddit search failed with status: {response.status}")
        
        except Exception as e:
            logger.error(f"Error searching Reddit: {str(e)}")
        
        # Sort by relevance and recency
        reddit_results.sort(key=lambda x: (x['relevance_score'], x['score']), reverse=True)
        return reddit_results[:5]  # Return top 5 most relevant
    
    async def _search_news_sources(self, search_terms: List[str]) -> List[Dict[str, Any]]:
        """Search news sources for relevant coverage."""
        news_results = []
        
        try:
            # For news search, we'll use Google News RSS
            query = " ".join(search_terms[:3])  # Simpler query for news
            
            google_news_url = f"https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"
            
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                }
                
                try:
                    async with session.get(google_news_url, headers=headers, timeout=10) as response:
                        if response.status == 200:
                            content = await response.text()
                            
                            # Simple RSS parsing (in production, use proper XML parser)
                            import xml.etree.ElementTree as ET
                            
                            try:
                                root = ET.fromstring(content)
                                
                                for item in root.findall('.//item')[:self.max_search_results]:
                                    title = item.find('title')
                                    link = item.find('link')
                                    pub_date = item.find('pubDate')
                                    description = item.find('description')
                                    source = item.find('source')
                                    
                                    news_result = {
                                        'title': title.text if title is not None else '',
                                        'url': link.text if link is not None else '',
                                        'published_date': pub_date.text if pub_date is not None else '',
                                        'description': description.text if description is not None else '',
                                        'source': source.text if source is not None else 'Google News',
                                        'relevance_score': self._calculate_relevance_score(
                                            (title.text if title is not None else '') + ' ' + 
                                            (description.text if description is not None else ''),
                                            search_terms
                                        )
                                    }
                                    
                                    news_results.append(news_result)
                            except ET.ParseError as e:
                                logger.error(f"Error parsing RSS feed: {str(e)}")
                
                except Exception as e:
                    logger.error(f"Error fetching Google News: {str(e)}")
        
        except Exception as e:
            logger.error(f"Error in news search: {str(e)}")
        
        # Sort by relevance
        news_results.sort(key=lambda x: x['relevance_score'], reverse=True)
        return news_results[:5]  # Return top 5 most relevant
    
    def _calculate_relevance_score(self, text: str, search_terms: List[str]) -> float:
        """Calculate relevance score for a piece of text."""
        if not text or not search_terms:
            return 0.0
        
        text_lower = text.lower()
        score = 0.0
        
        for term in search_terms:
            if term.lower() in text_lower:
                # Weight by term frequency
                count = text_lower.count(term.lower())
                score += count * (1.0 / len(search_terms))
        
        return min(score, 1.0)  # Cap at 1.0
    
    def _analyze_verification_results(self, reddit_results: List[Dict], news_results: List[Dict]) -> Dict[str, Any]:
        """Analyze verification results to summarize findings."""
        summary = {
            'total_reddit_posts': len(reddit_results),
            'total_news_articles': len(news_results),
            'high_relevance_reddit': len([r for r in reddit_results if r['relevance_score'] > 0.7]),
            'high_relevance_news': len([n for n in news_results if n['relevance_score'] > 0.7]),
            'reddit_engagement': {
                'total_score': sum(r['score'] for r in reddit_results),
                'total_comments': sum(r['num_comments'] for r in reddit_results),
                'avg_score': sum(r['score'] for r in reddit_results) / len(reddit_results) if reddit_results else 0
            },
            'keywords_found': set(),
            'sources_found': set()
        }
        
        # Extract keywords and sources
        for result in reddit_results:
            summary['keywords_found'].update(self._extract_keywords(result.get('title', '') + ' ' + result.get('selftext', '')))
            summary['sources_found'].add(f"r/{result.get('subreddit', 'unknown')}")
        
        for result in news_results:
            summary['keywords_found'].update(self._extract_keywords(result.get('title', '') + ' ' + result.get('description', '')))
            summary['sources_found'].add(result.get('source', 'unknown'))
        
        # Convert sets to lists for JSON serialization
        summary['keywords_found'] = list(summary['keywords_found'])
        summary['sources_found'] = list(summary['sources_found'])
        
        return summary
    
    def _extract_keywords(self, text: str) -> set:
        """Extract relevant keywords from text."""
        keywords = set()
        
        # Disaster-related keywords
        disaster_keywords = [
            'emergency', 'disaster', 'evacuation', 'rescue', 'urgent', 'critical',
            'flooding', 'flooded', 'inundated', 'waterlogged', 'submerged',
            'tsunami', 'waves', 'surge', 'cyclone', 'storm', 'hurricane',
            'casualties', 'damage', 'affected', 'stranded', 'trapped'
        ]
        
        text_lower = text.lower()
        for keyword in disaster_keywords:
            if keyword in text_lower:
                keywords.add(keyword)
        
        return keywords
    
    def _assess_seriousness(self, original_posts: List[Dict], verification_summary: Dict) -> str:
        """Assess the overall seriousness of the situation based on all available information."""
        
        # Count high urgency posts
        high_urgency_posts = len([
            p for p in original_posts 
            if p.get('ai_analysis', {}).get('urgency') == 'High'
        ])
        
        # Count high confidence posts
        high_confidence_posts = len([
            p for p in original_posts 
            if p.get('ai_analysis', {}).get('confidence', 0) >= 0.8
        ])
        
        # Internet verification signals
        reddit_engagement = verification_summary['reddit_engagement']['total_score'] + verification_summary['reddit_engagement']['total_comments']
        high_relevance_sources = verification_summary['high_relevance_reddit'] + verification_summary['high_relevance_news']
        
        # Scoring system
        seriousness_score = 0
        
        # Original posts indicators (40% weight)
        if high_urgency_posts >= 3:
            seriousness_score += 15
        elif high_urgency_posts >= 1:
            seriousness_score += 8
        
        if high_confidence_posts >= 5:
            seriousness_score += 15
        elif high_confidence_posts >= 2:
            seriousness_score += 8
        
        if len(original_posts) >= 20:
            seriousness_score += 10
        elif len(original_posts) >= 10:
            seriousness_score += 5
        
        # Internet verification indicators (35% weight)
        if high_relevance_sources >= 3:
            seriousness_score += 15
        elif high_relevance_sources >= 1:
            seriousness_score += 8
        
        if reddit_engagement >= 100:  # High engagement
            seriousness_score += 10
        elif reddit_engagement >= 20:
            seriousness_score += 5
        
        if verification_summary['total_news_articles'] >= 2:
            seriousness_score += 10
        elif verification_summary['total_news_articles'] >= 1:
            seriousness_score += 5
        
        # Keyword severity (25% weight)
        critical_keywords = ['emergency', 'disaster', 'evacuation', 'rescue', 'casualties', 'critical']
        found_critical = len([kw for kw in verification_summary['keywords_found'] if kw in critical_keywords])
        
        if found_critical >= 3:
            seriousness_score += 15
        elif found_critical >= 1:
            seriousness_score += 8
        
        # Determine final assessment
        if seriousness_score >= 70:
            return 'CRITICAL'
        elif seriousness_score >= 50:
            return 'HIGH'
        elif seriousness_score >= 30:
            return 'MEDIUM'
        elif seriousness_score >= 10:
            return 'LOW'
        else:
            return 'MINIMAL'
    
    def get_verification_summary_text(self, verification_results: Dict[str, Any]) -> str:
        """Generate a human-readable summary of verification results."""
        assessment = verification_results['seriousness_assessment']
        summary = verification_results['verification_summary']
        
        text_parts = [f"**Seriousness Assessment: {assessment}**\n"]
        
        # Reddit findings
        if summary['total_reddit_posts'] > 0:
            text_parts.append(f"📱 Reddit: {summary['total_reddit_posts']} discussions found")
            if summary['reddit_engagement']['total_score'] > 0:
                text_parts.append(f"   - Total engagement: {summary['reddit_engagement']['total_score']} upvotes, {summary['reddit_engagement']['total_comments']} comments")
        
        # News findings
        if summary['total_news_articles'] > 0:
            text_parts.append(f"📰 News: {summary['total_news_articles']} articles found")
        
        # Key indicators
        if summary['keywords_found']:
            critical_found = [kw for kw in summary['keywords_found'] if kw in ['emergency', 'disaster', 'evacuation', 'rescue']]
            if critical_found:
                text_parts.append(f"⚠️  Critical keywords found: {', '.join(critical_found)}")
        
        return "\n".join(text_parts)
