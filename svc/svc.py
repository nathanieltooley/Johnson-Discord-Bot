import discord
import pymongo
import mongoengine
import math

from random import randrange, choice
from svc.users import Users
from svc.servers import Servers

def get_user(user, server):
    response = Users.objects().filter(discord_id=user.id, server_id=server.id).first()
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
    user.server_name = server.name
    user.server_id = server.id

    if not get_server(server):
        create_server(server)

    if not get_user(discord_user, server):
        server_append = get_server(server)

        id_list = server_append.user_ids 
        id_list.append(discord_user.id)

        server_append.save()
        user.save()
        return True
    else:
        return False

def income(member, server, money):
    discord_id = member.id
    user = get_user(member, server)
    old_money = user.vbucks

    new_money = old_money + money

    Users.objects(discord_id=discord_id, server_id=server.id).update_one(vbucks=new_money)

def exp_check(member, server, min_exp, max_exp):
    discord_id = member.id

    user = get_user(member, server)
    old_exp = user.exp
    old_level = user.level

    new_exp = old_exp + (randrange(min_exp, max_exp))
    new_level = int(math.pow(new_exp, 1/4))

    if new_level > old_level:
        Users.objects(discord_id=discord_id).update_one(exp=new_exp)
        Users.objects(discord_id=discord_id).update_one(level=new_level)
        return (f"{member.mention} has leveled up from Level {old_level} to Level {new_level}!")
    else:
        Users.objects(discord_id=discord_id).update_one(exp=new_exp)
        return None
    
def pickrps():  # only used for rps command
    choices = ['rock', 'paper', 'scissors']
    return choice(choices)

def get_leaderboard_results(field, server):
    responses = Users.objects[:10]().filter(server_id=server.id).order_by(f"-{field}")
    return responses

def transact(giver, receiver, server, money: int):
    giver_user = get_user(giver, server)

    if giver_user.vbucks <= money:
        return False
    else:
        income(giver, server, -money)
        income(receiver, server, money)
        return True