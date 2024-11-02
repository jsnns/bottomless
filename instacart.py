from playwright.async_api import Page
from typing import List
from claude import ShoppingListItem


async def add_items_to_instacart(
    url: str, page: Page, shopping_list: List[ShoppingListItem]
):
    for item in shopping_list:
        # Search for item
        await page.click('a[href="/store/safeway/storefront"]')

        search_input = page.locator("#search-bar-input")
        await search_input.click()
        await search_input.fill(f"{item.item_name} {item.brand_name or ''}")
        await search_input.press("Enter")

        # Add first result to cart
        add_to_cart_button = page.locator(
            '[data-testid="addItemButtonExpandingAdd"]'
        ).first
        for _ in range(item.quantity):
            await add_to_cart_button.click()
