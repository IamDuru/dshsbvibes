import asyncio
import requests
from bs4 import BeautifulSoup
from ERAVIBES import app
from pyrogram import filters

def _get_link_from_toolsground(url: str) -> str:
    """
    toolsground.in se download link extract karta hai.
    Yeh function blocking hai.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Pehla try: <a> tag jismein class "download-btn" ho
            link_tag = soup.find("a", class_="download-btn")
            if link_tag and link_tag.get("href"):
                return link_tag.get("href")
            # Dusra try: koi <a> tag jismein "download" shabd text mein ho
            link_tag = soup.find("a", string=lambda text: text and "download" in text.lower())
            if link_tag and link_tag.get("href"):
                return link_tag.get("href")
            # Debug: agar link nahi mil raha, poore HTML ka kuch part print kar sakte hain
            # print(soup.prettify())
    except Exception as e:
        print(f"Error in toolsground scraping: {e}")
    return None

async def get_link_from_toolsground(url: str) -> str:
    return await asyncio.to_thread(_get_link_from_toolsground, url)

def _get_link_from_player(url: str) -> str:
    """
    player.terabox.tech se download link extract karta hai.
    Yeh blocking function hai.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            # Pehla try: Agar <video> tag hai jismein <source> tag ho
            video_tag = soup.find("video")
            if video_tag:
                source_tag = video_tag.find("source")
                if source_tag and source_tag.get("src"):
                    return source_tag.get("src")
            # Dusra try: <a> tag jismein id "download-link" ho
            link_tag = soup.find("a", id="download-link")
            if link_tag and link_tag.get("href"):
                return link_tag.get("href")
            # Tisra try: koi <a> tag jismein "download" text ho
            link_tag = soup.find("a", string=lambda text: text and "download" in text.lower())
            if link_tag and link_tag.get("href"):
                return link_tag.get("href")
    except Exception as e:
        print(f"Error in player scraping: {e}")
    return None

async def get_link_from_player(url: str) -> str:
    return await asyncio.to_thread(_get_link_from_player, url)

@app.on_message(filters.command("tb"))
async def tb_command_handler(client, message):
    """
    /tb command handle karta hai.
    Usage: /tb <URL>
    URL ya toh toolsground.in ka ho ya player.terabox.tech ka.
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

# 'app.run()' external runner ke through chalaya jayega.
