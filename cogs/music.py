import asyncio
import pprint

import discord
import youtube_dl

import svc.utils as utils

from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

from enums.bot_enums import Enums as bot_enums
from enums.bot_enums import DiscordEnums as discord_enums
from enums.bot_enums import ReturnTypes as return_types


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.queue = []

    @cog_ext.cog_slash(name="start_playlist_vote",
                       description="Start a vote to add a song to Our Playlist :) "
                                   "(Must have a link to song on spotify).",
                       options=[
                           create_option(
                               name="songurl",
                               description="A link to a song on spotify that you wish to add "
                                           "(ex. https://open.spotify.com/track/[track_id]). ",
                               option_type=3,
                               required=True
                           )
                       ],
                       guild_ids=utils.Level.get_guild_ids())
    async def _add_to_playlist(self, ctx: SlashContext, song_url):
        if ctx.author.id not in bot_enums.POLL_CREATORS.value:
            await ctx.send("Sorry, you cannot use this command", hidden=True)
            return

        if ctx.guild.id == 600162735975694356 and ctx.channel.id != 758528118209904671:
            await ctx.send("Wrong channel.", hidden=True)
            return

        if utils.SpotifyHelpers.is_song_in_playlist(bot_enums.OUR_PLAYLIST_ID.value, song_url):
            await ctx.send("Song is already in playlist", hidden=True)
            return

        does_url_pass = utils.SpotifyHelpers.verify_spotify_url(song_url, "track")

        await ctx.defer()

        if does_url_pass is None:
            await ctx.send("Make sure you submit a spotify link. "
                           "For example: *https://open.spotify.com/track/33i4H7iDxIes1d8Nd0S3QF?si=aa73a3fc629140c1*")
            return

        if does_url_pass:
            db_poll = utils.Mongo.create_spotify_poll(song_url, ctx.author, len(bot_enums.POLL_CREATORS.value))

            # there is already a poll for this person
            if not db_poll:
                await ctx.send("You already have a poll running!", hidden=True)
                return

            song_id = utils.SpotifyHelpers.parse_id_out_of_url(song_url)
            track = utils.SpotifyHelpers.get_track(song_id)

            artist_names = []

            for artist in track['artists']:
                artist_names.append(artist['name'])

            embed = discord.Embed(
                title=f"{utils.SpotifyHelpers.create_artist_string(artist_names)}",
                description=f"[{track['name']}]({song_url})",
                color=discord.Color.green()
            )

            url = utils.SpotifyHelpers.get_album_art_url(track)
            embed.set_image(url=url)

            embed.set_author(name="PLAYLIST VOTE")
            embed.set_footer(text="Those who are eligible: vote on this song to be in 'our playlist :)'")

            message = await ctx.send(embed=embed)

            utils.Mongo.set_poll_id(ctx.author, message.id)

        elif not does_url_pass:
            await ctx.send("Make sure you submit a song link and not a playlist link. "
                           "For example: https://open.spotify.com/**track**/")
            return

    @cog_ext.cog_slash(name="poll_vote_yes",
                       description="Vote yes on an active playlist vote.",
                       options=[
                           create_option(
                               name="pollauthor",
                               description="The user who created the poll you're voting for. "
                                           "Polls need unanimous agreement to pass.",
                               option_type=6,
                               required=True
                           )
                       ],
                       guild_ids=utils.Level.get_guild_ids())
    async def _vote_yes(self, ctx: SlashContext, poll_creator):
        if utils.Mongo.check_for_poll(poll_creator):
            if ctx.author.id not in bot_enums.POLL_CREATORS.value:
                await ctx.send("You cannot vote in these polls.", hidden=True)
                return

            pre_poll = utils.Mongo.get_spotify_poll(poll_creator)

            if ctx.author.id in pre_poll.voters:
                await ctx.send("You have already voted yes to this poll", hidden=True)
                return

            meets_vote_req = utils.Mongo.add_vote_to_poll(poll_creator, ctx.author)

            # person has no vote running (redundant)
            if meets_vote_req is None:
                await ctx.send("Make sure that this person has a poll running!", hidden=True)
                return

            poll = utils.Mongo.get_spotify_poll(poll_creator)
            track = utils.SpotifyHelpers.get_track(utils.SpotifyHelpers.parse_id_out_of_url(poll.song_url))

            if meets_vote_req:
                await ctx.send(f"The vote on {track['name']} has passed! It will be added to our playlist")
                # Music.add_song_to_playlist(poll.song_url)
                poll.delete()
                return

            if not meets_vote_req:
                await ctx.send(f"{poll.current_votes} / {poll.required_votes} for {track['name']}.")
        else:
            await ctx.send("Make sure that this person has a poll running!", hidden=True)

    @cog_ext.cog_slash(name="poll_vote_no",
                       description="Vote no on an active playlist vote. Polls need unanimous agreement to pass.",
                       options=[
                           create_option(
                               name="pollauthor",
                               description="The user who created the poll you're voting for.",
                               option_type=6,
                               required=True
                           )
                       ],
                       guild_ids=utils.Level.get_guild_ids())
    async def _vote_no(self, ctx: SlashContext, creator: discord.Member):
        if utils.Mongo.check_for_poll(creator):
            if ctx.author.id not in bot_enums.POLL_CREATORS.value:
                await ctx.send("You cannot vote in these polls.", hidden=True)
                return

            poll = utils.Mongo.get_spotify_poll(creator)
            track = utils.SpotifyHelpers.get_track(utils.SpotifyHelpers.parse_id_out_of_url(poll.song_url))

            if ctx.author.id in poll.voters:
                await ctx.send("You have already voted yes to this poll", hidden=True)
                return

            await ctx.send(f"{ctx.author.mention} has voted no to adding {track['name']} to the playlist! Vote is over!")
            message = await ctx.channel.fetch_message(poll.poll_id)

            poll.delete()
            await message.delete()

    @cog_ext.cog_slash(name="poll_cancel",
                       description="Cancel your poll.",
                       guild_ids=utils.Level.get_guild_ids())
    async def _cancel_vote(self, ctx: SlashContext):
        poll = utils.Mongo.get_spotify_poll(ctx.author)

        if not poll:
            await ctx.send("You have no poll to cancel", hidden=True)
            return

        track = utils.SpotifyHelpers.get_track(utils.SpotifyHelpers.parse_id_out_of_url(poll.song_url))

        await ctx.send(f"{ctx.author.mention} has cancelled their poll over adding {track['name']} to the playlist! "
                       f"Vote is over!")
        message = await ctx.channel.fetch_message(poll.poll_id)

        poll.delete()
        await message.delete()

    @commands.command()
    async def play(self, ctx: discord.ext.commands.Context, song_url):
        if Music.determine_url_type(song_url) == return_types.RETURN_TYPE_INVALID_URL:
            await ctx.send("Invalid URL!")
            return

        result = await Music.join(ctx)

        # If we didn't connect, stop command
        if result is None:
            return

        self.add_to_queue(song_url)

        if ctx.voice_client.is_playing():
            await ctx.send("Song currently playing. Will queue next song.")
            return

        await self.play_song(ctx, song_url)

    @commands.command()
    async def disconnect(self, ctx):
        await ctx.voice_client.disconnect()

    @commands.command(aliases=["skip"])
    async def stop(self, ctx):
        if ctx.voice_client:
            ctx.voice_client.stop()

    @commands.command()
    async def pause(self, ctx):
        if ctx.voice_client:
            ctx.voice_client.pause()

    @commands.command()
    async def resume(self, ctx):
        if ctx.voice_client:
            ctx.voice_client.resume()

    @staticmethod
    async def join(ctx: discord.ext.commands.Context):
        if ctx.author.voice is None:
            await ctx.send("You need to be in a voice channel.")
            return None

        voice_channel = ctx.author.voice.channel

        if ctx.voice_client is None:
            await voice_channel.connect()
        else:
            await ctx.voice_client.move_to(voice_channel)

        return True

    async def play_song(self, ctx, song_url):
        url_type = Music.determine_url_type(song_url)

        if url_type == return_types.RETURN_TYPE_SPOTIFY_URL:
            suffix = utils.SpotifyHelpers.search_song_on_youtube(song_url)["url_suffix"]
            song_url = utils.YoutubeHelpers.construct_url_from_suffix(suffix)

        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': "-vn"}
        ydl_options = {'format': 'bestaudio'}

        vc = ctx.voice_client

        utils.Logging.log("music_bot", f"Starting playback; url: {song_url}")
        with youtube_dl.YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(song_url, download=False)

            # pprint.pprint(info)

            url2 = info['formats'][0]['url']

            if utils.Level.get_bot_level() == "DEBUG":
                utils.Logging.log("music_bot", f"Probe Url: {url2}")

            source = await discord.FFmpegOpusAudio.from_probe(url2, method='fallback', **ffmpeg_options)

            # we use asyncio because we can't use await in lambda
            vc.play(source, after=lambda error: asyncio.run_coroutine_threadsafe(self.check_queue(ctx), self.client.loop))

    @staticmethod
    def add_song_to_playlist(song_url):
        utils.SpotifyHelpers.add_song_to_playlist(bot_enums.OUR_PLAYLIST_ID.value, song_url)

    @staticmethod
    def determine_url_type(song_url):
        # https://www.youtube.com/watch?v=_arqbQqq88M
        # https://open.spotify.com/track/74wtYmeZuNS59vcNyQhLY5?si=3e55a2bd614d4e29

        segments = song_url.split("/")
        segments.reverse()

        try:
            if segments[1] == "www.youtube.com":
                return return_types.RETURN_TYPE_YOUTUBE_URL
            elif segments[2] == "open.spotify.com":
                return return_types.RETURN_TYPE_SPOTIFY_URL
            else:
                return return_types.RETURN_TYPE_INVALID_URL
        except IndexError as e:
            return return_types.RETURN_TYPE_INVALID_URL

    def add_to_queue(self, song_url):
        self.queue.append(song_url)

    async def check_queue(self, ctx):
        print(f"before: {self.queue}")
        self.queue.pop(0)
        print(f"after: {self.queue}")
        if len(self.queue) > 0:
            await self.play_song(ctx, self.queue[0])
        else:
            await ctx.send("Done playing songs.")


def setup(client):
    client.add_cog(Music(client))
