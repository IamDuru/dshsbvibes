import asyncio
import os
import time
from time import time

import wget
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from youtubesearchpython import SearchVideos
from yt_dlp import YoutubeDL

from ERAVIBES import app
from ERAVIBES.platforms.Youtube import get_ytdl_options

# Define a dictionary to track the last query timestamp for each user
user_last_CallbackQuery_time = {}
user_CallbackQuery_count = {}

# Define the threshold for query spamming (e.g., 1 query within 60 seconds)
SPAM_THRESHOLD = 1
SPAM_WINDOW_SECONDS = 30

SPAM_AUDIO_THRESHOLD = 1
SPAM_AUDIO_WINDOW_SECONDS = 30

BANNED_USERS = []


@app.on_callback_query(filters.regex("downloadvideo") & ~filters.user(BANNED_USERS))
async def download_video(client, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    current_time = time.time()

    # Check if the user has exceeded the query limit
    last_Query_time = user_last_CallbackQuery_time.get(user_id, 0)
    if current_time - last_Query_time < SPAM_WINDOW_SECONDS:
        # If the limit is exceeded, send a response and return
        await CallbackQuery.answer(
            "➻ ʏᴏᴜ ʜᴀᴠᴇ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ʏᴏᴜʀ ᴠɪᴅᴇᴏ (ᴄʜᴇᴄᴋ ᴍʏ ᴅᴍ/ᴘᴍ).\n\n➥ ɴᴇxᴛ sᴏɴɢ ᴅᴏᴡɴʟᴏᴀᴅ ᴀғᴛᴇʀ 30 sᴇᴄᴏɴᴅs.",
            show_alert=True,
        )
        return
    else:
        # Update the last query time and query count
        user_last_CallbackQuery_time[user_id] = current_time
        user_CallbackQuery_count[user_id] = user_CallbackQuery_count.get(user_id, 0) + 1

    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    user_name = CallbackQuery.from_user.first_name
    chutiya = f'<a href="tg://user?id={user_id}">{user_name}</a>'
    await CallbackQuery.answer("ᴏᴋ sɪʀ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...", show_alert=True)
    pablo = await client.send_message(
        CallbackQuery.message.chat.id,
        f"<b>ʜᴇʏ {chutiya} ᴅᴏᴡɴʟᴏᴅɪɴɢ ʏᴏᴜʀ ᴠɪᴅᴇᴏ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>",
    )
    if not videoid:
        await pablo.edit(
            f"<b>ʜᴇʏ {chutiya} ʏᴏᴜʀ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ. ᴛʀʏ ᴀɢᴀɪɴ...</b>"
        )
        return

    search = SearchVideos(
        f"https://youtube.com/{videoid}", offset=1, mode="dict", max_results=1
    )
    mi = search.result()
    mio = mi.get("search_result", [])
    if not mio:
        await pablo.edit(
            f"<b>ʜᴇʏ {chutiya} ʏᴏᴜʀ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ. ᴛʀʏ ᴀɢᴀɪɴ...</b>"
        )
        return

    mo = mio[0].get("link", "")
    thum = mio[0].get("title", "")
    fridayz = mio[0].get("id", "")
    thums = mio[0].get("channel", "")
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "postprocessors": [{"key": "FFmpegVideoConvertor", "preferedformat": "mp4"}],
        "outtmpl": "%(id)s.mp4",
        "logtostderr": False,
        "quiet": True,
    }
    try:
        with YoutubeDL(get_ytdl_options(opts)) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=True)

    except Exception as e:
        await pablo.edit(
            f"<b>ʜᴇʏ {chutiya} ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ sᴏɴɢ.</b> \n<b>ᴇʀʀᴏʀ:</b> `{str(e)}`"
        )
        return

    file_stark = f"{ytdl_data['id']}.mp3"  # Adjusted file extension
    capy = (
        f"❄ <b>ᴛɪᴛʟᴇ :</b> <a href='{mo}'>{thum}</a>\n\n"
        f"💫 <b>ᴄʜᴀɴɴᴇʟ :</b> {thums}\n\n"
        f"🥀 <b>ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {chutiya}\n\n"
        f"⏳ <b>ᴅᴜʀᴀᴛɪᴏɴ :</b> {int(ytdl_data['duration']) // 60}:{int(ytdl_data['duration']) % 60}"
    )
    
    try:
        # Open the file in binary mode and send it
        with open(file_stark, "rb") as audio_file:
            await client.send_audio(
                chat_id=CallbackQuery.from_user.id,  # Send to the user who triggered the callback
                audio=audio_file,  # Pass the file object
                title=str(ytdl_data["title"]),  # Set the title of the audio
                thumb=sedlyf,  # Set the thumbnail
                caption=capy,  # Set the formatted caption
                parse_mode="html",  # Ensure HTML formatting is applied
                progress=upload_progress,  # Custom progress callback (if supported)
                progress_args=(
                    pablo,
                    f"<b>{chutiya} ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>\n\n<b>ᴜᴘʟᴏᴀᴅɪɴɢ ᴀᴜᴅɪᴏ ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ...💫</b>",
                    file_stark,
                ),
            )
        await client.send_message(
            CallbackQuery.message.chat.id,
            text=(
                f"<b>ʜᴇʏ</b> {chutiya}\n\n"
                f"<b>✅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ.</b>\n"
                f"<b>➻ ᴠɪᴅᴇᴏ sᴇɴᴛ ɪɴ ʏᴏᴜʀ ᴘᴍ/ᴅᴍ.</b>\n"
                f"<b>➥ ᴄʜᴇᴄᴋ ʜᴇʀᴇ » <a href='tg://openmessage?user_id={app.id}'>ʙᴏᴛ ᴘᴍ/ᴅᴍ</a></b>🤗"
            ),
            parse_mode="html"
        )
        
        await pablo.delete()
        for files in (sedlyf, file_stark):
            if files and os.path.exists(files):
                os.remove(files)

    except Exception as e:
        await pablo.delete()
        return await client.send_message(
            CallbackQuery.message.chat.id,
            f"<b>ʜᴇʏ {chutiya} ᴘʟᴇᴀsᴇ ᴜɴʙʟᴏᴄᴋ ᴍᴇ ғᴏʀ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ ᴠɪᴅᴇᴏ ʙʏ ᴄʟɪᴄᴋ ʜᴇʀᴇ 👇👇</b>",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"👉ᴜɴʙʟᴏᴄᴋ ᴍᴇ🤨",
                            url=f"https://t.me/{app.username}?start=info_{videoid}",
                        )
                    ]
                ]
            ),
        )


import os
import time

# Dicts to keep track of user query count and last query time
user_last_CallbackQuery_time = {}
user_CallbackQuery_count = {}


@app.on_callback_query(filters.regex("downloadaudio") & ~filters.user(BANNED_USERS))
async def download_audio(client, CallbackQuery):
    user_id = CallbackQuery.from_user.id
    current_time = time.time()

    # Check if the user has exceeded the query limit
    last_Query_time = user_last_CallbackQuery_time.get(user_id, 0)
    if current_time - last_Query_time < SPAM_AUDIO_WINDOW_SECONDS:
        # If the limit is exceeded, send a response and return
        await CallbackQuery.answer(
            "➻ ʏᴏᴜ ʜᴀᴠᴇ ʜᴀᴠᴇ ᴀʟʀᴇᴀᴅʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ ʏᴏᴜʀ ᴀᴜᴅɪᴏ (ᴄʜᴇᴄᴋ ᴍʏ ᴅᴍ/ᴘᴍ).\n\n➥ ɴᴇxᴛ sᴏɴɢ ᴅᴏᴡɴʟᴏᴀᴅ ᴀғᴛᴇʀ 30 sᴇᴄᴏɴᴅs.",
            show_alert=True,
        )
        return
    else:
        # Update the last query time and query count
        user_last_CallbackQuery_time[user_id] = current_time
        user_CallbackQuery_count[user_id] = user_CallbackQuery_count.get(user_id, 0) + 1

    callback_data = CallbackQuery.data.strip()
    videoid = callback_data.split(None, 1)[1]
    user_id = CallbackQuery.from_user.id
    user_name = CallbackQuery.from_user.first_name
    chutiya = f'<a href="tg://user?id={user_id}">{user_name}</a>'
    await CallbackQuery.answer("ᴏᴋ sɪʀ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...", show_alert=True)
    pablo = await client.send_message(
        CallbackQuery.message.chat.id,
        f"<b>ʜᴇʏ {chutiya} ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ʏᴏᴜʀ ᴀᴜᴅɪᴏ, ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>",
    )
    if not videoid:
        await pablo.edit(
            f"<b>ʜᴇʏ {chutiya} ʏᴏᴜʀ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ. ᴛʀʏ ᴀɢᴀɪɴ...</b>"
        )
        return

    search = SearchVideos(
        f"https://youtube.com/{videoid}", offset=1, mode="dict", max_results=1
    )
    mi = search.result()
    mio = mi.get("search_result", [])
    if not mio:
        await pablo.edit(
            f"<b>ʜᴇʏ {chutiya} ʏᴏᴜʀ sᴏɴɢ ɴᴏᴛ ғᴏᴜɴᴅ ᴏɴ ʏᴏᴜᴛᴜʙᴇ. ᴛʀʏ ᴀɢᴀɪɴ...</b>"
        )
        return

    mo = mio[0].get("link", "")
    thum = mio[0].get("title", "")
    fridayz = mio[0].get("id", "")
    thums = mio[0].get("channel", "")
    kekme = f"https://img.youtube.com/vi/{fridayz}/hqdefault.jpg"
    await asyncio.sleep(0.6)
    url = mo
    sedlyf = wget.download(kekme)
    opts = {
        "format": "bestaudio/best",
        "addmetadata": True,
        "key": "FFmpegMetadata",
        "prefer_ffmpeg": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "outtmpl": "%(id)s.mp3",  # Output format changed to mp3
        "logtostderr": False,
        "quiet": True,
    }
    try:
        with YoutubeDL(get_ytdl_options(opts)) as ytdl:
            ytdl_data = ytdl.extract_info(url, download=True)

    except Exception as e:
        await pablo.edit(
            f"<b>ʜᴇʏ {chutiya} ғᴀɪʟᴇᴅ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ ᴀᴜᴅɪᴏ.</b> \n<b>ᴇʀʀᴏʀ:</b> `{str(e)}`"
        )
        return

    
    file_stark = f"{ytdl_data['id']}.mp3"  # Adjusted file extension
    capy = (
        f"❄ <b>ᴛɪᴛʟᴇ :</b> <a href='{mo}'>{thum}</a>\n\n"
        f"💫 <b>ᴄʜᴀɴɴᴇʟ :</b> {thums}\n\n"
        f"🥀 <b>ʀᴇǫᴜᴇsᴛᴇᴅ ʙʏ :</b> {chutiya}\n\n"
        f"⏳ <b>ᴅᴜʀᴀᴛɪᴏɴ :</b> {int(ytdl_data['duration']) // 60}:{int(ytdl_data['duration']) % 60}"
    )
    
    try:
        # Open the file in binary mode and send it
        with open(file_stark, "rb") as audio_file:
            await client.send_audio(
                chat_id=CallbackQuery.from_user.id,  # Send to the user who triggered the callback
                audio=audio_file,  # Pass the file object
                title=str(ytdl_data["title"]),  # Set the title of the audio
                thumb=sedlyf,  # Set the thumbnail
                caption=capy,  # Set the formatted caption
                parse_mode="html",  # Ensure HTML formatting is applied
                progress=upload_progress,  # Custom progress callback (if supported)
                progress_args=(
                    pablo,
                    f"<b>{chutiya} ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ...</b>\n\n<b>ᴜᴘʟᴏᴀᴅɪɴɢ ᴀᴜᴅɪᴏ ғʀᴏᴍ ʏᴏᴜᴛᴜʙᴇ...💫</b>",
                    file_stark,
                ),
            )
            
        await client.send_message(
            CallbackQuery.message.chat.id,
            text=(
                f"<b>ʜᴇʏ</b> {chutiya}\n\n"
                f"<b>✅ sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴏᴡɴʟᴏᴀᴅᴇᴅ.</b>\n"
                f"<b>➻ ᴠɪᴅᴇᴏ sᴇɴᴛ ɪɴ ʏᴏᴜʀ ᴘᴍ/ᴅᴍ.</b>\n"
                f"<b>➥ ᴄʜᴇᴄᴋ ʜᴇʀᴇ » <a href='tg://openmessage?user_id={app.id}'>ʙᴏᴛ ᴘᴍ/ᴅᴍ</a></b>🤗"
            ),
            parse_mode="html"
        )
        
        await pablo.delete()
        for files in (sedlyf, file_stark):
            if files and os.path.exists(files):
                os.remove(files)

    except Exception as e:
        await pablo.delete()
        return await client.send_message(
            CallbackQuery.message.chat.id,
            f"<b>ʜᴇʏ {chutiya} ᴘʟᴇᴀsᴇ ᴜɴʙʟᴏᴄᴋ ᴍᴇ ғᴏʀ ᴅᴏᴡɴʟᴏᴀᴅ ʏᴏᴜʀ ᴀᴜᴅɪᴏ ʙʏ ᴄʟɪᴄᴋ ʜᴇʀᴇ 👇👇</b>",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            f"👉ᴜɴʙʟᴏᴄᴋ ᴍᴇ🤨",
                            url=f"https://t.me/{app.username}?start=info_{videoid}",
                        )
                    ]
                ]
            ),
        )

