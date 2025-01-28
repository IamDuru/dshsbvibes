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
        username = f"@{chat.username}" if chat.username else "Private Chat"
        added_by = (
            f'<a href="tg://user?id={message.from_user.id}">{message.from_user.first_name}</a>'
            if message.from_user
            else "Unknown User"
        )
        msg = (
            "🎉 <b><u>Mᴜsɪᴄ Bᴏᴛ Aᴅᴅᴇᴅ ɪɴ #New_Group</u></b> 🎉\n\n"
            f"• <b>Chat Name:</b> <code>{chat.title}</code>\n"
            f"• <b>Chat ID:</b> <code>{chat.id}</code>\n"
            f"• <b>Chat Username:</b> <code>{username}</code>\n"
            f"• <b>Total Members:</b> <code>{count}</code>\n"
            f"• <b>Added:</b> {added_by}"
        )

        await app.send_message(
            LOGGER_ID,
            text=msg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="👤 View Added User",
                            url=f"tg://user?id={message.from_user.id}",
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
            else "Unknown User"
        )
        username = f"@{chat.username}" if chat.username else "Private Chat"
        left_msg = (
            "❌ <b><u>Bᴏᴛ Rᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ Gʀᴏᴜᴘ #Left_group</u></b> ❌\n\n"
            f"• <b>Chat Name:</b> <code>{chat.title}</code>\n"
            f"• <b>Chat ID:</b> <code>{chat.id}</code>\n"
            f"• <b>Chat Username:</b> <code>{username}</code>\n"
            f"• <b>Removed:</b> {remove_by}"
        )

        await app.send_message(
            LOGGER_ID,
            text=left_msg,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            text="👤 View Removed User",
                            url=f"tg://user?id={message.from_user.id}",
                        )
                    ]
                ]
            ),
        )

        await delete_served_chat(chat.id)
        userbot = await get_assistant(chat.id)
        await userbot.leave_chat(chat.id)
