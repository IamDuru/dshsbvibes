import asyncio
import aiohttp
import os
import re
import json
import random
import glob
import logging
from typing import Union

import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from ERAVIBES.utils.database import is_on_off
from ERAVIBES.utils.formatters import time_to_seconds

# Global caching for cookie file path taaki baar baar folder scan na ho
_cached_cookie = None

def cookie_txt_file():
    global _cached_cookie
    if _cached_cookie:
        return _cached_cookie

    folder_path = os.path.join(os.getcwd(), "cookies")
    log_filename = os.path.join(os.getcwd(), "cookies", "logs.csv")
    txt_files = glob.glob(os.path.join(folder_path, '*.txt'))
    if not txt_files:
        raise FileNotFoundError("No .txt files found in the specified folder.")
    chosen_file = random.choice(txt_files)
    with open(log_filename, 'a') as file:
        file.write(f'Choosen File : {chosen_file}\n')
    _cached_cookie = f"cookies/{os.path.basename(chosen_file)}"
    return _cached_cookie

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
            if 'filesize' in fmt and fmt["filesize"]:
                total_size += fmt["filesize"]
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
        err_text = errorz.decode("utf-8")
        if "unavailable videos are hidden" in err_text.lower():
            return out.decode("utf-8")
        else:
            return err_text
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
        return bool(re.search(self.regex, link))

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset is not None:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset = entity.offset
                        length = entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
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
        search_result = (await results.next())["result"][0]
        title = search_result["title"]
        duration_min = search_result["duration"]
        thumbnail = search_result["thumbnails"][0]["url"].split("?")[0]
        vidid = search_result["id"]
        duration_sec = int(time_to_seconds(duration_min)) if duration_min else 0
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        search_result = (await results.next())["result"][0]
        return search_result["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        search_result = (await results.next())["result"][0]
        return search_result["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        search_result = (await results.next())["result"][0]
        thumbnail = search_result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

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
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --cookies {cookie_txt_file()} --playlist-end {limit} --skip-download {link}"
        )
        result = [item for item in playlist.split("\n") if item]
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        search_result = (await results.next())["result"][0]
        title = search_result["title"]
        duration_min = search_result["duration"]
        vidid = search_result["id"]
        yturl = search_result["link"]
        thumbnail = search_result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True, "cookiefile": cookie_txt_file()}
        def extract_info():
            with yt_dlp.YoutubeDL(ytdl_opts) as ydl:
                return ydl.extract_info(link, download=False)
        r = await asyncio.to_thread(extract_info)
        formats_available = []
        for fmt in r.get("formats", []):
            try:
                _ = str(fmt["format"])
            except Exception:
                continue
            if "dash" in str(fmt["format"]).lower():
                continue
            try:
                _ = fmt["filesize"]
                _ = fmt["format_id"]
                _ = fmt["ext"]
                _ = fmt["format_note"]
            except Exception:
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
        result = (await a.next()).get("result")
        title = result[query_type]["title"]
        duration_min = result[query_type]["duration"]
        vidid = result[query_type]["id"]
        thumbnail = result[query_type]["thumbnails"][0]["url"].split("?")[0]
        return title, duration_min, thumbnail, vidid

    async def download(self, link: str, mystic, video: Union[bool, str] = None,
                       videoid: Union[bool, str] = None,
                       songaudio: Union[bool, str] = None,
                       songvideo: Union[bool, str] = None,
                       format_id: Union[bool, str] = None,
                       title: Union[bool, str] = None) -> str:
        if videoid:
            vid_id = link
            link = self.base + link

        loop = asyncio.get_running_loop()

        # Asynchronous audio download using aiohttp (non-blocking network I/O)
        async def audio_dl():
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(f"https://yt.okflix.top/api/{vid_id}") as resp:
                        response = await resp.json()
                    if response.get('status') == 'success':
                        fpath = f"downloads/{vid_id}.mp3"
                        if os.path.exists(fpath):
                            return fpath
                        download_link = response.get('download_link')
                        async with session.get(download_link) as data_resp:
                            if data_resp.status == 200:
                                content = await data_resp.read()
                                with open(fpath, "wb") as f:
                                    f.write(content)
                                return fpath
            except Exception as e:
                print(e)
            # Fallback synchronous method via yt_dlp extraction if async fails
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile": cookie_txt_file(),
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
            return info['url']

        def video_dl():
            ydl_opts = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "cookiefile": cookie_txt_file(),
                "no_warnings": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(link, download=False)
            xyz = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if os.path.exists(xyz):
                return xyz
            ydl.download([link])
            return xyz

        def song_video_dl():
            formats_opt = f"{format_id}+140"
            fpath = f"downloads/{title}"
            ydl_opts = {
                "format": formats_opt,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "cookiefile": cookie_txt_file(),
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

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
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])

        if songvideo:
            await loop.run_in_executor(None, song_video_dl)
            return f"downloads/{title}.mp4"
        elif songaudio:
            await loop.run_in_executor(None, song_audio_dl)
            return f"downloads/{title}.mp3"
        elif video:
            if await is_on_off(1):
                downloaded_file = await loop.run_in_executor(None, video_dl)
                direct = True
            else:
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
                    downloaded_file = stdout.decode().split("\n")[0]
                    direct = False
                else:
                    file_size = await check_file_size(link)
                    if not file_size:
                        print("None file Size")
                        return
                    total_size_mb = file_size / (1024 * 1024)
                    if total_size_mb > 250:
                        print(f"File size {total_size_mb:.2f} MB exceeds the 100MB limit.")
                        return None
                    downloaded_file = await loop.run_in_executor(None, video_dl)
                    direct = True
        else:
            downloaded_file = await audio_dl()
            direct = True
        return downloaded_file, direct
