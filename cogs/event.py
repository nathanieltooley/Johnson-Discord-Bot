import svc.svc as svc
import discord
import os
import itertools

from discord.ext import commands, tasks

class Event(commands.Cog):
    
    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        lmessage = message.content
        qmessage = lmessage.lower()
        adl_list = ["nigger", 'nigga', 'negro', 'chink', 'niglet', 'nigtard'] # Open for expansion
        if message.author == self.client.user or message.author.bot: # bot check
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
        svc.income(message.author, message.guild, 5)
        level_up = svc.exp_check(message.author, message.guild, 1, 10)

        if level_up:
            await message.channel.send(level_up)

        # await check_level(message.author)

        # await self.client.process_commands(message)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
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
            await ctx.send(f"{error}")
            #await ctx.send("An error has occurred")
def setup(client):
    client.add_cog(Event(client))