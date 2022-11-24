import discord

from random import choice
from enums import bot_enums

card_names = {
        1: "Ace",
        2: "Two",
        3: "Three",
        4: "Four",
        5: "Five",
        6: "Six",
        7: "Seven",
        8: "Eight",
        9: "Nine",
        10: "Ten",
        11: "Jack",
        12: "Queen",
        13: "King"
    }

card_suits = {
    1: "Hearts",
    2: "Spades",
    3: "Clubs",
    4: "Diamonds"
}


def pickrps():  # only used for rps command
    choices = ['rock', 'paper', 'scissors']
    return choice(choices)


def create_card_view(member, cards: list, color: discord.Color):

    name = ""

    if type(member) == discord.Member:
        name = member.nick
    elif type(member) == discord.ClientUser:
        name = member.name

    title = f"{name}'s Cards"
    description = f"The Cards of {name}"
    url = bot_enums.BOT_AVATAR_URL.value

    card_embed = discord.Embed(title=title, description=description, color=color)

    card_embed.set_thumbnail(url=url)

    for card in cards:
        card_embed.add_field(name=card_names.get(card[0]), value=card_suits.get(card[1]))

    return card_embed


def send_blackjack_option(member: discord.Member):
    title = f"Blackjack"
    description = f"Time to Choose {member.mention}!"
    url = bot_enums.BOT_AVATAR_URL.value

    bj_embed = discord.Embed(title=title, description=description, color=discord.Color.blue())

    bj_embed.set_thumbnail(url=url)

    bj_embed.add_field(name="1", value="Hit")
    bj_embed.add_field(name="2", value="Stand")

    return bj_embed


def create_fight_view(starter_health: int, enemy_health: int, starter: discord.Member, enemy: discord.Member):
    starter_name = None
    enemy_name = None

    if starter.nick is None:
        starter_name = starter.display_name
    else:
        starter_name = starter.nick

    if enemy.nick is None:
        enemy_name = enemy.display_name
    else:
        enemy_name = enemy.nick

    title = f"Fight"
    description = f"A fight between {starter_name} and {enemy_name}"
    url = bot_enums.BOT_AVATAR_URL.value

    fight_embed = discord.Embed(
        title=title,
        description=description,
        color=discord.Color.random_color())

    fight_embed.set_thumbnail(url=url)

    fight_embed.add_field(name=f"{starter_name}", value=f"Health: {int(starter_health)}")
    fight_embed.add_field(name=f"{enemy_name}", value=f"Health: {int(enemy_health)}")

    return fight_embed