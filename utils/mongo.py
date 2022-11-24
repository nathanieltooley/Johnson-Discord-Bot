import discord
import mongoengine

from mongoengine.queryset import QuerySet

from data_models.users import Users
from data_models.servers import Servers
from data_models.items import Item, BaseItem
from data_models.spotify_check import SpotifyCheck, Song
from data_models.spotify_poll import songpoll

def get_user(member: discord.Member, server: discord.Guild, opp=None):
    server_group = Users.switch_collection(Users(), f"{server.id}")
    server_objects = QuerySet(Users, server_group._get_collection())

    response = None
    if opp is None:
        response = server_objects.filter(discord_id=member.id).first()
    if opp == "q":
        response = server_objects
    return response

def get_server(server_id):
    response = Servers.objects().filter(discord_id=server_id).first()
    return response

def create_server(server_id):
    server = Servers()
    server.discord_id = server_id

    if not get_server(server_id):
        server.save()
    else:
        return False

def create_user(discord_user: discord.Member, server):
    user = Users()

    user.name = discord_user.name
    user.discord_id = discord_user.id

    user.switch_collection(f"{server.id}")

    if not get_server(server.id):
        create_server(server.id)

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

def get_leaderboard_results(field, server):
    server_group = Users.switch_collection(Users(), f"{server.id}")
    server_objects = QuerySet(Users, server_group._get_collection())
    responses = server_objects[:10]().order_by(f"-{field}")
    return responses

def update_vbucks(member, server, money: int):
    user = get_user(member, server)
    user.switch_collection(f"{server.id}")
    user.vbucks = money
    user.save()

def update_exp(member, server, exp):
    user = get_user(member, server)
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

def add_to_slur_count(member: discord.Member, server: discord.Guild, number: int, slur: str):
    user = get_user(member, server)
    user.switch_collection(f"{server.id}")

    slur_dict: dict = user.slur_count
    old_count = 0
    if slur in slur_dict:
        old_count = slur_dict.get(slur)

    new_count = old_count + number
    update_dict = {slur: new_count}
    user.slur_count.update(update_dict)

    user.save()

def add_to_stroke_count(member, server, number):
    user = get_user(member, server)
    user.switch_collection(f"{server.id}")
    old_count = user.stroke_count
    user.stroke_count = old_count + number
    user.save()

def transact(giver, receiver, server, money):
    giver_user = get_user(giver, server)

    money = int(money)  # Make sure its an int

    if giver_user.vbucks <= money:
        return False
    else:
        income(giver, server, -money)
        income(receiver, server, money)
        return True

def create_base_item(item_id, name, value: int, rarity, description=None):
    item = BaseItem(item_id=item_id, name=name, value=value, rarity=rarity, description=description)

    try:
        item.save()
        return True
    except mongoengine.errors.NotUniqueError:
        print("Duplicate ID Error")
        return None

def create_item_instance(item_id, owner: discord.Member, last_owner=None):
    item = Item(ref_id=item_id, owner=owner.id, last_owner=last_owner)
    # item = {"ref_id": item_id, "owner": owner.id, "last_owner": last_owner}
    return item

def get_base_item(ref_id):
    query = BaseItem.objects(item_id=ref_id).first()
    return query

def give_item_to_user(member: discord.Member, item_id, server, last_owner: discord.Member = None):
    baseitem = BaseItem.objects(item_id=item_id).first()
    user = get_user(member, server)

    user.switch_collection(f"{server.id}")

    if last_owner is None:
        db_last_owner = None
    else:
        db_last_owner = last_owner.id

    user.inventory.create(ref_id=item_id, owner=member.id, last_owner=db_last_owner)

    user.save()

    return baseitem.name, baseitem.value

def get_user_inventory(member, server):
    user = get_user(member, server)
    _id = user.inventory.filter(owner=member.id)

    id_list = []

    if _id.count() > 1:
        for ref in _id:
            item = get_base_item(ref.ref_id)
            id_list.append(item)
        return id_list
    else:
        item = get_base_item(_id[0].ref_id)
        id_list.append(item)
        return id_list

def delete_item(member, server, item_id):
    user = get_user(member, server)
    user.switch_collection(collection_name=f"{server.id}")
    _id = user.inventory.filter(ref_id=item_id).delete()

    user.inventory.save()
    user.save()

def get_item_from_inventory(member, server, item_id):
    user = get_user(member, server)
    user.switch_collection(f"{server.id}")

    item = user.inventory.filter(ref_id=item_id).first()

    if not item:
        return False
    else:
        return item

def get_saved_spotify_change():
    try:
        checks = SpotifyCheck.objects.get()
        return SpotifyCheck.objects.first()
    except mongoengine.DoesNotExist:
        return None

def check_for_spotify_change():
    count = SpotifyHelpers.get_length_of_playlist()

    sc = get_saved_spotify_change()

    if sc is None:
        tracks = SpotifyHelpers.get_all_playlist_tracks()
        sc = create_spotify_check(tracks)
        sc.save()

    if count != sc.count:
        tracks = SpotifyHelpers.get_all_playlist_tracks()
        diff = SpotifyHelpers.determine_diff(tracks, sc.songs, sc.last_updated)
        update_spotify_check(tracks)

        return diff
    else:
        return None

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

def update_spotify_check(tracks):
    sc = create_spotify_check(tracks)

    update_dict = {
        'set__count': sc.count,
        'set__last_updated': sc.last_updated,
        'set__songs': sc.songs
    }

    SpotifyCheck.objects.update_one(upsert=True, **update_dict)
    return sc

def set_server_currency_name(server_id, currency_name):
    server = get_server(server_id)

    if server is None:
        create_server(server_id)
        server = get_server(server_id)

    server.currency_name = currency_name
    server.save()

def get_server_currency_name(server_id):
    server = get_server(server_id)

    c_name = server.currency_name

    if c_name is None:
        return "V-Bucks"
    else:
        return c_name

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

def get_spotify_poll(poll_creator: discord.Member):
    return SongPoll.objects(creator=poll_creator.id).first()

def check_for_poll(poll_creator: discord.Member):
    check = SongPoll.objects(creator=poll_creator.id).first()

    if check:
        return True
    else:
        return False

def set_poll_id(poll_creator: discord.Member, message_id):
    poll = SongPoll.objects(creator=poll_creator.id).first()

    if not poll:
        return False

    poll.poll_id = message_id
    poll.save()

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

def get_all_polls():
    polls = SongPoll.objects()
    return polls