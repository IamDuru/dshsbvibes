from ERAVIBES import app
from pyrogram import filters
import requests

def get_terabox_file_link(tera_url: str) -> str:
    """
    Yeh function Terabox URL se file download link fetch karta hai.
    Note: API endpoint example hai. Apne requirements ke hisaab se modify kar lena.
    """
    try:
        api_endpoint = f"https://api.terabox.com/getFile?url={tera_url}"
        response = requests.get(api_endpoint)
        data = response.json()
        return data.get("fileLink")
    except Exception as e:
        print(f"Error fetching file link: {e}")
        return None

@app.on_message(filters.command("tb"))
def tb_command_handler(client, message):
    """
    /tb command handle karta hai.
    Usage: /tb <Terabox URL>
    """
    if len(message.command) < 2:
        message.reply_text("Usage: /tb <Terabox URL>")
        return

    tera_url = message.command[1]
    message.reply_text("Processing your request, please wait...")
    
    file_link = get_terabox_file_link(tera_url)
    if file_link:
        message.reply_text(f"Yeh raha file download link:\n{file_link}")
    else:
        message.reply_text("Sorry, file link fetch nahi ho pa rahi.")

# 'app.run()' yahan se remove kar diya gaya hai.
