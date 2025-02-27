import asyncio
import requests
from bs4 import BeautifulSoup
from ERAVIBES import app
from pyrogram import filters

# Function for toolsground.in
def _get_link_from_toolsground(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                      "(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Example selector: <a id="download-link">
            link_tag = soup.find("a", {"id": "download-link"})
            if link_tag:
                return link_tag.get("href")
            # Agar upar wala selector na mile, "Download" text wale anchor tag try karo
            link_tag = soup.find("a", string=lambda text: text and "Download" in text)
            if link_tag:
                return link_tag.get("href")
    except Exception as e:
        print(f"Error during scraping toolsground.in: {e}")
    return None

async def get_link_from_toolsground(url: str) -> str:
    return await asyncio.to_thread(_get_link_from_toolsground, url)

# Function for player.terabox.tech
def _get_link_from_player(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                      "(KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Example: Agar page mein <video> tag ho jiske andar <source> tag ho
            video_tag = soup.find("video")
            if video_tag:
                source_tag = video_tag.find("source")
                if source_tag:
                    return source_tag.get("src")
            # Alternative: koi anchor tag jismein id="download-link" ya "Download" text ho
            link_tag = soup.find("a", {"id": "download-link"})
            if link_tag:
                return link_tag.get("href")
            link_tag = soup.find("a", string=lambda text: text and "Download" in text)
            if link_tag:
                return link_tag.get("href")
    except Exception as e:
        print(f"Error during scraping player.terabox.tech: {e}")
    return None

async def get_link_from_player(url: str) -> str:
    return await asyncio.to_thread(_get_link_from_player, url)

# /tb command handler using Pyrogram
@app.on_message(filters.command("tb"))
async def tb_command_handler(client, message):
    """
    /tb command handle karta hai.
    Usage: /tb <URL>
    URL ho sakta hai ya toh toolsground.in ka ho ya player.terabox.tech ka.
    """
    if len(message.command) < 2:
        await message.reply_text("Usage: /tb <URL>")
        return

    url = message.command[1]
    await message.reply_text("Processing your request, please wait...")

    download_link = None
    if "player.terabox.tech" in url:
        download_link = await get_link_from_player(url)
    else:
        download_link = await get_link_from_toolsground(url)
    
    if download_link:
        await message.reply_text(f"Yeh raha download link:\n{download_link}")
    else:
        await message.reply_text("Sorry, download link fetch nahi ho pa rahi.")
