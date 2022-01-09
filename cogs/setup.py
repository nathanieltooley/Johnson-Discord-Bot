import datetime

import svc.utils as utils
import discord
import os
import itertools
import random

from itertools import cycle
from svc.mongo_setup import global_init
from discord.ext import commands, tasks
from discord_slash import cog_ext, SlashContext
from enums.bot_enums import Enums as bot_enums

status = cycle(["Now Using Slash Commands!",
                    "Minecraft",
                    "Who uses this bot anyways?",
                    "Made by Nathaniel",
                    "Build: Different",
                    "Team Fortress 2",
                    "your mom"])


class Setup(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.change_status.start()
        self.check_playlist_changes.start()
        self.check_for_dead_polls.start()
        self.count = 0
        
    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        global_init()
        utils.Logging.log(__name__, "Johnson is spittin straight cog!")
        await self.client.change_presence(activity=discord.Game(name="For more info, use .helpme!"))
        utils.Logging.log(__name__, f"Johnson Level: {utils.Level.get_bot_level()}")
        utils.Logging.log(__name__, f"test server c_name: {utils.Mongo.get_server_currency_name(bot_enums.TEST_SERVER_ID.value)}")
        
    # Commands
    @cog_ext.cog_slash(name="ping", description="Tests Bot Latency", guild_ids=utils.Level.get_guild_ids())
    @utils.Checks.rude_name_check()
    async def _ping(self, ctx: SlashContext):
        self.count += 1
        await ctx.send(f"Pong! {round(self.client.latency * 1000)}ms; Times Pinged: {self.count}")


    @commands.command()
    async def shutdown(self, ctx):
        if ctx.message.author.id == 139374003365216256:
            print("Shutdown")
        try:
            await self.client.logout()
        except:
            print("EnvironmentError")
            self.client.clear()
        else:
            await ctx.send("You do not own this bot!")

    @tasks.loop(seconds=45)
    async def change_status(self):
        new_stat = next(status)
        await self.client.change_presence(activity=discord.Game(new_stat))

    def create_change_embeds(self, changes):
        embeds = []

        # removals
        if changes[0]:
            for song_id in changes[0]:
                track = utils.SpotifyHelpers.get_track(song_id)

                artists_names = [artist['name'] for artist in track['artists']]
                artist_string = utils.SpotifyHelpers.create_artist_string(artists_names)

                removed_embed = discord.Embed(title=track['name'],
                                              description="This song has been removed from the playlist.",
                                              color=discord.Color.red(),
                                              )

                removed_embed.set_author(name=artist_string)

                album_url = ""

                try:
                    album_url = track['album']['images'][0]['url']
                except IndexError:
                    album_url = bot_enums.BOT_AVATAR_URL.value

                removed_embed.set_image(url=album_url)

                embeds.append(removed_embed)

        # additions
        if changes[1]:
            for song_id in changes[1]:
                artists_names = [artist['name'] for artist in song_id['track']['artists']]
                artist_string = utils.SpotifyHelpers.create_artist_string(artists_names)

                added_embed = discord.Embed(title=song_id['track']['name'],
                                            description="This song has been added to the playlist.",
                                            color=discord.Color.blue())

                added_embed.set_author(name=artist_string)

                album_url = ""

                try:
                    album_url = song_id['track']['album']['images'][0]['url']
                except IndexError:
                    album_url = bot_enums.BOT_AVATAR_URL.value

                added_embed.set_image(url=album_url)

                embeds.append(added_embed)

        return embeds

    @tasks.loop(seconds=10)
    async def check_playlist_changes(self):
        start = datetime.datetime.now()
        # hard coded because fuck it, its my bot and my playlist
        # channel_id = 842246555205763092
        channel_id = 649781215808978946
        channel = self.client.get_channel(channel_id)

        try:
            diff = utils.Mongo.check_for_spotify_change()

            if diff:
                embeds = self.create_change_embeds(diff)

                for embed in embeds:
                    await channel.send(embed=embed)

            utils.Logging.log("Spotify Check", f"Check successful; took: {datetime.datetime.now() - start}")
        except Exception as e:
            utils.Logging.error("Spotify Check", f"Check unsuccessful: {e}")


    @tasks.loop(hours=1)
    async def check_for_dead_polls(self):
        polls = utils.Mongo.get_all_polls()

        for poll in polls:
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            td = now.replace(tzinfo=datetime.timezone.utc) - poll.created_at.replace(tzinfo=datetime.timezone.utc)

            utils.Logging.log("spotify_prune", f"Time delta: {td}")

            # limit is a day
            if td.total_seconds() >= 86400:
                channel = utils.Level.get_poll_channel(self.client)
                message = await channel.fetch_message(poll.poll_id)

                await message.delete()
                await channel.send(f"{self.client.get_user(poll.creator).mention}'s poll has been closed. opened at "
                                   f"{poll.created_at}. td: {td}. sec: ({td.total_seconds()})")
                poll.delete()

    @change_status.before_loop
    async def before_status(self):
        utils.Logging.log(__name__, "Waiting start status change...")
        await self.client.wait_until_ready()

    @check_playlist_changes.before_loop
    async def before_check(self):
        utils.Logging.log(__name__, "Waiting to start spotify polling...")
        await self.client.wait_until_ready()

    @check_for_dead_polls.before_loop
    async def before_polls(self):
        utils.Logging.log(__name__, "Waiting to start poll prune...")
        await self.client.wait_until_ready()
        

def setup(client):
    client.add_cog(Setup(client))
