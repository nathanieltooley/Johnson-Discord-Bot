import discord
import mongoengine
import math
import datetime
import colorama

from mongoengine.queryset import QuerySet
from random import randrange, choice
from data_models.users import Users
from data_models.servers import Servers
from data_models.items import Item, BaseItem
from enums.bot_enums import Enums as bot_enums

colorama.init()


class Mongo:

    @staticmethod
    def get_user(member: discord.Member, server: discord.Guild, opp=None):
        server_group = Users.switch_collection(Users(), f"{server.id}")
        server_objects = QuerySet(Users, server_group._get_collection())

        response = None
        if opp is None:
            response = server_objects.filter(discord_id=member.id).first()
        if opp == "q":
            response = server_objects
        return response

    @staticmethod
    def get_server(server):
        response = Servers.objects().filter(discord_id=server.id).first()
        return response

    @staticmethod
    def create_server(guild: discord.Guild):
        server = Servers()
        server.name = guild.name
        server.discord_id = guild.id

        if not Mongo.get_server(guild):
            server.save()
        else:
            return False

    @staticmethod
    def create_user(discord_user: discord.Member, server):
        user = Users()

        user.name = discord_user.name
        user.discord_id = discord_user.id

        user.switch_collection(f"{server.id}")

        if not Mongo.get_server(server):
            Mongo.create_server(server)

        if not Mongo.get_user(discord_user, server):
            user.save()
            return True
        else:
            return False

    @staticmethod
    def income(member, server, money):
        discord_id = member.id
        user = Mongo.get_user(member, server)
        old_money = user.vbucks

        new_money = old_money + money

        user.switch_collection(f"{server.id}")
        user.vbucks = new_money
        user.save()

        # Users.objects(discord_id=discord_id, server_id=server.id).update_one(vbucks=new_money)

    @staticmethod
    def exp_check(member, server, min_exp, max_exp):
        discord_id = member.id

        user = Mongo.get_user(member, server)
        old_exp = user.exp
        old_level = user.level

        user.switch_collection(f"{server.id}")

        new_exp = old_exp + (randrange(min_exp, max_exp) + pow(old_level, 2))
        new_level = int(math.pow(new_exp, 1 / 4))

        if new_level > old_level:
            user.exp = new_exp
            user.level = new_level
            user.save()

            # Users.objects(discord_id=discord_id).update_one(exp=new_exp)
            # Users.objects(discord_id=discord_id).update_one(level=new_level)

            return f"{member.mention} has leveled up from Level {old_level} to Level {new_level}!"
        else:
            user.exp = new_exp
            user.save()
            # Users.objects(discord_id=discord_id).update_one(exp=new_exp)
            return None

    @staticmethod
    def get_leaderboard_results(field, server):
        server_group = Users.switch_collection(Users(), f"{server.id}")
        server_objects = QuerySet(Users, server_group._get_collection())
        responses = server_objects[:10]().order_by(f"-{field}")
        return responses

    @staticmethod
    def update_vbucks(member, server, money: int):
        user = Mongo.get_user(member, server)
        user.switch_collection(f"{server.id}")
        user.vbucks = money
        user.save()

    @staticmethod
    def update_exp(member, server, exp):
        user = Mongo.get_user(member, server)
        user.switch_collection(f"{server.id}")

        old_level = user.level

        new_level = int(math.pow(exp, 1 / 4))
        user.exp = exp

        if old_level == new_level:
            user.save()
            return None
        else:
            user.level = new_level
            user.save()
            return new_level

    @staticmethod
    def add_to_slur_count(member: discord.Member, server: discord.Guild, number: int, slur: str):
        user = Mongo.get_user(member, server)
        user.switch_collection(f"{server.id}")

        slur_dict: dict = user.slur_count
        old_count = 0
        if slur in slur_dict:
            old_count = slur_dict.get(slur)

        new_count = old_count + number
        update_dict = {slur: new_count}
        user.slur_count.update(update_dict)

        user.save()

    @staticmethod
    def add_to_stroke_count(member, server, number):
        user = Mongo.get_user(member, server)
        user.switch_collection(f"{server.id}")
        old_count = user.stroke_count
        user.stroke_count = old_count + number
        user.save()

    @staticmethod
    def transact(giver, receiver, server, money):
        giver_user = Mongo.get_user(giver, server)

        money = int(money)  # Make sure its an int

        if giver_user.vbucks <= money:
            return False
        else:
            Mongo.income(giver, server, -money)
            Mongo.income(receiver, server, money)
            return True

    @staticmethod
    def create_base_item(item_id, name, value: int, rarity, description=None):
        item = BaseItem(item_id=item_id, name=name, value=value, rarity=rarity, description=description)

        try:
            item.save()
            return True
        except mongoengine.errors.NotUniqueError:
            print("Duplicate ID Error")
            return None

    @staticmethod
    def create_item_instance(item_id, owner: discord.Member, last_owner=None):
        item = Item(ref_id=item_id, owner=owner.id, last_owner=last_owner)
        # item = {"ref_id": item_id, "owner": owner.id, "last_owner": last_owner}
        return item

    @staticmethod
    def get_base_item(ref_id):
        query = BaseItem.objects(item_id=ref_id).first()
        return query

    @staticmethod
    def give_item_to_user(member: discord.Member, item_id, server, last_owner: discord.Member = None):
        baseitem = BaseItem.objects(item_id=item_id).first()
        user = Mongo.get_user(member, server)

        user.switch_collection(f"{server.id}")

        if last_owner is None:
            db_last_owner = None
        else:
            db_last_owner = last_owner.id

        user.inventory.create(ref_id=item_id, owner=member.id, last_owner=db_last_owner)

        user.save()

        return baseitem.name, baseitem.value

    @staticmethod
    def get_user_inventory(member, server):
        user = Mongo.get_user(member, server)
        _id = user.inventory.filter(owner=member.id)

        id_list = []

        if _id.count() > 1:
            for ref in _id:
                item = Mongo.get_base_item(ref.ref_id)
                id_list.append(item)
            return id_list
        else:
            item = Mongo.get_base_item(_id[0].ref_id)
            id_list.append(item)
            return id_list

    @staticmethod
    def delete_item(member, server, item_id):
        user = Mongo.get_user(member, server)
        user.switch_collection(collection_name=f"{server.id}")
        _id = user.inventory.filter(ref_id=item_id).delete()

        user.inventory.save()
        user.save()

    @staticmethod
    def get_item_from_inventory(member, server, item_id):
        user = Mongo.get_user(member, server)
        user.switch_collection(f"{server.id}")

        item = user.inventory.filter(ref_id=item_id).first()

        if not item:
            return False
        else:
            return item


class Games:

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

    @staticmethod
    def pickrps():  # only used for rps command
        choices = ['rock', 'paper', 'scissors']
        return choice(choices)

    @staticmethod
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
            card_embed.add_field(name=Games.card_names.get(card[0]), value=Games.card_suits.get(card[1]))

        return card_embed

    @staticmethod
    def send_blackjack_option(member: discord.Member):
        title = f"Blackjack"
        description = f"Time to Choose {member.mention}!"
        url = bot_enums.BOT_AVATAR_URL.value

        bj_embed = discord.Embed(title=title, description=description, color=discord.Color.blue())

        bj_embed.set_thumbnail(url=url)

        bj_embed.add_field(name="1", value="Hit")
        bj_embed.add_field(name="2", value="Stand")

        return bj_embed

    @staticmethod
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
            color=Color.random_color())

        fight_embed.set_thumbnail(url=url)

        fight_embed.add_field(name=f"{starter_name}", value=f"Health: {int(starter_health)}")
        fight_embed.add_field(name=f"{enemy_name}", value=f"Health: {int(enemy_health)}")

        return fight_embed

class Color:

    @staticmethod
    def random_color():
        return discord.Color.from_rgb(randrange(1, 256), randrange(randrange(1, 256)), randrange(1, 256))


class Logging:

    @staticmethod
    def log(name, log):
        print(colorama.Style.RESET_ALL + colorama.Fore.BLUE + f"{name}" + colorama.Fore.MAGENTA + f":{log}")

    @staticmethod
    def time_log(name, log):
        print(colorama.Style.RESET_ALL + colorama.Fore.BLUE + f"{name}" + colorama.Fore.GREEN +
              f"{datetime.datetime.now()}" + colorama.Fore.MAGENTA + f":{log}")

    @staticmethod
    def error(name, log):
        print(colorama.Fore.RED + f"ERROR:{name}:{log}")

    @staticmethod
    def warning(name, log):
        print(colorama.Fore.YELLOW + f"WARNING:{name}:{log}")
