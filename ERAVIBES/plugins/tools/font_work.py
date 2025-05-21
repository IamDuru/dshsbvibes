from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from ERAVIBES import app

def custom_smallcap(text):
    char_map = {
        'A': 'ᴧ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'є', 'F': 'ꜰ', 'G': 'ɢ', 'H': 'ʜ',
        'I': 'ɪ', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ϻ', 'N': 'η', 'O': 'σ', 'P': 'ᴘ',
        'Q': 'ǫ', 'R': 'ʀ', 'S': 'ꜱ', 'T': 'ᴛ', 'U': 'ᴜ', 'V': 'ᴠ', 'W': 'ᴡ', 'X': 'x',
        'Y': 'ʏ', 'Z': 'ᴢ',
        'a': 'ᴧ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'є', 'f': 'ꜰ', 'g': 'ɢ', 'h': 'ʜ',
        'i': 'ɪ', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ϻ', 'n': 'η', 'o': 'σ', 'p': 'ᴘ',
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
        original_message_text = m.message.reply_to_message.text
        if original_message_text.startswith(('/', '!', '.')):
            text_to_convert = original_message_text.split(' ', 1)[1]
        else:
            text_to_convert = original_message_text

        new_text = custom_smallcap(text_to_convert)
        
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
