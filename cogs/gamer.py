import svc.svc as svc
import discord
import math

from random import randrange
from discord.ext import commands, tasks

class Gamer(commands.Cog):
    
    def __init__(self, client):
        self.client = client
    

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
            url="https://cdn.discordapp.com/attachments/610520962898853908/610539291701149709/AntiHa.jpg")
        embed.add_field(name="V-Bucks", value=f"{vbucks}")
        embed.add_field(name="Experience", value=f"{exp}/{int((math.pow((level + 1), 4)))}") # Find out how much exp is need for the next level (i.e 6/16)
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
            ctx.send("Transaction failed. You attempted to give away more than you own.")
        
        

def setup(client):
    client.add_cog(Gamer(client))