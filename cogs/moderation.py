import discord
from asyncio import sleep

from discord.ext import commands

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
        mute_role = None
        check_mute = discord.utils.find(lambda x: x.name == "Muted", ctx.guild.roles)

        if check_mute:
            mute_role = check_mute
        else:
            mute_perms = discord.Permissions.text()
            mute_perms.send_messages = False
            mute_role = await ctx.guild.create_role(name="Muted", permissions=mute_perms, color=discord.Color.red(),
                                                    reason="Missing Mute Role")

        utils.Logging.log(__name__, f"print: {mute_role}")
        user_roles = member.roles

        await member.add_roles(mute_role, reason=f"{reason}; for {seconds} second(s)")

        await ctx.send(f"{member.mention} muted!")

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
