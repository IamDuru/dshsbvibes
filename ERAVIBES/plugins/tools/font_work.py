from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ERAVIBES import app

def custom_smallcap(text):
    char_map = {
        'A': 'ᴧ', 'N': 'η', 'M': 'ϻ', 'O': 'σ', 'E': 'є', 'I': '¡',
        'a': 'ᴧ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'є', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ', 
        'i': '¡', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ϻ', 'n': 'η', 'o': 'σ', 'p': 'ᴘ', 
        'q': 'ǫ', 'r': 'ʀ', 's': 'ꜱ', 't': 'ᴛ', 'u': 'ᴜ', 'v': 'ᴠ', 'w': 'ᴡ', 'x': 'x', 
        'y': 'ʏ', 'z': 'ᴢ'
    }
    return ''.join([char_map.get(c, c) for c in text])

@app.on_message(filters.command(["work", "w"], prefixes=["/", "!", ".", ""]))
async def work_command(c, m):
    try:
        text = m.text.split(' ', 1)[1]
    except IndexError:
        await m.reply_text("Please provide some text after the command.")
        return
    
    buttons = [
        [InlineKeyboardButton("ꜱᴀꜰᴇ", callback_data="safe_style")],
        [InlineKeyboardButton("ᴄʟᴏsᴇ", callback_data="close_reply")]
    ]
    
    await m.reply_text(
        f"<code>{text}</code>", 
        reply_markup=InlineKeyboardMarkup(buttons), 
        quote=True
    )

@app.on_callback_query(filters.regex("^safe_style"))
async def safe_style_callback(c, m):
    await m.answer()
    try:
        text = m.message.reply_to_message.text.split(' ', 1)[1]
        new_text = custom_smallcap(text)
        await m.message.edit_text(
            f"<code>{new_text}</code>",
            reply_markup=m.message.reply_markup
        )
    except Exception as e:
        print(f"Error in safe_style_callback: {e}")
        await m.answer("Error processing your request", show_alert=True)

@app.on_callback_query(filters.regex("^close_reply"))
async def close_reply(c, m):
    await m.message.delete()
