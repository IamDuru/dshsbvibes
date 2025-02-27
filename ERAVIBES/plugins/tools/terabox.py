import asyncio
import requests
from bs4 import BeautifulSoup
from ERAVIBES import app
from pyrogram import filters

def _get_terabox_link_from_toolsground(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                      "(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print("Status Code:", response.status_code)  # Debug print
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Debug: Print full HTML structure
            # print(soup.prettify())
            link_tag = soup.find("a", {"id": "download-link"})
            if link_tag:
                return link_tag.get("href")
            else:
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
