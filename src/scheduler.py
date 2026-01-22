"""
Daily Scheduler
Runs the ordering automation on a daily schedule.
"""

import os
import time
import logging
from datetime import datetime
from typing import Optional
import schedule

from dotenv import load_dotenv
from .reminders_reader import RemindersReader
from .amazon_automation import AmazonAutomation


logger = logging.getLogger(__name__)


class OrderingScheduler:
    """Schedules and runs daily ordering automation."""

    def __init__(
        self,
        run_time: str = "09:00",
        reminders_list_name: Optional[str] = None,
        headless: bool = True,
        dry_run: bool = False
    ):
        """
        Initialize the scheduler.

        Args:
            run_time: Time to run daily (HH:MM format)
            reminders_list_name: Name of reminders list to scan
            headless: Run browser in headless mode
            dry_run: Test mode without placing actual orders
        """
        self.run_time = run_time
        self.reminders_list_name = reminders_list_name
        self.headless = headless
        self.dry_run = dry_run

        # Load credentials
        load_dotenv()
        self.amazon_email = os.getenv('AMAZON_EMAIL')
        self.amazon_password = os.getenv('AMAZON_PASSWORD')

        if not self.amazon_email or not self.amazon_password:
            raise ValueError("AMAZON_EMAIL and AMAZON_PASSWORD must be set in .env file")

    def run_ordering_job(self):
        """Run the ordering job once."""
        logger.info("=" * 80)
        logger.info(f"Starting ordering job at {datetime.now()}")
        logger.info("=" * 80)

        try:
            # Step 1: Read reminders
            logger.info("\n[1/3] Reading Apple Reminders...")
            reader = RemindersReader()
            items = reader.get_shopping_items(self.reminders_list_name)

            if not items:
                logger.info("No items found in reminders. Nothing to order.")
                return

            logger.info(f"Found {len(items)} items to order:")
            for item in items:
                logger.info(f"  - {item}")

            # Step 2: Process orders
            logger.info("\n[2/3] Processing orders on Amazon...")
            with AmazonAutomation(
                self.amazon_email,
                self.amazon_password,
                headless=self.headless,
                dry_run=self.dry_run
            ) as automation:
                automation.login()
                result = automation.process_shopping_list(items)

            # Step 3: Report results
            logger.info("\n[3/3] Job completed!")
            logger.info(f"Successfully ordered: {len(result['successful'])} items")
            logger.info(f"Failed to order: {len(result['failed'])} items")

        except Exception as e:
            logger.error(f"Error running ordering job: {e}", exc_info=True)
        finally:
            logger.info("=" * 80)

    def run_once(self):
        """Run the job once immediately."""
        self.run_ordering_job()

    def start_scheduler(self):
        """Start the daily scheduler."""
        logger.info(f"Scheduler started. Will run daily at {self.run_time}")
        logger.info(f"Reminders list: {self.reminders_list_name or 'All lists'}")
        logger.info(f"Dry run mode: {self.dry_run}")
        logger.info("Press Ctrl+C to stop\n")

        # Schedule the job
        schedule.every().day.at(self.run_time).do(self.run_ordering_job)

        # Keep running
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("\nScheduler stopped by user")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Automate Amazon/Whole Foods orders from Apple Reminders'
    )
    parser.add_argument(
        '--run-now',
        action='store_true',
        help='Run immediately instead of scheduling'
    )
    parser.add_argument(
        '--time',
        default=os.getenv('RUN_TIME', '09:00'),
        help='Daily run time (HH:MM format, default: 09:00)'
    )
    parser.add_argument(
        '--list',
        default=os.getenv('REMINDERS_LIST_NAME'),
        help='Reminders list name (default: all lists)'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Show browser window'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Test mode without placing actual orders'
    )
    parser.add_argument(
        '--debug',
        action='store_true',
        help='Enable debug logging'
    )

    args = parser.parse_args()

    # Configure logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('ordering.log')
        ]
    )

    # Override dry-run from env if not set
    dry_run = args.dry_run or os.getenv('DRY_RUN', 'false').lower() == 'true'
    headless = not args.no_headless and os.getenv('HEADLESS', 'true').lower() == 'true'

    # Create scheduler
    scheduler = OrderingScheduler(
        run_time=args.time,
        reminders_list_name=args.list,
        headless=headless,
        dry_run=dry_run
    )

    # Run
    if args.run_now:
        scheduler.run_once()
    else:
        scheduler.start_scheduler()


if __name__ == '__main__':
    main()
