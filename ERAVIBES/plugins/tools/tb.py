import os
import requests
from pyrogram import filters
from pyrogram.types import Message
from ERAVIBES import app  # Pyrogram client ab ERAVIBES module se import ho raha hai

@app.on_message(filters.command("tg"))
def terabox_download(client, message: Message):
    # /tg command se URL extract karo
    if len(message.command) < 2:
        message.reply("Please /tg command ke baad terabox ka URL do.")
        return

    terabox_url = message.text.split(" ", 1)[1]
    status_message = message.reply("Video processing mein hai... please thoda wait karo.")

    # API endpoint call: terabox URL ke saath jodo
    api_endpoint = f"https://terabox.udayscriptsx.workers.dev/?url={terabox_url}"
    try:
        r = requests.get(api_endpoint)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        status_message.edit(f"API call mein error aayi: {e}")
        return

    # JSON response se required fields extract karo
    file_name = data.get("file_name")
    direct_link = data.get("direct_link")
    thumb_url = data.get("thumb")
    
    if not direct_link or not thumb_url:
        status_message.edit("API se sahi data nahi mila.")
        return

    # Temporary file paths
    video_path = f"temp_{file_name.replace(' ', '_')}"
    thumb_path = "temp_thumb.jpg"
    try:
        # Video file download karo
        with requests.get(direct_link, stream=True) as vid_req:
            vid_req.raise_for_status()
            with open(video_path, "wb") as f:
                for chunk in vid_req.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

        # Thumbnail download karo
        with requests.get(thumb_url, stream=True) as thumb_req:
            thumb_req.raise_for_status()
            with open(thumb_path, "wb") as f:
                for chunk in thumb_req.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
    except Exception as e:
        status_message.edit(f"Download error: {e}")
        return

    # Video file Telegram pe bhej do
    try:
        message.reply_video(
            video=video_path,
            thumb=thumb_path,
            caption=f"File: {file_name}\nSize: {data.get('size', 'Unknown')}"
        )
        status_message.delete()  # Processing message hata do
    except Exception as e:
        status_message.edit(f"Video send karte hue error aayi: {e}")
    finally:
        # Temporary files ko delete karo
        if os.path.exists(video_path):
            os.remove(video_path)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
