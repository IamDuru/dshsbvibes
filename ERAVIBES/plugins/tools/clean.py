import os
import shutil
import asyncio
from pyrogram import filters
from ERAVIBES import app

# Listen to all messages
@app.on_message(filters.text)
async def handle_message(_, message):
    # Check if the message contains trigger words
    trigger_words = ["clean", "clear", "delete", "p"]
    if any(word in message.text.lower() for word in trigger_words):
        # Clean directories
        A = await message.reply_text("ᴄʟᴇᴀɴɪɴɢ ᴛᴇᴍᴘ ᴅɪʀᴇᴄᴛᴏʀɪᴇs...")
        
        # Define directories
        dir = "downloads"
        dir1 = "cache"
        
        # Remove and recreate directories
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)
        
        if os.path.exists(dir1):
            shutil.rmtree(dir1)
        os.mkdir(dir1)
        
        await A.edit("ᴛᴇᴍᴘ ᴅɪʀᴇᴄᴛᴏʀɪᴇs ᴀʀᴇ ᴄʟᴇᴀɴᴇᴅ")
        
        # Add a delay and delete the bot's message
        await asyncio.sleep(0.3)
        await A.delete()
