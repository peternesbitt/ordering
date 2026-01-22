"""
Daily Scheduler
Runs the ordering automation on a daily schedule at 7pm.
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
        run_time: str = "19:00",  # 7 PM default
        reminders_list_name: Optional[str] = None,
        headless: bool = True,
        dry_run: bool = False,
        interactive: bool = True
    ):
        """
        Initialize the scheduler.

        Args:
            run_time: Time to run daily (HH:MM format, default 19:00/7pm)
            reminders_list_name: Name of reminders list to scan
            headless: Run browser in headless mode
            dry_run: Test mode without placing actual orders
            interactive: Require user approval before adding to cart
        """
        self.run_time = run_time
        self.reminders_list_name = reminders_list_name
        self.headless = headless
        self.dry_run = dry_run
        self.interactive = interactive

        # Load credentials
        load_dotenv()
        self.amazon_email = os.getenv('AMAZON_EMAIL')
        self.amazon_password = os.getenv('AMAZON_PASSWORD')

        if not self.amazon_email or not self.amazon_password:
            raise ValueError("AMAZON_EMAIL and AMAZON_PASSWORD must be set in .env file")

    def run_ordering_job(self):
        """Run the complete ordering workflow."""
        logger.info("=" * 80)
        logger.info(f"Starting ordering job at {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        logger.info("=" * 80)

        reader = None

        try:
            # Step 1: Read reminders
            logger.info("\n[1/4] Reading Apple Reminders...")
            reader = RemindersReader()
            items = reader.get_shopping_items(self.reminders_list_name)

            if not items:
                logger.info("No items found in reminders. Nothing to order.")
                return

            logger.info(f"Found {len(items)} items to order:")
            for item in items:
                logger.info(f"  - {item}")

            # Step 2: Find products and build cart
            logger.info("\n[2/4] Searching Whole Foods order history and building cart...")
            with AmazonAutomation(
                self.amazon_email,
                self.amazon_password,
                headless=self.headless,
                dry_run=self.dry_run
            ) as automation:
                automation.login()

                # Process shopping list with interactive approval
                result = automation.process_shopping_list(items, interactive=self.interactive)

                if result.get('cancelled'):
                    logger.info("Order cancelled by user")
                    return

                # Step 3: Mark successfully added items as complete in Reminders
                added_products = result.get('added', [])
                if added_products and not self.dry_run:
                    logger.info(f"\n[3/4] Marking {len(added_products)} items complete in Reminders...")

                    completed_items = []
                    for product in added_products:
                        if product.added_to_cart:
                            completed_items.append(product.reminder_item)

                    if completed_items:
                        completion_results = reader.mark_multiple_complete(completed_items)

                        success_count = sum(1 for success in completion_results.values() if success)
                        logger.info(f"Marked {success_count}/{len(completed_items)} items complete")
                else:
                    logger.info("\n[3/4] Skipping reminder completion (dry run mode)")

                # Step 4: Final summary
                logger.info("\n[4/4] Job completed!")
                logger.info(f"Items from reminders: {len(items)}")
                logger.info(f"Matched from order history: {len(result.get('matched', []))}")
                logger.info(f"Added to cart: {len(added_products)}")
                logger.info(f"Not found in history: {len(result.get('failed', []))}")

                if result.get('failed'):
                    logger.info("\nItems not found in order history:")
                    for item in result['failed']:
                        logger.info(f"  ✗ {item}")
                    logger.info("\nThese items were not ordered. You may need to:")
                    logger.info("  1. Order them manually once, or")
                    logger.info("  2. Update the reminder name to match previous orders")

        except Exception as e:
            logger.error(f"Error running ordering job: {e}", exc_info=True)
        finally:
            logger.info("=" * 80)

    def verify_recent_delivery(self):
        """
        Check recent order for delivered vs out-of-stock items.
        This should be run after delivery is completed.
        """
        logger.info("=" * 80)
        logger.info(f"Checking delivery status at {datetime.now().strftime('%Y-%m-%d %I:%M %p')}")
        logger.info("=" * 80)

        try:
            reader = RemindersReader()

            with AmazonAutomation(
                self.amazon_email,
                self.amazon_password,
                headless=self.headless,
                dry_run=False
            ) as automation:
                automation.login()

                # Check delivery status
                delivery_status = automation.verify_delivery()

                delivered = delivery_status.get('delivered', [])
                out_of_stock = delivery_status.get('out_of_stock', [])

                logger.info(f"\nDelivery Summary:")
                logger.info(f"  Delivered: {len(delivered)} items")
                logger.info(f"  Out of stock: {len(out_of_stock)} items")

                if delivered:
                    logger.info("\nDelivered items:")
                    for item in delivered:
                        logger.info(f"  ✓ {item}")

                if out_of_stock:
                    logger.info("\nOut of stock items (not delivered):")
                    for item in out_of_stock:
                        logger.info(f"  ✗ {item}")

                    # These items should be re-added to reminders
                    logger.info("\nThese items need to be reordered.")
                    logger.info("Add them back to your Reminders for tomorrow's order.")

        except Exception as e:
            logger.error(f"Error checking delivery: {e}", exc_info=True)
        finally:
            logger.info("=" * 80)

    def run_once(self):
        """Run the job once immediately."""
        self.run_ordering_job()

    def start_scheduler(self):
        """Start the daily scheduler."""
        logger.info(f"Scheduler started. Will run daily at {self.run_time}")
        logger.info(f"Reminders list: {self.reminders_list_name or 'All lists'}")
        logger.info(f"Interactive mode: {self.interactive}")
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
        description='Automate Whole Foods orders from Apple Reminders'
    )
    parser.add_argument(
        '--run-now',
        action='store_true',
        help='Run immediately instead of scheduling'
    )
    parser.add_argument(
        '--time',
        default=os.getenv('RUN_TIME', '19:00'),
        help='Daily run time (HH:MM format, default: 19:00/7pm)'
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
        '--no-interactive',
        action='store_true',
        help='Skip cart review approval (auto-approve)'
    )
    parser.add_argument(
        '--verify-delivery',
        action='store_true',
        help='Check recent order delivery status'
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

    # Override settings from env if not set
    dry_run = args.dry_run or os.getenv('DRY_RUN', 'false').lower() == 'true'
    headless = not args.no_headless and os.getenv('HEADLESS', 'true').lower() == 'true'
    interactive = not args.no_interactive

    # Create scheduler
    scheduler = OrderingScheduler(
        run_time=args.time,
        reminders_list_name=args.list,
        headless=headless,
        dry_run=dry_run,
        interactive=interactive
    )

    # Run based on mode
    if args.verify_delivery:
        scheduler.verify_recent_delivery()
    elif args.run_now:
        scheduler.run_once()
    else:
        scheduler.start_scheduler()


if __name__ == '__main__':
    main()
