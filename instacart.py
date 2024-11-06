from playwright.async_api import Page
from typing import List
from claude import ShoppingListItem


async def add_items_to_instacart(
    url: str, page: Page, shopping_list: List[ShoppingListItem]
):
    try:
        # Click on Safeway store and wait for navigation
        await page.click('a[href="/store/safeway/storefront"]')
        print("Clicked on Safeway store")
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(5000)  # Wait 5 seconds for any animations/popups

        # Try multiple approaches to close any modal
        try:
            # 1. Try the specific close button we found
            try:
                close_button = page.locator('button[data-testid="desktop-close"]')
                await close_button.click(timeout=3000)
                print("Closed modal using desktop-close button")
            except:
                print("Couldn't find desktop-close button")

            # 2. Try clicking outside the modal (top-left corner is usually safe)
            try:
                await page.mouse.click(10, 10)
                print("Clicked outside modal")
            except:
                print("Couldn't click outside modal")

            # 3. Try pressing Escape key
            try:
                await page.keyboard.press("Escape")
                print("Pressed Escape key")
            except:
                print("Couldn't press Escape")

        except Exception as e:
            print(f"Good, there was no overlay modal to dismiss. Error: {str(e)}")

        print("On Safeway store; about to add items to cart")
        for item in shopping_list:
            print(f"Searching for {item.item_name}")
            search_input = page.locator("#search-bar-input")
            await search_input.click()
            await search_input.fill(f"{item.item_name}")
            await search_input.press("Enter")
            await page.wait_for_timeout(3000)  # Wait for search results

            # Add first result to cart
            add_to_cart_button = page.locator(
                '[data-testid="addItemButtonExpandingAdd"]'
            ).first
            for _ in range(item.quantity):
                await add_to_cart_button.click()
                await page.wait_for_timeout(2000)  # Wait between clicks
        
        # Keep the session open for 30 seconds after completing
        print("Items added to cart. Keeping session open for 30 seconds...")
        await page.wait_for_timeout(30000)  # Playwright uses milliseconds

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Keeping session open for debugging...")
        await page.wait_for_timeout(30000)
