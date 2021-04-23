import asyncio
import random

import discord

from discord.ext import commands

from svc import utils as svc


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

    def __init__(self, client):
        self.client = client

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def fight_test(self, ctx):
        await ctx.send(f"Wait!")
        await asyncio.sleep(10)
        await ctx.send(f"Yep, it works")

    @commands.cooldown(1, 10, discord.ext.commands.BucketType.member)
    @commands.command()
    async def fight(self, ctx, enemy: discord.Member):

        starter_user = svc.Mongo.get_user(ctx.author, ctx.guild)
        enemy_user = svc.Mongo.get_user(enemy, ctx.guild)

        starter_health = self.base_health + (2 * starter_user.level)
        enemy_health = self.base_health + (2 * enemy_user.level)

        starter_attack = self.base_attack + (starter_user.level * self.attack_scale_factor)
        starter_defense = self.base_defense + (starter_user.level * self.defense_scale_factor)

        enemy_attack = self.base_attack + (enemy_user.level * self.attack_scale_factor)
        enemy_defense = self.base_defense + (enemy_user.level * self.defense_scale_factor)

        damage_to_enemy = round(starter_attack * (min(starter_attack / enemy_defense, 1)), 4)
        damage_to_starter = round(enemy_attack * (min(enemy_attack / starter_defense, 1)), 4)

        winner = None
        loser_user = None
        winner_user = None

        while True:
            chance_to_damage_enemy = random.random()
            chance_to_damage_starter = random.random()

            await ctx.send("", embed=svc.Games.create_fight_view(starter_health, enemy_health, ctx.author, enemy))

            await asyncio.sleep(3)
            # defender advantage
            if chance_to_damage_starter <= self.base_hit_chance:
                damage_variation = damage_to_starter + random.randint(0, self.max_damage_variation)

                chance_to_crit = random.random()

                if chance_to_crit <= self.base_crit_chance:
                    starter_health -= damage_variation * 2
                    await ctx.send(
                        f"{enemy.mention} hit a Crit {ctx.author.mention} for {damage_variation * 2} damage!")
                else:
                    starter_health -= damage_variation
                    await ctx.send(f"{enemy.mention} hit against {ctx.author.mention} for {damage_variation}!")

                if starter_health <= 0:
                    winner = enemy
                    loser_user = starter_user
                    winner_user = enemy_user
                    break
            else:
                await ctx.send(f"{enemy.mention} missed!")

            await asyncio.sleep(3)
            if chance_to_damage_enemy <= self.base_hit_chance:
                damage_variation = damage_to_enemy + random.randint(0, self.max_damage_variation)

                chance_to_crit = random.random()

                if chance_to_crit <= self.base_crit_chance:
                    enemy_health -= damage_variation * 2
                    await ctx.send(
                        f"{ctx.author.mention} hit a Crit against {enemy.mention} for {damage_variation * 2} damage!")
                else:
                    enemy_health -= damage_variation
                    await ctx.send(f"{ctx.author.mention} hit {enemy.mention} for {damage_to_enemy}!")

                if enemy_health <= 0:
                    winner = ctx.author
                    loser_user = enemy_user
                    winner_user = starter_user
                    break
            else:
                await ctx.send(f"{ctx.author.mention} missed!")

            await asyncio.sleep(2)

        exp_reward = int((100 + random.randint(0, self.max_reward_variation)) *
                         (loser_user.level * random.uniform(0, self.max_level_impact_variation)))
        vbuck_reward = int((1000 + random.randint(0, self.max_reward_variation)) *
                           (loser_user.level * random.uniform(0, self.max_level_impact_variation)))

        await ctx.send(f"{winner.mention} has won! They gained {exp_reward} EXP and {vbuck_reward} V-Bucks!")

        svc.Mongo.income(winner, ctx.guild, vbuck_reward)
        curr_exp = winner_user.exp
        svc.Mongo.update_exp(winner, ctx.guild, curr_exp + exp_reward)


def setup(client):
    client.add_cog(Fighting(client))
