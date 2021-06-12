import svc.utils as svc
import discord
import os
import itertools
import random

from itertools import cycle
from svc.mongo_setup import global_init
from discord.ext import commands, tasks
from enums.bot_enums import Enums

status = cycle(["For more info, use .helpme!",
                    "Minecraft",
                    "Who uses this bot anyways?",
                    "Made by Nathaniel",
                    "Fortnite",
                    "SwowS",
                    "Team Fortress 2",
                    "Back Online!"])


class Setup(commands.Cog):
    
    def __init__(self, client):
        self.client = client
        self.change_status.start()
        
    # Events
    @commands.Cog.listener()
    async def on_ready(self):
        global_init()
        svc.Logging.log(__name__, "Johnson is spittin straight cog!")
        # self.change_status.start()
        await self.client.change_presence(activity=discord.Game(name="For more info, use .helpme!"))
        self.check_playlist_changes.start()
        
    # Commands
    @commands.command()
    @svc.Checks.rude_name_check()
    async def ping(self, ctx):
        await ctx.send(f"Pong! {round(self.client.latency * 1000)}ms")

    @commands.command()
    async def shutdown(self, ctx):
        if ctx.message.author.id == 139374003365216256: #replace OWNERID with your user id
            print("Shutdown")
        try:
            await self.client.logout()
        except:
            print("EnvironmentError")
            self.client.clear()
        else:
            await ctx.send("You do not own this bot!")

    @commands.command(aliases=['helpme'])
    async def support(self, ctx):
        """Custom help message"""
        await ctx.send('--Made by Nathaniel--\n'
                    'Commands: \n'
                    '.ping: Pong!\n'
                    '.roll [number of sides]: Rolls a die, accepts a number; default is 6 \n'
                    '.rps [Player 1] [Player 2]: Shoot! There is a monetary reward for those who win\n'
                    ".viewgamerstats [id]: View a player's statistics.\n"
                    ".view_gamer_boards: View the server's leaderboard.\n"
                    ".gamble [amount]: Gamble to your hearts content. It's Vegas baby!\n"
                    "I'm also a part-time Dad now as well! (as per Noah's request)\n"
                    "I'm also now controlled by the ADL\n"
                    "Source code available at https://github.com/applememes69420/Johnson-Discord-Bot")

    @tasks.loop(seconds=45)
    async def change_status(self):
        new_stat = next(status)
        await self.client.change_presence(activity=discord.Game(new_stat))

    def create_change_embeds(self, changes):
        embeds = []

        # removals
        if changes[0]:
            for change in changes[0]:
                artist_string = svc.SpotifyHelpers.create_artist_string(change.artists)

                removed_embed = discord.Embed(title=change.name,
                                              description="This song has been removed from the playlist.",
                                              color=discord.Color.red(),
                                              )

                removed_embed.set_author(name=artist_string)
                removed_embed.set_image(url=change.album_url)

                embeds.append(removed_embed)

        # additions
        if changes[1]:
            for change in changes[1]:
                artists_names = [artist['name'] for artist in change['track']['artists']]
                artist_string = svc.SpotifyHelpers.create_artist_string(artists_names)

                added_embed = discord.Embed(title=change['track']['name'],
                                            description="This song has been added to the playlist.",
                                            color=discord.Color.blue())

                added_embed.set_author(name=artist_string)

                album_url = ""

                try:
                    album_url = change['track']['album']['images'][0]['url']
                except IndexError:
                    album_url = Enums.BOT_AVATAR_URL.value

                added_embed.set_image(url=album_url)

                embeds.append(added_embed)

        return embeds

    @tasks.loop(seconds=2)
    async def check_playlist_changes(self):
        # hard coded because fuck it, its my bot and my playlist
        channel_id = 649781215808978946
        channel = self.client.get_channel(channel_id)

        diff = svc.Mongo.check_for_spotify_change()

        if diff:
            embeds = self.create_change_embeds(diff)

            for embed in embeds:
                await channel.send(embed=embed)

    @change_status.before_loop
    async def before_status(self):
        svc.Logging.log(__name__, "Waiting...")
        await self.client.wait_until_ready()
        

def setup(client):
    client.add_cog(Setup(client))
