import discord

from discord.ext import commands


class Fighting(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def fight_test(self, ctx):
        await ctx.send("Yep, it works")


def setup(client):
    client.add_cog(Fighting(client))