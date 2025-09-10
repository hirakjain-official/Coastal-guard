#!/usr/bin/env python3
"""
Social Media Analytics Agent Runner
A streamlined agent that searches X with hashtags, analyzes with LLM, and verifies seriousness via internet search.
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta
from loguru import logger
from dotenv import load_dotenv

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.data_ingestion import DataIngestionService
from modules.preprocessing import PreprocessingService
from modules.ai_analysis import AIAnalysisService
from modules.aggregation import AggregationService
from modules.internet_verification import InternetVerificationService
from modules.storage import StorageService

# Load environment variables
load_dotenv()

class SocialMediaAnalyticsAgentRunner:
    """Streamlined agent runner for hashtag-based hazard detection with internet verification."""
    
    def __init__(self):
        """Initialize all service components."""
        self.data_ingestion = DataIngestionService()
        self.preprocessing = PreprocessingService()
        self.ai_analysis = AIAnalysisService()
        self.aggregation = AggregationService()
        self.internet_verification = InternetVerificationService()
        self.storage = StorageService()
        
        # Configure logging
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_file = os.getenv('LOG_FILE', 'logs/agent.log')
        
        logger.remove()
        logger.add(sys.stderr, level=log_level)
        logger.add(log_file, rotation="10 MB", retention="30 days", level=log_level)
        
        logger.info("Social Media Analytics Agent Runner initialized")
    
    async def run_agent(self) -> dict:
        """
        Execute the complete agent workflow:
        1. Search X for hashtags + India location
        2. Analyze with LLM
        3. Detect hotspots
        4. Verify seriousness with internet search
        5. Return comprehensive results
        """
        start_time = datetime.now()
        logger.info(f"Starting agent execution at {start_time}")
        
        try:
            # Step 1: Search X for hashtags and India location
            logger.info("Step 1: Searching X for hazard-related hashtags in India...")
            end_time = datetime.now()
            start_window = end_time - timedelta(hours=6)  # Last 6 hours for more comprehensive search
            
            raw_posts = await self.data_ingestion.fetch_social_media_posts(
                start_time=start_window,
                end_time=end_time,
                geo_filter='India'
            )
            logger.info(f"Found {len(raw_posts)} posts from X")
            
            if not raw_posts:
                return self._create_empty_results("No posts found matching criteria")
            
            # Step 2: Preprocess posts
            logger.info("Step 2: Preprocessing posts...")
            processed_posts = await self.preprocessing.process_posts(raw_posts)
            logger.info(f"Processed {len(processed_posts)} posts")
            
            if not processed_posts:
                return self._create_empty_results("No posts remaining after preprocessing")
            
            # Step 3: LLM Analysis
            logger.info("Step 3: Analyzing posts with LLM...")
            analyzed_posts = await self.ai_analysis.analyze_posts(processed_posts)
            logger.info(f"Analyzed {len(analyzed_posts)} posts")
            
            # Step 4: Detect hotspots
            logger.info("Step 4: Detecting hotspots...")
            hotspots = await self.aggregation.detect_hotspots(analyzed_posts)
            logger.info(f"Detected {len(hotspots)} hotspots")
            
            # Step 5: Internet verification for each hotspot
            logger.info("Step 5: Verifying hotspots with internet search...")
            verified_hotspots = []
            
            for hotspot in hotspots:
                # Get posts contributing to this hotspot
                contributing_posts = [
                    post for post in analyzed_posts 
                    if (post.get('inferred_location', {}).get('city') == hotspot['location_details'].get('city') and
                        post.get('ai_analysis', {}).get('hazard_type') == hotspot['hazard_type'])
                ]
                
                # Verify with internet sources
                verification_results = await self.internet_verification.verify_situation(
                    hazard_posts=contributing_posts,
                    location=hotspot['location'],
                    hazard_type=hotspot['hazard_type']
                )
                
                # Add verification to hotspot
                hotspot['internet_verification'] = verification_results
                verified_hotspots.append(hotspot)
                
                logger.info(f"Verified {hotspot['location']} - Assessment: {verification_results['seriousness_assessment']}")
            
            # Step 6: Generate comprehensive results
            processing_time = datetime.now() - start_time
            
            agent_results = {
                'execution_timestamp': start_time.isoformat(),
                'processing_time_seconds': processing_time.total_seconds(),
                'status': 'completed',
                'error': None,
                
                # Data pipeline results
                'pipeline_results': {
                    'raw_posts_found': len(raw_posts),
                    'posts_after_preprocessing': len(processed_posts),
                    'posts_analyzed': len(analyzed_posts),
                    'hazard_posts_detected': len([p for p in analyzed_posts if p.get('is_hazard', False)]),
                    'hotspots_detected': len(hotspots),
                    'hotspots_verified': len(verified_hotspots)
                },
                
                # X Posts results
                'x_posts_analysis': {
                    'total_posts': len(analyzed_posts),
                    'hazard_posts': [p for p in analyzed_posts if p.get('is_hazard', False)],
                    'high_confidence_posts': [p for p in analyzed_posts if p.get('meets_confidence_threshold', False)],
                    'by_urgency': {
                        'high': [p for p in analyzed_posts if p.get('ai_analysis', {}).get('urgency') == 'High'],
                        'medium': [p for p in analyzed_posts if p.get('ai_analysis', {}).get('urgency') == 'Medium'],
                        'low': [p for p in analyzed_posts if p.get('ai_analysis', {}).get('urgency') == 'Low']
                    },
                    'by_hazard_type': self._group_posts_by_hazard_type(analyzed_posts)
                },
                
                # Hotspots with verification
                'verified_hotspots': verified_hotspots,
                
                # Overall assessment
                'overall_assessment': self._generate_overall_assessment(verified_hotspots, analyzed_posts),
                
                # Summary statistics
                'summary_statistics': self._generate_summary_statistics(verified_hotspots, analyzed_posts)
            }
            
            # Store results
            logger.info("Step 6: Storing results...")
            batch_id = await self.storage.store_batch_results(
                raw_posts=raw_posts,
                processed_posts=processed_posts,
                analyzed_posts=analyzed_posts,
                hotspots=verified_hotspots,
                batch_timestamp=start_time
            )
            agent_results['batch_id'] = batch_id
            
            logger.info(f"Agent execution completed in {processing_time.total_seconds():.2f} seconds")
            return agent_results
            
        except Exception as e:
            error_msg = f"Error during agent execution: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            return {
                'execution_timestamp': start_time.isoformat(),
                'processing_time_seconds': (datetime.now() - start_time).total_seconds(),
                'status': 'error',
                'error': error_msg,
                'pipeline_results': None,
                'x_posts_analysis': None,
                'verified_hotspots': [],
                'overall_assessment': 'ERROR',
                'summary_statistics': {}
            }
    
    def _create_empty_results(self, reason: str) -> dict:
        """Create empty results structure when no data is found."""
        return {
            'execution_timestamp': datetime.now().isoformat(),
            'processing_time_seconds': 0,
            'status': 'no_data',
            'error': None,
            'reason': reason,
            'pipeline_results': {
                'raw_posts_found': 0,
                'posts_after_preprocessing': 0,
                'posts_analyzed': 0,
                'hazard_posts_detected': 0,
                'hotspots_detected': 0,
                'hotspots_verified': 0
            },
            'x_posts_analysis': {
                'total_posts': 0,
                'hazard_posts': [],
                'high_confidence_posts': [],
                'by_urgency': {'high': [], 'medium': [], 'low': []},
                'by_hazard_type': {}
            },
            'verified_hotspots': [],
            'overall_assessment': 'NO_DATA',
            'summary_statistics': {}
        }
    
    def _group_posts_by_hazard_type(self, posts):
        """Group analyzed posts by hazard type."""
        groups = {}
        for post in posts:
            if post.get('is_hazard', False):
                hazard_type = post.get('ai_analysis', {}).get('hazard_type', 'Other')
                if hazard_type not in groups:
                    groups[hazard_type] = []
                groups[hazard_type].append(post)
        return groups
    
    def _generate_overall_assessment(self, verified_hotspots, analyzed_posts):
        """Generate overall assessment based on hotspots and verification results."""
        if not verified_hotspots:
            hazard_posts = [p for p in analyzed_posts if p.get('is_hazard', False)]
            if len(hazard_posts) >= 5:
                return 'MONITORING_REQUIRED'
            elif len(hazard_posts) >= 1:
                return 'LOW_ACTIVITY'
            else:
                return 'NORMAL'
        
        # Check verification assessments
        critical_count = len([h for h in verified_hotspots if h['internet_verification']['seriousness_assessment'] == 'CRITICAL'])
        high_count = len([h for h in verified_hotspots if h['internet_verification']['seriousness_assessment'] == 'HIGH'])
        medium_count = len([h for h in verified_hotspots if h['internet_verification']['seriousness_assessment'] == 'MEDIUM'])
        
        if critical_count > 0:
            return 'CRITICAL_SITUATION_DETECTED'
        elif high_count >= 2:
            return 'HIGH_CONCERN_MULTIPLE_AREAS'
        elif high_count >= 1:
            return 'HIGH_CONCERN_SINGLE_AREA'
        elif medium_count >= 2:
            return 'MODERATE_CONCERN_MULTIPLE_AREAS'
        elif medium_count >= 1:
            return 'MODERATE_CONCERN_SINGLE_AREA'
        else:
            return 'SITUATION_MONITORING'
    
    def _generate_summary_statistics(self, verified_hotspots, analyzed_posts):
        """Generate summary statistics for the results."""
        hazard_posts = [p for p in analyzed_posts if p.get('is_hazard', False)]
        
        stats = {
            'total_posts_analyzed': len(analyzed_posts),
            'hazard_posts_count': len(hazard_posts),
            'hazard_detection_rate': (len(hazard_posts) / len(analyzed_posts) * 100) if analyzed_posts else 0,
            
            'urgency_distribution': {
                'high': len([p for p in hazard_posts if p.get('ai_analysis', {}).get('urgency') == 'High']),
                'medium': len([p for p in hazard_posts if p.get('ai_analysis', {}).get('urgency') == 'Medium']),
                'low': len([p for p in hazard_posts if p.get('ai_analysis', {}).get('urgency') == 'Low'])
            },
            
            'confidence_distribution': {
                'high_confidence': len([p for p in hazard_posts if p.get('ai_analysis', {}).get('confidence', 0) >= 0.8]),
                'medium_confidence': len([p for p in hazard_posts if 0.5 <= p.get('ai_analysis', {}).get('confidence', 0) < 0.8]),
                'low_confidence': len([p for p in hazard_posts if p.get('ai_analysis', {}).get('confidence', 0) < 0.5])
            },
            
            'verification_results': {
                'total_hotspots': len(verified_hotspots),
                'by_seriousness': {}
            }
        }
        
        # Count by seriousness assessment
        for hotspot in verified_hotspots:
            assessment = hotspot.get('internet_verification', {}).get('seriousness_assessment', 'UNKNOWN')
            if assessment not in stats['verification_results']['by_seriousness']:
                stats['verification_results']['by_seriousness'][assessment] = 0
            stats['verification_results']['by_seriousness'][assessment] += 1
        
        return stats

# Utility function for demo use
async def run_agent_once():
    """Run the agent once and return results."""
    agent = SocialMediaAnalyticsAgentRunner()
    return await agent.run_agent()

if __name__ == "__main__":
    # Run agent directly
    async def main():
        agent = SocialMediaAnalyticsAgentRunner()
        results = await agent.run_agent()
        print(f"Agent completed with status: {results['status']}")
        if results['status'] == 'completed':
            print(f"Found {results['pipeline_results']['hazard_posts_detected']} hazard posts")
            print(f"Detected {results['pipeline_results']['hotspots_detected']} hotspots")
            print(f"Overall assessment: {results['overall_assessment']}")

    asyncio.run(main())
