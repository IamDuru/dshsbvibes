import asyncio
import os
import re
import random
import glob
import logging
from typing import Union, Tuple, Dict, List

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
import aiohttp

async def is_on_off(setting_id: int) -> bool:
    logging.info(f"Mock: Checking setting {setting_id}")
    return True

def time_to_seconds(time_str: str) -> int:
    if not time_str:
        return 0
    parts = list(map(int, time_str.split(':')))
    seconds = 0
    if len(parts) == 3:
        seconds = parts[0] * 3600 + parts[1] * 60 + parts[2]
    elif len(parts) == 2:
        seconds = parts[0] * 60 + parts[1]
    elif len(parts) == 1:
        seconds = parts[0]
    return seconds


_cached_cookie_file_path: Union[str, None] = None
_yt_dlp_info_cache: Dict[str, Dict] = {}
_video_search_cache: Dict[str, Dict] = {}

def _get_cookie_file_path() -> str:
    global _cached_cookie_file_path
    if _cached_cookie_file_path:
        return _cached_cookie_file_path

    folder_path = os.path.join(os.getcwd(), "cookies")
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("Error: 'cookies' folder mein koi .txt file nahi mili.")

    chosen_file = random.choice(txt_files)
    _cached_cookie_file_path = f"cookies/{os.path.basename(chosen_file)}"
    return _cached_cookie_file_path

async def _get_yt_dlp_info(link: str) -> Dict:
    if link in _yt_dlp_info_cache:
        return _yt_dlp_info_cache[link]

    def _extract_blocking():
        ytdl_opts = {
            "quiet": True,
            "cookiefile": _get_cookie_file_path(),
            "no_warnings": True,
            "geo_bypass": True,
            "nocheckcertificate": True,
        }
        with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
            info = ydl.extract_info(link, download=False)
        return info

    info = await asyncio.to_thread(_extract_blocking)
    _yt_dlp_info_cache[link] = info
    return info

async def _get_video_search_results(link: str) -> Dict:
    cleaned_link = link.split("&")[0] if "&" in link else link

    if cleaned_link in _video_search_cache:
        return _video_search_cache[cleaned_link]

    results = VideosSearch(cleaned_link, limit=1)
    search_result = (await results.next())["result"][0]
    _video_search_cache[cleaned_link] = search_result
    return search_result

class YouTubeAPI:
    def __init__(self):
        self.youtube_regex = re.compile(r"(?:youtube\.com|youtu\.be)")

    async def is_youtube_link(self, link: str) -> bool:
        return bool(self.youtube_regex.search(link))

    async def extract_url_from_message(self, message: Message) -> Union[str, None]:
        messages_to_check = [message]
        if message.reply_to_message:
            messages_to_check.append(message.reply_to_message)

        for msg in messages_to_check:
            if msg.entities:
                for entity in msg.entities:
                    if entity.type == MessageEntityType.URL:
                        text = msg.text or msg.caption
                        return text[entity.offset: entity.offset + entity.length]
            elif msg.caption_entities:
                for entity in msg.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        return None

    # 'url' method for backward compatibility, now without the warning
    async def url(self, message: Message) -> Union[str, None]:
        return await self.extract_url_from_message(message)

    async def get_video_details(self, link: str) -> Tuple[str, str, int, str, str]:
        search_result = await _get_video_search_results(link)
        title = search_result["title"]
        duration_str = search_result["duration"]
        thumbnail = search_result["thumbnails"][0]["url"].split("?")[0]
        vidid = search_result["id"]
        duration_sec = int(time_to_seconds(duration_str)) if duration_str else 0
        return title, duration_str, duration_sec, thumbnail, vidid

    async def get_playlist_ids(self, link: str, limit: int) -> List[str]:
        info = await _get_yt_dlp_info(link)
        return [entry["id"] for entry in info.get("entries", []) if "id" in entry][:limit]

    async def get_available_formats(self, link: str) -> Tuple[List[Dict], str]:
        info = await _get_yt_dlp_info(link)
        available_formats = []
        for fmt in info.get("formats", []):
            if "dash" in fmt.get("format", "").lower():
                continue

            required_keys = ["filesize", "format_id", "ext", "format_note", "format"]
            if all(k in fmt for k in required_keys):
                available_formats.append({
                    "format": fmt["format"],
                    "filesize": fmt["filesize"],
                    "format_id": fmt["format_id"],
                    "ext": fmt["ext"],
                    "format_note": fmt["format_note"],
                    "yturl": link,
                })
        return available_formats, link

    async def get_slider_details(self, link: str, query_index: int) -> Tuple[str, str, str, str]:
        cleaned_link = link.split("&")[0] if "&" in link else link
        results = VideosSearch(cleaned_link, limit=10)
        entries = (await results.next()).get("result")

        if not entries or query_index >= len(entries):
            raise IndexError(f"Error: Query index {query_index} search results ke bounds se bahar hai.")

        selected = entries[query_index]
        return (
            selected["title"],
            selected["duration"],
            selected["thumbnails"][0]["url"].split("?")[0],
            selected["id"]
        )

    async def download_media(
        self,
        link: str,
        download_type: str = "audio",
        format_id: Union[str, None] = None,
        output_title: Union[str, None] = None
    ) -> Tuple[str, bool]:
        if not output_title:
            _, _, _, _, vid_id = await self.get_video_details(link)
            output_title = vid_id

        safe_title = re.sub(r'[\\/:*?"<>|]', '', output_title)

        ydl_opts = {
            "outtmpl": f"downloads/{safe_title}.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
            "cookiefile": _get_cookie_file_path(),
            "prefer_ffmpeg": True,
        }

        if download_type == "audio":
            vid_id = (await _get_video_search_results(link))["id"]
            fpath = f"downloads/{vid_id}.mp3"
            if os.path.exists(fpath):
                return fpath, True

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://yt.okflix.top/api/{vid_id}") as resp:
                        response = await resp.json()
                    if response.get('status') == 'success':
                        download_link = response.get('download_link')
                        async with session.get(download_link) as d_resp:
                            if d_resp.status == 200:
                                content = await d_resp.read()
                                with open(fpath, "wb") as f:
                                    f.write(content)
                                return fpath, True
            except Exception as e:
                logging.error(f"External audio download API fail ho gaya: {e}. yt_dlp par fallback kar rahe hain.")

            ydl_opts["format"] = "bestaudio/best"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
            ydl_opts["outtmpl"] = f"downloads/{safe_title}.mp3"

        elif download_type == "video":
            if await is_on_off(1):
                 ydl_opts["format"] = "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])"
                 ydl_opts["outtmpl"] = f"downloads/{safe_title}.mp4"
                 ydl_opts["merge_output_format"] = "mp4"
            else:
                ydl_opts["format"] = "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])"
                ydl_opts["outtmpl"] = f"downloads/{safe_title}.mp4"
                ydl_opts["merge_output_format"] = "mp4"

        elif download_type == "song_video" and format_id:
            ydl_opts["format"] = f"{format_id}+bestaudio[ext=m4a]"
            ydl_opts["outtmpl"] = f"downloads/{safe_title}.mp4"
            ydl_opts["merge_output_format"] = "mp4"

        elif download_type == "song_audio" and format_id:
            ydl_opts["format"] = format_id
            ydl_opts["outtmpl"] = f"downloads/{safe_title}.mp3"
            ydl_opts["postprocessors"] = [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }]
        else:
            raise ValueError(f"Error: Unsupported download type: '{download_type}' ya 'format_id' missing hai.")

        def _perform_download_blocking():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=True)
                final_path = ydl.prepare_filename(info)
                return final_path

        downloaded_file_path = await asyncio.to_thread(_perform_download_blocking)
        return downloaded_file_path, True
