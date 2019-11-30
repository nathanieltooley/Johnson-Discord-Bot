import svc.svc as svc
import discord
import os
import random

from discord.ext import commands, tasks

class Gamble(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        
@commands.command()
async def roll(ctx, sides=6):
    await ctx.send(f'{ctx.message.author.nick} rolled a {random.randrange(1, sides)}')

# might be reworked, probably won't
# could possibly use enums or something
@commands.command()
@commands.cooldown(1, 15, discord.ext.commands.BucketType.member)
async def rps(ctx, member1: discord.member.Member, member2: discord.member.Member):
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

        winnerUser = svc.get_user(winner) 
        loserUser = svc.get_user(loser)

        vbuckReward = int(loserUser.vbucks * (random.randrange(1, 10) / 100)) # Get between 0% and 10% of the loser's vbucks

        vbuckLimit = 1500
        if vbuckReward > vbuckLimit:
            vbuckReward = vbuckLimit

        svc.income(winner, vbuckReward)
        svc.income(loser, (-vbuckReward))
        
        await ctx.send(f"{winner.mention} won and got {vbuckReward} from {loser.mention}")
        # await ctx.send(f'{rpsdict.get(rpstotal)}')
    else:
        await ctx.send('Its a tie!')


def setup(client):
    client.add_cog(Gamble(client))