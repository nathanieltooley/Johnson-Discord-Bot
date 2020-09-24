import discord
from asyncio import sleep

from discord.ext import commands, tasks

import svc.utils as utils


class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def test_mod(self, ctx):
        await ctx.send("Yep it works")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def mute(self, ctx, member: discord.Member, seconds=0, reason="Just shut up"):
        await ctx.send(f"{member.mention} muted!")

        user_roles = member.roles
        mute_role = ctx.guild.get_role(758732926333747210)

        await member.add_roles(mute_role, reason=f"{reason}; for {seconds} seconds")

        # Skip the first role (@everyone)
        for i in range(1, len(user_roles)):
            await member.remove_roles(user_roles[i])

        if seconds < 0:
            seconds = 0

        await sleep(seconds)
        await ctx.send(f"{member.mention} unmuted!")
        await member.remove_roles(mute_role, reason="Mute expired")

        # Skip the first role
        for i in range(1, len(user_roles)):
            await member.add_roles(user_roles[i])


def setup(client):
    client.add_cog(Moderation(client))
