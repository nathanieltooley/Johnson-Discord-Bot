import svc.svc as svc
import discord
import os
import itertools
from enums import bot_enums

from discord.ext import commands, tasks


class Event(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message):
        l_message = message.content
        q_message = l_message.lower()

        obsc_check = False

        adl_list = ["nigger", 'nigga', 'negro', 'chink', 'niglet', 'nigtard', 'gook', 'kike',
                    'faggot']  # Open for expansion
        if message.author == self.client.user or message.author.bot:  # bot check
            return

        for adl in adl_list:
            if adl in q_message:
                obsc_check = True
                svc.Mongo.add_to_slur_count(message.author, message.guild, 1, adl)

        if obsc_check:
            await message.channel.send(
                f"Hey {message.author.mention}! That's racist, and racism is no good :disappointed:")
            await message.delete()

        if not obsc_check:

            if 'fortnite' in q_message:
                await message.channel.send("We like Fortnite! We like Fortnite! We like Fortnite! We like Fortnite!")

            if 'gay' in q_message:
                await message.channel.send(f"No Homo {message.author.mention}")

            if 'minecraft' in q_message:
                await message.channel.send(f"I prefer Roblox {message.author.mention}")

            if 'the game' in q_message:
                await message.channel.send("I lost the Game")

            if 'based' in q_message:
                await message.channel.send("Based on what?")

            if 'im ' in q_message:
                await self.im_check(message, "im ")

            if "i'm " in q_message:
                await self.im_check(message, "i'm ")

        svc.Mongo.create_user(message.author, message.guild)
        svc.Mongo.income(message.author, message.guild, 5)
        level_up = svc.Mongo.exp_check(message.author, message.guild, 1, 10)

        if level_up:
            await message.channel.send(level_up)

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
            # await ctx.send("An error has occurred")

    @commands.Cog.listener()
    async def on_member_update(self, ctx, member):

        if member.bot:
            return

        spotify = None

        for act in member.activities:
            if act.name == "Spotify":
                spotify = act

        if spotify is None:
            return

        if spotify.artist == "The Strokes":
            svc.Mongo.add_to_stroke_count(member, member.guild, 1)

            """dm_embed = discord.Embed(title="Nice Musical Taste Bro!",
                                     description=f"{spotify.title} - {spotify.album}",
                                     color=discord.Color.gold())

            dm_embed.set_thumbnail(url=bot_enums.BotString.BOT_AVATAR_URL.value)
            dm_embed.set_image(url=spotify.album_cover_url)

            await member.send(f"Nice Taste {member.display_name}", embed=dm_embed)"""

    @staticmethod
    async def im_check(message, check):

        q_message = message.content.lower()

        im_index = q_message.find(check)
        pre_im_index = im_index - 1

        period_index = q_message.find(".")

        if period_index < im_index:
            period_index = -1

        if period_index > 0:
            dad_message = q_message[(im_index + 2):period_index]
            join = f"Hi{dad_message}, I'm Johnson!"
            await message.channel.send(join)
        elif pre_im_index < 0 or q_message[pre_im_index].isspace():
            split = q_message.split(check, 1)
            join = f"Hi {split[1]}, I'm Johnson!"
            await message.channel.send(join)


def setup(client):
    client.add_cog(Event(client))
