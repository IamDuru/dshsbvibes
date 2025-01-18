from pyrogram import Client, filters
from config import OWNER_ID
from ERAVIBES import app 

# /eco command handler
@app.on_message(filters.command(["co", "c"], prefixes=["/", "!", ".", ""]) & filters.reply & filters.user(OWNER_ID))
async def eco_reply(client, message):
    try:
        if not message.reply_to_message:
            await message.reply("Please reply to a user's message to use this command.")
            return

        # Split the command from the message (removing the command /eco)
        command_text = message.text.split(" ", 1)

        if len(command_text) < 2:
            await message.reply("Please provide a message after the /eco command.")
            return

        # The message to reply with
        reply_message = command_text[1]

        await message.delete()
        await message.reply_to_message.reply(reply_message)
    except Exception as e:
        await message.reply(f"An error occurred: {e}")
