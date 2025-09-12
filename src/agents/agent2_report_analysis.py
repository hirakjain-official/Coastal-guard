"""
Agent 2 - Report Analysis Engine
Processes user reports, generates search keywords via LLM, and correlates with social media data.
"""

import os
import json
import asyncio
import aiohttp
import uuid
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Tuple
from loguru import logger
import math
import re

class ReportAnalysisAgent:
    """Agent 2: Processes user reports and correlates with social media data"""
    
    def __init__(self):
        self.deepseek_api_key = os.getenv('OPENROUTER_API_KEY') or os.getenv('DEEPSEEK_API_KEY')
        self.deepseek_base_url = os.getenv('DEEPSEEK_BASE_URL', 'https://openrouter.ai/api/v1')
        self.model_name = os.getenv('DEEPSEEK_MODEL', 'deepseek/deepseek-chat')
        
        # RapidAPI Twitter configuration
        self.rapidapi_key = os.getenv('RAPIDAPI_KEY')
        self.twitter_api_url = "https://twitter-api47.p.rapidapi.com/v2/search"
        self.twitter_headers = {
            "X-RapidAPI-Key": self.rapidapi_key,
            "X-RapidAPI-Host": "twitter-api47.p.rapidapi.com"
        }
        
        # Keyword generation prompt
        self.keyword_generation_prompt = """You are an expert in social media search optimization for disaster monitoring in India. Your task is to generate effective search keywords for Twitter/X based on a user's disaster report.

Given a user report about a potential disaster/hazard, generate comprehensive search keywords that would help find related social media posts.

You must respond with ONLY a valid JSON object containing:
- "primary_keywords": List of main search terms (3-5 keywords)
- "location_keywords": List of location-specific terms (include variations, local names)
- "hashtag_suggestions": List of relevant hashtags (5-8 hashtags)
- "combined_queries": List of complete search query strings ready for Twitter API (3-4 queries)
- "language_variations": Keywords in local languages if relevant

Guidelines:
- Focus on Indian coastal areas and disaster types
- Include local language variations (Hindi, Tamil, Telugu, etc.)
- Consider local place name variations (Mumbai/Bombay, Chennai/Madras, etc.)
- Create comprehensive but targeted search queries
- Include urgency indicators (emergency, help, rescue, etc.)
- Consider temporal aspects (happening now, ongoing, etc.)

Example format:
{
    "primary_keywords": ["flood", "waterlogging", "heavy rain"],
    "location_keywords": ["mumbai", "bombay", "maharashtra", "andheri"],
    "hashtag_suggestions": ["#MumbaiFloods", "#MumbaiRains", "#Emergency"],
    "combined_queries": ["flood mumbai urgent", "waterlogging andheri help", "#MumbaiFloods rescue"],
    "language_variations": ["बाढ़ मुंबई", "వరద ముంబై"]
}"""

        # Multilingual Hazard Analysis Prompt - EXACT USER SPECIFICATION
        self.hazard_analysis_prompt = """You are an expert multilingual AI agent specializing in ocean hazard monitoring and disaster intelligence for India. 
You analyze real-time citizen and social media reports about hazards such as floods, tsunamis, storm surges, coastal erosion, high waves, and abnormal tides. 
Posts may be in English, Hindi, Tamil, Telugu, Malayalam, Bengali, Odia, Gujarati, or mixed code-switching. 

Your responsibilities:
- Accurately translate or interpret posts into English internally (do not output translations unless asked).
- Preserve local context, idioms, and colloquial hazard expressions (e.g., "samundar ka paani ghus gaya" = "seawater intrusion").
- Detect hazard types, urgency, and credibility across multiple languages.
- Always normalize your final outputs in English, but you may mention the detected original language if relevant.
- Accuracy and credibility are critical; avoid speculation, but highlight confidence levels.
- Use historical hazard knowledge and seasonal patterns in India to strengthen context.
- Produce structured, machine-parseable JSON outputs only."""

        logger.info("Agent 2 (Report Analysis) initialized")

    async def process_user_report(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a user report through the complete analysis pipeline.
        
        Args:
            report_data: User report dictionary with location, description, etc.
            
        Returns:
            Enhanced report data with keywords and correlations
        """
        logger.info(f"Processing user report: {report_data.get('title', 'Untitled')}")
        
        try:
            # Step 1: Generate search keywords using LLM
            keywords_data = await self._generate_search_keywords(report_data)
            report_data['generated_keywords'] = keywords_data
            
            # Step 2: Search social media using generated keywords
            social_media_matches = await self._search_social_media_correlations(
                keywords_data, report_data
            )
            
            # Step 3: Analyze correlations with found posts
            correlations = await self._analyze_correlations(report_data, social_media_matches)
            report_data['social_media_correlations'] = correlations
            
            # Step 4: Calculate overall correlation confidence
            report_data['correlation_confidence'] = self._calculate_overall_confidence(correlations)
            
            logger.info(f"Report analysis complete. Found {len(correlations)} correlations with confidence {report_data['correlation_confidence']:.2f}")
            
            return report_data
            
        except Exception as e:
            logger.error(f"Error processing user report: {str(e)}")
            report_data['processing_error'] = str(e)
            report_data['correlation_confidence'] = 0.0
            return report_data

    async def _generate_search_keywords(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimized search keywords using LLM."""
        
        # Build context for LLM
        location_context = ""
        if report_data.get('city') or report_data.get('state'):
            city = report_data.get('city', 'Unknown')
            state = report_data.get('state', 'Unknown')
            location_context = f"Location: {city}, {state}, India"
        
        if report_data.get('latitude') and report_data.get('longitude'):
            location_context += f" (Coordinates: {report_data['latitude']}, {report_data['longitude']})"

        user_prompt = f"""Generate search keywords for this disaster report:

Title: "{report_data.get('title', '')}"
Description: "{report_data.get('description', '')}"
Hazard Type: {report_data.get('hazard_type', 'Unknown')}
Severity: {report_data.get('severity', 'Unknown')}
{location_context}
Reported At: {report_data.get('created_at', datetime.now().isoformat())}

Generate comprehensive search keywords to find related social media posts."""

        try:
            keywords_result = await self._call_deepseek_api(
                self.keyword_generation_prompt, 
                user_prompt
            )
            return keywords_result
            
        except Exception as e:
            logger.error(f"Error generating keywords: {str(e)}")
            # Fallback to basic keyword generation
            return self._generate_basic_keywords(report_data)

    def _generate_basic_keywords(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback keyword generation without LLM."""
        hazard = report_data.get('hazard_type', '').lower()
        city = report_data.get('city', '').lower()
        
        # Basic keyword mapping
        hazard_keywords = {
            'flood': ['flood', 'flooding', 'waterlogged', 'inundated'],
            'cyclone': ['cyclone', 'storm', 'hurricane', 'typhoon'],
            'tsunami': ['tsunami', 'tidal wave', 'sea wave'],
            'high_waves': ['high waves', 'rough seas', 'giant waves'],
        }
        
        primary = hazard_keywords.get(hazard, [hazard, 'disaster', 'emergency'])
        
        return {
            'primary_keywords': primary,
            'location_keywords': [city] if city else [],
            'hashtag_suggestions': [f"#{hazard.title()}", "#Emergency", "#India"],
            'combined_queries': [f"{hazard} {city}", f"{hazard} emergency", f"help {city}"],
            'language_variations': []
        }

    async def _search_social_media_correlations(
        self, 
        keywords_data: Dict[str, Any], 
        report_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search for social media posts using RapidAPI Twitter search."""
        
        matches = []
        search_queries = keywords_data.get('combined_queries', [])
        
        if not self.rapidapi_key:
            logger.warning("RapidAPI key not found, using fallback simulation")
            return await self._fallback_simulated_search(search_queries, report_data)
        
        for query in search_queries[:3]:  # Limit to 3 queries to avoid rate limits
            try:
                # Call real RapidAPI Twitter search with max 10 results, latest
                query_matches = await self._real_twitter_search(query)
                matches.extend(query_matches)
                
                # Add delay between searches to respect rate limits
                await asyncio.sleep(2)
                
            except Exception as e:
                logger.error(f"Error searching for query '{query}': {str(e)}")
                continue
        
        # Remove duplicates based on post ID
        seen_ids = set()
        unique_matches = []
        for match in matches:
            post_id = match.get('id')
            if post_id and post_id not in seen_ids:
                seen_ids.add(post_id)
                unique_matches.append(match)
        
        logger.info(f"Found {len(unique_matches)} unique social media matches from RapidAPI")
        return unique_matches

    async def _simulate_social_media_search(
        self, 
        query: str, 
        report_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Simulate social media search results (replace with real implementation)."""
        
        # This is a placeholder - in production, integrate with your existing
        # social media search from the data ingestion module
        
        simulated_posts = [
            {
                'id': f'sim_{uuid.uuid4()}',
                'text': f"Experiencing {report_data.get('hazard_type', 'issues')} in {report_data.get('city', 'area')}. Water levels rising rapidly! #Emergency",
                'location': {
                    'city': report_data.get('city'),
                    'state': report_data.get('state')
                },
                'created_at': datetime.now().isoformat(),
                'author': 'citizen_reporter',
                'confidence': 0.8,
                'source': 'simulated_twitter'
            }
        ]
        
        return simulated_posts
    
    async def _real_twitter_search(self, query: str) -> List[Dict[str, Any]]:
        """Search Twitter using RapidAPI with your exact syntax."""
        
        querystring = {
            "query": query,
            "type": "Latest",
            "max_results": "4"  # Limit to 4 tweets per keyword as requested
        }
        
        try:
            # Use synchronous requests (can be made async later if needed)
            response = requests.get(self.twitter_api_url, headers=self.twitter_headers, params=querystring)
            
            if response.status_code != 200:
                logger.error(f"RapidAPI request failed with status {response.status_code}: {response.text}")
                return []
            
            data = response.json()
            real_posts = []
            
            # Process tweets - handle different possible field names
            for tweet in data.get("tweets", []):
                # Try different possible content field names
                tweet_text = (
                    tweet.get("content") or 
                    tweet.get("text") or 
                    tweet.get("full_text") or 
                    tweet.get("tweet", {}).get("content") or 
                    tweet.get("tweet", {}).get("text") or 
                    str(tweet)[:100] if tweet else 
                    "[No content found]"
                )
                
                # Extract tweet ID
                tweet_id = (
                    tweet.get("entryId") or 
                    tweet.get("id") or 
                    tweet.get("tweet_id") or 
                    f'rapid_{uuid.uuid4()}'
                )
                
                # Extract timestamp  
                timestamp = (
                    tweet.get("date") or 
                    tweet.get("created_at") or 
                    tweet.get("timestamp") or 
                    datetime.now().isoformat()
                )
                
                post = {
                    'id': str(tweet_id),
                    'text': str(tweet_text),  # Ensure always string
                    'created_at': str(timestamp),
                    'author': tweet.get("author", {}).get("username", "unknown") if tweet.get("author") else "unknown",
                    'source': 'rapidapi_twitter',
                    'location': {
                        'city': 'Unknown',
                        'state': 'Unknown'
                    }
                }
                
                logger.info(f"Successfully parsed tweet: ID={post['id']}, Text='{post['text'][:50]}...'")
                real_posts.append(post)
            
            logger.info(f"RapidAPI returned {len(real_posts)} tweets for query: {query}")
            return real_posts
            
        except Exception as e:
            logger.error(f"Error calling RapidAPI: {str(e)}")
            return []
    
    async def _fallback_simulated_search(self, queries: List[str], report_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Fallback to simulated search when RapidAPI is not available."""
        matches = []
        for query in queries[:3]:
            try:
                query_matches = await self._simulate_social_media_search(query, report_data)
                matches.extend(query_matches)
            except Exception as e:
                logger.error(f"Error in fallback simulation for query '{query}': {str(e)}")
                continue
        return matches

    async def _analyze_correlations(
        self, 
        report_data: Dict[str, Any], 
        social_posts: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Analyze correlation between user report and social media posts."""
        
        print("\n" + "="*80)
        print(f"🤖 AGENT 2: STARTING SOCIAL MEDIA INTELLIGENCE ANALYSIS")
        print(f"📍 Report Location: {report_data.get('city', 'Unknown')}, {report_data.get('state', 'India')}")
        print(f"⚡ Hazard Type: {report_data.get('hazard_type', 'Unknown')}")
        print(f"📱 Social Media Posts Found: {len(social_posts)}")
        print("="*80)
        
        logger.info(f"📊 Starting correlation analysis for {len(social_posts)} social media posts")
        correlations = []
        
        for i, post in enumerate(social_posts, 1):
            try:
                post_text = post.get('text', '')
                print(f"\n📝 TWEET {i}/{len(social_posts)}:")
                print(f"{'─'*50}")
                print(f"📱 Post ID: {post.get('id', 'N/A')}")
                print(f"👤 Author: {post.get('author', 'N/A')}")
                print(f"📅 Posted: {post.get('created_at', 'N/A')}")
                print(f"💬 Content: {post_text}")
                print(f"{'─'*50}")
                
                logger.info(f"🔍 Analyzing post {i}/{len(social_posts)}: {post_text[:30]}...")
                correlation = await self._analyze_single_correlation(report_data, post)
                
                confidence_score = correlation.get('correlation_score', 0)
                logger.info(f"🎯 Post {i} correlation score: {confidence_score:.2f}")
                
                if confidence_score > 0.3:  # Only keep significant correlations
                    correlations.append(correlation)
                    logger.info(f"✅ Post {i} added to correlations (score > 0.3)")
                else:
                    logger.info(f"❌ Post {i} filtered out (score ≤ 0.3)")
                    
            except Exception as e:
                logger.error(f"⚠️ Error analyzing correlation for post {post.get('id')}: {str(e)}")
                continue
        
        # Sort by correlation score
        correlations.sort(key=lambda x: x.get('correlation_score', 0), reverse=True)
        
        # Calculate urgency distribution for insights
        urgency_stats = {'High': 0, 'Medium': 0, 'Low': 0}
        for corr in correlations:
            urgency = corr.get('urgency', 'Low')
            urgency_stats[urgency] = urgency_stats.get(urgency, 0) + 1
        
        print(f"\n🏁 ANALYSIS SUMMARY:")
        print(f"{'='*50}")
        print(f"📊 Total Posts Analyzed: {len(social_posts)}")
        print(f"✅ Posts Passed Filter (>0.3): {len(correlations)}")
        print(f"🚨 Urgency Distribution:")
        print(f"   • High: {urgency_stats['High']} posts")
        print(f"   • Medium: {urgency_stats['Medium']} posts")
        print(f"   • Low: {urgency_stats['Low']} posts")
        if correlations:
            avg_confidence = sum(c.get('correlation_score', 0) for c in correlations) / len(correlations)
            print(f"📊 Average Confidence: {avg_confidence:.2f}")
        print(f"{'='*50}\n")
        
        logger.info(f"🏁 Correlation analysis complete: {len(correlations)} posts passed filter")
        logger.info(f"📊 Urgency distribution - High:{urgency_stats['High']}, Medium:{urgency_stats['Medium']}, Low:{urgency_stats['Low']}")
        return correlations

    async def _analyze_single_correlation(
        self, 
        report_data: Dict[str, Any], 
        post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Analyze hazard using exact DeepSeek prompt specification."""
        
        # Extract location from report data
        location = f"{report_data.get('city', 'Unknown')}, {report_data.get('state', 'India')}"
        
        # Extract post text, timestamp, and location for the exact user prompt format
        post_text = post_data.get('text', '')
        timestamp = post_data.get('created_at', '')
        
        # Use exact multilingual user prompt format (escape braces for f-string)
        user_prompt = f"""New Social Media Signal

Post Text (may be in multiple languages): "{post_text}"
Timestamp (UTC): "{timestamp}"
User Location (if available): "{location}"

Tasks:
1. Event Detection (Multilingual):  
   - Translate internally into English, interpret the meaning, and detect hazard signals.  
   - Does this post indicate a possible ocean or coastal hazard? (yes/no with confidence).  
   - Identify hazard type: ["Flood", "Tsunami", "Storm Surge", "High Waves", "Coastal Erosion", "Other"].  
   - Estimate urgency (Low/Medium/High).  

2. Historical Pattern Analysis:  
   - Identify past similar events in the same region.  
   - Provide a one-line historical precedent with date/month if available.  

3. Seasonal & Probabilistic Context:  
   - Check whether >60% of similar past events in this region occur in the same season/month.  
   - If yes, highlight the seasonal risk explicitly.  

4. Risk Communication:  
   - Provide one actionable recommendation.  
   - Generate a human-readable summary linking current post → historical precedent → seasonal risk.  

5. Output Format: Strict JSON only:
{{
  "original_language": "Detected language code (e.g., hi, ta, te, en, etc.)",
  "hazard_detected": true/false,
  "hazard_type": "Flood/Tsunami/Storm Surge/High Waves/Coastal Erosion/Other",
  "urgency": "Low/Medium/High",
  "confidence": 0.0-1.0,
  "historical_context": "One-line summary of past similar events or null",
  "seasonal_pattern": "Yes/No with explanation",
  "recommended_action": "One-line recommendation",
  "final_summary": "Concise human-readable intelligence for decision-makers"
}}"""

        try:
            print(f"\n🤖 DEEPSEEK LLM ANALYSIS:")
            print(f"{'='*60}")
            logger.info(f"🤖 Sending tweet to DeepSeek LLM for analysis: {post_text[:50]}...")
            hazard_analysis = await self._call_deepseek_api(
                self.hazard_analysis_prompt, 
                user_prompt
            )
            
            # Normalize urgency to avoid over-classification as High
            normalized_urgency = self._normalize_urgency(
                hazard_analysis.get('urgency', 'Low'),
                hazard_analysis.get('confidence', 0.0),
                post_text
            )
            hazard_analysis['urgency'] = normalized_urgency
            
            # Display detailed LLM results in terminal
            print(f"✅ DEEPSEEK ANALYSIS RESULTS:")
            print(f"{'-'*40}")
            print(f"🌍 Original Language: {hazard_analysis.get('original_language', 'N/A')}")
            print(f"⚠️ Hazard Detected: {hazard_analysis.get('hazard_detected', 'N/A')}")
            print(f"🌊 Hazard Type: {hazard_analysis.get('hazard_type', 'N/A')}")
            print(f"🚨 Urgency Level: {hazard_analysis.get('urgency', 'N/A')}")
            print(f"📊 Confidence Score: {hazard_analysis.get('confidence', 'N/A')}")
            print(f"📅 Historical Context: {hazard_analysis.get('historical_context', 'N/A')}")
            print(f"🍂 Seasonal Pattern: {hazard_analysis.get('seasonal_pattern', 'N/A')}")
            print(f"💡 Recommended Action: {hazard_analysis.get('recommended_action', 'N/A')}")
            print(f"📝 Final Summary: {hazard_analysis.get('final_summary', 'N/A')}")
            print(f"{'-'*40}")
            print(f"{'='*60}\n")
            
            logger.info(f"✅ DeepSeek analysis complete with confidence: {hazard_analysis.get('confidence', 0)}")
            
            # Add enhanced metadata for admin display
            hazard_analysis['post_id'] = post_data.get('id')
            hazard_analysis['post_text'] = post_data.get('text', '')
            hazard_analysis['post_text_preview'] = post_data.get('text', '')[:100] + '...' if len(post_data.get('text', '')) > 100 else post_data.get('text', '')
            hazard_analysis['post_author'] = post_data.get('author', 'Unknown')
            hazard_analysis['post_source'] = post_data.get('source', 'twitter')
            hazard_analysis['post_location'] = location
            hazard_analysis['analyzed_at'] = datetime.now().isoformat()
            hazard_analysis['correlation_score'] = hazard_analysis.get('confidence', 0.0)  # Use LLM confidence as correlation
            
            # Add severity classification based on urgency and confidence
            urgency = hazard_analysis.get('urgency', 'Low')
            confidence = hazard_analysis.get('confidence', 0.0)
            
            if urgency == 'High' and confidence > 0.7:
                hazard_analysis['severity_class'] = 'critical'
                hazard_analysis['priority_score'] = 5
            elif urgency == 'High' or (urgency == 'Medium' and confidence > 0.8):
                hazard_analysis['severity_class'] = 'high'
                hazard_analysis['priority_score'] = 4
            elif urgency == 'Medium' and confidence > 0.6:
                hazard_analysis['severity_class'] = 'medium'
                hazard_analysis['priority_score'] = 3
            elif confidence > 0.5:
                hazard_analysis['severity_class'] = 'low'
                hazard_analysis['priority_score'] = 2
            else:
                hazard_analysis['severity_class'] = 'minimal'
                hazard_analysis['priority_score'] = 1
            
            # Add matching elements for filtering
            hazard_analysis['matching_elements'] = self._extract_matching_elements(report_data, post_data, hazard_analysis)
            
            return hazard_analysis
            
        except Exception as e:
            print(f"\n❌ DEEPSEEK LLM FAILED - USING FALLBACK:")
            print(f"{'='*60}")
            print(f"⚠️ Error: {str(e)}")
            print(f"🔄 Switching to basic keyword-based analysis...")
            print(f"{'='*60}\n")
            
            logger.error(f"❌ DeepSeek LLM analysis failed for post {post_data.get('id')}: {str(e)}")
            logger.info(f"🔄 Using fallback analysis instead")
            
            # Return basic analysis with terminal output
            fallback_result = self._basic_hazard_analysis(report_data, post_data)
            
            print(f"🔄 FALLBACK ANALYSIS RESULTS:")
            print(f"{'-'*40}")
            print(f"🌍 Original Language: {fallback_result.get('original_language', 'N/A')}")
            print(f"⚠️ Hazard Detected: {fallback_result.get('hazard_detected', 'N/A')}")
            print(f"🌊 Hazard Type: {fallback_result.get('hazard_type', 'N/A')}")
            print(f"🚨 Urgency Level: {fallback_result.get('urgency', 'N/A')}")
            print(f"📊 Confidence Score: {fallback_result.get('confidence', 'N/A')}")
            print(f"📝 Final Summary: {fallback_result.get('final_summary', 'N/A')}")
            print(f"{'-'*40}")
            print(f"{'='*60}\n")
            
            return fallback_result
    
    def _basic_hazard_analysis(self, report_data: Dict[str, Any], post_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback hazard analysis without LLM using your exact output format."""
        
        post_text = post_data.get('text', '').lower()
        location = f"{report_data.get('city', 'Unknown')}, {report_data.get('state', 'India')}"
        
        # Basic hazard detection
        hazard_keywords = {
            'Flood': ['flood', 'flooding', 'water', 'rain', 'inundated', 'waterlogged', 'baarish', 'paani'],
            'Storm Surge': ['surge', 'storm', 'cyclone', 'hurricane', 'toofan'],
            'High Waves': ['waves', 'tsunami', 'tidal', 'sea', 'ocean', 'samundar'],
            'Coastal Erosion': ['erosion', 'coast', 'beach', 'shore']
        }
        
        detected_hazard = 'Other'
        hazard_detected = False
        confidence = 0.5
        urgency = 'Low'
        
        for hazard_type, keywords in hazard_keywords.items():
            if any(keyword in post_text for keyword in keywords):
                detected_hazard = hazard_type
                hazard_detected = True
                confidence = 0.6  # Start more conservative
                
                # More conservative urgency indicators
                if any(word in post_text for word in ['emergency', 'evacuate', 'rescue', 'life threatening', 'trapped']):
                    urgency = 'High'
                    confidence = 0.75
                elif any(word in post_text for word in ['urgent', 'help', 'danger', 'severe', 'heavy']):
                    urgency = 'Medium'
                    confidence = 0.65
                elif any(word in post_text for word in ['rising', 'increasing', 'getting worse', 'warning']):
                    urgency = 'Medium'
                    confidence = 0.6
                else:
                    urgency = 'Low'  # Default to Low if no clear urgency indicators
                    confidence = 0.55
                break
        
        # Detect language (basic)
        original_language = 'en'  # Default
        if any(word in post_text for word in ['paani', 'baarish', 'toofan', 'samundar']):
            original_language = 'hi'  # Hindi indicators
        
        fallback_result = {
            'original_language': original_language,
            'hazard_detected': hazard_detected,
            'hazard_type': detected_hazard,
            'urgency': urgency,
            'confidence': confidence,
            'historical_context': f"Similar events have occurred in {location} region during monsoon seasons",
            'seasonal_pattern': "Yes - Coastal hazards in India show strong seasonal clustering during monsoon months (Jun-Oct)",
            'recommended_action': "Monitor situation closely and prepare for potential evacuation if conditions worsen",
            'final_summary': f"{detected_hazard} indicators detected in {location} with {urgency.lower()} urgency level",
            'post_id': post_data.get('id'),
            'post_text': post_data.get('text', ''),
            'post_text_preview': post_data.get('text', '')[:100] + '...' if len(post_data.get('text', '')) > 100 else post_data.get('text', ''),
            'post_author': post_data.get('author', 'Unknown'),
            'post_source': post_data.get('source', 'twitter'),
            'post_location': location,
            'analyzed_at': datetime.now().isoformat(),
            'correlation_score': confidence
        }
        
        # Add severity classification for fallback too
        if urgency == 'High' and confidence > 0.7:
            fallback_result['severity_class'] = 'critical'
            fallback_result['priority_score'] = 5
        elif urgency == 'High' or (urgency == 'Medium' and confidence > 0.8):
            fallback_result['severity_class'] = 'high'
            fallback_result['priority_score'] = 4
        elif urgency == 'Medium' and confidence > 0.6:
            fallback_result['severity_class'] = 'medium'
            fallback_result['priority_score'] = 3
        elif confidence > 0.5:
            fallback_result['severity_class'] = 'low'
            fallback_result['priority_score'] = 2
        else:
            fallback_result['severity_class'] = 'minimal'
            fallback_result['priority_score'] = 1
        
        # Add matching elements
        fallback_result['matching_elements'] = self._extract_matching_elements(report_data, post_data, fallback_result)
        
        # Normalize urgency in fallback too to avoid bias
        fallback_result['urgency'] = self._normalize_urgency(
            fallback_result.get('urgency', 'Low'),
            fallback_result.get('confidence', 0.0),
            post_data.get('text', '')
        )
        return fallback_result

    def _basic_correlation_analysis(
        self, 
        report_data: Dict[str, Any], 
        post_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Basic correlation analysis without LLM."""
        
        score = 0.0
        matching_elements = []
        
        # Check location similarity
        if (report_data.get('city', '').lower() in post_data.get('text', '').lower() or
            report_data.get('state', '').lower() in post_data.get('text', '').lower()):
            score += 0.4
            matching_elements.append('location_mentioned')
        
        # Check hazard type similarity
        hazard = report_data.get('hazard_type', '').lower()
        if hazard in post_data.get('text', '').lower():
            score += 0.3
            matching_elements.append('hazard_type_match')
        
        # Check for emergency keywords
        emergency_words = ['emergency', 'help', 'urgent', 'rescue', 'danger']
        if any(word in post_data.get('text', '').lower() for word in emergency_words):
            score += 0.2
            matching_elements.append('urgency_indicators')
        
        return {
            'correlation_score': min(score, 1.0),
            'correlation_type': 'keyword_location' if matching_elements else 'low',
            'confidence': 0.6,
            'matching_elements': matching_elements,
            'reasoning': f"Basic analysis found {len(matching_elements)} matching elements",
            'post_id': post_data.get('id'),
            'post_text_preview': post_data.get('text', '')[:100] + '...',
            'analyzed_at': datetime.now().isoformat()
        }

    def _calculate_overall_confidence(self, correlations: List[Dict[str, Any]]) -> float:
        """Enhanced confidence calculation with multiple factors."""
        if not correlations:
            return 0.0
        
        # Base weighted scoring
        total_weight = 0.0
        weighted_score = 0.0
        high_confidence_count = 0
        urgency_boost = 0.0
        location_matches = 0
        hazard_matches = 0
        
        for corr in correlations:
            score = corr.get('correlation_score', 0.0)
            confidence = corr.get('confidence', 0.0)
            weight = score * confidence
            
            weighted_score += weight * score
            total_weight += weight
            
            # Count high confidence correlations
            if score > 0.7:
                high_confidence_count += 1
            
            # Track urgency indicators
            if corr.get('urgency') == 'High':
                urgency_boost += 0.05
            elif corr.get('urgency') == 'Medium':
                urgency_boost += 0.02
            
            # Track location and hazard matches
            if 'location' in str(corr.get('matching_elements', [])):
                location_matches += 1
            if 'hazard' in str(corr.get('matching_elements', [])):
                hazard_matches += 1
        
        if total_weight == 0:
            return 0.0
        
        overall_confidence = weighted_score / total_weight
        
        # Enhancement factors (reduced bonuses to prevent 100% confidence)
        # Multiple high-quality correlations (reduced bonuses)
        if high_confidence_count >= 3:
            overall_confidence = min(overall_confidence + 0.05, 0.95)  # Cap at 95%
        elif high_confidence_count >= 2:
            overall_confidence = min(overall_confidence + 0.03, 0.92)  # Cap at 92%
        
        # Location consistency bonus (reduced)
        if location_matches >= 2:
            overall_confidence = min(overall_confidence + 0.03, 0.90)
        
        # Hazard type consistency bonus (reduced)
        if hazard_matches >= 2:
            overall_confidence = min(overall_confidence + 0.02, 0.88)
        
        # Urgency factor (reduced and capped)
        overall_confidence = min(overall_confidence + (urgency_boost * 0.5), 0.92)
        
        # Recency bonus (reduced)
        recent_posts = [c for c in correlations if self._is_recent_post(c.get('post_text', ''))]
        if len(recent_posts) >= 2:
            overall_confidence = min(overall_confidence + 0.02, 0.90)
        
        # Final cap to ensure never reaches 100%
        overall_confidence = min(overall_confidence, 0.95)
        
        return round(overall_confidence, 3)
    
    def _is_recent_post(self, post_text: str) -> bool:
        """Check if post contains recent time indicators."""
        recent_indicators = ['now', 'currently', 'right now', 'happening', 'just', 'minutes ago', 'hours ago']
        return any(indicator in post_text.lower() for indicator in recent_indicators)
    
    def _normalize_urgency(self, urgency: str, confidence: float, post_text: str) -> str:
        """Normalize urgency to reduce false 'High' classifications.
        Rules:
        - High only if strong emergency cues present AND confidence >= 0.7
        - Medium if moderate cues present AND confidence >= 0.55
        - Otherwise Low
        - If negation/hoax cues present, force Low
        """
        text = (post_text or '').lower()
        strong_cues = ['emergency', 'evacuate', 'evacuation', 'rescue', 'immediately', 'life threatening', 'impassable', 'trapped', 'collapsed', 'collapse', 'mayday']
        moderate_cues = ['rising', 'increasing', 'severe', 'heavy', 'warning', 'alert', 'overflow', 'breach', 'breached']
        down_cues = ['rumor', 'hoax', 'false alarm', 'fake', 'test drill', 'drill']

        if any(c in text for c in down_cues):
            return 'Low'

        if any(c in text for c in strong_cues) and confidence >= 0.7:
            return 'High'

        if any(c in text for c in moderate_cues) and confidence >= 0.55:
            return 'Medium'

        # If model said High but cues are missing and confidence is not strong, downgrade
        if urgency == 'High' and confidence < 0.7:
            return 'Medium'
        if urgency == 'Medium' and confidence < 0.5:
            return 'Low'

        # Default to provided urgency if none of the above rules apply
        return urgency or 'Low'

    def _extract_matching_elements(self, report_data: Dict[str, Any], post_data: Dict[str, Any], analysis: Dict[str, Any]) -> List[str]:
        """Extract specific matching elements between report and post for admin insights."""
        matching_elements = []
        post_text = post_data.get('text', '').lower()
        
        # Location matches
        report_city = report_data.get('city', '').lower()
        report_state = report_data.get('state', '').lower()
        if report_city and report_city in post_text:
            matching_elements.append(f'location_city:{report_city}')
        if report_state and report_state in post_text:
            matching_elements.append(f'location_state:{report_state}')
        
        # Hazard type matches
        report_hazard = report_data.get('hazard_type', '').lower()
        detected_hazard = analysis.get('hazard_type', '').lower()
        if report_hazard and report_hazard in post_text:
            matching_elements.append(f'hazard_direct:{report_hazard}')
        if detected_hazard and detected_hazard.lower() == report_hazard:
            matching_elements.append(f'hazard_ai:{detected_hazard}')
        
        # Urgency indicators
        if analysis.get('urgency') in ['High', 'Medium']:
            matching_elements.append(f'urgency:{analysis.get("urgency").lower()}')
        
        # Time relevance
        if self._is_recent_post(post_text):
            matching_elements.append('temporal:recent')
        
        # Language detection
        if analysis.get('original_language') != 'en':
            matching_elements.append(f'language:{analysis.get("original_language")}')
        
        # Seasonal patterns
        if 'seasonal_pattern' in analysis and analysis['seasonal_pattern'].startswith('Yes'):
            matching_elements.append('pattern:seasonal')
        
        return matching_elements

    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """Calculate distance between two coordinates in kilometers."""
        R = 6371  # Earth's radius in km
        
        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)
        a = (math.sin(dlat / 2) ** 2 + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c

    async def _call_deepseek_api(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        """Call DeepSeek API for analysis."""
        if not self.deepseek_api_key:
            raise Exception("DeepSeek API key not configured")
        
        url = f"{self.deepseek_base_url}/chat/completions"
        
        headers = {
            'Authorization': f'Bearer {self.deepseek_api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model_name,
            'messages': [
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ],
            'temperature': 0.1,
            'max_tokens': 500
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    result = await response.json()
                    content = result['choices'][0]['message']['content'].strip()
                    
                    # Extract JSON from response (handle markdown code blocks)
                    json_content = self._extract_json_from_response(content)
                    return json.loads(json_content)
                else:
                    error_text = await response.text()
                    raise Exception(f"DeepSeek API error {response.status}: {error_text}")

    def _extract_json_from_response(self, content: str) -> str:
        """Extract JSON from response, handling markdown code blocks."""
        content = content.strip()
        
        if content.startswith('```json') and content.endswith('```'):
            lines = content.split('\n')
            json_lines = lines[1:-1]
            return '\n'.join(json_lines)
        elif content.startswith('```') and content.endswith('```'):
            lines = content.split('\n')
            json_lines = lines[1:-1]
            return '\n'.join(json_lines)
        else:
            return content

# Global instance
report_analysis_agent = ReportAnalysisAgent()

async def process_user_report(report_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Public interface to process a user report.
    
    Args:
        report_data: User report with location, description, etc.
        
    Returns:
        Enhanced report with keywords and correlations
    """
    return await report_analysis_agent.process_user_report(report_data)
