from playwright.async_api import Page
from typing import List
from claude import ShoppingListItem


async def add_items_to_instacart(
    url: str, page: Page, shopping_list: List[ShoppingListItem]
):
    await page.click('a[href="/store/safeway/storefront"]')
    print("On Safeway store; about to add items to cart")
    for item in shopping_list:
        print(f"Searching for {item.item_name}")
        search_input = page.locator("#search-bar-input")
        await search_input.click()
        await search_input.fill(f"{item.item_name}")
        await search_input.press("Enter")

        # Add first result to cart
        add_to_cart_button = page.locator(
            '[data-testid="addItemButtonExpandingAdd"]'
        ).first
        for _ in range(item.quantity):
            await add_to_cart_button.click()
    
    # Keep the session open for 30 seconds after completing
    print("Items added to cart. Keeping session open for 30 seconds...")
    await page.wait_for_timeout(30000)  # Playwright uses milliseconds
