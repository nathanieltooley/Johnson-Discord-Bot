import discord

from discord.ext import commands, tasks
from enums.bot_enums import Enums as bot_enums
from utils import messaging, level, jlogging, checks, mongo
from data_models.kwr import KeywordResponse

class Event(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.keyword_responses = KeywordResponse.read_keyword_responses()

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        user_slur = False

        if type(message.channel) == discord.channel.DMChannel and message.author != self.client.user:
            await self.process_dm(message)
            return

        if message.author == self.client.user or message.author.bot:  # bot check
            await self.bot_checks(message)
            return

        user_slur = self.slur_checks(message)
        await self.determine_response(user_slur, message)

        # if no slur has been said, reward the user for messaging (gold and xp)
        if user_slur is None:
            await Event.add_to_stats(message)

    @commands.Cog.listener()
    async def on_command_error(self, interaction: discord.Interaction, error):
        if isinstance(error, commands.MissingPermissions):
            await messaging.respond(interaction, "You do not have permission to use this command")
        elif isinstance(error, commands.MissingRequiredArgument):
            await messaging.respond(interaction, "Please give all required parameters")
        elif isinstance(error, commands.CommandOnCooldown):
            await messaging.respond(interaction, "Command on cooldown. Please wait")
        elif isinstance(error, commands.UserInputError):
            await messaging.respond(interaction, "You seemed to have messed up, try again")
        else:
            if level.get_bot_level() == "DEBUG":
                raise error
            else:
                await messaging.respond_embed(interaction, title="ERROR", code_block=f"{error}", color=discord.Color.red())

        jlogging.error("command_error", error)

    @commands.Cog.listener()
    async def on_member_update(self, ctx, member):

        if member.bot:
            return

        Event.stroke_check(member)

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        id_check = 249997264553115648

        if member.id == id_check and after.channel is not None:
            self.remind_wyatt.start()
            jlogging.time_log(__name__, "Sending reminders to wyatt!")
        
        if member.id == id_check and after.channel is None:
            self.remind_wyatt.stop() 
            jlogging.time_log(__name__, "Ending reminders to wyatt!")

    @tasks.loop(minutes=7)
    async def remind_wyatt(self):
        wyatt_id = 249997264553115648

        wyatt_user = self.client.get_user(wyatt_id)

        await wyatt_user.send("Wyatt! Uncross your legs and sit up straight!")

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        user_slur = self.slur_checks(after)
        await self.determine_response(user_slur, after)

        if user_slur is None:
            await Event.add_to_stats(after)

    @staticmethod
    def create_check_message(message: discord.Message):
        return message.content.lower()

    @staticmethod
    async def bot_checks(message):
        c_message = Event.create_check_message(message)

        for adl in checks.slur_list:
            if adl in c_message:
                await message.delete()
                break

    @staticmethod
    def slur_checks(message):
        c_message = Event.create_check_message(message)

        for slur in checks.slur_list:
            if slur in c_message and not c_message.startswith("https://tenor.com/"):  # Ignore gif links
                return slur

        return None

    @staticmethod
    def record_said_slur(message, slur):
        mongo.add_to_slur_count(message.author, message.guild, 1, slur)
        jlogging.log(__name__, f"{message.author.name} said slur: {slur}")

    @staticmethod
    async def respond_to_slur(message):
        message_author = message.author.name
        message_content = message.content

        await message.channel.send(
            f"Hey {message.author.mention}! That's racist, and racism is no good :disappointed:")
        await message.delete()
        jlogging.log(__name__, f"Message deleted, from {message_author}:{message_content}")

    async def determine_response(self, said_slur, message):

        if said_slur is not None:
            Event.record_said_slur(message, said_slur)
            await Event.respond_to_slur(message)

        if said_slur is None:
            await self.check_keyword_responses(message)
            await Event.im_responses(message)

    @staticmethod
    async def dad_check(message, check):

        lowercase_message = message.content.lower()

        im_index = lowercase_message.find(check)
        pre_im_index = im_index - 1

        period_index = lowercase_message.find(".")

        if period_index < im_index:
            period_index = -1

        # End at the period if there is one
        if period_index > 0:
            dad_message = lowercase_message[(im_index + 2):period_index]
            join = f"Hi{dad_message}, I'm Johnson!"
            await message.channel.send(join)
        # Split the message in two if there is no space
        # We check if the previous index is -1 or a space so that we dont respond to words that end in "im" like him
        elif pre_im_index < 0 or lowercase_message[pre_im_index].isspace():
            split = lowercase_message.split(check, 1)
            join = f"Hi {split[1]}, I'm Johnson!"
            await message.channel.send(join)

    async def check_keyword_responses(self, message):
        for kw in self.keyword_responses:
            if kw.message_trigger_response(self.create_check_message(message)):
                await message.channel.send(kw.choose_response())

    @staticmethod
    async def add_to_stats(message):
        mongo.create_user(message.author, message.guild)
        mongo.income(message.author, message.guild, 50)
        level_up = mongo.exp_check(message.author, message.guild, 1, 10)

        if level_up:
            await message.channel.send(level_up)

    async def process_dm(self, message: discord.Message):
        target_guild = None
        target_channel = None

        if level.get_bot_level() == "DEBUG":
            target_guild = self.client.get_guild(bot_enums.TEST_SERVER_ID.value)
            target_channel = target_guild.get_channel(842246555205763092)
        else:
            target_guild = self.client.get_guild(bot_enums.JOHNSON_ID.value)
            target_channel = target_guild.get_channel(758528118209904671)

        if target_guild.get_member(message.author.id):
            await target_channel.send(f"{message.author.mention} says: {message.content}")
            await Event.send_admin_req_dm(message)

    @staticmethod
    async def send_admin_req_dm(message):
        await message.channel.send("Message received. Forwarding to Johnson HQ.")

    @staticmethod
    def stroke_check(member):
        spotify = None

        for act in member.activities:
            if act.name == "Spotify":
                spotify = act

        if spotify is None:
            return

        if spotify.artist == "The Strokes":
            mongo.add_to_stroke_count(member, member.guild, 1)

            """dm_embed = discord.Embed(title="Nice Musical Taste Bro!",
                                     description=f"{spotify.title} - {spotify.album}",
                                     color=discord.Color.gold())

            dm_embed.set_thumbnail(url=bot_enums.BotString.BOT_AVATAR_URL.value)
            dm_embed.set_image(url=spotify.album_cover_url)

            await member.send(f"Nice Taste {member.display_name}", embed=dm_embed)"""

    @staticmethod
    async def im_responses(message):
        c_message = Event.create_check_message(message)
        im_variations = ["im ", "i'm ", "i‘m ", "i’m "]

        for im in im_variations:
            if im in c_message:
                await Event.dad_check(message, im)

async def setup(client):
    await client.add_cog(Event(client), guilds=level.get_guild_objects())
