from ERAVIBES.core.bot import ERA
from ERAVIBES.core.dir import dirr
from ERAVIBES.core.git import git
from ERAVIBES.core.userbot import Userbot
from ERAVIBES.misc import dbb, heroku

from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = ERA()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
Saavn = SaavnAPI()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
HELPABLE = {}
