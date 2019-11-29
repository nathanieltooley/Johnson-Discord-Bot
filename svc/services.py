import boto3
import pymongo
import mongoengine
import discord
import math

from random import randrange
from datatypes.johnmon import Johnmon, UserJohnmon
from datatypes.users import User
from datatypes.servers import Servers
from datatypes.stats import Stats
from datatypes.weapons import Weapons

default_stats = {"health": 20, "attack": 10, "defense": 5, "speed": 10, "aim": 85}

def get_user(user):
    response = User.objects().filter(discord_id=user.id).first()
    return response

def get_server(server):
    response = Servers.objects().filter(discord_id=server.id).first()
    return response

def johnmon_disambiguation(responses):
    embed_fields = enumerate(responses, 1)
    responses = enumerate(responses, 1)
    
    embed = discord.Embed(
        title="Johnmon Query",
        description="Select the correct Johnmon",
        color=discord.Color.dark_purple()
    )

    for count, johnmon in embed_fields:
        embed.add_field(name=f"```{count}```", value=johnmon.name, inline=False)

    return (responses, embed)

def get_johnmon_by_name(name):
    response = Johnmon.objects().filter(name__icontains=name)
    if len(response) == 1:
        return response[0]
    elif len(response) > 1:
        x = johnmon_disambiguation(response)
        return x

def get_johnmon_by_id(objectid):
    response = Johnmon.objects().filter(id=objectid).first()
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
    user = User()
    user.name = discord_user.name
    user.discord_id = discord_user.id

    if not get_server(server):
        create_server(server)

    if not get_user(discord_user):
        server_append = get_server(server)

        id_list = server_append.user_ids 
        id_list.append(discord_user.id)

        server_append.save()
        user.save()
        return True
    else:
        return False

def income(member, money):
    discord_id = member.id
    user = get_user(member)
    old_money = user.vbucks

    new_money = old_money + money

    User.objects(discord_id=discord_id).update_one(vbucks=new_money)

def exp_check(member, min_exp, max_exp):
    discord_id = member.id

    user = get_user(member)
    old_exp = user.exp
    old_level = user.level

    new_exp = old_exp + (randrange(min_exp, max_exp))
    new_level = int(math.pow(new_exp, 1/4))

    if new_level > old_level:
        User.objects(discord_id=discord_id).update_one(exp=new_exp)
        User.objects(discord_id=discord_id).update_one(level=new_level)
        return (f"{member.mention} has leveled up from to Level {new_level}!")
    else:
        User.objects(discord_id=discord_id).update_one(exp=new_exp)
        return None

def create_stats_class(stats_dict=None, health=20, attack=10, defense=5, speed=10, aim=85) -> Stats:
    if stats_dict:
        stats = Stats()

        stats.health = stats_dict["health"]
        stats.defense = stats_dict["defense"]
        stats.attack = stats_dict["attack"]
        stats.speed = stats_dict["speed"]
        stats.aim = stats_dict["aim"]

        return stats


    args: dict = locals()
    new_stats = {}
    for k, v in args.items():
        if v == "":
            dstat = default_stats[k]
            change = {f"{k}": dstat}
            new_stats.update(change)
        else:
            change = {f"{k}": args[k]}
            new_stats.update(change)
    
    print(new_stats)

    health = new_stats["health"]
    attack = new_stats["attack"]
    defense = new_stats["defense"]
    speed = new_stats["speed"]
    aim = new_stats["aim"]

    stats = Stats()

    stats.health = health
    stats.attack = attack
    stats.defense = defense
    stats.speed = speed
    stats.aim = aim

    print("class", stats.health)

    return stats

def get_stats_as_dict(stats: Stats):
    health = stats.health
    attack = stats.attack
    defense = stats.defense
    speed = stats.speed
    aim = stats.aim

    stats = {"health": health, "attack": attack, "defense": defense, "speed": speed, "aim": aim}

    print("dict", stats)

    return stats

def create_johnmon(name, kind, key, special_move, stats: Stats, author=None, rarity=0, ):
    johnmon = Johnmon()

    johnmon.name = name
    johnmon.johnmon_type = kind
    johnmon.s3key = key
    johnmon.special_move = special_move

    johnmon.author = author
    johnmon.rarity = rarity

    johnmon.stats = stats

    johnmon.save()

    #weapon = johnmon.weapons

    # got to figure out stats, level, exp for johnmon
    # figure this out later

def show_johnmon_stats(johnmon):

    embed = discord.Embed(
            title=f"{johnmon.name}'s Base Stats",
            description=f"All of {johnmon.name} Global Base Stats",
            color=discord.Color.blurple()
    )

    embed.set_image(url=create_presigned_url("gacha-images", johnmon.s3key))
    # print(create_presigned_url("gacha-images", johnmon.s3key))
    embed.add_field(name="Name", value=johnmon.name)
    embed.add_field(name="Type", value=johnmon.johnmon_type)
    embed.add_field(name="Rarity", value=johnmon.rarity)

    if johnmon.author:
        embed.add_field(name="Author", value=johnmon.author)

    embed.add_field(name="Special Move", value=johnmon.special_move)

    return embed

    print("Success")

def list_johnmon_in_box(discord_user):
    user = get_user(discord_user)
    box_johnmon = user.box_johnmon

    enum_johnmon = enumerate(box_johnmon, 1)
    responses = enumerate(box_johnmon, 1)
    
    embed = discord.Embed(
                title = f"{discord_user.nick}'s Box",
                description = f"{discord_user.nick}'s List of Johnmon",
                color = discord.Color.dark_red()
            )

    for count, johnmon in enum_johnmon():
        embed.add_field(name=f"{count}", value=f"{johnmon.name}")


    if enum_johnmon.count() <= 10:
        return embed
    
    if enum_johnmon.count() > 10:
        return {"responses": responses, "embed": embed}

    print(user.box_johnmon)

def johnmon_random_stats(stats: dict):
    new_stats = {}
    for k, v in stats.items():
        val = v + randrange(0, 4)
        x = {f"{k}": val}
        new_stats.update(x)

    print("random", new_stats)
    
    return new_stats

def add_johnmon_to_box(objectid, discord_user):
    server_johnmon = get_johnmon_by_id(objectid)
    user = get_user(discord_user)

    base_stats = get_stats_as_dict(server_johnmon.stats)
    new_stats = johnmon_random_stats(base_stats)
    new_stats = create_stats_class(stats_dict=new_stats)

    client_johnmon = UserJohnmon()
    client_johnmon.johnmon_id = server_johnmon.id
    client_johnmon.stats = new_stats

    if user.box_johnmon.count() > 100:
        return None

    user.box_johnmon.append(client_johnmon)
    user.save()

def select_box_johnmon(discord_user):
    pass

def remove_box_johnmon(objectid, discord_user):
    pass


def create_presigned_url(bucket_name, object_name, expiration=3600):
    s3_client = boto3.client('s3')
    response = s3_client.generate_presigned_url('get_object',
                                                Params={'Bucket': bucket_name,
                                                        'Key': object_name},
                                                ExpiresIn=expiration)

    return response