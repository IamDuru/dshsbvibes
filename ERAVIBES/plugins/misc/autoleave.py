import asyncio
from datetime import datetime, timedelta

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



async def auto_end():
    while True:
        await asyncio.sleep(5)  # Ensure sleep is awaited properly
        ender = await is_autoend()
        if not ender:
            continue
        
        for chat_id in list(autoend.keys()):  # Iterate safely over keys
            timer = autoend.get(chat_id)
            if not timer:
                continue
            
            if datetime.now() > timer:
                if await is_active_chat(chat_id):  # Check if chat is active
                    autoend[chat_id] = datetime.now() + timedelta(minutes=1)  # Extend timer if active
                    continue  # Skip ending if active
                
                autoend.pop(chat_id, None)  # Remove from autoend safely
                try:
                    await ERA.stop_stream(chat_id)
                except Exception as e:
                    print(f"Error stopping stream for {chat_id}: {e}")
                    continue
                
                try:
                    await app.send_message(
                        chat_id,
                        "❖ ʙᴏᴛ ᴀᴜᴛᴏᴍᴀᴛɪᴄᴀʟʟʏ ʟᴇғᴛ ᴠɪᴅᴇᴏᴄʜᴀᴛ ʙᴇᴄᴀᴜsᴇ ɴᴏ ᴏɴᴇ ᴡᴀs ʟɪsᴛᴇɴɪɴɢ ᴏɴ ᴠɪᴅᴇᴏᴄʜᴀᴛ.",
                    )
                except Exception as e:
                    print(f"Error sending message to {chat_id}: {e}")
                    continue

# Start the auto_end task
asyncio.create_task(auto_end())
