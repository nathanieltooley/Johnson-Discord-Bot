import os

import utils.utils as utils
import discord

from discord.ext import commands, tasks

from enums.bot_enums import Enums as bot_enums
from utils.mongo_setup import global_init


class JohnsonBot(commands.Bot):

    def __init__(self, **options):
        intents = discord.Intents.default()
        intents.presences = True
        intents.members = True
        intents.message_content = True

        super().__init__(
            command_prefix=".",
            intents=intents,
            application_id=utils.Level.get_application_id(),
            **options
        )

    async def setup_hook(self):
        enabled_cogs = ["setup.py", "music.py", "gamer.py", "gamble.py", "event.py"]
        utils.Logging.log(__name__, "Johnson Bot is Loading!")

        for filename in os.listdir("./cogs"):
            if filename.endswith(".py") and filename in enabled_cogs:
                await self.load_extension(f'cogs.{filename[:-3]}')  # Cut off .py
                utils.Logging.log("coggers", f"{filename} loaded")

        environ_vars = ["DISCORD_HOST", "LEVEL", "SPOTIPY_CLIENT_ID", "SPOTIPY_CLIENT_SECRET",
                        "SPOTIPY_REDIRECT_URI", "TOKEN"]

        ev_not_set = False
        for var in environ_vars:
            if os.getenv(var, None) is None:
                utils.Logging.error(__name__, f"Environment Variable, {var}, is not set")
                ev_not_set = True

        if ev_not_set:
            exit()

    async def on_ready(self):
        global_init()

        def create_command_string(client: commands.Bot):
            command_string = ""
            for command in client.tree.get_commands(guild=utils.Level.get_guild_objects()[0]):
                command_string = command_string + f"{command.name}, "

            return command_string

        await self.change_presence(activity=discord.Game(name="For more info, use .helpme!"))
        utils.Logging.log(__name__, f"Johnson Level: {utils.Level.get_bot_level()}")
        utils.Logging.log(__name__,
                          f"Loaded Server Currency Name: {utils.Mongo.get_server_currency_name(bot_enums.TEST_SERVER_ID.value)}")
        utils.Logging.log("coggers", f"Loaded Commands: {create_command_string(self)}")

    async def close(self) -> None:
        await super().close()


def main():
    bot = JohnsonBot()
    bot.run(os.getenv("TOKEN"))


if __name__ == '__main__':
    main()





