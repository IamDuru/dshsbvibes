import asyncio
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from ERAVIBES import app
from ERAVIBES.core.call import ERA
from ERAVIBES.utils.database import (
    set_loop,
    get_assistant,
)
from ERAVIBES.utils.decorators import AdminRightsCheck
from ERAVIBES.utils.inline import close_markup
from config import BANNED_USERS


@app.on_message(
    filters.command(["end", "stop", "cend", "cstop"]) & filters.group & ~BANNED_USERS
)
@AdminRightsCheck
async def stop_music(cli, message: Message, _, chat_id):
    if not len(message.command) == 1:
        return
    await ERA.stop_stream(chat_id)
    await set_loop(chat_id, 0)
    r = await message.reply_text(
        _["admin_5"].format(message.from_user.mention), reply_markup=close_markup(_)
    )
    await asyncio.sleep(3)
    await r.delete()
