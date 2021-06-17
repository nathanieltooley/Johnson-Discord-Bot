import svc.utils as svc
import discord
import math
from enums import bot_enums

from random import randrange
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice


class Gamer(commands.Cog):

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name="view_gamer_stats",
                       description="View the stats of yourself or your fellow gamers",
                       options=[
                           create_option(
                               name="user",
                               description="The user you wish to view",
                               option_type=6,
                               required=True),
                       ],
                       guild_ids=bot_enums.Enums.GUILD_IDS.value)
    @svc.Checks.rude_name_check()
    async def view_gamer_stats(self, ctx, member: discord.Member):
        """This command allows a user to view his/her 'Gamer' stats, include their V-Buck amount, 
        their experience, and their current level."""

        svc.Mongo.create_user(member, ctx.guild)

        embed = self.create_user_stats(member, ctx.guild)

        await ctx.send(embed=embed)

    @staticmethod
    def create_user_stats(member: discord.Member, server: discord.Guild):

        svc.Mongo.create_user(member, server)
        user = svc.Mongo.get_user(member, server)

        username = ""

        if member.nick is None:
            username = member.display_name
        else:
            username = member.nick

        embed = discord.Embed(
            title=f"{username}'s Stats",
            description=f"All of {username}'s personal information",
            color=discord.Colour.blurple()
        )

        vbucks = user.vbucks
        exp = user.exp
        level = user.level

        embed.set_thumbnail(
            url=bot_enums.Enums.BOT_AVATAR_URL.value)
        embed.add_field(name="V-Bucks", value=f"{vbucks}")
        embed.add_field(name="Experience",
                        value=f"{exp}/{int((math.pow((level + 1), 4)))}")
        embed.add_field(name="Level", value=f"{level}")

        return embed

    @cog_ext.cog_slash(name="view_slur_stats",
                       description="View the slur stats of yourself or your fellow gamers",
                       options=[
                           create_option(
                               name="user",
                               description="The user you wish to view",
                               option_type=6,
                               required=True),
                       ],
                       guild_ids=bot_enums.Enums.GUILD_IDS.value)
    @svc.Checks.rude_name_check()
    async def slur_check(self, ctx, member: discord.Member):
        user = svc.Mongo.get_user(member, member.guild)
        if not user.slur_count:
            await ctx.send("This person is clean!")
            return

        embed = discord.Embed(title=f"{member.nick}'s Racist Resume",
                              description=f"How racist is {member.nick}",
                              color=svc.Color.random_color())

        for k, v in user.slur_count.items():
            embed.add_field(name=k, value=v, inline=False)

        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="view_leader_boards",
                       description="See who's on top!",
                       options=[
                           create_option(
                               name="sortby",
                               description="The user you wish to view",
                               option_type=3,
                               required=True,
                               choices=[create_choice(value="vbucks", name="V-Bucks"),
                                        create_choice(value="xp", name="XP")]
                           ),
                       ],
                       guild_ids=bot_enums.Enums.GUILD_IDS.value)
    @svc.Checks.rude_name_check()
    async def view_gamer_boards(self, ctx, field="vbucks"):
        embed_title = None
        field = field.lower()

        if field == "vbucks":
            embed_title = "Richest"
        elif field == "exp" or field == "experience" or field == "xp":
            embed_title = "Most Experienced"
            field = "exp"
        else:
            await ctx.send(f"ERROR: {field} is not a vaild field")
            return

        results = svc.Mongo.get_leaderboard_results(field, ctx.guild)
        results = enumerate(results, 1)

        embed = discord.Embed(
            title=f"{embed_title} Gamers",
            description=f"The {embed_title} Gamers! Can you match them?",
            color=discord.Colour.from_rgb(randrange(0, 256), randrange(0, 256), randrange(0, 256))
        )

        embed.set_thumbnail(url=bot_enums.Enums.BOT_AVATAR_URL.value)

        if field == "vbucks":
            for count, gamer in results:
                embed.add_field(name=f"{gamer.name}", value=f"{gamer.vbucks} V-Bucks", inline=False)
        else:
            for count, gamer in results:
                embed.add_field(name=f"{gamer.name}", value=f"Level {gamer.level}: {gamer.exp} EXP", inline=False)
        await ctx.send(embed=embed)

    @cog_ext.cog_slash(name="give_money",
                       description="Gift your hard earned cash to the less fortunate",
                       options=[
                           create_option(
                               name="reciever",
                               description="The user you wish to view",
                               option_type=6,
                               required=True
                           ),
                           create_option(
                               name="money",
                               description="The amount of money to gift",
                               option_type=4,
                               required=True
                           )
                       ],
                       guild_ids=bot_enums.Enums.GUILD_IDS.value)
    @svc.Checks.rude_name_check()
    async def give_money(self, ctx, reciever: discord.Member, money):
        if ctx.author == reciever:
            await ctx.send("You can't send yourself money")
            return

        transact = svc.Mongo.transact(ctx.author, reciever, ctx.guild, money)

        if not transact:
            await ctx.send("Transaction failed. You attempted to give away more than you own.")
        elif transact:
            await ctx.send(f"Transaction of {money} V-Bucks Successful!")

    @cog_ext.cog_slash(name="xp_exchange",
                       description="Pay your way to knowledge and experience!",
                       options=[
                           create_option(
                               name="payment",
                               description="The user you wish to view",
                               option_type=4,
                               required=True,
                           ),
                       ],
                       guild_ids=bot_enums.Enums.GUILD_IDS.value)
    @svc.Checks.rude_name_check()
    async def exp_exchange(self, ctx, vbuck_payment: int):
        conversion_ratio = .1

        user = svc.Mongo.get_user(ctx.author, ctx.guild)
        current_vbucks = user.vbucks

        if vbuck_payment > current_vbucks:
            await ctx.send("You do not have enough vbucks")
            return

        added_exp = vbuck_payment * conversion_ratio
        new_exp = user.exp + added_exp

        svc.Mongo.income(ctx.author, ctx.guild, -vbuck_payment)
        svc.Mongo.update_exp(ctx.author, ctx.guild, new_exp)

        await ctx.send(f"{ctx.author.mention} You gained {added_exp} XP. You have {new_exp}")


def setup(client):
    client.add_cog(Gamer(client))
