import math
from config import SUPPORT_CHAT, OWNER_USERNAME
from pyrogram.types import InlineKeyboardButton
from ERAVIBES.utils.formatters import time_to_seconds


def stream_markup_timer(_, chat_id, played, dur):
    played_sec = time_to_seconds(played)
    duration_sec = time_to_seconds(dur)
    percentage = (played_sec / duration_sec) * 100
    umm = math.floor(percentage)
    # Fun and engaging sentences with progress bar
    if 10 < umm <= 20:
        bar = "💞 ᴄʟɪᴄᴋ ᴛᴏ ᴀᴅᴅ ɪɴ ᴄʜᴀɴɴᴇʟs 💞"
    elif 20 <= umm < 35:
        bar = "🎄 ᴛᴀᴘ ᴛᴏ ᴇɴᴛᴇʀ ᴍᴏʀᴇ ɢʀᴏᴜᴘs 🎄"
    elif 35 <= umm < 50:
        bar = "🎁 ᴄʟɪᴄᴋ ᴛᴏ ᴀᴅᴅ ɪɴ ɴᴇᴡ ᴄʜᴀᴛ 🎁"
    elif 50 <= umm < 75:
        bar = "⚜️ ᴛᴀᴘ ʜᴇʀᴇ ғᴏʀ ᴄʜᴀᴛ ɪɴᴠɪᴛᴇ ⚜️"
    elif 75 <= umm < 80:
        bar = "🔥 ᴄʟɪᴄᴋ ᴛᴏ ᴀᴄᴄᴇss ɪɴ ɢʀᴏᴜᴘ 🔥"
    elif 80 <= umm < 85:
        bar = "🌟 ᴛᴀᴘ ᴛᴏ ᴇxᴘʟᴏʀᴇ ᴍᴏʀᴇ ᴄʜᴀᴛ 🌟"
    elif 85 <= umm < 90:
        bar = "🐥ᴄʟɪᴄᴋ ᴛᴏ ᴀᴅᴅ ɴᴇᴡ ᴄʜᴀᴛ ʀᴏᴏᴍ🐥"
    elif 90 <= umm < 95:
        bar = "❣️ᴛᴀᴘ ᴛᴏ ᴀᴅᴅ ᴅɪғғᴇʀᴇɴᴛ ɢʀᴏᴜᴘ❣️"
    elif 95 <= umm < 100:
        bar = "⚡ᴄʟɪᴄᴋ ғᴏʀ ɢᴇᴛ ᴀᴅᴅ ɪɴ ᴄʜᴀᴛs⚡"
    else:
        bar = "✨ ᴛᴀᴘ ʜᴇʀᴇ ᴛᴏ ɢʀᴏᴜᴘ ɪɴᴠɪᴛᴇs ✨"
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{bar}",
                url=f"https://t.me/{app.username}?startgroup=true",
            )
        ],
        [
            InlineKeyboardButton(text="❚❚", callback_data=f"ADMIN Pause|{chat_id}"),            
            InlineKeyboardButton(text="ᐅ", callback_data=f"ADMIN Resume|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons




def stream_markup(_, chat_id):
    buttons = [
        [
            InlineKeyboardButton(text="❚❚", callback_data=f"ADMIN Pause|{chat_id}"),            
            InlineKeyboardButton(text="ᐅ", callback_data=f"ADMIN Resume|{chat_id}"),
        ],
        [
            InlineKeyboardButton(text=_["CLOSE_BUTTON"], callback_data="close"),
        ],
    ]
    return buttons


def track_markup(_, videoid, user_id, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            )
        ],
    ]
    return buttons



def playlist_markup(_, videoid, user_id, ptype, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"EraPlaylists {videoid}|{user_id}|{ptype}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"EraPlaylists {videoid}|{user_id}|{ptype}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


def livestream_markup(_, videoid, user_id, mode, channel, fplay):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_3"],
                callback_data=f"LiveStream {videoid}|{user_id}|{mode}|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {videoid}|{user_id}",
            ),
        ],
    ]
    return buttons


def slider_markup(_, videoid, user_id, query, query_type, channel, fplay):
    query = f"{query[:20]}"
    buttons = [
        [
            InlineKeyboardButton(
                text=_["P_B_1"],
                callback_data=f"MusicStream {videoid}|{user_id}|a|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["P_B_2"],
                callback_data=f"MusicStream {videoid}|{user_id}|v|{channel}|{fplay}",
            ),
        ],
        [
            InlineKeyboardButton(
                text="◁",
                callback_data=f"slider B|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
            InlineKeyboardButton(
                text=_["CLOSE_BUTTON"],
                callback_data=f"forceclose {query}|{user_id}",
            ),
            InlineKeyboardButton(
                text="▷",
                callback_data=f"slider F|{query_type}|{query}|{user_id}|{channel}|{fplay}",
            ),
        ],
    ]
    return buttons
    
