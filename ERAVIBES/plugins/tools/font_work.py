from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ERAVIBES import app

def custom_smallcap(text):
    char_map = {
        'A': 'ᴧ', 'N': 'η', 'M': 'ϻ', 'O': 'σ', 'E': 'є', 'I': '¡',
        'a': 'ᴀ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'ᴇ', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 
        'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ', 'o': 'ᴏ', 'p': 'ᴘ', 
        'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 
        'y': 'ʏ', 'z': 'ᴢ'
    }
    return ''.join([char_map.get(c, c) for c in text])

@app.on_message(filters.command(["work", "w"], prefixes=["/", "!", ".", ""]))
async def style_buttons(c, m, cb=False):
    if cb:
        text = m.message.reply_to_message.text.split(' ', 1)[1]
    else:
        text = m.text.split(' ', 1)[1]
    
    buttons = [
        [InlineKeyboardButton("ꜱᴀꜰᴇ", callback_data="style+custom_smallcap")],
        [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close_reply")]
    ]
    
    if not cb:
        await m.reply_text(
            f"<code>{text}</code>", reply_markup=InlineKeyboardMarkup(buttons), quote=True
        )
    else:
        await m.answer()
        await m.message.edit_text(f"<code>{text}</code>", reply_markup=InlineKeyboardMarkup(buttons))

@app.on_callback_query(filters.regex("^style"))
async def style(c, m):
    await m.answer()
    cmd, style_type = m.data.split('+')
    text = m.message.reply_to_message.text.split(" ", 1)[1]
    
    if style_type == "custom_smallcap":
        new_text = custom_smallcap(text)
    else:
        new_text = text  # Fallback for unknown styles
    
    try:
        await m.message.edit_text(f"<code>{new_text}</code>", reply_markup=m.message.reply_markup)
    except Exception as e:
        print(f"Error editing message: {e}")
