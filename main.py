from anon import get_instacart_url_from_anon
from claude import get_shopping_list, ShoppingListItem
from instacart import add_items_to_instacart
from playwright.sync_api import Page


# 1. create url with anon
def get_authorized_url() -> str:
    return get_instacart_url_from_anon()


# 2. create shopping list from images
def create_shopping_list(
    before_image_path: str, after_image_path: str
) -> list[ShoppingListItem]:
    """returns a list of dictionaries with the item name and quantity.
    {item_name: str, quantity: int, brand_name?: str}"""
    return get_shopping_list(before_image_path, after_image_path)


# 3. add items to cart with computer use
def add_items_to_cart(url: str, shopping_list: list[ShoppingListItem]) -> None:
    from playwright.sync_api import sync_playwright

    with sync_playwright() as playwright:
        browser = playwright.chromium.connect_over_cdp(url)
        default_context = browser.contexts[0]
        page = default_context.pages[0]
        add_items_to_instacart(url, page, shopping_list)


# 4. manually checkout on phone
def send_prompt_to_complete_on_mobile() -> None:
    pass


def run():
    before_image_path = "before.jpeg"
    after_image_path = "after.jpeg"

    url = get_authorized_url()
    print("Got url from anon", url)
    shopping_list = create_shopping_list(before_image_path, after_image_path)
    print("Created shopping list")
    for item in shopping_list:
        print(item)
    add_items_to_cart(url, shopping_list)
    print("Added items to cart")
    send_prompt_to_complete_on_mobile()


if __name__ == "__main__":
    run()
