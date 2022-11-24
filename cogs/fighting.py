import asyncio
import random

import discord

from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option

from enums.bot_enums import Enums
from utils import utils as utils
from enums.bot_enums import Enums as bot_enums


class Fighting(commands.Cog):
    base_health = 100
    base_attack = 25
    base_defense = 20

    attack_scale_factor = 2
    defense_scale_factor = 2.5

    base_hit_chance = .7
    base_crit_chance = .15

    max_damage_variation = 5
    max_reward_variation = 25
    max_level_impact_variation = 2

    game_speed = 1

    def __init__(self, client):
        self.client = client
        self.is_fighting = False

    @cog_ext.cog_slash(
        name="fight",
        description="Fight with another user",
        options=[
            create_option(
                name="user",
                description="User to fight",
                option_type=6,
                required=True
            ),
        ],
        guild_ids=utils.Level.get_guild_ids()
    )
    @utils.Checks.rude_name_check()
    async def fight(self, ctx, enemy: discord.Member):
        await ctx.send("Not implemented at all lol", hidden=True)
        return

        if ctx.author == enemy:
            await ctx.send("You cannot fight yourself.")
            return

        starter_user = svc.Mongo.get_user(ctx.author, ctx.guild)
        enemy_user = svc.Mongo.get_user(enemy, ctx.guild)

        if enemy_user is None:
            await ctx.send("They do not want to fight you.")
            return

        # i get to fight whoever I want because I have special privilege
        if enemy.status != discord.Status.online and ctx.author.id != bot_enums.OWNER_ID.value:
            await ctx.send("They do not want to fight you.")
            return

        starter_health = self.base_health + (2 * starter_user.level)
        enemy_health = self.base_health + (2 * enemy_user.level)

        starter_attack = self.base_attack + (starter_user.level * self.attack_scale_factor)
        starter_defense = self.base_defense + (starter_user.level * self.defense_scale_factor)

        enemy_attack = self.base_attack + (enemy_user.level * self.attack_scale_factor)
        enemy_defense = self.base_defense + (enemy_user.level * self.defense_scale_factor)

        damage_to_enemy = round(starter_attack * (min(starter_attack / enemy_defense, 1)), 4)
        damage_to_starter = round(enemy_attack * (min(enemy_attack / starter_defense, 1)), 4)

        winner = None
        loser = None
        loser_user = None
        winner_user = None

        while True:
            chance_to_damage_enemy = random.random()
            chance_to_damage_starter = random.random()

            await ctx.send("", embed=svc.Games.create_fight_view(starter_health, enemy_health, ctx.author, enemy))

            await asyncio.sleep(3 / self.game_speed)
            # defender advantage
            if chance_to_damage_starter <= self.base_hit_chance:
                damage_variation = damage_to_starter + random.randint(0, self.max_damage_variation)

                chance_to_crit = random.random()

                if chance_to_crit <= self.base_crit_chance:
                    starter_health -= damage_variation * 2
                    await ctx.send(
                        f"{enemy.mention} hit a Crit against {ctx.author.mention} for {damage_variation * 2} damage!")
                else:
                    starter_health -= damage_variation
                    await ctx.send(f"{enemy.mention} hit {ctx.author.mention} for {damage_variation}!")

                if starter_health <= 0:
                    winner = enemy
                    loser = ctx.author
                    loser_user = starter_user
                    winner_user = enemy_user
                    break
            else:
                await ctx.send(f"{enemy.mention} missed!")

            await asyncio.sleep(3 / self.game_speed)
            if chance_to_damage_enemy <= self.base_hit_chance:
                damage_variation = damage_to_enemy + random.randint(0, self.max_damage_variation)

                chance_to_crit = random.random()

                if chance_to_crit <= self.base_crit_chance:
                    enemy_health -= damage_variation * 2
                    await ctx.send(
                        f"{ctx.author.mention} hit a Crit against {enemy.mention} for {damage_variation * 2} damage!")
                else:
                    enemy_health -= damage_variation
                    await ctx.send(f"{ctx.author.mention} hit {enemy.mention} for {damage_variation}!")

                if enemy_health <= 0:
                    winner = ctx.author
                    loser = enemy
                    loser_user = enemy_user
                    winner_user = starter_user
                    break
            else:
                await ctx.send(f"{ctx.author.mention} missed!")

            await asyncio.sleep(2 / self.game_speed)

        exp_reward = int((100 + random.randint(0, self.max_reward_variation)) *
                         ((loser_user.level / winner_user.level) * random.uniform(1, self.max_level_impact_variation) * .75))
        vbuck_reward = int((1000 + random.randint(0, self.max_reward_variation)) *
                           ((loser_user.level / winner_user.level) * random.uniform(1, self.max_level_impact_variation)))

        await ctx.send(f"{winner.mention} has won! They gained {exp_reward} EXP and {vbuck_reward} V-Bucks!")

        svc.Mongo.income(winner, ctx.guild, vbuck_reward)
        curr_exp = winner_user.exp
        svc.Mongo.update_exp(winner, ctx.guild, curr_exp + exp_reward)

        vbuck_loss = int(loser_user.vbucks / 3)

        svc.Mongo.income(loser, ctx.guild, -vbuck_loss)

        await ctx.send(f"{loser.mention} has lost and does not have insurance! They lose {vbuck_loss} in medical bills.")


def setup(client):
    client.add_cog(Fighting(client))
