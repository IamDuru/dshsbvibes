import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters
from distutils.util import strtobool

load_dotenv()

def parse_list(value):
    return [item.strip() for item in value.split()] if value else []

#❖ Get this value from my.telegram.org/apps
API_ID = int(getenv("API_ID", None))
API_HASH = getenv("API_HASH", None)

#❖ Add Owner Username without @ 
OWNER_USERNAME = getenv("OWNER_USERNAME", "OfficialDurgesh")

#❖  Get Your bot username
BOT_USERNAME = getenv("BOT_USERNAME", "DuruXbot")

#❖  Don't Add style font 
BOT_NAME = getenv("BOT_NAME")

#❖ get Your Assistant User name
ASSUSERNAME = getenv("ASSUSERNAME")

#❖ Get your token from @BotFather on Telegram.
BOT_TOKEN = getenv("BOT_TOKEN")

#❖ Get your mongo url from cloud.mongodb.com
MONGO_DB_URI = getenv("MONGO_DB_URI", None)

DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 600000))

#❖  Chat id of a group for logging bot's activities
LOGGER_ID = int(getenv("LOGGER_ID"))

#❖ Get this value from @FallenxBot on Telegram by /id
OWNER_ID = int(getenv("OWNER_ID", "1679112664"))

#❖  Your heroku app name
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", None)

#❖  Get it from http://dashboard.heroku.com/account
HEROKU_API_KEY = getenv("HEROKU_API_KEY", None)

# You can paste your cookies to https://batbin.me, save them, and get a link to paste here
COOKIES = getenv("COOKIES", None)

# External APIs - Get these from their respective providers
GPT_API = getenv("GPT_API", None)

UPSTREAM_REPO = getenv(
    "UPSTREAM_REPO",
    "https://github.com/IamDuru/dshsbvibes",
)

UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "main")

GIT_TOKEN = getenv(
    "GIT_TOKEN", None
)  #❖ Fill this variable if your upstream repository is private

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/net_pro_max")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/+cXIPgHSuJnxiNjU1")

#❖ Set it in True if you want to leave your assistant after a certain amount of time. [Set time via AUTO_LEAVE_ASSISTANT_TIME]
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "True")

#❖ Time after which you're assistant account will leave chats automatically.
'''AUTO_LEAVE_ASSISTANT_TIME = int(
    getenv("ASSISTANT_LEAVE_TIME", 1800)
) ''' # Remember to give value in Seconds

#❖ Get this credentials from https://developer.spotify.com/dashboard
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "e319091f771445b18c029299505d5d4f")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "293c334a2861415197a697b2d11dd4de")


#❖ Maximum limit for fetching playlist's track from youtube, spotify, apple links.
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 2500))


#❖ Telegram audio and video file size limit (in bytes)
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))
#❖ Checkout https://www.gbmb.org/mb-to-bytes for converting mb to bytes

# Set it true if you want your bot to be private only [You'll need to allow CHAT_ID via /authorize command then only your bot will play music in that chat.]
PRIVATE_BOT_MODE = strtobool(getenv("PRIVATE_BOT_MODE", "False"))

# If you want your bot to setup the commands automatically in the bot's menu set it to true.
# Refer to https://i.postimg.cc/Bbg3LQTG/image.png
SET_CMDS = getenv("SET_CMDS", "False")

# Updated list with React emojis
D = ["😘", "👾", "🤝", "👀", "❤️‍🔥", "💘", "😍", "😇", "🕊️", "🐳", "🎉", "🏆", "🗿", "⚡", "💯", "👌", "🍾"]



#❖ Get your pyrogram v2 session from @StringFatherBot on Telegram
STRING_SESSIONS = parse_list(getenv("STRING_SESSIONS", ""))


BANNED_USERS = filters.user()
TEMP_DB_FOLDER = "tempdb"
LOG = 2
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}


START_IMG_URL = getenv(
    "START_IMG_URL", "https://envs.sh/nAT.jpg"
)
PING_IMG_URL = getenv(
    "PING_IMG_URL", "https://envs.sh/qEB.jpg"
)
PLAYLIST_IMG_URL = "https://envs.sh/nOh.jpg"
STATS_IMG_URL = "https://files.catbox.moe/h7gxwd.jpg"
TELEGRAM_AUDIO_URL = "https://telegra.ph/file/8234d704952738ebcda7f.jpg"
TELEGRAM_VIDEO_URL = "https://telegra.ph/file/8d02ff3bde400e465219a.jpg"
STREAM_IMG_URL = "https://telegra.ph/file/e24f4a5f695ec5576a8f3.jpg"
SOUNCLOUD_IMG_URL = "https://telegra.ph/file/7645d1e04021323c21db9.jpg"
YOUTUBE_IMG_URL = "https://telegra.ph/file/76d29aa31c40a7f026d7e.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://telegra.ph/file/b7758d4e1bc32aa9fb6ec.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://telegra.ph/file/60ed85638e00df10985db.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://telegra.ph/file/f4edfbd83ec3150284aae.jpg"



def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))


DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))


def seconds_to_time(seconds):
    minutes = seconds // 60
    remaining_seconds = seconds % 60
    return f"{minutes:02d}:{remaining_seconds:02d}"



if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        print(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )


if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        print(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
        )


if UPSTREAM_REPO:
    if not re.match("(?:http|https)://", UPSTREAM_REPO):
        print(
            "[ERROR] - Your UPSTREAM_REPO url is wrong. Please ensure that it starts with https://"
        )
        

if PING_IMG_URL:
    if PING_IMG_URL != "https://telegra.ph/file/91533956c91d0fd7c9f20.jpg":
        if not re.match("(?:http|https)://", PING_IMG_URL):
            print(
                "[ERROR] - Your PING_IMG_URL url is wrong. Please ensure that it starts with https://"
            )


if STATS_IMG_URL:
    if STATS_IMG_URL != "https://telegra.ph/file/4dd9e2c231eaf7c290404.jpg":
        if not re.match("(?:http|https)://", STATS_IMG_URL):
            print(
                "[ERROR] - Your STATS_IMG_URL url is wrong. Please ensure that it starts with https://"
            )


if TELEGRAM_AUDIO_URL:
    if TELEGRAM_AUDIO_URL != "https://telegra.ph/file/8234d704952738ebcda7f.jpg":
        if not re.match("(?:http|https)://", TELEGRAM_AUDIO_URL):
            print(
                "[ERROR] - Your TELEGRAM_AUDIO_URL url is wrong. Please ensure that it starts with https://"
            )


if STREAM_IMG_URL:
    if STREAM_IMG_URL != "https://telegra.ph/file/e24f4a5f695ec5576a8f3.jpg":
        if not re.match("(?:http|https)://", STREAM_IMG_URL):
            print(
                "[ERROR] - Your STREAM_IMG_URL url is wrong. Please ensure that it starts with https://"
            )


if SOUNCLOUD_IMG_URL:
    if SOUNCLOUD_IMG_URL != "https://telegra.ph/file/7645d1e04021323c21db9.jpg":
        if not re.match("(?:http|https)://", SOUNCLOUD_IMG_URL):
            print(
                "[ERROR] - Your SOUNCLOUD_IMG_URL url is wrong. Please ensure that it starts with https://"
            )


if YOUTUBE_IMG_URL:
    if YOUTUBE_IMG_URL != "https://telegra.ph/file/76d29aa31c40a7f026d7e.jpg":
        if not re.match("(?:http|https)://", YOUTUBE_IMG_URL):
            print(
                "[ERROR] - Your YOUTUBE_IMG_URL url is wrong. Please ensure that it starts with https://"
            )


if TELEGRAM_VIDEO_URL:
    if TELEGRAM_VIDEO_URL != "https://telegra.ph/file/8d02ff3bde400e465219a.jpg":
        if not re.match("(?:http|https)://", TELEGRAM_VIDEO_URL):
            print(
                "[ERROR] - Your TELEGRAM_VIDEO_URL url is wrong. Please ensure that it starts with https://"
            )
