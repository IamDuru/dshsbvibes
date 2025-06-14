import asyncio
import os

from pyrogram import idle
from pytgcalls.exceptions import NoActiveGroupCall

import config
from config import BANNED_USERS
from ERAVIBES import HELPABLE, LOGGER, app, userbot
from ERAVIBES.core.call import ERA
from ERAVIBES.misc import sudo
from ERAVIBES.utils.database import get_banned_users, get_gbanned

logger = LOGGER("ERAVIBES")
loop = asyncio.get_event_loop()


async def init():
    if not any([config.STRING1, config.STRING2, config.STRING3, config.STRING4, config.STRING5]):
        logger.error("✦ No Assistant client variables defined, exiting...")
        return
    if not config.SPOTIFY_CLIENT_ID and not config.SPOTIFY_CLIENT_SECRET:
        logger.warning(
            "No Spotify Vars defined. Your bot won't be able to play spotify queries."
        )
    try:
        users = await get_gbanned()
        for user_id in users:
            BANNED_USERS.add(user_id)
        users = await get_banned_users()
        for user_id in users:
            BANNED_USERS.add(user_id)
    except Exception:        pass
    await sudo()
    await app.start()
    # Load plugins
    app.plugins_dir = "ERAVIBES/plugins"
    modules = app.load_plugins()
    for mod in modules:
        if mod and hasattr(mod, "__MODULE__") and mod.__MODULE__:
            if hasattr(mod, "__HELP__") and mod.__HELP__:
                HELPABLE[mod.__MODULE__.lower()] = mod

    if config.EXTRA_PLUGINS:
        if os.path.exists("xtraplugins"):
            result = await app.run_shell_command(["git", "-C", "xtraplugins", "pull"])
            if result["returncode"] != 0:
                logger.error(
                    f"Error pulling updates for extra plugins: {result['stderr']}"
                )
                exit()
        else:
            result = await app.run_shell_command(
                ["git", "clone", config.EXTRA_PLUGINS_REPO, "xtraplugins"]
            )
            if result["returncode"] != 0:
                logger.error(f"Error cloning extra plugins: {result['stderr']}")
                exit()

        req = os.path.join("xtraplugins", "requirements.txt")
        if os.path.exists(req):
            result = await app.run_shell_command(
                ["uv", "pip", "install", "--system", "-r", req]
            )
            if result["returncode"] != 0:                logger.error(f"Error installing requirements: {result['stderr']}")        # Load extra plugins
        app.plugins_dir = "xtraplugins"
        extra_modules = app.load_plugins()
        for mod in extra_modules:
            if mod and hasattr(mod, "__MODULE__") and mod.__MODULE__:
                if hasattr(mod, "__HELP__") and mod.__HELP__:
                    HELPABLE[mod.__MODULE__.lower()] = mod

    await userbot.start()
    await ERA.start()
    LOGGER("ERAVIBES").info("✦ Successfully Imported Modules...💞")
    try:
        await ERA.stream_call(
            "http://docs.evostream.com/sample_content/assets/sintel1m720p.mp4"
        )
    except NoActiveGroupCall:
        LOGGER("ERAVIBES").error(
            "✦ Please turn on the videochat of your log group\channel.\n\n✦ Stopping Bot...💣"
        )
        exit()

    await ERA.decorators()
    LOGGER("ERAVIBES").info("✦ Created By ➥ The Dvis...🐝")
    await idle()
    await app.stop()
    await userbot.stop()
    await ERA.stop()


def main():
    loop.run_until_complete(init())
    LOGGER("ERAVIBES").info("❖ Stopping ERA Music Bot...💌")


if __name__ == "__main__":
    main()
