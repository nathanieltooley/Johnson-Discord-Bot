import svc.svc as svc
import discord
import os

from discord.ext import commands, tasks

client = commands.Bot(command_prefix = ".")


@client.command()
async def load(ctx, extension):
    try:
        client.load_extension(f"cogs.{extension}")
        await ctx.send(f"{extension} has been loaded")
    except:
        print(Exception)
        await ctx.send("An error has occured")

@client.command()
async def unload(ctx, extension):
    try:
        client.unload_extension(f"cogs.{extension}")
        await ctx.send(f"{extension} has been unloaded")
    except:
        print(Exception)
        await ctx.send("An error has occured")

@client.command()
async def reload(ctx, extension):
    try:
        client.unload_extension(f"cogs.{extension}")
        client.load_extension(f"cogs.{extension}")
        await ctx.send(f"{extension} has been reloaded")
    except:
        print(Exception)
        await ctx.send("An error has occured")
    
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f'cogs.{filename[:-3]}')
        print(f"{filename} loaded") # Cut off .py


client.run(os.environ.get("TOKEN"))