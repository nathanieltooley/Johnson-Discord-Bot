import svc.utils as svc
import sys
import traceback
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
            if adl in q_message and not q_message.startswith("https://tenor.com/"):  # Ignore gif links
                obsc_check = True
                svc.Mongo.add_to_slur_count(message.author, message.guild, 1, adl)
                svc.Logging.log(__name__, f"{message.author.name} said slur: {adl}")

        if obsc_check:
            await message.channel.send(
                f"Hey {message.author.mention}! That's racist, and racism is no good :disappointed:")
            await message.delete()
            svc.Logging.log(__name__, f"Message deleted, from f{message.author.name}:{message.content}")

        if not obsc_check:

            if self.message_check(message, 'fortnite'):
                await message.channel.send("We like Fortnite! We like Fortnite! We like Fortnite! We like Fortnite!")

            if self.message_check(message, 'gay'):
                await message.channel.send(f"No Homo {message.author.mention}")

            if self.message_check(message, 'minecraft'):
                await message.channel.send(f"I prefer Roblox {message.author.mention}")

            if self.message_check(message, 'the game'):
                await message.channel.send("I lost the Game")

            if self.message_check(message, 'based'):
                await message.channel.send("Based on what?")

            if self.message_check(message, "poggers"):
                await message.channel.send(
                    f"{message.author.mention} https://tenor.com/view/anime-poggers-anime-poggers-anime-gif-18290524")

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
            svc.Logging.error("command_error", error)
            await ctx.send(f"{error}")

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

    @staticmethod
    def message_check(message, check):
        q_message = message.content.lower()

        check_index = q_message.find(check)
        pre_check_index = check_index - 1

        before_space = q_message[pre_check_index].isspace()
        is_beginning = pre_check_index < 0
        nothing_after = False
        after_space = False

        # Not Found
        if check_index < 0:
            return False

        # See if there is anything after the word
        try:
            q_message[check_index + len(check)]
            after_space = q_message[check_index + len(check)].isspace()
        except IndexError:
            nothing_after = True

        if (before_space or is_beginning) and (nothing_after or after_space):
            return True
        else:
            return False


def setup(client):
    client.add_cog(Event(client))
