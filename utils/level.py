import os
import discord

def get_bot_level():
    return os.getenv("LEVEL")


def get_guild_ids():
    level = get_bot_level()

    if level == "DEBUG":
        return [427299383474782208]
    elif level == "PROD":
        return [600162735975694356]


def get_guild_objects():
    level = get_bot_level()
    guild_ids = get_guild_ids()

    guilds = []

    for guild_id in guild_ids:
        guilds.append(discord.Object(id=guild_id))

    return guilds


def get_application_id():
    level = get_bot_level()

    if level == "DEBUG":
        return 617964031801819166
    elif level == "PROD":
        return 840363188427161640


def get_poll_channel(client):
    level = get_bot_level()

    if level == "DEBUG":
        guild = client.get_guild(427299383474782208)
        return guild.get_channel(427299383474782210)
    elif level == "PROD":
        guild = client.get_guild(600162735975694356)
        return guild.get_channel(758528118209904671)