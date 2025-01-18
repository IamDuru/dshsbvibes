from pyrogram import Client, filters
import requests
from ERAVIBES import app

# API base URL
API_BASE_URL = "https://codesearchdevapi.vercel.app/download/song?name="

@app.on_message(filters.command("gana"))
async def fetch_song(client, message):
    # Extract the song name from the command
    if len(message.command) < 2:
        await message.reply_text("Please provide a song name. Example: /gana Yad")
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
            
            # Prepare the reply message (plain text)
            reply = (
                f"🎶 {song_name}\n"
                f"👤 Artist: {artist}\n"
                f"🔗 Listen here: {song_url}\n"
            )
            
            # Add download link if available
            if download_url:
                reply += f"⬇️ Download here: {download_url}"
            else:
                reply += "⬇️ Download link not available."

            # Send the reply as plain text
            await message.reply_text(reply)
        else:
            await message.reply_text("Sorry, I couldn't find any results for that song.")
    else:
        await message.reply_text("An error occurred while fetching the song. Please try again later.")
