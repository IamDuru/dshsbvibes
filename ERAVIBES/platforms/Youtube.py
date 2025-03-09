import asyncio
import os
import re
from typing import Union

import aiohttp
import yt_dlp
from pyrogram.types import Message
from youtubesearchpython.__future__ import VideosSearch
from youtube_search import YoutubeSearch

import config
from ERAVIBES.utils.database import is_on_off
from ERAVIBES.utils.formatters import time_to_seconds
from ytdlx import ytdlx

async def shell_cmd(cmd):
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    out, errorz = await proc.communicate()
    if errorz:
        if "unavailable videos are hidden" in (errorz.decode("utf-8")).lower():
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
                    if entity.type == "url":
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == "text_link":
                        return entity.url
        if offset is None:
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        async for result in results.next()["result"]:
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
        async for result in results.next()["result"]:
            return result["title"]

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        async for result in results.next()["result"]:
            return result["duration"]

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = VideosSearch(link, limit=1)
        async for result in results.next()["result"]:
            return result["thumbnails"][0]["url"].split("?")[0]

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
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
        return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]
        playlist = await shell_cmd(
            f"yt-dlp -i --get-id --flat-playlist --playlist-end {limit} --skip-download {link}"
        )
        try:
            result = playlist.split("\n")
            for key in result:
                if key == "":
                    result.remove(key)
        except Exception:
            result = []
        return result

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        results = YoutubeSearch(link, max_results=1).to_dict()
        for result in results:
            track_details = {
                "title": result["title"],
                "link": f"https://youtube.com{result['url_suffix']}",
                "vidid": result["id"],
                "duration_min": result["duration"],
                "thumb": f"https://img.youtube.com/vi/{result['id']}/hqdefault.jpg",
            }
            return track_details, result["id"]

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    _ = format["format"]
                except Exception:
                    continue
                if "dash" not in str(format["format"]).lower():
                    try:
                        _ = format["filesize"]
                        _ = format["format_id"]
                        _ = format["ext"]
                        _ = format["format_note"]
                    except Exception:
                        continue
                    formats_available.append({
                        "format": format["format"],
                        "filesize": format["filesize"],
                        "format_id": format["format_id"],
                        "ext": format["ext"],
                        "format_note": format["format_note"],
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
        return (result[query_type]["title"],
                result[query_type]["duration"],
                result[query_type]["thumbnails"][0]["url"].split("?")[0],
                result[query_type]["id"])

    # Hybrid _download: Returns a direct streaming URL for immediate playback,
    # while concurrently downloading the complete file in the background.
    async def _download(self, link: str, mystic,
                        video: Union[bool, str] = None,
                        videoid: Union[bool, str] = None,
                        songaudio: Union[bool, str] = None,
                        songvideo: Union[bool, str] = None,
                        format_id: Union[bool, str] = None,
                        title: Union[bool, str] = None) -> str:
        if videoid:
            link = self.base + link

        loop = asyncio.get_running_loop()

        # Functions to download complete file (background process)
        def audio_dl():
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "concurrent_fragment_downloads": 4,
                "http_chunk_size": 1048576,
            }
            x = yt_dlp.YoutubeDL(ydl_opts)
            info = x.extract_info(link, False)
            filepath = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if not os.path.exists(filepath):
                x.download([link])
            return filepath

        def video_dl():
            ydl_opts = {
                "format": "(bestvideo[height<=?720][width<=?1280][ext=mp4])+(bestaudio[ext=m4a])",
                "outtmpl": "downloads/%(id)s.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "concurrent_fragment_downloads": 4,
                "http_chunk_size": 1048576,
            }
            x = yt_dlp.YoutubeDL(ydl_opts)
            info = x.extract_info(link, False)
            filepath = os.path.join("downloads", f"{info['id']}.{info['ext']}")
            if not os.path.exists(filepath):
                x.download([link])
            return filepath

        def song_video_dl():
            fmt = f"{format_id}+140"
            fpath = f"downloads/{title}"
            ydl_opts = {
                "format": fmt,
                "outtmpl": fpath,
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "merge_output_format": "mp4",
                "concurrent_fragment_downloads": 4,
                "http_chunk_size": 1048576,
            }
            x = yt_dlp.YoutubeDL(ydl_opts)
            x.download([link])

        def song_audio_dl():
            fpath = f"downloads/{title}.%(ext)s"
            ydl_opts = {
                "format": format_id,
                "outtmpl": f"downloads/{title}.%(ext)s",
                "geo_bypass": True,
                "nocheckcertificate": True,
                "quiet": True,
                "no_warnings": True,
                "prefer_ffmpeg": True,
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
                "concurrent_fragment_downloads": 4,
                "http_chunk_size": 1048576,
            }
            x = yt_dlp.YoutubeDL(ydl_opts)
            x.download([link])

        # Hybrid approach:
        # 1. Get a direct streaming URL quickly using "-g" option.
        # 2. Start background download of complete file.
        if video:
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp",
                "-g",
                "-f",
                "best[height<=?720][width<=?1280]",
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            direct_url = stdout.decode().split("\n")[0] if stdout else None
            asyncio.create_task(loop.run_in_executor(None, video_dl))
            return direct_url, True
        else:
            proc = await asyncio.create_subprocess_exec(
                "yt-dlp",
                "-g",
                "-f",
                "bestaudio[ext=m4a]",
                link,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await proc.communicate()
            direct_url = stdout.decode().split("\n")[0] if stdout else None
            asyncio.create_task(loop.run_in_executor(None, audio_dl))
            return direct_url, True

    async def download(self, link: str, mystic,
                       video: Union[bool, str] = None,
                       videoid: Union[bool, str] = None,
                       songaudio: Union[bool, str] = None,
                       songvideo: Union[bool, str] = None,
                       format_id: Union[bool, str] = None,
                       title: Union[bool, str] = None):
        # Agar file pehle se exist kare toh use return karo.
        if os.path.exists(f"downloads/{link.replace(self.base, '')}.mp3"):
            return f"downloads/{link.replace(self.base, '')}.mp3", True
        options = {
            "format": "bestaudio[ext=m4a]",
            "outtmpl": "downloads/%(id)s.%(ext)s",
        }
        try:
            async with ytdlx("Ehab_@flaregun", options) as client:
                path = await client.download(link.replace(self.base, ''))
        except Exception as e:
            print(e)
            return
        return path, True
