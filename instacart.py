from playwright.async_api import Page
from typing import List
from claude import ShoppingListItem


async def dismiss_modal(page: Page):
    """Attempts to dismiss any modal/popup that might be present"""
    try:
        # First try the most specific approach - the close button
        try:
            close_button = page.locator('button[data-testid="desktop-close"]').first
            if await close_button.is_visible():
                print("Found close button with desktop-close, clicking it...")
                await close_button.click()
                await page.wait_for_timeout(1000)  # Wait for animation
                return True
        except Exception as e:
            print(f"Could not click desktop-close button: {str(e)}")

        # Then try finding the modal container and its close button
        try:
            modal = page.locator('div[data-dialog-ref]').first
            if await modal.is_visible():
                print("Found modal with dialog-ref, looking for its close button...")
                close_button = modal.locator('button').first
                await close_button.click()
                await page.wait_for_timeout(1000)
                return True
        except Exception as e:
            print(f"Could not close modal via container: {str(e)}")

        # Last resort - try clicking outside
        try:
            print("Attempting to click outside modal...")
            await page.mouse.click(10, 10)
            await page.wait_for_timeout(1000)
            return True
        except Exception as e:
            print(f"Could not click outside modal: {str(e)}")

        return False

    except Exception as e:
        print(f"Error in dismiss_modal: {str(e)}")
        return False


async def retry_with_modal_handling(page: Page, action):
    """Retries an async action if it fails due to a modal, attempting to dismiss the modal first"""
    try:
        return await action()
    except Exception as e:
        if "intercepted" in str(e) or "Timeout" in str(e):
            print("Action failed, checking for modal...")
            if await dismiss_modal(page):
                print("Modal dismissed, retrying action...")
                await page.wait_for_timeout(1000)  # Brief wait after dismissal
                return await action()
        raise e


async def add_items_to_instacart(
    url: str, page: Page, shopping_list: List[ShoppingListItem]
):
    try:
        # Wait for initial page load
        await page.wait_for_load_state('networkidle')
        print("Initial page loaded, waiting for Safeway link...")
        
        # Click Safeway with detailed logging
        safeway_selector = 'a[href="/store/safeway/storefront"]'
        print(f"Looking for Safeway link with selector: {safeway_selector}")
        
        await retry_with_modal_handling(page, 
            lambda: page.click(safeway_selector)
        )
        
        current_url = page.url
        print(f"Navigation complete. Current URL: {current_url}")
        
        print("On Safeway store; about to add items to cart")
        for item in shopping_list:
            print(f"Searching for {item.item_name}")
            
            # Search for item (with modal handling)
            print("Attempting to click search input...")
            await retry_with_modal_handling(page, lambda: page.locator("#search-bar-input").click())
            print(f"Filling search input with: {item.item_name}")
            await page.fill("#search-bar-input", item.item_name)
            await page.press("#search-bar-input", "Enter")
            print("Waiting for search results...")
            await page.wait_for_timeout(3000)

            # Add to cart (with modal handling)
            print("Looking for add to cart button...")
            add_to_cart_button = page.locator(
                '[data-testid="addItemButtonExpandingAdd"]'
            ).first
            for i in range(item.quantity):
                print(f"Adding to cart (attempt {i+1}/{item.quantity})...")
                await retry_with_modal_handling(page, lambda: add_to_cart_button.click())
                await page.wait_for_timeout(2000)
            print(f"Successfully added {item.item_name} to cart")
        
        print("All items added to cart. Keeping session open for 30 seconds...")
        await page.wait_for_timeout(30000)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Current URL:", page.url)
        print("Keeping session open for debugging...")
        await page.wait_for_timeout(30000)
