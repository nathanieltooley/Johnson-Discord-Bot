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
from enums.bot_enums import Enums

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
        self.count = 0
        
    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        global_init()
        utils.Logging.log(__name__, "Johnson is spittin straight cog!")
        await self.client.change_presence(activity=discord.Game(name="For more info, use .helpme!"))
        utils.Logging.log(__name__, f"Johnson Level: {utils.Level.get_bot_level()}")
        
    # Commands
    @cog_ext.cog_slash(name="ping", description="Tests Bot Latency", guild_ids=utils.Level.get_guild_ids())
    @utils.Checks.rude_name_check()
    async def _ping(self, ctx: SlashContext):
        self.count += 1
        await ctx.send(f"Pong! {round(self.client.latency * 1000)}ms: test {self.count}")


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
                    album_url = Enums.BOT_AVATAR_URL.value

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
                    album_url = Enums.BOT_AVATAR_URL.value

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

        diff = utils.Mongo.check_for_spotify_change()

        if diff:
            embeds = self.create_change_embeds(diff)

            for embed in embeds:
                await channel.send(embed=embed)

        print(f"check took: {datetime.datetime.now() - start}")

    @change_status.before_loop
    async def before_status(self):
        utils.Logging.log(__name__, "Waiting start status change...")
        await self.client.wait_until_ready()

    @check_playlist_changes.before_loop
    async def before_check(self):
        utils.Logging.log(__name__, "Waiting to start spotify polling...")
        await self.client.wait_until_ready()
        

def setup(client):
    client.add_cog(Setup(client))
