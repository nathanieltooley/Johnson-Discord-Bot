from discord_slash import SlashContext

import svc.utils as svc
import discord

from discord.ext import commands, tasks
from discord_slash.error import CheckFailure


class Event(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        user_slur = False

        if message.author == self.client.user or message.author.bot:  # bot check
            await self.bot_checks(message)
            return

        user_slur = self.slur_checks(message)
        await Event.determine_response(user_slur, message)

        if user_slur is None:
            await Event.add_to_stats(message)

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
            await ctx.send(f"{error}")

        svc.Logging.error("command_error", error)

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx: SlashContext, ex):
        if isinstance(ex, CheckFailure):
            await ctx.send("You cannot use this command. Try changing your name")

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
    def create_check_message(message: discord.Message):
        return message.content.lower()

    @staticmethod
    async def bot_checks(message):
        c_message = Event.create_check_message(message)

        for adl in svc.Checks.slur_list:
            if adl in c_message:
                await message.delete()
                break

    @staticmethod
    def slur_checks(message):
        c_message = Event.create_check_message(message)

        for slur in svc.Checks.slur_list:
            if slur in c_message and not c_message.startswith("https://tenor.com/"):  # Ignore gif links
                return slur

        return None

    @staticmethod
    def record_said_slur(message, slur):
        svc.Mongo.add_to_slur_count(message.author, message.guild, 1, slur)
        svc.Logging.log(__name__, f"{message.author.name} said slur: {slur}")

    @staticmethod
    async def respond_to_slur(message):
        await message.channel.send(
            f"Hey {message.author.mention}! That's racist, and racism is no good :disappointed:")
        await message.delete()
        svc.Logging.log(__name__, f"Message deleted, from {message.author.name}:{message.content}")

    @staticmethod
    async def determine_response(said_slur, message):
        c_message = Event.create_check_message(message)

        if said_slur is not None:
            Event.record_said_slur(message, said_slur)
            await Event.respond_to_slur(message)

        if said_slur is None:
            await Event.keyword_responses(message)

            if 'im ' in c_message:
                await Event.im_check(message, "im ")

            if "i'm " in c_message:
                await Event.im_check(message, "i'm ")

            if 'i‘m ' in c_message:
                await Event.im_check(message, "i‘m ")

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

        # Not Found
        if check_index < 0:
            return False

        before_space = q_message[pre_check_index].isspace()
        is_beginning = pre_check_index < 0
        nothing_after = False
        after_space = False

        # See if there is anything after the word
        try:
            after_space = q_message[check_index + len(check)].isspace()
        except IndexError:
            nothing_after = True

        if (before_space or is_beginning) and (nothing_after or after_space):
            return True
        else:
            return False

    @staticmethod
    async def keyword_responses(message):
        if Event.message_check(message, 'fortnite'):
            await message.channel.send("We like Fortnite! We like Fortnite! We like Fortnite! We like Fortnite!")

        if Event.message_check(message, 'based'):
            await message.channel.send("Based on what?")

        if Event.message_check(message, "poggers"):
            await message.channel.send(
                f"{message.author.mention} https://tenor.com/view/anime-poggers-anime-poggers-anime-gif-18290524")

        if Event.message_check(message, "smile"):
            await message.channel.send(
                "https://media.discordapp.net/attachments/694702814915723295/798703969803042867/Johnson_Smile.png?width=468&height=468"
            )

        if Event.message_check(message, "thanks") or Event.message_check(message, "thank you"):
            await message.channel.send("you're welcome :)")

        if Event.message_check(message, "flanksteak"):
            await message.channel.send("Why did you say that?")

    @staticmethod
    async def add_to_stats(message):
        svc.Mongo.create_user(message.author, message.guild)
        svc.Mongo.income(message.author, message.guild, 50)
        level_up = svc.Mongo.exp_check(message.author, message.guild, 1, 10)

        if level_up:
            await message.channel.send(level_up)


def setup(client):
    client.add_cog(Event(client))
