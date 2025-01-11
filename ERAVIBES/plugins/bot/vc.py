import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ERAVIBES import app
from ERAVIBES.core.call import ERA
from ERAVIBES.utils.database import (
    set_loop,
    get_assistant,
)


# vc on
@app.on_message(filters.video_chat_started & filters.group)
async def brah(_, msg):
    chat_id = msg.chat.id
    try:
        await msg.reply("<b>😍ᴠɪᴅᴇᴏ ᴄʜᴀᴛ sᴛᴀʀᴛᴇᴅ🥳</b>")
        await ERA.stop_stream(chat_id)
        await set_loop(chat_id, 0)
    except Exception as e:
        return await msg.reply(f"<b>Error {e}</b>")


# vc off
@app.on_message(filters.video_chat_ended & filters.group)
async def brah2(_, msg):
    chat_id = msg.chat.id
    try:
        await msg.reply("<b>😕ᴠɪᴅᴇᴏ ᴄʜᴀᴛ ᴇɴᴅᴇᴅ💔</b>")
        await ERA.stop_stream(chat_id)
        await set_loop(chat_id, 0)
    except Exception as e:
        return await msg.reply(f"<b>Error {e}</b>")


# vc invite
@app.on_message(filters.video_chat_members_invited)
async def brah3(app: app, message: Message):
    # Check if message.from_user is not None
    if message.from_user is None:
        return  # Exit the function if there's no from_user

    text = f"➪ {message.from_user.mention}\n\n<b>๏ ɪɴᴠɪᴛɪɴɢ ɪɴ ᴠᴄ ᴛᴏ :</b>\n\n➪ "
    x = 0
    for user in message.video_chat_members_invited.users:
        try:
            text += f'<a href="tg://user?id={user.id}">{user.first_name}</a> '
            x += 1
        except Exception:
            pass
    
    try:
        add_link = f"https://t.me/{app.username}?startgroup=true"
        reply_text = f"{text} 🤭🤭"
        userbot = await get_assistant(message.chat.id)
        await message.reply(reply_text, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text="๏ ᴊᴏɪɴ ᴠᴄ ๏", url=add_link)]]))
        
    except Exception as e:
        print(f"Error: {e}")
