import discord
import svc.svc as svc

from discord.ext import commands, tasks

class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def update_vbucks(self, ctx, member: discord.Member, money: int):
        svc.update_vbucks(member, ctx.guild, money)
        await ctx.send(f"{member.mention}'s V-Buck amount has been updated to {money}")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def update_exp(self, ctx, member: discord.Member, exp: int):
        check = svc.update_exp(member, ctx.guild, exp)
        if check == None:
            await ctx.send(f"{member.mention}'s XP has been set to {exp}")
        else:
            await ctx.send(f"{member.mention}'s XP has been set to {exp} and their level has changed to {check}")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def spawn_item(self, ctx, member: discord.Member, ref_id):
        pass


def setup(client):
    client.add_cog(Admin(client))