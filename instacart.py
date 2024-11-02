from playwright.sync_api import Page
from typing import List
from claude import ShoppingListItem


def add_items_to_instacart(url: str, page: Page, shopping_list: List[ShoppingListItem]):
    page.goto(url)
    for item in shopping_list:
        # Search for item
        search_input = page.locator("#search-bar-input")
        search_input.click()
        search_input.fill(item.item_name)
        search_input.press("Enter")

        # Add first result to cart
        add_to_cart_button = page.get_by_role("button", name="Add to cart").first
        add_to_cart_button.click()
