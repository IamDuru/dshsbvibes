import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import RPCError
import time
import asyncio
from ERAVIBES import app

# Terabox API endpoint
TERABOX_API = "https://terabox.udayscriptsx.workers.dev/?url="

async def download_file(url: str, file_name: str, message: Message):
    try:
        # Send initial downloading status
        status_msg = await message.reply_text(f"📥 Downloading video...\n\n{file_name}")
        
        # Download the file
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        total_size = int(response.headers.get('content-length', 0))
        downloaded_size = 0
        start_time = time.time()
        
        with open(file_name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)
                    downloaded_size += len(chunk)
                    
                    # Update progress every 5 seconds
                    if time.time() - start_time > 5:
                        progress = (downloaded_size / total_size) * 100
                        await status_msg.edit_text(
                            f"📥 Downloading video...\n\n"
                            f"📁 {file_name}\n"
                            f"📊 Progress: {progress:.2f}%\n"
                            f"⚡ Speed: {(downloaded_size / (time.time() - start_time)) / 1024:.2f} KB/s"
                        )
                        start_time = time.time()
        
        return True
    except Exception as e:
        await message.reply_text(f"❌ Download failed: {str(e)}")
        return False
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)

@app.on_message(filters.command("tg"))
async def handle_terabox(client, message: Message):
    # Check if URL is provided
    if len(message.command) < 2:
        await message.reply_text("Please provide a Terabox URL after the /tg command.")
        return
    
    terabox_url = message.text.split(" ", 1)[1].strip()
    
    # Show processing message
    processing_msg = await message.reply_text("🔍 Processing Terabox link...")
    
    try:
        # Fetch video info from API
        api_url = TERABOX_API + terabox_url
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
        
        # Extract video details
        file_name = data.get("file_name", "video.mp4")
        direct_link = data.get("direct_link")
        thumb_url = data.get("thumb")
        size = data.get("size", "Unknown size")
        
        if not direct_link:
            await processing_msg.edit_text("❌ Failed to get direct download link.")
            return
        
        # Download thumbnail
        thumb_file = None
        if thumb_url:
            try:
                thumb_response = requests.get(thumb_url)
                thumb_response.raise_for_status()
                thumb_file = "thumbnail.jpg"
                with open(thumb_file, 'wb') as f:
                    f.write(thumb_response.content)
            except Exception as e:
                print(f"Failed to download thumbnail: {e}")
                thumb_file = None
        
        # Update status
        await processing_msg.edit_text(f"📥 Preparing to download...\n\n📁 {file_name}\n📦 Size: {size}")
        
        # Temporary file name
        temp_file = f"temp_{file_name}"
        
        # Download the video
        success = await download_file(direct_link, temp_file, message)
        if not success:
            return
        
        # Send the video to user
        await processing_msg.edit_text("📤 Uploading video to Telegram...")
        
        try:
            await message.reply_video(
                video=temp_file,
                thumb=thumb_file,
                caption=f"🎬 {file_name}\n\n🔗 Original URL: {terabox_url}",
                progress=lambda current, total: asyncio.get_event_loop().create_task(
                    update_progress(processing_msg, current, total, file_name)
                )
            )
            
            await processing_msg.edit_text("✅ Video sent successfully!")
        except RPCError as e:
            await processing_msg.edit_text(f"❌ Failed to send video: {str(e)}")
        
    except Exception as e:
        await processing_msg.edit_text(f"❌ Error: {str(e)}")
    finally:
        # Clean up
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if thumb_file and os.path.exists(thumb_file):
            os.remove(thumb_file)

async def update_progress(message: Message, current: int, total: int, file_name: str):
    progress = (current / total) * 100
    try:
        await message.edit_text(
            f"📤 Uploading video...\n\n"
            f"📁 {file_name}\n"
            f"📊 Progress: {progress:.2f}%"
        )
    except:
        pass
