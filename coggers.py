import os
import svc.utils as utils
import discord

from discord_slash import SlashCommand, SlashContext
from discord.ext import commands, tasks

intents = discord.Intents.default()
intents.members = True

client = commands.Bot(intents=intents, command_prefix=".")
slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True)

if __name__ == '__main__':
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            client.load_extension(f'cogs.{filename[:-3]}')  # Cut off .py
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

    client.run(os.environ.get("TOKEN"))



