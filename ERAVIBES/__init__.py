from ERAVIBES.core.bot import Era
from ERAVIBES.core.dir import dirr
from ERAVIBES.core.git import git
from ERAVIBES.core.userbot import Userbot
from ERAVIBES.misc import dbb, heroku

from .logging import LOGGER

dirr()
git()
dbb()
heroku()

app = Era()
userbot = Userbot()


from .platforms import *

Apple = AppleAPI()
Carbon = CarbonAPI()
Savan = Savan()
SoundCloud = SoundAPI()
Spotify = SpotifyAPI()
Resso = RessoAPI()
Telegram = TeleAPI()
YouTube = YouTubeAPI()
HELPABLE = {}
