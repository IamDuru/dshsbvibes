import asyncio
import os
import re
import json
from typing import Union
import requests
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
import glob
import random
import aiohttp
from youtube_search import YoutubeSearch
import config
from ERAVIBES.utils.database import is_on_off
from ERAVIBES.utils.formatters import time_to_seconds
from ytdlx import ytdlx

def cookie_txt_file():
    folder_path = f"{os.getcwd()}/cookies"
    filename = f"{os.getcwd()}/cookies/logs.csv"
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    cookie_file = random.choice(txt_files)
    with open(filename, 'a') as file:
        file.write(f'Choosen File : {cookie_file}\n')
    return f"cookies/{os.path.basename(cookie_file)}"

async def is_cookie_working():
    test_link = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    try:
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_txt_file(),
            "-J",
            test_link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        return proc.returncode == 0
    except Exception as e:
        print("Error checking cookies:", e)
        return False

async def check_file_size(link):
    async def get_format_info(link):
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_txt_file(),
            "-J",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            print(f'Error:\n{stderr.decode()}')
            return None
        return json.loads(stdout.decode())
    def parse_size(formats):
        total_size = 0
        for fmt in formats:
            if 'filesize' in fmt and fmt['filesize']:
                total_size += fmt['filesize']
        return total_size
    info = await get_format_info(link)
    if info is None:
        return None
    formats = info.get('formats', [])
    if not formats:
        print("No formats found.")
        return None
    total_size = parse_size(formats)
    return total_size

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in errorz.decode("utf-8").lower():
            return out.decode("utf-8")
        else:
            return errorz.decode("utf-8")
    return out.decode("utf-8")

class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    
    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        return True if re.search(self.regex, link) else False
    
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
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            duration_sec = 0 if str(duration_min) == "None" else int(time_to_seconds(duration_min))
            return title, duration_min, duration_sec, thumbnail, vidid
    
    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            return result["title"]
    
    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            return result["duration"]
    
    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]
    
    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "--cookies", cookie_txt_file(),
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            link,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()
    
    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        playlist_ids = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_txt_file()} --playlist-end {limit} --skip-download {link}"
        )
        return [pid for pid in playlist_ids.split("\n") if pid.strip() != ""]
    
    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        results_dict = await results.next()
        for result in results_dict["result"]:
            track_details = {
                "title": result["title"],
                "link": result["link"],
                "vidid": result["id"],
                "duration_min": result["duration"],
                "thumb": result["thumbnails"][0]["url"].split("?")[0],
            }
            return track_details, result["id"]
    
    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True, "cookiefile": cookie_txt_file()}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            info = ydl.extract_info(link, download=False)
            for fmt in info.get("formats", []):
                try:
                    str(fmt["format"])
                except:
                    continue
                if "dash" not in str(fmt["format"]).lower():
                    try:
                        fmt["format"]
                        fmt["filesize"]
                        fmt["format_id"]
                        fmt["ext"]
                        fmt["format_note"]
                    except:
                        continue
                    formats_available.append({
                        "format": fmt["format"],
                        "filesize": fmt["filesize"],
                        "format_id": fmt["format_id"],
                        "ext": fmt["ext"],
                        "format_note": fmt["format_note"],
                        "yturl": link,
                    })
            return formats_available, link
    
    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        a = VideosSearch(link, limit=10)
        results_dict = await a.next()
        result = results_dict.get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid
    
    async def download(self, link: str, mystic, video: Union[bool, str] = None,
                       videoid: Union[bool, str] = None, songaudio: Union[bool, str] = None,
                       songvideo: Union[bool, str] = None, format_id: Union[bool, str] = None,
                       title: Union[bool, str] = None):
        file_identifier = link.replace(self.base, "")
        if os.path.exists(f"downloads/{file_identifier}.mp3"):
            return f"downloads/{file_identifier}.mp3", True
        if videoid:
            vid_id = link
            link = self.base + link
        loop = asyncio.get_running_loop()
        def cookies_audio_dl():
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile": cookie_txt_file(),
                "no_warnings": True,
            }
            x = yt_dlp.YoutubeDL(ydl_opts)
            info = x.extract_info(link, download=False)
            return info.get('url')
        def cookies_video_dl():
            ydl_opts = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile": cookie_txt_file(),
                "no_warnings": True,
            }
            x = yt_dlp.YoutubeDL(ydl_opts)
            info = x.extract_info(link, download=False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            x.download([link])
            return xyz
        def api_audio_dl():
            try:
                res = requests.get(f"https://yt.okflix.top/api/{vid_id}")
                response = res.json()
                if response.get('status') == 'success':
                    fpath = f"downloads/{vid_id}.mp3"
                    if os.path.exists(fpath):
                        return fpath
                    download_link = response.get('download_link')
                    data = requests.get(download_link)
                    if data.status_code == 200:
                        with open(fpath, "wb") as f:
                            f.write(data.content)
                        return fpath
            except Exception as e:
                print("API audio error:", e)
            return None
        def api_video_dl():
            return None
        async def download_audio():
            result = None
            if await is_cookie_working():
                result = await loop.run_in_executor(None, cookies_audio_dl)
                if result:
                    return result, True
            result = await loop.run_in_executor(None, api_audio_dl)
            if result:
                return result, False
            return await loop.run_in_executor(None, cookies_audio_dl), True
        async def download_video():
            result = None
            if await is_cookie_working():
                result = await loop.run_in_executor(None, cookies_video_dl)
                if result:
                    return result, True
            result = await loop.run_in_executor(None, api_video_dl)
            if result:
                return result, False
            return await loop.run_in_executor(None, cookies_video_dl), True
        if songvideo:
            await loop.run_in_executor(None, lambda: None)
            fpath = f"downloads/{title}.mp4"
            return fpath, True
        elif songaudio:
            def song_audio_dl():
                fpath = f"downloads/{title}.%(ext)s"
                ydl_opts = {
                    "format": format_id,
                    "outtmpl": fpath,
                    "geo_bypass": True,
                    "nocheckcertificate": True,
                    "quiet": True,
                    "no_warnings": True,
                    "cookiefile": cookie_txt_file(),
                    "prefer_ffmpeg": True,
                    "postprocessors": [
                        {
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "mp3",
                            "preferredquality": "192",
                        }
                    ],
                }
                x = yt_dlp.YoutubeDL(ydl_opts)
                x.download([link])
            await loop.run_in_executor(None, song_audio_dl)
            fpath = f"downloads/{title}.mp3"
            return fpath, True
        elif video:
            return await download_video()
        else:
            return await download_audio()
