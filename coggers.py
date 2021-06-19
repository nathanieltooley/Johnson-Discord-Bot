import os
import svc.utils as utils
import discord

from discord_slash import SlashCommand, SlashContext
from discord.ext import commands, tasks

client = commands.Bot(command_prefix=".")
slash = SlashCommand(client, sync_commands=True, sync_on_cog_reload=True)
       
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f'cogs.{filename[:-3]}') # Cut off .py
        utils.Logging.log("coggers", f"{filename} loaded")

client.run(os.environ.get("TOKEN"))

