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

    base_hit_chance = .50

    def __init__(self, client):
        self.client = client

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def fight_test(self, ctx):
        await ctx.send(f"Yep, it works")

    @commands.cooldown(1, 10, discord.ext.commands.BucketType.member)
    @commands.command()
    async def fight(self, ctx, enemy: discord.Member):
        exp_reward = 100
        vbuck_reward = 100

        starter_user = svc.Mongo.get_user(ctx.author, ctx.guild)
        enemy_user = svc.Mongo.get_user(enemy, ctx.guild)

        starter_health = self.base_health + (2 * starter_user.level)
        enemy_health = self.base_health + (2 * enemy_user.level)

        starter_attack = self.base_attack + (starter_user.level * self.attack_scale_factor)
        starter_defense = self.base_defense + (starter_user.level * self.defense_scale_factor)

        enemy_attack = self.base_attack + (enemy_user.level * self.attack_scale_factor)
        enemy_defense = self.base_defense + (enemy_user.level * self.defense_scale_factor)

        damage_to_enemy = starter_attack * (min(starter_attack / enemy_defense, 1))
        damage_to_starter = enemy_attack * (min(enemy_attack / starter_defense, 1))



        winner = None
        winner_user = None

        while True:
            chance_to_damage_enemy = random.random()
            chance_to_damage_starter = random.random()

            # defender advantage
            if chance_to_damage_starter > self.base_hit_chance:
                starter_health -= damage_to_starter
                if starter_health <= 0:
                    winner = enemy
                    winner_user = enemy_user
                    break

            if chance_to_damage_enemy > self.base_hit_chance:
                enemy_health -= damage_to_enemy
                if enemy_health <= 0:
                    winner = ctx.author
                    winner_user = starter_user
                    break

        await ctx.send(f"{winner.mention} has won! They gained {exp_reward} EXP and {vbuck_reward} V-Bucks!")

        svc.Mongo.income(winner, ctx.guild, vbuck_reward)
        curr_exp = winner_user.exp
        svc.Mongo.update_exp(winner, ctx.guild, curr_exp + exp_reward)


def setup(client):
    client.add_cog(Fighting(client))