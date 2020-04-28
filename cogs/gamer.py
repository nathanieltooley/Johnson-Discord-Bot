import svc.svc as svc
import discord
import math
import asyncio
from enums import bot_enums

from random import randrange
from discord.ext import commands, tasks

# Cancelled indefinitely

"""class Transaction:
    items = []
    trade_money = {}

    def __init__(self, members: tuple):
        self.member1 = members[0]
        self.member2 = members[1]

    def add_item(self, item):
        self.items.append(item)

    def remove_item(self, item):
        self.items.remove(item)

    def add_money(self, money, owner):

        money = abs(money)

        if not (self.trade_money.has_key(f"{owner.id}")):
            values = {f"{owner.id}": money}
            self.trade_money.update(values)
        else:
            current_money = self.trade_money.get(f"{owner.id}")
            values = {f"{owner.id}": (money + current_money)}
            self.trade_money.popitem(f"{owner.id}")
            self.trade_money.update(values)

    def remove_money(self, money, owner):

        money = abs(money)

        if not (self.trade_money.has_key(f"{owner.id}")):
            values = {f"{owner.id}": money}
            self.trade_money.update(values)
        else:
            current_money = self.trade_money.get(f"{owner.id}")
            values = {f"{owner.id}": (current_money - money)}
            self.trade_money.popitem(f"{owner.id}")
            self.trade_money.update(values)

    def clear_trade_money(self, user):
        x = None  # anonymous variable

        try:
            x = self.trade_money.popitem(f"{user.id}")
        except KeyError:
            return None
        else:
            return x

    def return_item_embed(self):
        embed = discord.Embed(title="Current Trade Details",
                              description="The current trade details between",
                              color=discord.Color.magenta)

        for i in self.items:
            name: discord.Member = i.owner
            embed.add_field(name=name, value=svc.get_base_item(i.ref_id))

        return embed
"""


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
            url=bot_enums.Bot.BOT_AVATAR_URL.value)
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

    @commands.command()
    async def trade(self, ctx, member: discord.Member):
        # use wait_for thingy a lot, gonna have to accept a lot user input babeyyuyyyyy
        await ctx.send("wait_for Test: Reply with 'test'")

        # Cancelled indefinitely

        """def check(message):
            return ctx.author == message.author and message.content == "test"

        try:
            msg = await self.client.wait_for("message", timeout=30.0, check=check)
        except asyncio.TimeoutError:
            await ctx.send("Check failed.")
            return
        else:

            await ctx.send("Check Passed!")
            trans_id = ctx.author.id + member.id
            # trans_instance = Transaction(members=(ctx.author, member))

            # t_update = {f"{trans_id}": trans_instance}
            # transaction = self.transactions.update(t_update)

            # print(self.transactions)"""


def setup(client):
    client.add_cog(Gamer(client))
