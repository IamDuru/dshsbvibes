from pyrogram import Client, errors
from pyrogram.enums import ChatMemberStatus, ParseMode
from pyrogram.types import (
    BotCommand,
    BotCommandScopeAllChatAdministrators,
    BotCommandScopeAllGroupChats,
    BotCommandScopeAllPrivateChats,
)

import config

from ..logging import LOGGER

class Era(Client):
    def __init__(self):
        LOGGER(__name__).info(f"❖ Starting Bot...♥︎")
        super().__init__(
            name="ERAVIBES",
            api_id=config.API_ID,
            api_hash=config.API_HASH,
            bot_token=config.BOT_TOKEN,
            in_memory=True,
            parse_mode=ParseMode.HTML,
            max_concurrent_transmissions=7,
        )

    async def start(self):
        await super().start()
        self.id = self.me.id
        self.name = self.me.first_name + " " + (self.me.last_name or "")
        self.username = self.me.username
        self.mention = self.me.mention

        try:
            await self.send_message(
                chat_id=config.LOGGER_ID,
                text=f"❖<b> {self.mention} ʙᴏᴛ sᴛᴀʀᴛᴇᴅ</b>\n\n● ɪᴅ ➥ <code>{self.id}</code>\n● ɴᴀᴍᴇ ➥ {self.name}\n● ᴜsᴇʀɴᴀᴍᴇ ➥ @{self.username}",
            )
        except (errors.ChannelInvalid, errors.PeerIdInvalid):
            LOGGER(__name__).error(
                "❖ Bot has failed to access the log group/channel. Make sure that you have added your bot to your log group/channel."
            )
            exit()
        except Exception as ex:
            LOGGER(__name__).error(
                f"❖ Bot has failed to access the log group/channel.\n● Reason ➥ {type(ex).__name__}."
            )
            exit()

        # Setting commands
        if config.SET_CMDS == str(True):
            try:
                await self.set_bot_commands(
                    commands=[
                        BotCommand("start", "❍ 𝗺𝗮𝗸𝗲 𝘁𝗵𝗲 𝗯𝗼𝘁 𝘀𝘁𝗮𝗿𝘁"),
                        BotCommand("help", "❍ 𝗴𝗲𝘁 𝘁𝗵𝗲 𝗵𝗲𝗹𝗽 𝗺𝗲𝗻𝘂"),
                        BotCommand("ping", "❍ 𝗰𝗵𝗲𝗰𝗸 𝗶𝗳 𝘁𝗵𝗲 𝗯𝗼𝘁 𝗶𝘀 𝗮𝗹𝗶𝘃𝗲 𝗼𝗿 𝗱𝗲𝗮𝗱"),
                    ],
                    scope=BotCommandScopeAllPrivateChats(),
                )
                await self.set_bot_commands(
                    commands=[
                        BotCommand("start", "❍ 𝘀𝘁𝗮𝗿𝘁 𝘁𝗵𝗲 𝗯𝗼𝘁"),
                        BotCommand("ping", "❍ 𝗰𝗵𝗲𝗰𝗸 𝘁𝗵𝗲 𝗽𝗶𝗻𝗴"),
                        BotCommand("help", "❍ 𝗴𝗲𝘁 𝗵𝗲𝗹𝗽"),
                        BotCommand("play", "❍ 𝘀𝘁𝗮𝗿𝘁 𝗽𝗹𝗮𝘆𝗶𝗻𝗴 𝗿𝗲𝘃𝘂𝗲𝘀𝘁𝗲𝗱 𝘀𝗼𝗻𝗴"),
                        BotCommand("vplay", "❍ 𝗽𝗹𝗮𝘆 𝘃𝗶𝗱𝗲𝗼 𝗮𝗹𝗼𝗻𝗴 𝘄𝗶𝘁𝗵 𝗺𝘂𝘀𝗶𝗰"),
                        BotCommand("song", "❍ 𝗱𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝘁𝗵𝗲 𝗿𝗲𝘃𝘂𝗲𝘀𝘁𝗲𝗱 𝘀𝗼𝗻𝗴"),
                        BotCommand("yt", "❍ 𝘆𝗼𝘂𝘁𝘂𝗯𝗲 𝘀𝗲𝗮𝗿𝗰𝗵"),
                    ],
                    scope=BotCommandScopeAllGroupChats(),
                )
                await self.set_bot_commands(
                    commands=[
                        BotCommand("start", "❍ 𝘀𝘁𝗮𝗿𝘁 𝘁𝗵𝗲 𝗯𝗼𝘁"),
                        BotCommand("ping", "❍ 𝗰𝗵𝗲𝗰𝗸 𝘁𝗵𝗲 𝗽𝗶𝗻𝗴"),
                        BotCommand("help", "❍ 𝗴𝗲𝘁 𝗵𝗲𝗹𝗽"),
                        BotCommand("cancel", "❍ 𝗰𝗮𝗻𝗰𝗲𝗹 𝘁𝗵𝗲 𝘁𝗮𝗴𝗴𝗶𝗻𝗴"),
                        BotCommand("settings", "❍ 𝗴𝗲𝘁 𝘁𝗵𝗲 𝘀𝗲𝘁𝘁𝗶𝗻𝗴𝘀"),
                        BotCommand("reload", "❍ 𝗿𝗲𝗹𝗼𝗮𝗱 𝘁𝗵𝗲 𝗯𝗼𝘁"),
                        BotCommand("play", "❍ 𝗽𝗹𝗮𝘆 𝘁𝗵𝗲 𝗿𝗲𝘃𝘂𝗲𝘀𝘁𝗲𝗱 𝘀𝗼𝗻𝗴"),
                        BotCommand("vplay", "❍ 𝗽𝗹𝗮𝘆 𝘃𝗶𝗱𝗲𝗼 𝗮𝗹𝗼𝗻𝗴 𝘄𝗶𝘁𝗵 𝗺𝘂𝘀𝗶𝗰"),
                        BotCommand("pause", "❍ 𝗽𝗮𝘂𝘀𝗲 𝘁𝗵𝗲 𝗰𝘂𝗿𝗿𝗲𝗻𝘁 𝘀𝗼𝗻𝗴"),
                        BotCommand("resume", "❍ 𝗿𝗲𝘀𝘂𝗺𝗲 𝘁𝗵𝗲 𝗽𝗮𝘂𝘀𝗲𝗱 𝘀𝗼𝗻𝗴"),
                        BotCommand("end", "❍ 𝗲𝗺𝗽𝘁𝘆 𝘁𝗵𝗲 𝘀𝘂𝗲𝘂𝗲"),
                        BotCommand("skip", "❍ 𝘀𝗸𝗶𝗽 𝘁𝗵𝗲 𝗰𝘂𝗿𝗿𝗲𝗻𝘁 𝘀𝗼𝗻𝗴"),
                        BotCommand("queue", "❍ 𝗰𝗵𝗲𝗰𝗸 𝘁𝗵𝗲 𝘀𝘂𝗲𝘂𝗲 𝗼𝗳 𝘀𝗼𝗻𝗴𝘀"),
                        BotCommand("song", "❍ 𝗱𝗼𝘄𝗻𝗹𝗼𝗮𝗱 𝘁𝗵𝗲 𝗿𝗲𝘃𝘂𝗲𝘀𝘁𝗲𝗱 𝘀𝗼𝗻𝗴"),
                        BotCommand("yt", "❍ 𝘆𝗼𝘂𝘁𝘂𝗯𝗲 𝘀𝗲𝗮𝗿𝗰𝗵"),
                    ],
                    scope=BotCommandScopeAllChatAdministrators(),
                )

            except Exception as e:
                LOGGER(__name__).error(f"❖ Failed to set bot commands: {e}")

        a = await self.get_chat_member(config.LOGGER_ID, self.id)
        if a.status != ChatMemberStatus.ADMINISTRATOR:
            LOGGER(__name__).error(
                "❖ Please promote your bot as an admin in your log group/channel."
            )
            exit()
        LOGGER(__name__).info(f"❖ Music Bot Started as ➥ {self.name} ...♥︎")

    async def stop(self):
        await super().stop()
