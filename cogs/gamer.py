import svc.svc as svc
import discord
import math
import asyncio
from enums import bot_enums

from random import randrange
from discord.ext import commands, tasks


class Gamer(commands.Cog):

    def __init__(self, client):
        self.client = client
        # self.transactions = {}

    @commands.command(aliases=["viewgamerstats"])
    async def view_gamer_stats(self, ctx):
        """This command allows a user to view his/her 'Gamer' stats, include their V-Buck amount, 
        their experience, and their current level."""

        svc.create_user(ctx.author, ctx.guild)
        user = svc.get_user(ctx.author, ctx.guild)

        embed = discord.Embed(
            title=f"{ctx.message.author.nick}'s Stats",
            description=f"All of {ctx.message.author.nick}'s personal information",
            color=discord.Colour.blurple()
        )

        vbucks = user.vbucks
        exp = user.exp
        level = user.level

        embed.set_thumbnail(
            url=bot_enums.BotString.BOT_AVATAR_URL.value)
        embed.add_field(name="V-Bucks", value=f"{vbucks}")
        embed.add_field(name="Experience",
                        value=f"{exp}/{int((math.pow((level + 1), 4)))}")
        embed.add_field(name="Level", value=f"{level}")

        await ctx.send(embed=embed)

    @commands.command()
    async def view_gamer_boards(self, ctx, field="vbucks"):
        embed_title = None
        field = field.lower()

        if field == "vbucks":
            embed_title = "Richest"
        elif field == "exp" or "exprience":
            embed_title = "Most Experienced"
            field = "exp"
        else:
            await ctx.send(f"ERROR: {field} is not a vaild field")
            return

        results = svc.get_leaderboard_results(field, ctx.guild)
        results = enumerate(results, 1)

        embed = discord.Embed(
            title=f"{embed_title} Gamers",
            description=f"The {embed_title} Gamers! Can you match them?",
            color=discord.Colour.from_rgb(randrange(0, 256), randrange(0, 256), randrange(0, 256))
        )

        if field == "vbucks":
            for count, gamer in results:
                embed.add_field(name=f"{gamer.name}", value=f"{gamer.vbucks} V-Bucks", inline=False)
        else:
            for count, gamer in results:
                embed.add_field(name=f"{gamer.name}", value=f"Level {gamer.level}: {gamer.exp} EXP", inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def give_money(self, ctx, reciever: discord.Member, money):
        if ctx.author == reciever:
            await ctx.send("You can't send yourself money")
            return

        transact = svc.transact(ctx.author, reciever, ctx.guild, money)

        if not transact:
            await ctx.send("Transaction failed. You attempted to give away more than you own.")
        elif transact:
            await ctx.send(f"Transaction of {money} V-Bucks Successful!")

    @commands.command()
    async def give_gift(self, ctx, reciever: discord.Member, item_id):
        if ctx.author == reciever:
            await ctx.send("You can't gift yourself this item!")
            return

        if not svc.get_item_from_inventory(member=ctx.author, server=ctx.guild, item_id=item_id):
            await ctx.send("You do not have this item.")
            return

        svc.delete_item(ctx.author, ctx.guild, item_id)
        last_owner = ctx.author
        item = svc.give_item_to_user(member=reciever, item_id=item_id, server=ctx.guild, last_owner=ctx.author)

        await ctx.send(f"{item[0]} was given to {reciever.display_name}!")

    @commands.command()
    async def get_user_inventory(self, ctx, member: discord.Member = None):
        if member is None:
            item = svc.get_user_inventory(ctx.author, ctx.guild)
            name = ctx.author.nick
        else:
            item = svc.get_user_inventory(member, ctx.guild)
            if member.bot:
                name = member.name
            else:
                name = member.nick

        count = len(item)

        embed = discord.Embed(
            title=f"{name}'s Inventory",
            description=f"The inventory of {name}. Total Item Count {count}",
            color=discord.Colour.dark_purple()
        )

        if isinstance(item, list):
            item = enumerate(item, 1)
            for count, i in item:
                embed.add_field(name=f"{i.name}", value=f"{i.value} V-Bucks", inline=False)

            await ctx.send(embed=embed)
        else:
            await ctx.send(item)


def setup(client):
    client.add_cog(Gamer(client))
