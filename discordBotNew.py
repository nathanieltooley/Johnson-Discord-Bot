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

def pickrps():  # only used for rps command
    choices = ['rock', 'paper', 'scissors']
    return random.choice(choices)


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
                await message.channel.send("Hey {0}! That's racist, and racism is no good".format(message.author.mention))
                await message.delete()
                break

    if 'fortnite' in qmessage:
        await message.channel.send("We like Fortnite! We like Fortnite! We like Fortnite! We like Fortnite!")
        

    if 'gay' in qmessage:
        await message.channel.send("No Homo {0}".format(message.author.mention))
        

    if 'minecraft' in qmessage:
        await message.channel.send("I prefer Roblox {}".format(message.author.mention))
        

    if 'the game' in qmessage:
        await message.channel.send("I lost the Game")
        

    # ignore this convoluted mess
    if 'im ' in qmessage:
        imind = qmessage.find("im")  # start index
        stopind = qmessage.find(".")  # end index

        if stopind == -1 or (stopind < imind):
            split = qmessage.split('im')
            join = "Hi{0}, I'm Johnson!".format(split[1])
            print("no period")
            await message.channel.send(join)
        else:
            dadmessage = qmessage[(imind + 2):stopind]
            print(stopind)
            print(dadmessage)
            join = "Hi{0}, I'm Johnson!".format(dadmessage)
            await message.channel.send(join)
    elif "i'm " in qmessage:
        imind = qmessage.find("i'm")  # start index
        stopind = qmessage.find(".")  # end index

        if stopind == -1 or (stopind < imind):
            split = qmessage.split("i'm")
            join = "Hi{0}, I'm Johnson!".format(split[1])
            print("no period")
            await message.channel.send(join)
        else:
            dadmessage = qmessage[(imind + 2):stopind]
            print(stopind)
            print(dadmessage)
            join = "Hi{0}, I'm Johnson!".format(dadmessage)
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
    await ctx.send('{0} rolled a {1}'.format(ctx.message.author.nick, random.randrange(1, sides)))

# might be reworked, probably won't
# could possibly use enums or something
@client.command()
async def rps(ctx, member1: discord.member.Member, member2: discord.member.Member):
    rpsmember1 = pickrps()
    rpsmember2 = pickrps()
    rpstotal = rpsmember1 + ' ' + rpsmember2
    rpsdict = {
        "rock scissors": '{0} wins!'.format(member1.nick),
        "paper rock": '{0} wins!'.format(member1.nick),
        "scissors paper": '{0} wins!'.format(member1.nick),
        "scissors rock": '{0} wins!'.format(member2.nick),
        "rock paper": '{0} wins!'.format(member2.nick),
        "paper scissors": '{0} wins!'.format(member2.nick)
    }

    await ctx.send('{0} got {1}, and {2} got {3}'.format(member1.mention, rpsmember1, member2.mention, rpsmember2))

    if rpsmember1 != rpsmember2:
        await ctx.send('{0}'.format(rpsdict.get(rpstotal)))
    else:
        await ctx.send('Its a tie!')

@client.command(aliases=['helpme'])
async def support(ctx):
    await ctx.send('--Made by Nathaniel--\n'
                   'Commands: \n'
                   '.ping: Pong!\n'
                   '.roll [number of sides]: Rolls a die, accepts a number; default is 6 \n'
                   '.rps [Player 1] [Player 2]: Shoot!\n'
                   ".viewgamerstats [id]: View a player's statistics.\n"
                   ".gamble [amount]: Gamble to your hearts content. It's Vegas baby!\n"
                   "I'm also a part-time Dad now as well!(as per Noah's request)\n"
                   "I'm also now controlled by the ADL")
    print(type(ctx))

@client.command(aliases=["viewgamerstats"])
async def gamerViewStats(ctx):
    user = svc.get_user(ctx.author)
    # await ctx.send("{0}'s Stats: {1}".format(ctx.message.author.mention, json.dumps(data['Gamers'][gamer], indent=2)))

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
    embed.add_field(name="Experience", value=f"{exp}/{int((math.pow((level + 1), 4)))}")
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
        await ctx.send(f"You got {(new_amount + amount)}. You now have {print_vbucks}.")

    elif (randselection > 9 and randselection <= 10) and (amount < user.vbucks):
        new_amount = (-amount)
        svc.income(ctx.author, new_amount)
        print_vbucks = user.vbucks - amount
        await ctx.send("You lost {0}. You have {1} left.".format(amount, print_vbucks))
    else:
        await ctx.send("You can't gamble for more than you own, I can't program loans")

status = cycle(["For more info, use .helpme!",
                "Minecraft",
                "Who uses this bot anyways?",
                "Made by Nathaniel",
                "Fortnite",
                "Vibe Check",
                "SwowS"])


@tasks.loop(seconds=60)
async def change_status():
    #new_stat = random.choice(status)
    await client.change_presence(activity=discord.Game(next(status)))

client.run(os.environ['TOKEN'])