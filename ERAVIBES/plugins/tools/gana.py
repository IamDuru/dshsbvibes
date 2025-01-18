from pyrogram import Client, filters
import requests
from ERAVIBES import app

# API base URL
API_BASE_URL = "https://codesearchdevapi.vercel.app/download/song?name="

@app.on_message(filters.command("gana"))
async def fetch_song(client, message):
    # Extract the song name from the command
    if len(message.command) < 2:
        await message.reply_text("Please provide a song name. Example: /gana Yad", parse_mode="html")
        return

    song_name = " ".join(message.command[1:])
    response = requests.get(API_BASE_URL + song_name)

    if response.status_code == 200:
        data = response.json()
        if data.get("success") and data["data"]["results"]:
            # Get the first song from the results
            song = data["data"]["results"][0]
            song_name = song["name"]
            song_url = song["url"]
            download_url = song.get("downloadUrl")  # Get the download URL
            artist = song["artists"]["primary"][0]["name"]
            
            # Prepare the reply message with HTML formatting
            reply = (
                f"🎶 <b>{song_name}</b>\n"
                f"👤 <b>Artist</b>: {artist}\n"
                f"🔗 <a href='{song_url}'>Listen here</a>\n"
            )
            
            # Add download link if available
            if download_url:
                reply += f"⬇️ <a href='{download_url}'>Download here</a>"
            else:
                reply += "⬇️ Download link not available."

            # Send the reply with HTML formatting
            await message.reply_text(reply, parse_mode="html")
        else:
            await message.reply_text("Sorry, I couldn't find any results for that song.", parse_mode="html")
    else:
        await message.reply_text("An error occurred while fetching the song. Please try again later.", parse_mode="html")
