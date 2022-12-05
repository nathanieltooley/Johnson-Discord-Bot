import discord
import math

from enums import bot_enums
from random import randrange
from discord.ext import commands
from discord import app_commands


class Gamer(commands.Cog):

    def __init__(self, client):
        self.client = client

    @app_commands.command(
        name="view_gamer_stats",
        description="View the stats of yourself or your fellow gamers"
    )
    @app_commands.describe(
        user="The user you wish to view"
    )
    @utils.Checks.rude_name_check()
    async def view_gamer_stats(self, interaction: discord.Interaction, user: discord.Member):
        """This command allows a user to view his/her 'Gamer' stats, include their V-Buck amount, 
        their experience, and their current level."""

        utils.Mongo.create_user(user, interaction.guild)

        embed = self.create_user_stats(user, interaction.guild)

        await utils.MessageHelpers.respond(interaction, "", embed=embed)

    @staticmethod
    def create_user_stats(member: discord.Member, server: discord.Guild):

        utils.Mongo.create_user(member, server)
        user = utils.Mongo.get_user(member, server)

        username = ""

        if member.nick is None:
            username = member.display_name
        else:
            username = member.nick

        embed = utils.EmbedHelpers.create_message_embed(title=f"{username}'s Stats",
                                                        message=f"All of {username}'s personal information")

        vbucks = user.vbucks
        exp = user.exp
        level = user.level

        server_currency = utils.Mongo.get_server_currency_name(server.id)

        embed.set_thumbnail(
            url=bot_enums.Enums.BOT_AVATAR_URL.value)
        embed.add_field(name=f"{server_currency}", value=f"{vbucks}")
        embed.add_field(name="Experience",
                        value=f"{exp}/{int((math.pow((level + 1), 4)))}")
        embed.add_field(name="Level", value=f"{level}")

        return embed

    @app_commands.command(
        name="view_slur_stats",
        description="View the slur stats of yourself or your fellow gamers"
    )
    @app_commands.describe(
        user="The user you wish to view"
    )
    @utils.Checks.rude_name_check()
    async def slur_check(self, interaction: discord.Interaction, user: discord.Member):
        user = utils.Mongo.get_user(user, user.guild)
        if not user.slur_count:
            await utils.MessageHelpers.respond(interaction, "This person is clean!")
            return

        embed = utils.EmbedHelpers.create_message_embed(title=f"{user.nick}'s Racist Resume",
                                                        message=f"How racist is {user.nick}")

        for k, v in user.slur_count.items():
            embed.add_field(name=k, value=v, inline=False)

        await utils.MessageHelpers.respond(interaction, "", embed=embed)

    @app_commands.command(
        name="view_leader_boards",
        description="See who's on Top!"
    )
    @app_commands.describe(sort="What to sort the leaderboards by.")
    @app_commands.choices(sort=[
        app_commands.Choice(name="Currency", value="money"),
        app_commands.Choice(name="XP", value="xp")
    ])
    @utils.Checks.rude_name_check()
    async def view_gamer_boards(self, interaction: discord.Interaction, sort: str = "money"):
        embed_title = None
        sort = sort.lower()

        server_currency = utils.Mongo.get_server_currency_name(interaction.guild.id)

        if sort == "money":
            embed_title = "Richest"
        elif sort == "exp" or sort == "experience" or sort == "xp":
            embed_title = "Most Experienced"
            sort = "exp"
        else:
            await utils.EmbedHelpers.respond_embed(interaction, code_block=f"ERROR: {sort} is not a valid field",
                                                   color=discord.Color.red())
            return

        results = utils.Mongo.get_leaderboard_results(sort, interaction.guild)
        results = enumerate(results, 1)

        embed = utils.EmbedHelpers.create_message_embed(title=f"{embed_title} Gamers",
                                                        message=f"The {embed_title} Gamers! Can you match them?")

        embed.set_thumbnail(url=bot_enums.Enums.BOT_AVATAR_URL.value)

        if sort == "money":
            for count, gamer in results:
                embed.add_field(name=f"{gamer.name}", value=f"{gamer.vbucks} {server_currency}", inline=False)
        else:
            for count, gamer in results:
                embed.add_field(name=f"{gamer.name}", value=f"Level {gamer.level}: {gamer.exp} EXP", inline=False)
        await utils.MessageHelpers.respond(interaction, "", embed=embed)

    @app_commands.command(
        name="give_money",
        description="Gift your hard earned cash to the less fortunate"
    )
    @app_commands.describe(
        receiver="The user you wish to gift money to",
        money="Money"
    )
    @utils.Checks.rude_name_check()
    async def give_money(self, interaction: discord.Interaction, receiver: discord.Member, money: int):
        if interaction.user == receiver:
            await utils.EmbedHelpers.respond_embed(interaction, code_block="You can't send yourself money",
                                                   color=discord.Color.red())
            return

        transact = utils.Mongo.transact(interaction.user, receiver, interaction.guild, money)

        if not transact:
            await utils.EmbedHelpers.respond_embed(interaction, title="Transaction Failed",
                                                   code_block="You attempted to give away more than you own",
                                                   color=discord.Color.red())
        elif transact:
            server_currency = utils.Mongo.get_server_currency_name(interaction.guild.id)
            await utils.EmbedHelpers.respond_embed(interaction,
                                                   message=f"Transaction of {money} {server_currency} Successful!")

    """@cog_ext.cog_slash(name="xp_exchange",
                       description="Pay your way to knowledge and experience!",
                       options=[
                           create_option(
                               name="payment",
                               description="The user you wish to view",
                               option_type=4,
                               required=True,
                           ),
                       ],
                       guild_ids=utils.Level.get_guild_ids())"""

    # @utils.Checks.rude_name_check()
    async def exp_exchange(self, ctx, vbuck_payment: int):
        conversion_ratio = .1

        user = utils.Mongo.get_user(ctx.author, ctx.guild)
        current_vbucks = user.vbucks

        if vbuck_payment > current_vbucks:
            server_currency = utils.Mongo.get_server_currency_name(ctx.guild.id)
            # await utils.EmbedHelpers.send_message_embed(ctx, code_block=f"You do not have enough {server_currency}",
            #                                           color=discord.Color.red())
            return

        added_exp = vbuck_payment * conversion_ratio
        new_exp = user.exp + added_exp

        utils.Mongo.income(ctx.author, ctx.guild, -vbuck_payment)
        utils.Mongo.update_exp(ctx.author, ctx.guild, new_exp)

        # await utils.EmbedHelpers.send_message_embed(ctx,
        #                                           code_block=f"{ctx.author.mention} You gained {added_exp} XP. "
        #                                                      f"You have {new_exp}",
        #                                           color=discord.Color.green())


async def setup(client):
    await client.add_cog(Gamer(client), guilds=utils.Level.get_guild_objects())
