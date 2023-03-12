import asyncio
import datetime

import discord

from itertools import cycle
from discord.ext import commands, tasks
from discord import app_commands
from enums.bot_enums import Enums

from utils import level, messaging, jspotify, mongo, jlogging

status = cycle(["Fortnite",
                "Omori. And you should too!"
                "Made by Nathaniel",
                ])

class Setup(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.change_status.start()
        # self.check_playlist_changes.start()
        # self.check_for_dead_polls.start()
        self.count = 0

    # Commands

    @commands.has_permissions(administrator=True)
    @commands.command()
    async def sync(self, ctx):
        await ctx.send("Syncing!")
        await self.client.tree.sync(guild=level.get_guild_objects()[0])
        await ctx.send("Synced!")

    @app_commands.command(
        description="Pings the bot."
    )
    async def ping(self, interaction: discord.Interaction):
        self.count += 1

        await messaging.respond(interaction, f"Bong! {round(self.client.latency * 1000)}ms; Times Pinged: {self.count}")

    @app_commands.command(
        name="test_defer",
        description="fuck off"
    )
    async def test_defer(self, interaction: discord.Interaction):
        await interaction.response.defer()

        print("fuck")
        await asyncio.sleep(3)
        print("you")

        await interaction.followup.send("fuck yeah")
        await interaction.followup.send("oh nyo")

    @tasks.loop(seconds=45)
    async def change_status(self):
        new_stat = next(status)
        await self.client.change_presence(activity=discord.Game(name=new_stat))

    def create_change_embeds(self, changes):
        embeds = []

        # removals
        if changes[0]:
            for song_id in changes[0]:
                track = jspotify.get_track(song_id)

                artists_names = [artist['name'] for artist in track['artists']]
                artist_string = jspotify.create_artist_string(artists_names)

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
                artist_string = jspotify.create_artist_string(artists_names)

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
        jlogging.log(__name__, "Running Spotify Check!")
        start = datetime.datetime.now()
        # hard coded because fuck it, its my bot and my playlist
        # channel_id = 842246555205763092
        channel_id = 649781215808978946
        channel = self.client.get_channel(channel_id)

        try:
            diff = mongo.check_for_spotify_change()

            if diff:
                embeds = self.create_change_embeds(diff)

                for embed in embeds:
                    await channel.send(embed=embed)

            jlogging.log("Spotify Check", f"Check successful; took: {datetime.datetime.now() - start}")
        except Exception as e:
            jlogging.error("Spotify Check", f"Check unsuccessful: {e}")

    # @tasks.loop(hours=1)
    async def check_for_dead_polls(self):
        polls = mongo.get_all_polls()

        for poll in polls:
            now = datetime.datetime.now(tz=datetime.timezone.utc)
            td = now.replace(tzinfo=datetime.timezone.utc) - poll.created_at.replace(tzinfo=datetime.timezone.utc)

            jlogging.log("spotify_prune", f"Time delta: {td}")

            # limit is a day
            if td.total_seconds() >= 86400:
                channel = level.get_poll_channel(self.client)
                message = await channel.fetch_message(poll.poll_id)

                await message.delete()

                embed = messaging.create_message_embed("Poll Closed!",
                                                                f"{self.client.get_user(poll.creator).mention}'s poll "
                                                                f"has been closed. opened at "
                                                                f"{poll.created_at}. td: {td}. sec: ({td.total_seconds()})")
                await channel.send(embed=embed)
                poll.delete()

    @change_status.before_loop
    async def before_status(self):
        jlogging.log(__name__, "Waiting start status change...")
        await self.client.wait_until_ready()

    @check_playlist_changes.before_loop
    async def before_check(self):
        jlogging.log(__name__, "Waiting to start spotify polling...")
        await self.client.wait_until_ready()

    # @check_for_dead_polls.before_loop
    async def before_polls(self):
        jlogging.log(__name__, "Waiting to start poll prune...")
        await self.client.wait_until_ready()


async def setup(client):
    await client.add_cog(Setup(client), guilds=level.get_guild_objects())
