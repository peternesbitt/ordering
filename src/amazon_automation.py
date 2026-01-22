"""
Amazon/Whole Foods Automation
Automates ordering from Amazon/Whole Foods using browser automation.
"""

import os
import time
import logging
from typing import List, Dict, Optional
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeout


logger = logging.getLogger(__name__)


class AmazonAutomation:
    """Automates ordering from Amazon/Whole Foods."""

    def __init__(self, email: str, password: str, headless: bool = True, dry_run: bool = False):
        """
        Initialize Amazon automation.

        Args:
            email: Amazon account email
            password: Amazon account password
            headless: Run browser in headless mode
            dry_run: If True, don't actually place orders
        """
        self.email = email
        self.password = password
        self.headless = headless
        self.dry_run = dry_run
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def start(self):
        """Start the browser."""
        playwright = sync_playwright().start()
        self.browser = playwright.chromium.launch(headless=self.headless)

        # Use persistent context to save login state
        context = self.browser.new_context(
            viewport={'width': 1280, 'height': 720},
            user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        )
        self.page = context.new_page()

    def close(self):
        """Close the browser."""
        if self.browser:
            self.browser.close()

    def login(self):
        """Log in to Amazon."""
        logger.info("Logging in to Amazon...")

        self.page.goto('https://www.amazon.com')

        try:
            # Click sign in
            self.page.click('#nav-link-accountList', timeout=5000)

            # Enter email
            self.page.fill('#ap_email', self.email)
            self.page.click('#continue')

            # Enter password
            self.page.fill('#ap_password', self.password)
            self.page.click('#signInSubmit')

            # Wait for login to complete
            self.page.wait_for_selector('#nav-link-accountList', timeout=10000)
            logger.info("Successfully logged in")

        except PlaywrightTimeout as e:
            logger.error(f"Login failed: {e}")
            raise

    def search_in_order_history(self, item_name: str) -> Optional[Dict[str, str]]:
        """
        Search for an item in order history.

        Args:
            item_name: Name of the item to search for

        Returns:
            Dictionary with product details if found, None otherwise
        """
        logger.info(f"Searching order history for: {item_name}")

        try:
            # Go to order history
            self.page.goto('https://www.amazon.com/gp/your-account/order-history')
            time.sleep(2)

            # Search within orders
            search_box = self.page.query_selector('input[name="search"]')
            if search_box:
                search_box.fill(item_name)
                search_box.press('Enter')
                time.sleep(2)

                # Look for "Buy it again" button for the first matching item
                buy_again_button = self.page.query_selector('[data-action="a-declarative"]')

                if buy_again_button:
                    # Get product details
                    product_title = self.page.query_selector('.yohtmlc-product-title')
                    title = product_title.inner_text() if product_title else item_name

                    logger.info(f"Found product: {title}")
                    return {
                        'name': title,
                        'original_query': item_name,
                        'buy_again_available': True
                    }

            logger.warning(f"Product not found in order history: {item_name}")
            return None

        except Exception as e:
            logger.error(f"Error searching order history: {e}")
            return None

    def buy_again(self, item_name: str) -> bool:
        """
        Add item to cart using "Buy it again" feature.

        Args:
            item_name: Name of the item to reorder

        Returns:
            True if successfully added to cart
        """
        product = self.search_in_order_history(item_name)

        if not product or not product.get('buy_again_available'):
            logger.warning(f"Cannot reorder {item_name} - not found or not available")
            return False

        if self.dry_run:
            logger.info(f"[DRY RUN] Would add to cart: {product['name']}")
            return True

        try:
            # Click "Buy it again" button
            buy_again_button = self.page.query_selector('[data-action="a-declarative"]')
            if buy_again_button:
                buy_again_button.click()
                time.sleep(1)
                logger.info(f"Added to cart: {product['name']}")
                return True
            else:
                logger.error("Buy it again button not found")
                return False

        except Exception as e:
            logger.error(f"Error adding to cart: {e}")
            return False

    def order_whole_foods_item(self, item_name: str) -> bool:
        """
        Order an item from Whole Foods.

        Args:
            item_name: Name of the item to order

        Returns:
            True if successfully added to cart
        """
        logger.info(f"Searching Whole Foods for: {item_name}")

        try:
            # Go to Whole Foods on Amazon
            self.page.goto('https://www.amazon.com/alm/storefront?almBrandId=QW1hem9uIEZyZXNo')
            time.sleep(2)

            # Search for item
            search_box = self.page.query_selector('#searchDropdownBox')
            if search_box:
                search_box.select_option('search-alias=wholefoods')

            search_input = self.page.query_selector('#twotabsearchtextbox')
            if search_input:
                search_input.fill(item_name)
                search_input.press('Enter')
                time.sleep(2)

                # Click first result
                first_result = self.page.query_selector('[data-component-type="s-search-result"]')
                if first_result:
                    first_result.click()
                    time.sleep(2)

                    if self.dry_run:
                        logger.info(f"[DRY RUN] Would add to cart: {item_name}")
                        return True

                    # Add to cart
                    add_to_cart = self.page.query_selector('#add-to-cart-button')
                    if add_to_cart:
                        add_to_cart.click()
                        time.sleep(1)
                        logger.info(f"Added to Whole Foods cart: {item_name}")
                        return True

            logger.warning(f"Could not add Whole Foods item: {item_name}")
            return False

        except Exception as e:
            logger.error(f"Error ordering from Whole Foods: {e}")
            return False

    def process_shopping_list(self, items: List[str], prefer_whole_foods: bool = True):
        """
        Process a list of shopping items.

        Args:
            items: List of item names to order
            prefer_whole_foods: Try Whole Foods first before regular Amazon
        """
        logger.info(f"Processing {len(items)} items...")

        successful = []
        failed = []

        for item in items:
            logger.info(f"\nProcessing: {item}")

            success = False

            # Try order history first (fastest)
            if self.buy_again(item):
                successful.append(item)
                continue

            # Try Whole Foods if preferred
            if prefer_whole_foods:
                if self.order_whole_foods_item(item):
                    successful.append(item)
                    continue

            failed.append(item)

        # Summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Order Summary:")
        logger.info(f"  Successful: {len(successful)}/{len(items)}")
        logger.info(f"  Failed: {len(failed)}/{len(items)}")

        if successful:
            logger.info(f"\nSuccessfully ordered:")
            for item in successful:
                logger.info(f"  ✓ {item}")

        if failed:
            logger.info(f"\nFailed to order:")
            for item in failed:
                logger.info(f"  ✗ {item}")

        logger.info(f"{'='*60}")

        return {
            'successful': successful,
            'failed': failed
        }


def main():
    """Test Amazon automation."""
    from dotenv import load_dotenv
    load_dotenv()

    email = os.getenv('AMAZON_EMAIL')
    password = os.getenv('AMAZON_PASSWORD')

    if not email or not password:
        print("Error: AMAZON_EMAIL and AMAZON_PASSWORD must be set in .env file")
        return

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    # Test items
    test_items = ['bananas', 'milk', 'eggs']

    with AmazonAutomation(email, password, headless=False, dry_run=True) as automation:
        automation.login()
        automation.process_shopping_list(test_items)


if __name__ == '__main__':
    main()
