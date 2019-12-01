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
        rpsMember1 = svc.pickrps()
        rpsMember2 = svc.pickrps()
        rpstotal = rpsMember1 + ' ' + rpsMember2
        
        rpsdict = {
            "rock scissors": member1,
            "paper rock": member1,
            "scissors paper": member1,
            "scissors rock": member2,
            "rock paper": member2,
            "paper scissors": member2
        }

        await ctx.send(f'{member1.mention} got {rpsMember1}, and {member2.mention} got {rpsMember2}')

        if rpsMember1 != rpsMember2:
            winner = rpsdict[rpstotal]
            loser = None

            if winner == member1: # find the loser using the winner
                loser = member2
            else:
                loser = member1

            winnerUser = svc.create_user(winner, ctx.guild) # Create the user if there isn't one
            loserUser = svc.create_user(loser, ctx.guild)

            winnerUser = svc.get_user(winner, ctx.guild) 
            loserUser = svc.get_user(loser, ctx.guild)

            vbuckReward = int(loserUser.vbucks * (random.randrange(1, 10) / 100)) # Get between 0% and 10% of the loser's vbucks

            vbuckLimit = 1500
            if vbuckReward > vbuckLimit:
                vbuckReward = vbuckLimit

            svc.income(winner, ctx.guild, vbuckReward)
            svc.income(loser, ctx.guild, (-vbuckReward))
            
            await ctx.send(f"{winner.mention} won and got {vbuckReward} from {loser.mention}")
            # await ctx.send(f'{rpsdict.get(rpstotal)}')
        else:
            await ctx.send('Its a tie!')

    @commands.command()
    @commands.cooldown(1, 30, discord.ext.commands.BucketType.member)
    async def gamble(self, ctx, amount: int):
        user = svc.get_user(ctx.author, ctx.guild)

        randselection = random.random()
        if (randselection >= .1 and randselection <= .7) and (amount < user.vbucks):
            new_amount = amount * ((random.randrange(1, 20)) / 10)
            int(new_amount)
            svc.income(ctx.author, ctx.guild, new_amount)
            print_vbucks = new_amount + user.vbucks
            await ctx.send(f"You gained {(new_amount)}. You now have {print_vbucks}.")
        elif (randselection >= .7) and (amount < user.vbucks):
            new_amount = (-amount)
            svc.income(ctx.author, ctx.guild, new_amount)
            print_vbucks = user.vbucks - amount
            await ctx.send(f"You lost {amount}. You have {print_vbucks} left.")
        else:
            await ctx.send("You can't gamble for more than you own, I can't program loans")



def setup(client):
    client.add_cog(Gamble(client))