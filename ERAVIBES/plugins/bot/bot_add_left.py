from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from config import LOG, LOGGER_ID
from ERAVIBES import app
from ERAVIBES.utils.database import delete_served_chat, get_assistant, is_on_off


@app.on_message(filters.new_chat_members)
async def on_bot_added(_, message: Message):
    if not await is_on_off(LOG):
        return

    chat = message.chat
    if any(member.id == app.id for member in message.new_chat_members):
        count = await app.get_chat_members_count(chat.id)
        username = f"@{chat.username}" if chat.username else "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"
        added_by = (
            f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
            if message.from_user
            else "Unknown User"
        )
        msg = (
            "<b>Music bot added in new Group #New_Group</b>\n\n"
            f"<b>Chat Name:</b> {chat.title}\n"
            f"<b>Chat Id:</b> {chat.id}\n"
            f"<b>Chat Username:</b> {username}\n"
            f"<b>Chat Member Count:</b> {count}\n"
            f"<b>Added By:</b> {added_by}"
        )

        await app.send_message(
            LOGGER_ID,
            text=msg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"Added by: {message.from_user.first_name}",
                            user_id=message.from_user.id,
                        )
                    ]
                ]
            ),
        )

        if chat.username:
            userbot = await get_assistant(chat.id)
            await userbot.join_chat(chat.username)


@app.on_message(filters.left_chat_member)
async def on_bot_kicked(_, message: Message):
    if not await is_on_off(LOG):
        return

    left_chat_member = message.left_chat_member
    if left_chat_member and left_chat_member.id == app.id:
        chat = message.chat
        remove_by = (
            f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
            if message.from_user
            else "𝐔ɴᴋɴᴏᴡɴ 𝐔sᴇʀ"
        )
        username = f"@{chat.username}" if chat.username else "ᴘʀɪᴠᴀᴛᴇ ᴄʜᴀᴛ"
        left_msg = (
            f"<b>Bot was Removed in {chat.title} #Left_group</b>\n"
            f"<b>Chat Name:</b> {chat.title}\n"
            f"<b>Chat Id:</b> {chat.id}\n"
            f"<b>Chat Username:</b> {username}\n"
            f"<b>Removed By:</b> {remove_by}"
        )

        await app.send_message(
            LOGGER_ID,
            text=left_msg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text=f"Removed By: {message.from_user.first_name}",
                            user_id=message.from_user.id,
                        )
                    ]
                ]
            ),
        )

        await delete_served_chat(chat.id)
        userbot = await get_assistant(chat.id)
        await userbot.leave_chat(chat.id)
