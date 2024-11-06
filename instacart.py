from playwright.async_api import Page
from typing import List
from claude import ShoppingListItem


async def dismiss_modal(page: Page):
    """Attempts to dismiss any modal/popup that might be present"""
    try:
        # First try clicking outside
        try:
            print("Attempting to click outside modal...")
            await page.mouse.click(10, 10)
            await page.wait_for_timeout(1000)
            return True
        except Exception as e:
            print(f"Could not click outside modal: {str(e)}")

        # Try the most specific approach - the close button
        try:
            close_button = page.locator('button[data-testid="desktop-close"]').first
            if await close_button.is_visible():
                print("Found close button with desktop-close, clicking it...")
                await close_button.click()
                await page.wait_for_timeout(1000)  # Wait for animation
                return True
        except Exception as e:
            print(f"Could not click desktop-close button: {str(e)}")

        # Try finding the modal container and its close button
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


async def go_to_the_safeway_store(page: Page):
    """Ensures we're on the Safeway storefront in Instacart"""
    try:
        print("Waiting for initial page load...")
        # wait_for_load_state('networkidle') might be too strict - it waits until there are no network connections for at least 500ms. In a modern web app like Instacart, there might always be some background network activity, causing this to timeout.
        await page.wait_for_timeout(3500)  # Simple timeout instead of networkidle
        print(f"Initial page loaded. Current URL: {page.url}") 
        print("Ensuring we're on Safeway storefront...")
        
        # Click Safeway with detailed logging
        safeway_selector = 'a[href="/store/safeway/storefront"]'
        print(f"Looking for Safeway link with selector: {safeway_selector}")
        
        # Check if element exists and is visible
        safeway_link = page.locator(safeway_selector).first
        is_visible = await safeway_link.is_visible()
        print(f"Safeway link visible: {is_visible}")
        
        # Get page content if element not found
        if not is_visible:
            print("Safeway link not visible, checking page content...")
            # Get all links on the page
            all_links = await page.locator('a').all()
            print("Found links on page:")
            for link in all_links:
                href = await link.get_attribute('href')
                text = await link.text_content()
                print(f"Link: href='{href}', text='{text}'")
        else:
            await retry_with_modal_handling(page, lambda: safeway_link.click())
            await page.wait_for_timeout(3500)
            
        print(f"Navigation complete. Current URL: {page.url}")
        
    except Exception as e:
        print(f"Error going to Safeway store: {str(e)}")
        print(f"Current URL: {page.url}")


async def add_items_to_instacart(
    url: str, page: Page, shopping_list: List[ShoppingListItem]
):
    try:
        # First ensure we're on Safeway storefront
        await go_to_the_safeway_store(page)
        
        print("On Safeway store; about to add items to cart")
        for item in shopping_list:  # Remove the [:1] slice
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
        
        print("All items added to cart. Keeping session open for 3 seconds...")
        await page.wait_for_timeout(3000)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        print("Current URL:", page.url)
        print("Keeping session open for debugging...")
        await page.wait_for_timeout(30000)


async def complete_checkout(page: Page):
    """WARNING: Complete the checkout process after items are in cart,
       without any further confirmation. 
       If you leave this code as is, you may wish to be ready to 
       immediately cancel the order manually.
    """
    try:
        print("Starting checkout process...")
        
        # Step 1: View cart
        print("Opening cart...")
        cart_button = page.locator('button[aria-controls="cart_dialog"]').first
        await retry_with_modal_handling(page, lambda: cart_button.click())
        # wait_for_load_state('networkidle') might be too strict - it waits until there are no network connections for at least 500ms. In a modern web app like Instacart, there might always be some background network activity, causing this to timeout.
        await page.wait_for_timeout(3000)  # Simple timeout instead of networkidle
        
        
        # Step 2: Go to checkout
        print("Go to checkout...")
        checkout_button = page.locator('button:has-text("Go to checkout")').first
        # print("Waiting for checkout button to be enabled...")
        await page.wait_for_selector('button:has-text("Go to checkout"):not([disabled])', timeout=27800)
        await checkout_button.click()
        await page.wait_for_timeout(3000)
        
        # Step 3: Continue to checkout
        print("Continue to checkout...")
        continue_button = page.locator('button:has-text("Continue to checkout")').first
        await continue_button.click()
        await page.wait_for_timeout(3000)
        
        # Step 4: Handle ID verification if it appears
        try:
            id_continue_button = page.locator('button:has-text("Continue")').first
            if await id_continue_button.is_visible():
                print("ID verification modal detected, clicking Continue...")
                await id_continue_button.click()
                await page.wait_for_timeout(3000)  # Simple timeout instead of networkidle
        except Exception as e:
            print("No ID verification needed, continuing...")
        
        # Step 5: Select Super Saver delivery
        try:
            print("Selecting Super Saver delivery...")
            # Click Super Saver option
            super_saver = page.locator('li:has-text("Super Saver")').first
            await super_saver.click()
            await page.wait_for_timeout(2000)
            
            # Select second available day
            print("Selecting second available day...")
            day_buttons = page.locator('div[role="tablist"] button')
            second_day = day_buttons.nth(1)  # Get second button (index 1)
            print("Selecting second soonest Super Saver day...")
            await second_day.click()
            await page.wait_for_timeout(2000)

            # Select second available time slot
            print("Selecting second available time slot...")
            day_buttons = page.locator('div[role="tabpanel"] button')
            button_count = await day_buttons.count()
            print(f"Found {button_count} time slot buttons")

            if button_count > 1:
                second_day = day_buttons.nth(1)  # Get second button (index 1)
                print("Selecting second soonest Super Saver day...")
                await second_day.click()
            else:
                print("Not enough time slot buttons found")

            await page.wait_for_timeout(2000)

            # Select first available morning time slot
            print("Looking for first available morning time slot...")
            morning_times = ["7am", "8am", "9am", "10am", "11am"]
            time_found = False
            
            for time in morning_times:
                try:
                    # Look for button containing this time
                    slot = page.locator(f'button:has-text("{time}")').first
                    if await slot.is_visible():
                        print(f"Found time slot with {time}")
                        await slot.click()
                        time_found = True
                        break
                except Exception as e:
                    continue
            
            if not time_found:
                print("Could not find any morning time slots")
            
            await page.wait_for_timeout(2000)
            
        except Exception as e:
            print(f"Error setting delivery time: {str(e)}")
            print("Super saver delivery might not be available")
        
        # Dismiss time-picking modal if it didn't auto-close
        try:
            print("Checking if time selection modal needs dismissing...")
            await page.mouse.click(10, 10)
            await page.wait_for_timeout(2000)
        except Exception as e:
            print("Time selection modal already closed")
            
        # Step 5B Handle ID verification if it appears after delivery selection
        try:
            id_continue_button = page.locator('button:has-text("Continue")').first
            if await id_continue_button.is_visible():
                print("ID verification modal detected after delivery selection, clicking Continue...")
                await id_continue_button.click()
                await page.wait_for_timeout(3000)
        except Exception as e:
            print("No ID verification needed after delivery selection...")

        # Step 6: Place order
        print("Place order...")
        place_order_button = page.locator('button:has-text("Place order")').first
        await place_order_button.click()
        await page.wait_for_timeout(3000)

        # Step 6B: Handle ID verification if it appears here
        try:
            id_continue_button = page.locator('button:has-text("Continue")').first
            if await id_continue_button.is_visible():
                print("ID verification modal detected, clicking Continue...")
                await id_continue_button.click()
                await page.wait_for_timeout(3000)
        except Exception as e:
            print("No ID verification needed, continuing...")
        
        # Step 7: Confirm payment method
        print("Confirm payment method...")
        payment_button = page.locator('button:has-text("Confirm payment method")').first
        await payment_button.click()
        await page.wait_for_timeout(3000)
        
        # Step 8: Handle ID verification if it appears here
        try:
            id_continue_button = page.locator('button:has-text("Continue")').first
            if await id_continue_button.is_visible():
                print("ID verification modal detected, clicking Continue...")
                await id_continue_button.click()
                await page.wait_for_timeout(3000)
        except Exception as e:
            print("No ID verification needed, continuing...")
        
        print("Order placed successfully! You may wish to cancel this in your app!")
        await page.wait_for_timeout(35000)  # Wait to see confirmation
        
    except Exception as e:
        print(f"Error during checkout: {str(e)}")


async def clear_cart(page: Page):
    """Clears all items from the Instacart cart"""
    try:
        # First ensure we're on Safeway storefront
        await go_to_the_safeway_store(page)

        print("Opening cart to clear items...")
        # Try to find and click the cart button
        cart_button = page.locator('button[aria-controls="cart_dialog"]').first
        is_visible = await cart_button.is_visible()
        
        if not is_visible:
            print("Cart button not immediately visible, waiting for load...")
            await page.wait_for_timeout(5000)
            is_visible = await cart_button.is_visible()
            
        if is_visible:
            await retry_with_modal_handling(page, lambda: cart_button.click())
            await page.wait_for_timeout(3000)

            while True:
                # Find all Remove buttons
                remove_buttons = page.locator('button:has-text("Remove")')
                
                # Check if there are any remove buttons left
                count = await remove_buttons.count()
                if count == 0:
                    print("Cart is empty!")
                    break
                    
                # Click the first remove button we find
                print(f"Found {count} items to remove. Removing first item...")
                first_remove = remove_buttons.first
                await first_remove.click()
                await page.wait_for_timeout(1000)  # Brief wait between removals
        else:
            print("Could not find cart button - cart might already be empty")
            
    except Exception as e:
        print(f"Error while clearing cart: {str(e)}")
        print(f"Current URL: {page.url}")
