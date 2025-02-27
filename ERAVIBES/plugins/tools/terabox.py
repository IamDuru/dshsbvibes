ev import asyncio
import requests
from bs4 import BeautifulSoup
from ERAVIBES import app
from pyrogram import filters

def _get_terabox_link_from_toolsground(url: str) -> str:
    """
    Yeh blocking function toolsground.in se download link extract karta hai.
    Aapko yahan HTML structure ke hisaab se selectors adjust karne pad sakte hain.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                      "(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Yahan aapko inspect karke dekhna hoga ke download link kis element mein hai.
            # Example: agar download link <a> tag mein id="download-link" ke saath ho:
            link_tag = soup.find("a", {"id": "download-link"})
            if link_tag:
                return link_tag.get("href")
            else:
                # Agar aisa tag nahi milta, toh alternative selector try karo:
                link_tag = soup.find("a", string=lambda text: text and "Download" in text)
                if link_tag:
                    return link_tag.get("href")
    except Exception as e:
        print(f"Error during scraping: {e}")
    return None

async def get_terabox_link_from_toolsground(url: str) -> str:
    """
    Async wrapper jo blocking scraping function ko asyncio.to_thread se run karta hai.
    """
    return await asyncio.to_thread(_get_terabox_link_from_toolsground, url)

@app.on_message(filters.command("tb"))
async def tb_command_handler(client, message):
    """
    /tb command handle karta hai.
    Usage: /tb <toolsground URL>
    """
    if len(message.command) < 2:
        await message.reply_text("Usage: /tb <toolsground URL>")
        return

    url = message.command[1]
    await message.reply_text("Processing your request, please wait...")

    download_link = await get_terabox_link_from_toolsground(url)
    if download_link:
        await message.reply_text(f"Yeh raha download link:\n{download_link}")
    else:
        await message.reply_text("Sorry, download link fetch nahi ho pa rahi.")
