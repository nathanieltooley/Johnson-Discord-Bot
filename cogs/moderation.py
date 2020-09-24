import discord

from discord.ext import commands, tasks

class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def test_mod(self, ctx):
        # Test
        # Testy tset
        await ctx.send("Yep it works")

def setup(client):
    client.add_cog(Moderation(client))