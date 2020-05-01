import svc.svc as svc
import discord
import os
import itertools
import pymongo


from discord.ext import commands, tasks

client = commands.Bot(command_prefix=".")


@commands.has_permissions(administrator=True)
@client.command()
async def load(ctx, extension):
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} has been loaded")


@commands.has_permissions(administrator=True)
@client.command()
async def unload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} has been unloaded")


@commands.has_permissions(administrator=True)
@client.command()
async def reload(ctx, extension):
    client.unload_extension(f"cogs.{extension}")
    client.load_extension(f"cogs.{extension}")
    await ctx.send(f"{extension} has been reloaded")
       
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        client.load_extension(f'cogs.{filename[:-3]}')
        print(f"{filename} loaded")  # Cut off .py


client.run(os.environ.get("TOKEN"))

