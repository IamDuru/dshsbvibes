import os, aiohttp, asyncio, shutil

from pyrogram import filters, enums
from pyrogram.types import Message

from config import API_URL, API_KEY
from ERAVIBES import YouTube, app
from ERAVIBES.misc import SUDOERS


@app.on_message(filters.command("clean") & SUDOERS)
async def clean(_, message):
    A = await message.reply_text("ᴄʟᴇᴀɴɪɴɢ ᴛᴇᴍᴘ ᴅɪʀᴇᴄᴛᴏʀɪᴇs...")
    dirs = ["downloads", "cache"]
    for d in dirs:
        if os.path.exists(d):
            shutil.rmtree(d)
        os.mkdir(d)
    await A.edit("✅ ᴛᴇᴍᴘ ᴅɪʀᴇᴄᴛᴏʀɪᴇs ᴀʀᴇ ᴄʟᴇᴀɴᴇᴅ")


# -------------------

TEST = "dQw4w9WgXcQ"

@app.on_message(filters.command("chk") & SUDOERS)
async def chk(_, m: Message):
    wait = await m.reply("⏳ **ᴄʜєᴄᴋɪηɢ. . .**", parse_mode=enums.ParseMode.MARKDOWN)
    api_ok, ck_ok = False, False

    # 1. Ping API
    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as s:
            async with s.get(f"{API_URL}/song/{TEST}?api={API_KEY}") as r:
                api_ok = r.status == 200
    except:
        pass

    # 2. Check cookies
    try:
        ck_ok = await YouTube.exists(TEST, videoid=True)
    except:
        pass

    await wait.edit(
        "❖ **ʏσᴜᴛᴜʙє ʜєᴧʟᴛʜʏ** ❖\n\n"
        f"● **ᴧᴘɪ** ➥  {'✅ ᴧʟɪᴠє' if api_ok else '❌ ᴅσᴡη'}\n"
        f"● **ᴄσσᴋɪєꜱ** ➥  {'✅ ᴡσʀᴋɪηɢ' if ck_ok else '❌ ᴅєᴧᴅ'}",
        parse_mode=enums.ParseMode.MARKDOWN
    )
