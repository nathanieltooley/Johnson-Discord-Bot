import svc.svc as svc
import discord
import os
import random

from discord.ext import commands, tasks


class Gamble(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        
    @commands.command()
    async def roll(self, ctx, sides=6):
        await ctx.send(f'{ctx.message.author.nick} rolled a {random.randrange(1, sides)}')

    # might be reworked, probably won't
    # could possibly use enums or something
    @commands.command()
    @commands.cooldown(1, 15, discord.ext.commands.BucketType.member)
    async def rps(self, ctx, member1: discord.member.Member, member2: discord.member.Member):
        rps_member1 = svc.Games.pickrps()
        rps_member2 = svc.Games.pickrps()
        rpstotal = rps_member1 + ' ' + rps_member2
        
        rpsdict = {
            "rock scissors": member1,
            "paper rock": member1,
            "scissors paper": member1,
            "scissors rock": member2,
            "rock paper": member2,
            "paper scissors": member2
        }

        await ctx.send(f'{member1.mention} got {rps_member1}, and {member2.mention} got {rps_member2}')

        if rps_member1 != rps_member2:
            winner = rpsdict[rpstotal]
            loser = None

            if winner == member1:  # find the loser using the winner
                loser = member2
            else:
                loser = member1

            winner_user = svc.Mongo.create_user(winner, ctx.guild)  # Create the user if there isn't one
            loser_user = svc.Mongo.create_user(loser, ctx.guild)

            winner_user = svc.Mongo.get_user(winner, ctx.guild)
            loser_user = svc.Mongo.get_user(loser, ctx.guild)

            vbuck_reward = int(loser_user.vbucks * (random.randrange(1, 10) / 100))  # Get between 0% and 10% of the loser's vbucks

            vbuck_limit = 1500
            if vbuck_reward > vbuck_limit:
                vbuck_reward = vbuck_limit

            svc.Mongo.income(winner, ctx.guild, vbuck_reward)
            svc.Mongo.income(loser, ctx.guild, (-vbuck_reward))
            
            await ctx.send(f"{winner.mention} won and got {vbuck_reward} from {loser.mention}")
        else:
            await ctx.send('Its a tie!')

    @commands.command()
    @commands.cooldown(1, 30, discord.ext.commands.BucketType.member)
    async def gamble(self, ctx, amount: int):
        user = svc.Mongo.get_user(ctx.author, ctx.guild)

        rand_selection = random.random()
        if (.1 <= rand_selection <= .7) and (amount < user.vbucks):
            new_amount = amount * ((random.randrange(1, 20)) / 10)
            int(new_amount)
            svc.Mongo.income(ctx.author, ctx.guild, new_amount)
            print_vbucks = new_amount + user.vbucks
            await ctx.send(f"You gained {new_amount}. You now have {print_vbucks}.")
        elif (rand_selection >= .7) and (amount < user.vbucks):
            new_amount = (-amount)
            svc.Mongo.income(ctx.author, ctx.guild, new_amount)
            print_vbucks = user.vbucks - amount
            await ctx.send(f"You lost {amount}. You have {print_vbucks} left.")
        else:
            await ctx.send("You can't gamble for more than you own, I can't program loans")


def setup(client):
    client.add_cog(Gamble(client))
