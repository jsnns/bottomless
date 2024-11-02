import os
import discord
from discord.ext import commands
from main import create_shopping_list, add_items_to_cart, get_authorized_url

from discord.ext import commands

# create discord bot
intents = discord.Intents.default()
intents.message_content = True
intents.dm_messages = True
intents.guild_messages = True
intents.members = True
bot = commands.Bot(intents=intents, command_prefix="!")


@bot.event
async def on_ready():
    print(f"{bot.user} has connected to Discord!")


@bot.event
async def on_message(message):
    # only respond in dms
    if message.guild:
        return

    if message.author == bot.user:
        return

    if len(message.attachments) == 2:
        # send loading message
        await message.channel.send("Building shopping list...")

        # Download the images
        before_img = message.attachments[0]
        after_img = message.attachments[1]

        await before_img.save("before.jpeg")
        await after_img.save("after.jpeg")

        # Generate shopping list
        shopping_list = create_shopping_list("before.jpeg", "after.jpeg")

        # Format shopping list message
        list_msg = "Shopping List:\n"
        for item in shopping_list:
            list_msg += f"• {item.item_name}"
            if hasattr(item, "quantity") and item.quantity:
                list_msg += f" (x{item.quantity})"
            if hasattr(item, "brand_name") and item.brand_name:
                list_msg += f" - {item.brand_name}"
            list_msg += "\n"

        # Send message and add reaction
        msg = await message.channel.send(list_msg)
        await msg.add_reaction("✅")

        # Store shopping list in bot's memory
        setattr(bot, "shopping_list", shopping_list)

    else:
        await message.channel.send(
            "Please attach exactly 2 images - before and after photos"
        )


@bot.event
async def on_reaction_add(reaction, user):
    if user == bot.user:
        return

    if reaction.emoji == "✅" and hasattr(bot, "shopping_list"):
        await reaction.message.channel.send("Adding items to cart...")
        try:
            url, debug_url = get_authorized_url()

            # send debug url
            await reaction.message.channel.send(
                f"[Watch me add them to your cart!]({debug_url})"
            )

            await add_items_to_cart(url, getattr(bot, "shopping_list"))
            await reaction.message.channel.send(
                "Items have been added to your cart! Please complete checkout on your mobile device."
            )
        except Exception as e:
            await reaction.message.channel.send(f"Error adding items to cart: {str(e)}")


# Replace TOKEN with your Discord bot token
bot.run(os.getenv("DISCORD_TOKEN") or "")
