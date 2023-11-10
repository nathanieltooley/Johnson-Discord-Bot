import discord
from enums.bot_enums import Enums as bot_enums

from utils import jlogging, level

logger = jlogging.get_logger(__name__, level.get_bot_level)


def create_message_embed(
    title="", message="", code_block=None, color=discord.Color.blurple()
):
    embed = discord.Embed(
        title=title,
        description=f"{message}\n```{code_block}```"
        if code_block is not None
        else message,
        color=color,
    )

    embed.set_author(
        name="Johnson Bot",
        icon_url=bot_enums.BOT_AVATAR_URL.value,
        url="https://github.com/nathanieltooley/Johnson-Discord-Bot",
    )
    embed.set_footer(
        text="Made by Nathaniel", icon_url=bot_enums.ASTAR_AVATAR_URL.value
    )

    return embed


async def respond_embed(
    interaction, title="", message="", code_block=None, color=discord.Color.random()
):
    embed = create_message_embed(title, message, code_block, color)
    return await respond(interaction, "", embed)


async def safe_message_delete(message: discord.Message):
    try:
        logger.info("Deleting message %d", message.id)
        await message.delete()

        # we return None here so that the stored message gets replaced with None
        return None
    except discord.NotFound or discord.HTTPException:
        logger.error("Error occurred when trying to delete message %d", message.id)


async def respond(
    interaction: discord.Interaction, message: str, embed: discord.Embed = None
):
    if "responded" in interaction.extras.keys() and interaction.extras["responded"]:
        return await interaction.followup.send(message, embed=embed)
    else:
        await interaction.response.send_message(message, embed=embed)
        interaction.extras.update({"responded": True})
        return await interaction.original_response()


async def defer(interaction: discord.Interaction):
    await interaction.response.defer()
    interaction.extras.update({"responded": True})
