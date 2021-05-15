import discord
import svc.utils as utils
import enums.bot_enums as enums

from discord.ext import commands, tasks

from cogs.event import Event


class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.has_permissions(administrator=True)
    @utils.Checks.check_is_owner()
    @commands.command()
    async def update_vbucks(self, ctx, member: discord.Member, money: int):
        utils.Mongo.update_vbucks(member, ctx.guild, money)
        await ctx.send(f"{member.mention}'s V-Buck amount has been updated to {money}")

    @commands.has_permissions(administrator=True)
    @utils.Checks.check_is_owner()
    @commands.command()
    async def update_exp(self, ctx, member: discord.Member, exp: int):
        check = utils.Mongo.update_exp(member, ctx.guild, exp)
        if check is None:
            await ctx.send(f"{member.mention}'s XP has been set to {exp}")
        else:
            await ctx.send(f"{member.mention}'s XP has been set to {exp} and their level has changed to {check}")

    @commands.has_permissions(administrator=True)
    @utils.Checks.check_is_owner()
    @commands.command()
    async def set_user_level(self, ctx, member: discord.Member, level: int):

        required_exp = pow(level, 4)
        utils.Mongo.update_exp(member, ctx.guild, required_exp)

        await ctx.send(f"{member.mention}'s level is now {level}. XP is {required_exp}")

    @commands.has_permissions(administrator=True)
    @utils.Checks.check_is_owner()
    @commands.command()
    async def spawn_item(self, ctx, member: discord.Member, ref_id):
        item, value = utils.Mongo.give_item_to_user(member, ref_id, ctx.guild)
        await ctx.send(f"Given User Item: {item}, of Value: {value} V-Bucks")

    @commands.has_permissions(administrator=True)
    @utils.Checks.check_is_owner()
    @commands.command()
    async def create_account(self, ctx, member: discord.Member):
        utils.Mongo.create_user(member, ctx.guild)
        await ctx.send(f"{member.display_name}'s account was created.")

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def talk(self, ctx, message):
        # im gonna keep this in cuz i think the message is funny
        if ctx.author.id != enums.Enums.OWNER_ID.value:
            await ctx.send("nope")
            return

        # Hard Coded, use talk_ch other wise
        channel = discord.utils.find(lambda x: x.id == 649780790468542516, ctx.guild.text_channels)
        await channel.send(message)

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def talk_ch(self, ctx, message, channel_name: str):
        # im gonna keep this in cuz i think the message is funny
        if ctx.author.id != enums.Enums.OWNER_ID.value:
            await ctx.send("nope")
            return

        channel = discord.utils.find(lambda x: channel_name.lower() in x.name.lower(), ctx.guild.text_channels)
        await channel.send(message)


def setup(client):
    client.add_cog(Admin(client))
