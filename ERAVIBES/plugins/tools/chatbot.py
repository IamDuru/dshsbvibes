import requests
from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.enums import ChatType
from ERAVIBES import app

@app.on_message(~filters.bot & ~filters.me & filters.text)
async def chatbot(_:Client, message:Message):
    if message.chat.type != ChatType.PRIVATE:
        if not message.reply_to_message:
            return
        if message.reply_to_message.from_user.id != (await _.get_me()).id:
            return
    if message.text and message.text[0] in ["/", "!", "?", "."]:
        return
    
    response = requests.get("https://chatwithai.codesearch.workers.dev/?chat=" + message.text)
    
    if response.status_code == 200:
        try:
            data = response.json()
            if 'response' in data:
                return await message.reply_text(data['response'])
            else:
                return await message.reply_text("ChatBot Error: Invalid response format from the API.")
        except ValueError:
            return await message.reply_text("ChatBot Error: Invalid JSON response from the API.")
    elif response.status_code == 429:
        return await message.reply_text("ChatBot Error: Too many requests. Please wait a few moments.")
    elif response.status_code >= 500:
        return await message.reply_text("ChatBot Error: API server error. Contact us at @net_pro_max.")
    else:
        return await message.reply_text("ChatBot Error: Unknown Error Occurred. Contact us at @net_pro_max.")
