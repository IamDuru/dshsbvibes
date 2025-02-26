import asyncio
from datetime import datetime

from pyrogram.enums import ChatType

import config
from ERAVIBES import app
from ERAVIBES.core.call import ERA, autoend
from ERAVIBES.utils.database import get_client, is_active_chat, is_autoend


async def auto_leave():
    if config.AUTO_LEAVING_ASSISTANT:
        while not await asyncio.sleep(18000):
            from ERAVIBES.core.userbot import assistants

            for num in assistants:
                client = await get_client(num)
                left = 0
                try:
                    async for i in client.get_dialogs():
                        if i.chat.type in [
                            ChatType.SUPERGROUP,
                            ChatType.GROUP,
                            ChatType.CHANNEL,
                        ]:
                            if (
                                i.chat.id != config.LOGGER_ID
                                and i.chat.id != -1002342994330
                                and i.chat.id != -1002296968230
                            ):
                                if left == 20:
                                    continue
                                if not await is_active_chat(i.chat.id):
                                    try:
                                        await client.leave_chat(i.chat.id)
                                        left += 1
                                    except:
                                        continue
                except:
                    pass


asyncio.create_task(auto_leave())



# Dictionary to track user activity timestamps
user_activity = {}

async def update_user_activity(chat_id):
    """Update the last activity timestamp for a chat."""
    user_activity[chat_id] = datetime.now()

async def is_active_chat(chat_id):
    """Check if the chat is still active based on user activity."""
    if chat_id not in user_activity:
        return False
    last_activity = user_activity[chat_id]
    # Consider the chat active if the last activity was within the last 1 minutes
    return datetime.now() - last_activity <= timedelta(minutes=99999)

async def auto_end():
    while True:
        await asyncio.sleep(5)  # Check every 5 seconds
        for chat_id in list(autoend.keys()):  # Use list to avoid RuntimeError: dictionary changed size during iteration
            timer = autoend.get(chat_id)
            if not timer:
                continue
            if datetime.now() > timer:
                if not await is_active_chat(chat_id):
                    try:
                        await ERA.stop_stream(chat_id)
                    except Exception as e:
                        print(f"Error stopping stream in chat {chat_id}: {e}")
                        continue
                    try:
                        await app.send_message(
                            chat_id,
                            "❖ ʙᴏᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʟᴇғᴛ ᴠɪᴅᴇᴏᴄʜᴀᴛ ʙᴇᴄᴀᴜsᴇ ɴᴏ ᴏɴᴇ ᴡᴀs ʟɪsᴛᴇɴɪɴɢ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.",
                        )
                    except Exception as e:
                        print(f"Error sending message to chat {chat_id}: {e}")
                        continue
                    del autoend[chat_id]  # Remove chat from autoend dictionary

asyncio.create_task(auto_end())
