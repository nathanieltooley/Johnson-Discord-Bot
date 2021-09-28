import discord
import svc.utils as utils
import enums.bot_enums as enums


from discord_slash import cog_ext, SlashContext
from discord.ext import commands, tasks
from discord_slash.utils.manage_commands import create_option, create_choice, create_permission

from cogs.event import Event


class Admin(commands.Cog):

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(
        name="update_vbucks",
        description="Update a user's V-Bucks",
        options=[
            create_option(
                name="user",
                description="User to update",
                option_type=6,
                required=True
            ),
            create_option(
                name="money",
                description="New V-Bucks Amount",
                option_type=4,
                required=True
            )
        ],
        guild_ids=utils.Level.get_guild_ids()
    )
    @utils.Checks.check_is_owner()
    async def update_vbucks(self, ctx, member: discord.Member, money: int):
        utils.Mongo.update_vbucks(member, ctx.guild, money)
        await ctx.send(f"{member.mention}'s V-Buck amount has been updated to {money}")

    @cog_ext.cog_slash(
        name="update_xp",
        description="Update a user's XP",
        options=[
            create_option(
                name="user",
                description="User to update",
                option_type=6,
                required=True
            ),
            create_option(
                name="xp",
                description="New XP Amount",
                option_type=4,
                required=True
            )
        ],
        guild_ids=utils.Level.get_guild_ids()
    )
    @utils.Checks.check_is_owner()
    async def update_exp(self, ctx, member: discord.Member, exp: int):
        check = utils.Mongo.update_exp(member, ctx.guild, exp)
        if check is None:
            await ctx.send(f"{member.mention}'s XP has been set to {exp}")
        else:
            await ctx.send(f"{member.mention}'s XP has been set to {exp} and their level has changed to {check}")

    @cog_ext.cog_slash(
        name="set_user_level",
        description="Set a user's level and update their XP",
        options=[
            create_option(
                name="user",
                description="User to update",
                option_type=6,
                required=True
            ),
            create_option(
                name="level",
                description="New User Level",
                option_type=4,
                required=True
            )
        ],
        guild_ids=utils.Level.get_guild_ids()
    )
    @utils.Checks.check_is_owner()
    async def set_user_level(self, ctx, member: discord.Member, level: int):

        required_exp = pow(level, 4)
        utils.Mongo.update_exp(member, ctx.guild, required_exp)

        await ctx.send(f"{member.mention}'s level is now {level}. XP is {required_exp}")

    @cog_ext.cog_slash(
        name="create_account",
        description="Create an database entry for a user",
        options=[
            create_option(
                name="user",
                description="User to create entry for",
                option_type=6,
                required=True
            ),
        ],
        guild_ids=utils.Level.get_guild_ids()
    )
    @utils.Checks.check_is_owner()
    async def create_account(self, ctx, member: discord.Member):
        utils.Mongo.create_user(member, ctx.guild)
        await ctx.send(f"{member.display_name}'s account was created.")

    @cog_ext.cog_slash(
        name="talk",
        description="Make Johnson Bot talk in any channel you want!",
        options=[
            create_option(
                name="message",
                description="Message to Send",
                option_type=3,
                required=True
            ),
            create_option(
                name="channel",
                description="Channel to send it to",
                option_type=7,
                required=True
            )
        ],
        guild_ids=utils.Level.get_guild_ids()
    )
    async def talk_ch(self, ctx: SlashContext, message, channel: discord.abc.GuildChannel):
        # im gonna keep this in cuz i think the message is funny
        if ctx.author.id != enums.Enums.OWNER_ID.value:
            await ctx.send("nope")
            return

        if isinstance(channel, discord.TextChannel):
            await channel.send(message)
            await ctx.send(content="Sent", hidden=True)
        else:
            await ctx.send("Not a text channel")

    @cog_ext.cog_slash(
        name="change_currency_name",
        description="Don't want to trade V-Bucks? No worries, just change the name!",
        options=[
            create_option(
                name="currencyname",
                description="New Name",
                option_type=3,
                required=True
            )
        ],
        guild_ids=utils.Level.get_guild_ids()
    )
    @utils.Checks.check_is_owner()
    async def change_currency_name(self, ctx: SlashContext, c_name):
        utils.Mongo.set_server_currency_name(ctx.guild.id, c_name)
        await ctx.send(f"Name has changed to: {c_name}")


def setup(client):
    client.add_cog(Admin(client))
