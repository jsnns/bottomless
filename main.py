from anon import get_instacart_url_from_anon
from claude import get_shopping_list, ShoppingListItem
from instacart import add_items_to_instacart, complete_checkout, clear_cart
from playwright.sync_api import Page
import os


# 1. create url with anon
def get_authorized_url() -> str:
    return get_instacart_url_from_anon()[0]


# 2. create shopping list from images
def create_shopping_list(
    before_image_path: str, after_image_path: str
) -> list[ShoppingListItem]:
    """returns a list of dictionaries with the item name and quantity.
    {item_name: str, quantity: int, brand_name?: str}"""
    return get_shopping_list(before_image_path, after_image_path)


# 3. add items to cart with computer use
async def go_shopping(url: str, shopping_list: list[ShoppingListItem]) -> None:
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser = await playwright.chromium.connect_over_cdp(url)
        default_context = browser.contexts[0]
        page = default_context.pages[0]
        try:
            # Don't navigate away - the WebSocket URL is probably single-use
            if os.getenv('CLEAR_CART_BEFORE_SHOPPING', 'false').lower() == 'true':
                print("First, clear cart in case there are items already in it")
                await clear_cart(page)
            print("Ok, now go shopping for just the new items")
            await add_items_to_instacart(url, page, shopping_list)
            print("Added items to Instacart cart")
            if os.getenv('DO_PAY_WITHOUT_HUMAN_CONFIRMATION', 'false').lower() == 'true':
                await complete_checkout(page)
            print("Completed checkout")
        except Exception as e:
            print(f"Shopping failed: {str(e)}")
            raise e  # Re-raise to handle in the calling function


# 4. manually checkout on phone
def send_prompt_to_complete_on_mobile() -> None:
    print("To do: send_prompt_to_complete_on_mobile")


def run():
    # Temporary hard-coded shopping list for testing
    use_hardcoded_list = os.getenv('USE_HARDCODED_SHOPPING_LIST', 'false').lower() == 'true'
    
    if use_hardcoded_list:
        shopping_list = [
            ShoppingListItem(
                item_name='Hard Seltzer',
                category='Beverages',
                quantity=1,
                unit='six pack',
                brand_name='Blue Drop'
            ),
            # ShoppingListItem(
            #     item_name='Whole Milk',
            #     category='Dairy',
            #     quantity=1,
            #     unit='half gallon',
            #     brand_name='Whole Foods'
            # ),
            # ShoppingListItem(
            #     item_name='Prepared Meals',
            #     category='Ready-to-eat',
            #     quantity=2,
            #     unit='container',
            #     brand_name='Fresh'
            # )
        ]
    else:
        before_image_path = "before.jpeg"
        after_image_path = "after.jpeg"
        shopping_list = create_shopping_list(before_image_path, after_image_path)

    url = get_authorized_url()
    print("Got url from anon", url)
    
    if use_hardcoded_list:
        print("Using hard-coded shopping list for testing:")
    else:
        print("Using shopping list from images:")
    
    for item in shopping_list:
        print(item)
        
    import asyncio
    asyncio.run(go_shopping(url, shopping_list))
    print("Went shopping. ")
    send_prompt_to_complete_on_mobile()


if __name__ == "__main__":
    run()
