from anon import get_instacart_url_from_anon
from claude import get_shopping_list, ShoppingListItem


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
def add_items_to_cart(
    url: str, store_name: str, shopping_list: list[ShoppingListItem]
) -> None:
    pass


# 4. manually checkout on phone
def send_prompt_to_complete_on_mobile() -> None:
    pass


def run():
    before_image_path = "before.jpeg"
    after_image_path = "after.jpeg"
    store_name = "Safeway"

    url = get_authorized_url()
    shopping_list = create_shopping_list(before_image_path, after_image_path)
    add_items_to_cart(url, store_name, shopping_list)
    send_prompt_to_complete_on_mobile()


if __name__ == "__main__":
    run()
