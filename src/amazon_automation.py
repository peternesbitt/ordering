"""
Amazon/Whole Foods Automation
Automates ordering from Whole Foods using browser automation with interactive cart review.
"""

import os
import time
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from playwright.sync_api import sync_playwright, Page, Browser, TimeoutError as PlaywrightTimeout


logger = logging.getLogger(__name__)


class ProductMatch:
    """Represents a product match from order history."""

    def __init__(self, reminder_item: str, product_name: str, product_url: str = None,
                 order_date: str = None, asin: str = None):
        self.reminder_item = reminder_item
        self.product_name = product_name
        self.product_url = product_url
        self.order_date = order_date
        self.asin = asin
        self.added_to_cart = False

    def to_dict(self):
        return {
            'reminder_item': self.reminder_item,
            'product_name': self.product_name,
            'product_url': self.product_url,
            'order_date': self.order_date,
            'asin': self.asin,
            'added_to_cart': self.added_to_cart
        }


class AmazonAutomation:
    """Automates ordering from Whole Foods with interactive cart review."""

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
        self.playwright_instance = None
        self.matched_products: List[ProductMatch] = []

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def start(self):
        """Start the browser."""
        self.playwright_instance = sync_playwright().start()
        self.browser = self.playwright_instance.chromium.launch(headless=self.headless)

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
        if self.playwright_instance:
            self.playwright_instance.stop()

    def login(self):
        """Log in to Amazon."""
        logger.info("Logging in to Amazon...")

        self.page.goto('https://www.amazon.com')
        time.sleep(2)

        try:
            # Check if already logged in
            account_list = self.page.query_selector('#nav-link-accountList')
            if account_list and 'Hello' in account_list.inner_text():
                logger.info("Already logged in")
                return

            # Click sign in
            self.page.click('#nav-link-accountList', timeout=5000)
            time.sleep(1)

            # Enter email
            email_field = self.page.query_selector('#ap_email')
            if email_field:
                email_field.fill(self.email)
                self.page.click('#continue')
                time.sleep(1)

            # Enter password
            password_field = self.page.query_selector('#ap_password')
            if password_field:
                password_field.fill(self.password)
                self.page.click('#signInSubmit')
                time.sleep(3)

            # Wait for login to complete
            self.page.wait_for_selector('#nav-link-accountList', timeout=10000)
            logger.info("Successfully logged in")

        except PlaywrightTimeout as e:
            logger.error(f"Login failed: {e}")
            raise

    def find_product_in_whole_foods_orders(self, item_name: str) -> Optional[ProductMatch]:
        """
        Search Whole Foods order history for most recent matching product.

        Args:
            item_name: Generic item name from reminder (e.g., "whole milk")

        Returns:
            ProductMatch with exact product details if found
        """
        logger.info(f"Searching Whole Foods order history for: {item_name}")

        try:
            # Go to order history
            self.page.goto('https://www.amazon.com/gp/your-account/order-history')
            time.sleep(2)

            # Filter to show only Whole Foods orders
            # Look through recent orders
            orders = self.page.query_selector_all('.order-card')

            for order in orders[:20]:  # Check last 20 orders
                try:
                    # Check if this is a Whole Foods order
                    order_text = order.inner_text().lower()
                    if 'whole foods' not in order_text and 'amazon fresh' not in order_text:
                        continue

                    # Search for item within this order
                    if item_name.lower() in order_text:
                        # Find the specific product
                        products = order.query_selector_all('.yohtmlc-product-title')
                        for product in products:
                            product_text = product.inner_text()

                            # Check if this product matches the search term
                            if any(word in product_text.lower() for word in item_name.lower().split()):
                                # Get product link
                                product_link = product.query_selector('a')
                                product_url = product_link.get_attribute('href') if product_link else None

                                # Get order date
                                date_elem = order.query_selector('.order-date-invoice-item')
                                order_date = date_elem.inner_text() if date_elem else None

                                # Extract ASIN from URL
                                asin = None
                                if product_url and '/dp/' in product_url:
                                    asin = product_url.split('/dp/')[1].split('/')[0]

                                match = ProductMatch(
                                    reminder_item=item_name,
                                    product_name=product_text,
                                    product_url=product_url,
                                    order_date=order_date,
                                    asin=asin
                                )

                                logger.info(f"Found match: {product_text}")
                                return match

                except Exception as e:
                    logger.debug(f"Error processing order: {e}")
                    continue

            # If not found in orders, search order history
            logger.info(f"Searching order history search for: {item_name}")
            search_box = self.page.query_selector('input[name="search"]')
            if search_box:
                search_box.fill(item_name)
                search_box.press('Enter')
                time.sleep(3)

                # Look for first Whole Foods result
                results = self.page.query_selector_all('.order-card')
                for result in results[:5]:
                    result_text = result.inner_text().lower()
                    if 'whole foods' in result_text or 'amazon fresh' in result_text:
                        products = result.query_selector_all('.yohtmlc-product-title')
                        if products:
                            product = products[0]
                            product_text = product.inner_text()
                            product_link = product.query_selector('a')
                            product_url = product_link.get_attribute('href') if product_link else None

                            # Extract ASIN
                            asin = None
                            if product_url and '/dp/' in product_url:
                                asin = product_url.split('/dp/')[1].split('/')[0]

                            match = ProductMatch(
                                reminder_item=item_name,
                                product_name=product_text,
                                product_url=product_url,
                                asin=asin
                            )

                            logger.info(f"Found match from search: {product_text}")
                            return match

            logger.warning(f"No Whole Foods order history found for: {item_name}")
            return None

        except Exception as e:
            logger.error(f"Error searching order history: {e}")
            return None

    def add_to_cart_by_asin(self, product: ProductMatch) -> bool:
        """
        Add a product to cart using its ASIN.

        Args:
            product: ProductMatch with ASIN

        Returns:
            True if successfully added to cart
        """
        if not product.asin and not product.product_url:
            logger.error(f"No ASIN or URL for product: {product.product_name}")
            return False

        try:
            # Go to product page
            if product.product_url:
                url = f"https://www.amazon.com{product.product_url}" if product.product_url.startswith('/') else product.product_url
            else:
                url = f"https://www.amazon.com/dp/{product.asin}"

            logger.info(f"Loading product page: {product.product_name}")
            self.page.goto(url)
            time.sleep(2)

            if self.dry_run:
                logger.info(f"[DRY RUN] Would add to cart: {product.product_name}")
                product.added_to_cart = True
                return True

            # Look for "Add to Cart" button
            add_to_cart = self.page.query_selector('#add-to-cart-button')
            if not add_to_cart:
                # Try alternative selectors
                add_to_cart = self.page.query_selector('[name="submit.add-to-cart"]')

            if add_to_cart:
                add_to_cart.click()
                time.sleep(2)
                logger.info(f"Added to cart: {product.product_name}")
                product.added_to_cart = True
                return True
            else:
                logger.warning(f"Add to cart button not found for: {product.product_name}")
                return False

        except Exception as e:
            logger.error(f"Error adding to cart: {e}")
            return False

    def build_cart(self, items: List[str]) -> Tuple[List[ProductMatch], List[str]]:
        """
        Build shopping cart by finding and adding products from order history.

        Args:
            items: List of item names from reminders

        Returns:
            Tuple of (matched_products, failed_items)
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"Building cart for {len(items)} items...")
        logger.info(f"{'='*60}\n")

        matched = []
        failed = []

        for item in items:
            logger.info(f"Processing: {item}")

            # Find product in order history
            product = self.find_product_in_whole_foods_orders(item)

            if product:
                matched.append(product)
                logger.info(f"  ✓ Found: {product.product_name}")
            else:
                failed.append(item)
                logger.warning(f"  ✗ Not found in order history")

            time.sleep(1)  # Be nice to Amazon

        self.matched_products = matched
        return matched, failed

    def display_cart_review(self, matched: List[ProductMatch], failed: List[str]):
        """
        Display cart for user review.

        Args:
            matched: List of matched products
            failed: List of items that couldn't be matched
        """
        print(f"\n{'='*70}")
        print("CART REVIEW - Please verify before ordering")
        print(f"{'='*70}\n")

        if matched:
            print(f"Items to be ordered ({len(matched)}):")
            print(f"{'-'*70}")
            for i, product in enumerate(matched, 1):
                print(f"{i}. {product.product_name}")
                print(f"   From reminder: '{product.reminder_item}'")
                if product.order_date:
                    print(f"   Last ordered: {product.order_date}")
                print()

        if failed:
            print(f"\nItems NOT found in order history ({len(failed)}):")
            print(f"{'-'*70}")
            for item in failed:
                print(f"  ✗ {item}")
            print()

        print(f"{'='*70}\n")

    def get_user_approval(self) -> bool:
        """
        Get user approval to proceed with order.

        Returns:
            True if user approves
        """
        while True:
            response = input("Proceed with adding these items to cart? (yes/no): ").lower().strip()
            if response in ['yes', 'y']:
                return True
            elif response in ['no', 'n']:
                return False
            else:
                print("Please enter 'yes' or 'no'")

    def add_all_to_cart(self) -> List[ProductMatch]:
        """
        Add all matched products to cart.

        Returns:
            List of successfully added products
        """
        logger.info(f"\n{'='*60}")
        logger.info("Adding items to cart...")
        logger.info(f"{'='*60}\n")

        successfully_added = []

        for product in self.matched_products:
            logger.info(f"Adding: {product.product_name}")
            if self.add_to_cart_by_asin(product):
                successfully_added.append(product)
                logger.info("  ✓ Success")
            else:
                logger.warning("  ✗ Failed")
            time.sleep(1)

        return successfully_added

    def verify_delivery(self, order_id: str = None) -> Dict[str, List[str]]:
        """
        Check order status and verify what was delivered vs out of stock.

        Args:
            order_id: Optional specific order ID to check

        Returns:
            Dict with 'delivered' and 'out_of_stock' lists
        """
        logger.info("Checking delivery status...")

        try:
            # Go to recent orders
            self.page.goto('https://www.amazon.com/gp/your-account/order-history')
            time.sleep(2)

            # Get most recent order (or specific order)
            orders = self.page.query_selector_all('.order-card')
            if not orders:
                logger.warning("No orders found")
                return {'delivered': [], 'out_of_stock': []}

            recent_order = orders[0]  # Most recent

            # Check order status
            status_text = recent_order.inner_text().lower()

            delivered = []
            out_of_stock = []

            # Parse delivered items
            products = recent_order.query_selector_all('.yohtmlc-product-title')
            for product in products:
                product_name = product.inner_text()

                # Check if item shows as out of stock or refunded
                parent = product.evaluate_handle('el => el.closest(".shipment")')
                if parent:
                    shipment_text = parent.json_value().lower() if hasattr(parent, 'json_value') else ""

                    if 'out of stock' in shipment_text or 'not available' in shipment_text or 'refund' in shipment_text:
                        out_of_stock.append(product_name)
                    else:
                        delivered.append(product_name)
                else:
                    # If can't determine, assume delivered
                    delivered.append(product_name)

            logger.info(f"Delivered: {len(delivered)} items")
            logger.info(f"Out of stock: {len(out_of_stock)} items")

            return {
                'delivered': delivered,
                'out_of_stock': out_of_stock
            }

        except Exception as e:
            logger.error(f"Error verifying delivery: {e}")
            return {'delivered': [], 'out_of_stock': []}

    def process_shopping_list(self, items: List[str], interactive: bool = True) -> Dict:
        """
        Complete workflow: find products, review cart, add to cart.

        Args:
            items: List of item names from reminders
            interactive: If True, require user approval before adding to cart

        Returns:
            Dict with results including matched, failed, and added products
        """
        # Step 1: Build cart from order history
        matched, failed = self.build_cart(items)

        if not matched and not failed:
            logger.info("No items to process")
            return {'matched': [], 'failed': [], 'added': []}

        # Step 2: Display cart for review
        self.display_cart_review(matched, failed)

        # Step 3: Get approval (if interactive)
        if interactive and not self.dry_run:
            if not self.get_user_approval():
                logger.info("User cancelled order")
                return {'matched': matched, 'failed': failed, 'added': [], 'cancelled': True}

        # Step 4: Add to cart
        added = self.add_all_to_cart()

        # Summary
        logger.info(f"\n{'='*60}")
        logger.info("SUMMARY")
        logger.info(f"{'='*60}")
        logger.info(f"Items processed: {len(items)}")
        logger.info(f"Matched from history: {len(matched)}")
        logger.info(f"Added to cart: {len(added)}")
        logger.info(f"Failed to find: {len(failed)}")
        logger.info(f"{'='*60}\n")

        return {
            'matched': matched,
            'failed': failed,
            'added': added,
            'cancelled': False
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
    test_items = ['whole milk', 'bananas', 'eggs']

    with AmazonAutomation(email, password, headless=False, dry_run=True) as automation:
        automation.login()
        result = automation.process_shopping_list(test_items, interactive=True)

        print("\n" + "="*60)
        print("Test completed!")
        print(f"Matched: {len(result['matched'])}")
        print(f"Failed: {len(result['failed'])}")
        print("="*60)


if __name__ == '__main__':
    main()
