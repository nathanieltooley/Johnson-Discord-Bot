import discord
import pymongo
import mongoengine
import math

from mongoengine.context_managers import *
from mongoengine.queryset import QuerySet
from mongoengine import connection
from random import randrange, choice
from svc.users import Users
from svc.servers import Servers

def get_user(user, server):
    server_group = Users.switch_collection(Users(), f"{server.id}")
    server_objects = QuerySet(Users, server_group._get_collection())
    response = server_objects.filter(discord_id=user.id).first()
    return response

def get_server(server):
    response = Servers.objects().filter(discord_id=server.id).first()
    return response

def create_server(guild: discord.Guild):
    server = Servers()
    server.name = guild.name
    server.discord_id = guild.id

    if not get_server(guild):
        server.save()
    else:
        return False

def create_user(discord_user: discord.Member, server):
    user = Users()
    
    user.name = discord_user.name
    user.discord_id = discord_user.id

    user.switch_collection(f"{server.id}")

    if not get_server(server):
        create_server(server)

    if not get_user(discord_user, server):
        user.save()
        return True
    else:
        return False

def income(member, server, money):
    discord_id = member.id
    user = get_user(member, server)
    old_money = user.vbucks

    new_money = old_money + money

    user.switch_collection(f"{server.id}")
    user.vbucks = new_money
    user.save()

    # Users.objects(discord_id=discord_id, server_id=server.id).update_one(vbucks=new_money)

def exp_check(member, server, min_exp, max_exp):
    discord_id = member.id

    user = get_user(member, server)
    old_exp = user.exp
    old_level = user.level

    user.switch_collection(f"{server.id}")

    new_exp = old_exp + (randrange(min_exp, max_exp))
    new_level = int(math.pow(new_exp, 1/4))

    if new_level > old_level:
        user.exp = new_exp
        user.level = new_level
        user.save()

        # Users.objects(discord_id=discord_id).update_one(exp=new_exp)
        # Users.objects(discord_id=discord_id).update_one(level=new_level)

        return (f"{member.mention} has leveled up from Level {old_level} to Level {new_level}!")
    else:
        user.exp = new_exp
        user.save()
        # Users.objects(discord_id=discord_id).update_one(exp=new_exp)
        return None
    
def pickrps():  # only used for rps command
    choices = ['rock', 'paper', 'scissors']
    return choice(choices)

def get_leaderboard_results(field, server):
    server_group = Users.switch_collection(Users(), f"{server.id}")
    server_objects = QuerySet(Users, server_group._get_collection())
    responses = server_objects[:10]().order_by(f"-{field}")
    return responses

def update_vbucks(member, server, money: int):
    user = get_user(member, server)
    user.switch_collection(f"{server.id}")
    user.vbucks = money
    user.save

def update_exp(member, server, exp):
    user = get_user(member, server)
    user.switch_collection(f"{server.id}")

    old_level = user.level

    new_level = int(math.pow(exp, 1/4))
    user.exp = exp

    if old_level == new_level:
        user.save()
    else:
        user.level = new_level
        user.save()

def transact(giver, receiver, server, money):
    giver_user = get_user(giver, server)

    money = int(money) # Make sure its an int

    if giver_user.vbucks <= money:
        return False
    else:
        income(giver, server, -money)
        income(receiver, server, money)
        return True