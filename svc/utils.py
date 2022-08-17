import os

import discord
import mongoengine
import math
import datetime
import colorama
import spotipy

from mongoengine.queryset import QuerySet
from random import randrange, choice
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

import enums.bot_enums
from data_models.users import Users
from data_models.servers import Servers
from data_models.items import Item, BaseItem
from data_models.spotify_check import SpotifyCheck, Song
from data_models.spotify_poll import SongPoll
from enums.bot_enums import Enums as bot_enums
from discord.ext import commands
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL

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
    def get_server(server_id):
        response = Servers.objects().filter(discord_id=server_id).first()
        return response

    @staticmethod
    def create_server(server_id):
        server = Servers()
        server.discord_id = server_id

        if not Mongo.get_server(server_id):
            server.save()
        else:
            return False

    @staticmethod
    def create_user(discord_user: discord.Member, server):
        user = Users()

        user.name = discord_user.name
        user.discord_id = discord_user.id

        user.switch_collection(f"{server.id}")

        if not Mongo.get_server(server.id):
            Mongo.create_server(server.id)

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

        new_exp = old_exp + (randrange(min_exp, max_exp) + (old_level * 1.5))
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

    @staticmethod
    def get_saved_spotify_change():
        try:
            checks = SpotifyCheck.objects.get()
            return SpotifyCheck.objects.first()
        except mongoengine.DoesNotExist:
            return None

    @staticmethod
    def check_for_spotify_change():
        count = SpotifyHelpers.get_length_of_playlist()

        sc = Mongo.get_saved_spotify_change()

        if sc is None:
            tracks = SpotifyHelpers.get_all_playlist_tracks()
            sc = Mongo.create_spotify_check(tracks)
            sc.save()

        if count != sc.count:
            tracks = SpotifyHelpers.get_all_playlist_tracks()
            diff = SpotifyHelpers.determine_diff(tracks, sc.songs, sc.last_updated)
            Mongo.update_spotify_check(tracks)

            return diff
        else:
            return None

    @staticmethod
    def create_spotify_check(tracks):
        sc = SpotifyCheck(count=len(tracks), last_updated=datetime.datetime.now(datetime.timezone.utc))

        for track in tracks:
            artist_names = []

            for artist in track['track']['artists']:
                artist_names.append(artist['name'])

            # date format: YYYY-MM-DDTHH-MM-SSZ
            added_at = SpotifyHelpers.parse_date(track['added_at'])

            album_url = None

            if track['track']['is_local']:
                album_url = bot_enums.BOT_AVATAR_URL.value
            else:
                album_url = track['track']['album']['images'][0]['url']


            song = Song(name=track['track']['name'],
                        artists=artist_names,
                        album=track['track']['album']['name'],
                        album_url=album_url,
                        added_at=added_at)



            # sc.songs.append(song)

            sc.songs.append(track['track']['id'])

        return sc

    @staticmethod
    def update_spotify_check(tracks):
        sc = Mongo.create_spotify_check(tracks)

        update_dict = {
            'set__count': sc.count,
            'set__last_updated': sc.last_updated,
            'set__songs': sc.songs
        }

        SpotifyCheck.objects.update_one(upsert=True, **update_dict)
        return sc

    @staticmethod
    def set_server_currency_name(server_id, currency_name):
        server = Mongo.get_server(server_id)

        if server is None:
            Mongo.create_server(server_id)
            server = Mongo.get_server(server_id)

        server.currency_name = currency_name
        server.save()

    @staticmethod
    def get_server_currency_name(server_id):
        server = Mongo.get_server(server_id)

        c_name = server.currency_name

        if c_name is None:
            return "V-Bucks"
        else:
            return c_name

    @staticmethod
    def create_spotify_poll(song_url, poll_creator: discord.Member, required_votes):
        poll = SongPoll(
            creator=poll_creator.id,
            song_url=song_url,
            required_votes=required_votes
        )

        check = SongPoll.objects(creator=poll_creator.id).first()

        if check:
            return False

        poll.voters.append(poll_creator.id)
        poll.save()

        return True

    @staticmethod
    def get_spotify_poll(poll_creator: discord.Member):
        return SongPoll.objects(creator=poll_creator.id).first()

    @staticmethod
    def check_for_poll(poll_creator: discord.Member):
        check = SongPoll.objects(creator=poll_creator.id).first()

        if check:
            return True
        else:
            return False

    @staticmethod
    def set_poll_id(poll_creator: discord.Member, message_id):
        poll = SongPoll.objects(creator=poll_creator.id).first()

        if not poll:
            return False

        poll.poll_id = message_id
        poll.save()

    @staticmethod
    def add_vote_to_poll(poll_creator: discord.Member, voter: discord.Member):
        poll = SongPoll.objects(creator=poll_creator.id).first()

        if not poll:
            return None

        poll.current_votes += 1
        poll.voters.append(voter.id)

        if poll.current_votes >= poll.required_votes:
            poll.save()
            return True
        else:
            poll.save()
            return False

    @staticmethod
    def get_all_polls():
        polls = SongPoll.objects()
        return polls


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


class Checks:
    slur_list = ["nigger", 'nigga', 'negro', 'chink', 'niglet', 'nigtard', 'gook', 'kike',
                 'faggot', 'beaner']

    @staticmethod
    def rude_name_check():
        def predicate(ctx):
            check_name = ""

            if ctx.author.nick is None:
                check_name = ctx.author.display_name
            else:
                check_name = ctx.author.nick

            for adl in Checks.slur_list:
                if adl in check_name:
                    return False

            return True

        return commands.check(predicate)

    @staticmethod
    def check_is_owner():
        def predicate(ctx):
            return ctx.author.id == bot_enums.OWNER_ID.value

        return commands.check(predicate)


class SpotifyCreator:

    @staticmethod
    def create_spotify_object():
        scope = "playlist-modify-public"

        sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
        return sp

    @staticmethod
    def create_auth_spotify_object():
        scope = "playlist-modify-private"
        cache = ".spotipyoauthcache"

        sp_oauth = SpotifyOAuth(scope=scope, cache_path=cache)
        url = sp_oauth.get_authorize_url()
        # code = sp_oauth.parse_response_code(url)

        Logging.log(__name__, f"url: {url}")
        # Logging.log(__name__, f"code: {code}")
        Logging.log(__name__, f"auth: {sp_oauth.get_authorize_url()}")

        token = sp_oauth.get_access_token(url)
        sp = spotipy.Spotify(auth=token['access_token'])

        return sp


class SpotifyHelpers:

    spotify = SpotifyCreator.create_spotify_object()
    auth_spotify = None # SpotifyCreator.create_auth_spotify_object()

    @staticmethod
    def get_all_playlist_tracks(playlist_id='6yO77cQ0JTMKuNxLh47oLX'):
        my_user_id = "yallmindifiyeet"

        results = SpotifyHelpers.spotify.user_playlist_tracks(my_user_id, playlist_id)
        tracks = results['items']

        while results['next']:
            results = SpotifyHelpers.spotify.next(results)
            tracks.extend(results['items'])

        return tracks

    @staticmethod
    def get_track(id):
        return SpotifyHelpers.spotify.track(id)

    @staticmethod
    def get_length_of_playlist():
        my_user_id = "yallmindifiyeet"
        playlist_id = '6yO77cQ0JTMKuNxLh47oLX'

        results = SpotifyHelpers.spotify.user_playlist_tracks(my_user_id, playlist_id)
        return results['total']

    @staticmethod
    def parse_date(date_string):
        return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")

    @staticmethod
    def determine_diff(tracks, songs, check_updated):
        songs_in_tracks = []
        songs_gone = []

        for song in songs:
            found = False
            for track in tracks:
                if song == track['track']['id']: # song.name == track['track']['name'] and song.artists[0] == track['track']['artists'][0]['name']:
                    songs_in_tracks.append(song)
                    found = True

                    break

            if not found:
                songs_gone.append(song)

        tracks_added = []

        for track in tracks:
            parsed_date = SpotifyHelpers.parse_date(track['added_at'])

            td = check_updated - parsed_date

            if td.total_seconds() < 0:
                tracks_added.append(track)

        return songs_gone, tracks_added

    @staticmethod
    def create_artist_string(artists):
        artist_string = ""

        for artist in artists:
            if artist == artists[-1]:
                artist_string += artist
            else:
                artist_string += f"{artist}, "

        return artist_string

    @staticmethod
    def verify_spotify_url(url, desired_type):
        # ex. "https://open.spotify.com/track/33i4H7iDxIes1d8Nd0S3QF?si=aa73a3fc629140c1"

        # remove https://
        pre_split = url[8: len(url)]

        sections = pre_split.split('/')

        # three responses: correct form, incorrect type, not a spotify link (in that order)
        try:
            domain_name = sections[0]
            spotify_type = sections[1]

            if spotify_type == desired_type:
                return True
            else:
                return False

        except IndexError:
            return None

    @staticmethod
    def parse_id_out_of_url(song_url):
        # https://open.spotify.com/track/1bt443XPmX5ZG5DjhMJ8Rh?si=f6f953ba6c594500
        sections = song_url.split('/')
        end = sections[-1]

        if "?" in end:
            q_pos = end.find("?")
            return end[0: q_pos]
        else:
            return end

    @staticmethod
    def get_album_art_url(track):
        return track['album']['images'][0]['url']

    @staticmethod
    def add_song_to_playlist(playlist_id, song_url):
        SpotifyHelpers.auth_spotify.user_playlist_add_tracks("yallmindifiyeet", playlist_id, [SpotifyHelpers.parse_id_out_of_url(song_url)])

    @staticmethod
    def is_song_in_playlist(playlist_id, song_url):
        tracks = SpotifyHelpers.get_all_playlist_tracks(playlist_id)

        for track in tracks:
            if SpotifyHelpers.parse_id_out_of_url(song_url) == track['track']['id']:
                return True

        return False

    @staticmethod
    def get_artist_names(track_info):
        artist_names = []

        for artist in track_info['artists']:
            artist_names.append(artist['name'])

        return artist_names

    @staticmethod
    def search_song_on_youtube(song_url, just_title=False):
        track_info = SpotifyHelpers.get_track(SpotifyHelpers.parse_id_out_of_url(song_url))

        artists = SpotifyHelpers.get_artist_names(track_info)

        search_query = ""

        if just_title:
            search_query = f"{track_info['name']}"
        else:
            search_query = f"{track_info['name']} {SpotifyHelpers.create_artist_string(artists)}"

        search_results = YoutubeSearch(search_query).to_dict()

        return SpotifyHelpers.determine_best_search_result(search_results)

    @staticmethod
    def determine_best_search_result(search_results: dict):
        if search_results is None or len(search_results) == 0:
            return None

        return search_results[0]

    @staticmethod
    def get_all_album_tracks(album_id):
        album_page = SpotifyHelpers.spotify.album_tracks(album_id)
        tracks = album_page['items']

        while album_page['next']:
            t = SpotifyHelpers.spotify.next(album_page)
            tracks.extend(t)


class Level:

    @staticmethod
    def get_bot_level():
        return os.getenv("LEVEL")

    @staticmethod
    def get_guild_ids():
        level = Level.get_bot_level()

        if level == "DEBUG":
            return [427299383474782208]
        elif level == "PROD":
            return [600162735975694356]

    @staticmethod
    def get_poll_channel(client):
        level = Level.get_bot_level()

        if level == "DEBUG":
            guild = client.get_guild(427299383474782208)
            return guild.get_channel(427299383474782210)
        elif level == "PROD":
            guild = client.get_guild(600162735975694356)
            return guild.get_channel(758528118209904671)

class YoutubeHelpers:

    @staticmethod
    def construct_url_from_suffix(suffix):
        return f"https://www.youtube.com{suffix}"

    @staticmethod
    def construct_url_from_id(id):
        return f"https://www.youtube.com/watch?v={id}"

    @staticmethod
    def get_video_info(url):
        with YoutubeDL({}) as ydl:
            info = ydl.extract_info(url, download=False)

            return info

    @staticmethod
    def find_best_audio_link(formats, url_type):
        if url_type == enums.bot_enums.ReturnTypes.RETURN_TYPE_SOUNDCLOUD_URL:
            for f in formats:
                if f['audio_ext'] == "opus":
                    return f["url"]
        else:
            for f in formats:
                if f['acodec'] == "opus":
                    return f["url"]

class EmbedHelpers:

    @staticmethod
    def create_message_embed(title="", message="", code_block=None, color=discord.Color.blurple()):
        embed = discord.Embed(
            title=title,
            description=f"{message}\n```{code_block}```" if code_block is not None else message,
            color=color
        )

        embed.set_author(name="Johnson Bot", icon_url=bot_enums.BOT_AVATAR_URL.value, url="https://github.com/nathanieltooley/Johnson-Discord-Bot")
        embed.set_footer(text="Made by Nathaniel", icon_url=bot_enums.ASTAR_AVATAR_URL.value)

        return embed

    @staticmethod
    async def send_message_embed(ctx, title="", message="", code_block=None, color=discord.Color.blurple()):
        embed = EmbedHelpers.create_message_embed(title, message, code_block, color)
        return await ctx.send(embed=embed)

class MessageHelpers:

    @staticmethod
    async def safe_message_delete(message: discord.Message):
        try:
            Logging.log("message_deletion", f"Deleting message {message.id}")
            await message.delete()

            # we return None here so that the stored message gets replaced with None
            return None
        except discord.NotFound or discord.HTTPException:
            Logging.error("message_deletion", f"Error occurred when trying to delete message {message.id}")

class VoiceClientManager:

    @staticmethod
    async def connect_to_member(client: commands.Bot, member: discord.Member):
        voice_state: discord.VoiceState = member.voice

        # My bot can only have one voice_client
        if voice_state is None:
            return None

        if len(client.voice_clients) == 0:
            return await voice_state.channel.connect()
        else:
            # move the voice client to the correct channel
            voice_client = client.voice_clients[0]

            # if we are already connected with the right member, just return the vc
            for vc_member in voice_client.channel.members:
                if vc_member.id == member.id:
                    return voice_client

            await voice_client.move_to(voice_state.channel)
            return voice_client

    @staticmethod
    async def disconnect(client: commands.Bot):
        if len(client.voice_clients) != 0:
            await client.voice_clients[0].disconnect()
            return enums.bot_enums.ReturnTypes.RETURN_TYPE_SUCCESSFUL_DISCONNECT
        else:
            return None
