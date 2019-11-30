import discord
import random
import sys
import os
import math
import itertools
import svc.svc as svc
from configparser import ConfigParser

from discord.ext import commands, tasks
from itertools import cycle
from svc.mongo_setup import global_init

client = commands.Bot(command_prefix=".")

@client.event
async def on_ready():
    global_init();
    print("Johnson spittin' straight fax!")
    change_status.start()
    await client.change_presence(activity=discord.Game(name="For more info, use .helpme!"))


@client.event
async def on_message(message):
    lmessage = message.content
    qmessage = lmessage.lower()
    adl_list = ["nigger", 'nigga', 'negro', 'chink', 'niglet', 'nigtard'] # Open for expansion
    if message.author == client.user or message.author.bot: # bot check
        return

    for adl in adl_list:
            if adl in qmessage:
                await message.channel.send(f"Hey {message.author.mention}! That's racist, and racism is no good")
                await message.delete()
                break

    if 'fortnite' in qmessage:
        await message.channel.send("We like Fortnite! We like Fortnite! We like Fortnite! We like Fortnite!")
        

    if 'gay' in qmessage:
        await message.channel.send(f"No Homo {message.author.mention}")
        

    if 'minecraft' in qmessage:
        await message.channel.send(f"I prefer Roblox {message.author.mention}")
        

    if 'the game' in qmessage:
        await message.channel.send("I lost the Game")
        

    # ignore this convoluted mess, just don't touch it
    if 'im ' in qmessage:
        imInd = qmessage.find("im")  # start index
        stopInd = qmessage.find(".")  # end index

        if stopInd == -1 or (stopInd < imInd):
            split = qmessage.split('im')
            join = f"Hi{split[1]}, I'm Johnson!"
            print("no period")
            await message.channel.send(join)
        else:
            dadmessage = qmessage[(imInd + 2):stopInd]
            print(stopInd)
            print(dadmessage)
            join = f"Hi{dadmessage}, I'm Johnson!"
            await message.channel.send(join)
    elif "i'm " in qmessage:
        imInd = qmessage.find("i'm")  # start index
        stopInd = qmessage.find(".")  # end index

        if stopInd == -1 or (stopInd < imInd):
            split = qmessage.split("i'm")
            join = f"Hi{split[1]}, I'm Johnson!"
            print("no period")
            await message.channel.send(join)
        else:
            dadmessage = qmessage[(imInd + 2):stopInd]
            print(stopInd)
            print(dadmessage)
            join = f"Hi{dadmessage}, I'm Johnson!"
            await message.channel.send(join)

    svc.create_user(message.author, message.guild)
    svc.income(message.author, 5)
    level_up = svc.exp_check(message.author, 1, 10)

    if level_up:
        await message.channel.send(level_up)

    # await check_level(message.author)

    await client.process_commands(message)

@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to use this command")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please give all required parameters")
    elif isinstance(error, commands.CommandOnCooldown):
        await ctx.send("Command on cooldown. Please wait")
    elif isinstance(error, commands.UserInputError):
        await ctx.send("You seemed to have messed up, try again")
    else:
        print(error)
        await ctx.send(f"Error {type(error)} has occured: {error}")
        #await ctx.send("An error has occurred")

@client.command()
async def ping(ctx):
    await ctx.send("Pong!")

@client.command()
async def roll(ctx, sides=6):
    await ctx.send(f'{ctx.message.author.nick} rolled a {random.randrange(1, sides)}')

# might be reworked, probably won't
# could possibly use enums or something
@client.command()
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

@client.command(aliases=['helpme'])
async def support(ctx):
    """Custom help message"""
    await ctx.send('--Made by Nathaniel--\n'
                   'Commands: \n'
                   '.ping: Pong!\n'
                   '.roll [number of sides]: Rolls a die, accepts a number; default is 6 \n'
                   '.rps [Player 1] [Player 2]: Shoot! There is a monetary reward for those who win\n'
                   ".viewgamerstats [id]: View a player's statistics.\n"
                   ".gamble [amount]: Gamble to your hearts content. It's Vegas baby!\n"
                   "I'm also a part-time Dad now as well!(as per Noah's request)\n"
                   "I'm also now controlled by the ADL\n"
                   "Source code available at https://github.com/applememes69420/Johnson-Discord-Bot")
    print(type(ctx))

@client.command(aliases=["viewgamerstats"])
async def gamerViewStats(ctx):
    """This command allows a user to view his/her 'Gamer' stats, include their V-Buck amount, 
    their experience, and their current level."""

    user = svc.get_user(ctx.author)

    embed = discord.Embed(
        title="{0}'s Stats".format(ctx.message.author.nick),
        description="All of {0}'s personal information".format(ctx.message.author.nick),
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


@client.command()
@commands.cooldown(1, 30, discord.ext.commands.BucketType.member)
async def gamble(ctx, amount: int):
    user = svc.get_user(ctx.author)

    randselection = random.random()
    if (randselection >= .1 and randselection <= .8) and (amount < user.vbucks):
        new_amount = amount * ((random.randrange(1, 20)) / 10)
        int(new_amount)
        svc.income(ctx.author, new_amount)
        print_vbucks = new_amount + user.vbucks
        await ctx.send(f"You gained {(new_amount)}. You now have {print_vbucks}.")
    elif (randselection >= .9) and (amount < user.vbucks):
        new_amount = (-amount)
        svc.income(ctx.author, new_amount)
        print_vbucks = user.vbucks - amount
        await ctx.send(f"You lost {amount}. You have {print_vbucks} left.")
    else:
        await ctx.send("You can't gamble for more than you own, I can't program loans")

status = cycle(["For more info, use .helpme!",
                "Minecraft",
                "Who uses this bot anyways?",
                "Made by Nathaniel",
                "Fortnite",
                "Vibe Check",
                "SwowS"])


@tasks.loop(seconds=45)
async def change_status():
    #new_stat = random.choice(status)
    await client.change_presence(activity=discord.Game(next(status)))


client.run(os.environ.get('TOKEN'))