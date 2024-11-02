from playwright.sync_api import Page
from typing import List
from claude import ShoppingListItem


def add_items_to_instacart(url: str, page: Page, shopping_list: List[ShoppingListItem]):
    for item in shopping_list:
        # Search for item
        page.goto(f"https://www.instacart.com/store/safeway/s?k={item.item_name}")

        # Add first result to cart
        add_to_cart_button = page.locator(
            '[data-testid="addItemButtonExpandingAdd"]'
        ).first
        add_to_cart_button.click()
