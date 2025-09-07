"""
Scheduler Service
Manages the hourly batch job scheduling for the social media analytics agent.
"""

import time
import schedule
import threading
from loguru import logger
from datetime import datetime

class SchedulerService:
    """Handles job scheduling and execution."""
    
    def __init__(self):
        """Initialize the scheduler service."""
        self.running = False
        self.scheduler_thread = None
        logger.info("Scheduler service initialized")
    
    def schedule_hourly_job(self, job_func, interval_seconds=3600):
        """
        Schedule a job to run at regular intervals.
        
        Args:
            job_func: The function to execute
            interval_seconds: Interval between executions (default 1 hour)
        """
        interval_minutes = interval_seconds // 60
        
        schedule.every(interval_minutes).minutes.do(job_func)
        logger.info(f"Scheduled job to run every {interval_minutes} minutes")
    
    def start(self):
        """Start the scheduler in a separate thread."""
        if self.running:
            logger.warning("Scheduler is already running")
            return
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        logger.info("Scheduler started successfully")
    
    def stop(self):
        """Stop the scheduler."""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)
        
        schedule.clear()
        logger.info("Scheduler stopped")
    
    def _run_scheduler(self):
        """Internal method to run the scheduler loop."""
        logger.info("Scheduler thread started")
        
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in scheduler thread: {str(e)}", exc_info=True)
                time.sleep(60)  # Wait 1 minute before retrying
        
        logger.info("Scheduler thread stopped")
    
    def get_next_run_time(self):
        """Get the next scheduled run time."""
        jobs = schedule.get_jobs()
        if jobs:
            return jobs[0].next_run
        return None
    
    def run_now(self, job_func):
        """Run a job immediately (for testing purposes)."""
        logger.info("Running job immediately")
        try:
            job_func()
            logger.info("Job completed successfully")
        except Exception as e:
            logger.error(f"Error running job: {str(e)}", exc_info=True)
