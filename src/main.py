#!/usr/bin/env python3
"""
Social Media Analytics Agent - Main Application Entry Point
Handles the hourly batch processing workflow for social media hazard detection.
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta
from loguru import logger
from dotenv import load_dotenv

# Add src/modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.scheduler import SchedulerService
from modules.data_ingestion import DataIngestionService
from modules.preprocessing import PreprocessingService
from modules.ai_analysis import AIAnalysisService
from modules.aggregation import AggregationService
from modules.validation import ValidationService
from modules.alerts import AlertService
from modules.storage import StorageService

# Load environment variables
load_dotenv()

class SocialMediaAnalyticsAgent:
    """Main orchestrator for the social media analytics workflow."""
    
    def __init__(self):
        """Initialize all service components."""
        self.scheduler = SchedulerService()
        self.data_ingestion = DataIngestionService()
        self.preprocessing = PreprocessingService()
        self.ai_analysis = AIAnalysisService()
        self.aggregation = AggregationService()
        self.validation = ValidationService()
        self.alerts = AlertService()
        self.storage = StorageService()
        
        # Configure logging
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        log_file = os.getenv('LOG_FILE', 'logs/social_analytics.log')
        
        logger.remove()
        logger.add(sys.stderr, level=log_level)
        logger.add(log_file, rotation="10 MB", retention="30 days", level=log_level)
        
        logger.info("Social Media Analytics Agent initialized")
    
    async def run_hourly_batch(self):
        """Execute the complete hourly batch processing workflow."""
        start_time = datetime.now()
        logger.info(f"Starting hourly batch processing at {start_time}")
        
        try:
            # Step 1: Data Ingestion (last 60 minutes)
            logger.info("Step 1: Starting data ingestion...")
            end_time = datetime.now()
            start_window = end_time - timedelta(minutes=int(os.getenv('FETCH_WINDOW_MINUTES', 60)))
            
            raw_posts = await self.data_ingestion.fetch_social_media_posts(
                start_time=start_window,
                end_time=end_time,
                geo_filter='India'
            )
            logger.info(f"Fetched {len(raw_posts)} raw posts")
            
            if not raw_posts:
                logger.warning("No posts fetched. Ending batch processing.")
                return
            
            # Step 2: Preprocessing
            logger.info("Step 2: Starting preprocessing...")
            processed_posts = await self.preprocessing.process_posts(raw_posts)
            logger.info(f"Processed {len(processed_posts)} posts after deduplication and cleaning")
            
            # Step 3: AI Analysis
            logger.info("Step 3: Starting AI analysis...")
            analyzed_posts = await self.ai_analysis.analyze_posts(processed_posts)
            logger.info(f"Analyzed {len(analyzed_posts)} posts for hazard classification")
            
            # Step 4: Aggregation & Hotspot Detection
            logger.info("Step 4: Starting aggregation and hotspot detection...")
            hotspots = await self.aggregation.detect_hotspots(analyzed_posts)
            logger.info(f"Detected {len(hotspots)} potential hotspots")
            
            # Step 5: Store results
            logger.info("Step 5: Storing results...")
            batch_id = await self.storage.store_batch_results(
                raw_posts=raw_posts,
                processed_posts=processed_posts,
                analyzed_posts=analyzed_posts,
                hotspots=hotspots,
                batch_timestamp=start_time
            )
            
            # Step 6: Validation (send to analyst dashboard)
            if hotspots:
                logger.info("Step 6: Sending hotspots for validation...")
                await self.validation.submit_for_validation(hotspots, batch_id)
            
            # Step 7: Check for confirmed alerts from previous batches
            logger.info("Step 7: Processing validated alerts...")
            confirmed_alerts = await self.validation.get_confirmed_alerts()
            
            if confirmed_alerts:
                logger.info(f"Processing {len(confirmed_alerts)} confirmed alerts...")
                await self.alerts.send_alerts(confirmed_alerts)
            
            processing_time = datetime.now() - start_time
            logger.info(f"Hourly batch processing completed in {processing_time.total_seconds():.2f} seconds")
            
        except Exception as e:
            logger.error(f"Error during batch processing: {str(e)}", exc_info=True)
            raise
    
    def start_scheduler(self):
        """Start the hourly scheduler."""
        logger.info("Starting scheduled batch processing...")
        interval_seconds = int(os.getenv('SCHEDULER_INTERVAL', 3600))  # Default 1 hour
        
        self.scheduler.schedule_hourly_job(
            job_func=lambda: asyncio.run(self.run_hourly_batch()),
            interval_seconds=interval_seconds
        )
        
        logger.info(f"Scheduler started with {interval_seconds}s interval")
        self.scheduler.start()
    
    async def run_single_batch(self):
        """Run a single batch for testing purposes."""
        logger.info("Running single batch for testing...")
        await self.run_hourly_batch()

def main():
    """Main entry point."""
    agent = SocialMediaAnalyticsAgent()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        # Run single batch for testing
        asyncio.run(agent.run_single_batch())
    else:
        # Start scheduled processing
        agent.start_scheduler()

if __name__ == "__main__":
    main()
