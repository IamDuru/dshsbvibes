import asyncio
import os
import re
import json
import aiohttp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from ERAVIBES.utils.formatters import time_to_seconds
from ERAVIBES.utils.database import is_on_off
from typing import Union

try:
    from moviepy.editor import VideoFileClip
except ImportError:
    print("WARNING: moviepy library not found. Please install it using 'pip install moviepy'.")
    print("WARNING: Also ensure FFmpeg is installed and accessible in your system's PATH.")
    VideoFileClip = None


async def _download_from_maybechiku_api(link: str, file_extension: str, vid_id: str = None):
    maybechiku_base_url = "https://youtube.maybechiku.workers.dev/"
    query_string = {"url": link}

    if not vid_id:
        match = re.search(r'(?:youtu\.be\/|youtube\.com\/watch\?v=)([a-zA-Z0-9_-]{11})', link)
        if match:
            vid_id = match.group(1)
        else:
            vid_id = "unknown_id_" + str(hash(link))[:8]

    download_file_path = os.path.join("downloads", f"{vid_id}.mp4") 

    if os.path.exists(download_file_path):
        print(f"DEBUG: File already exists: {download_file_path}. Skipping download.")
        return download_file_path, True

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(maybechiku_base_url, params=query_string) as response:
                response.raise_for_status()
                data = await response.json()

                if data.get('success') and data.get('data') and data['data'].get('downloadURL'):
                    download_url = data['data']['downloadURL']
                    print(f"DEBUG: Maybechiku API returned download URL: {download_url}")
                    
                    async with session.get(download_url) as file_response:
                        file_response.raise_for_status()
                        
                        os.makedirs("downloads", exist_ok=True)
                        
                        with open(download_file_path, "wb") as f:
                            while True:
                                chunk = await file_response.content.read(8192)
                                if not chunk:
                                    break
                                f.write(chunk)
                        print(f"DEBUG: Successfully downloaded via Maybechiku API to: {download_file_path}")
                        return download_file_path, True
                else:
                    print(f"ERROR: Maybechiku API reports failure or missing downloadURL for {link}: {data}")
                    return None, False
        except aiohttp.ClientError as e:
            print(f"ERROR: Maybechiku API AIOHTTP error for {link}: {e}")
            return None, False
        except json.JSONDecodeError as e:
            print(f"ERROR: Maybechiku API JSON decode error for {link}: {e}. Response was not valid JSON.")
            return None, False
        except Exception as e:
            print(f"ERROR: An unexpected error occurred with Maybechiku API for {link}: {e}")
            return None, False

async def _convert_mp4_to_mp3(mp4_file_path: str, mp3_output_path: str) -> bool:
    if not VideoFileClip:
        print("ERROR: moviepy library available nahi hai, MP4 se MP3 conversion nahi ho sakta.")
        return False
    
    if not os.path.exists(mp4_file_path):
        print(f"ERROR: MP4 file '{mp4_file_path}' conversion ke liye nahi mila.")
        return False

    loop = asyncio.get_running_loop()
    
    def sync_convert():
        try:
            video_clip = VideoFileClip(mp4_file_path)
            audio_clip = video_clip.audio
            audio_clip.write_audiofile(mp3_output_path, logger=None)
            audio_clip.close()
            video_clip.close()
            print(f"DEBUG: Successfully converted '{mp4_file_path}' to '{mp3_output_path}'")
            return True
        except Exception as e:
            print(f"ERROR: MP4 se MP3 convert karte waqt error aayi: {e}")
            return False

    success = await loop.run_in_executor(None, sync_convert)
    return success

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    async def exists(self, link: str, videoid: Union[bool, str] = None) -> bool:
        if videoid:
            link = self.base + videoid
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        
        text = ""
        offset = None
        length = None
        
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == "text_link":
                        return entity.url
        
        if offset is None:
            return None
        return text[offset: offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + videoid
        if "&" in link:
            link = link.split("&")[0]
        
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        
        if not results_dict["result"]:
            print(f"WARNING: No search results found for link: {link}")
            return None, None, None, None, None

        result = results_dict["result"][0]
        title = result["title"]
        duration_min = result["duration"]
        thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        vidid = result["id"]
        duration_sec = 0 if str(duration_min) == "None" else int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None) -> Union[str, None]:
        if videoid:
            link = self.base + videoid
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            return result["title"]
        return None

    async def duration(self, link: str, videoid: Union[bool, str] = None) -> Union[str, None]:
        if videoid:
            link = self.base + videoid
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            return result["duration"]
        return None

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None) -> Union[str, None]:
        if videoid:
            link = self.base + videoid
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]
        return None

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + videoid
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        
        if not results_dict["result"]:
            print(f"WARNING: No track results found for link: {link}")
            return None, None

        result = results_dict["result"][0]
        track_details = {
            "title": result["title"],
            "link": result["link"],
            "vidid": result["id"],
            "duration_min": result["duration"],
            "thumb": result["thumbnails"][0]["url"].split("?")[0],
        }
        return track_details, result["id"]

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + videoid
        if "&" in link:
            link = link.split("&")[0]
        
        a = VideosSearch(link, limit=10)
        results_dict = await a.next()
        result = results_dict.get("result")
        
        if not result or query_type >= len(result) or query_type < 0:
            print(f"WARNING: Invalid query_type ({query_type}) or no results for link: {link}")
            return None, None, None, None

        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(self, link: str, mystic, videoid: Union[bool, str] = None, songvideo: bool = False, songaudio: bool = False, video: bool = False):
        if mystic is None:
            print(f"ERROR: 'mystic' (chat_id) is None for link: {link} or videoid: {videoid}. Cannot proceed with download or send message downstream.")
            return None, False

        title, duration_min, duration_sec, thumbnail, actual_vidid = await self.details(link, videoid)
        if not actual_vidid:
            print(f"ERROR: Video details nahi mil payi link ke liye: {link} ya videoid: {videoid}")
            return None, False

        full_link = self.base + actual_vidid
        
        downloaded_file = None
        direct = False

        print(f"INFO: Download karne ki koshish kar rahe hain {full_link} type ke liye: songvideo={songvideo}, songaudio={songaudio}, video={video}")

        if songvideo:
            downloaded_mp4_path, direct = await _download_from_maybechiku_api(full_link, "mp4", actual_vidid)
            if downloaded_mp4_path:
                print(f"INFO: Song video downloaded as MP4: {downloaded_mp4_path}")
                return downloaded_mp4_path, True
            else:
                return None, False
        elif songaudio:
            downloaded_mp4_path, direct = await _download_from_maybechiku_api(full_link, "mp4", actual_vidid)
            
            if downloaded_mp4_path:
                mp3_output_path = os.path.join("downloads", f"{actual_vidid}.mp3")
                print(f"INFO: MP4 downloaded, ab MP3 conversion ki koshish kar rahe hain '{downloaded_mp4_path}' to '{mp3_output_path}'")
                
                conversion_success = await _convert_mp4_to_mp3(downloaded_mp4_path, mp3_output_path)
                
                if conversion_success:
                    try:
                        os.remove(downloaded_mp4_path)
                        print(f"DEBUG: Original MP4 file '{downloaded_mp4_path}' delete kar diya gaya.")
                    except OSError as e:
                        print(f"WARNING: MP4 file delete karte waqt error: {e}")
                    return mp3_output_path, True
                else:
                    print(f"ERROR: MP4 to MP3 conversion failed for {full_link}.")
                    return None, False
            else:
                print(f"ERROR: Maybechiku API se MP4 download nahi ho paya {full_link} ke liye, isliye MP3 bhi nahi ban paya.")
                return None, False
        elif video:
            if await is_on_off(1):
                downloaded_file, direct = await _download_from_maybechiku_api(full_link, "mp4", actual_vidid)
            else:
                downloaded_file, direct = await _download_from_maybechiku_api(full_link, "mp4", actual_vidid)
            
            if downloaded_file:
                return downloaded_file, True
            else:
                return None, False
        else:
            downloaded_mp4_path, direct = await _download_from_maybechiku_api(full_link, "mp4", actual_vidid)
            
            if downloaded_mp4_path:
                mp3_output_path = os.path.join("downloads", f"{actual_vidid}.mp3")
                print(f"INFO: Default audio download (MP3) request. MP4 downloaded, ab MP3 conversion ki koshish kar rahe hain '{downloaded_mp4_path}' to '{mp3_output_path}'")
                
                conversion_success = await _convert_mp4_to_mp3(downloaded_mp4_path, mp3_output_path)
                
                if conversion_success:
                    try:
                        os.remove(downloaded_mp4_path)
                        print(f"DEBUG: Original MP4 file '{downloaded_mp4_path}' delete kar diya gaya.")
                    except OSError as e:
                        print(f"WARNING: MP4 file delete karte waqt error: {e}")
                    return mp3_output_path, True
                else:
                    print(f"ERROR: Default audio download (MP3) conversion failed for {full_link}.")
                    return None, False
            else:
                print(f"ERROR: Default audio download (MP3) ke liye Maybechiku API se MP4 download nahi ho paya {full_link}.")
                return None, False
