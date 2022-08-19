import asyncio
import pprint
import random

import discord
import youtube_dl

from yt_dlp import YoutubeDL

import svc.utils as utils

from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice

from data_models.bot_dataclasses import QueuedSong
from enums.bot_enums import Enums as bot_enums
from enums.bot_enums import DiscordEnums as discord_enums
from enums.bot_enums import ReturnTypes as return_types


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.queue = []
        self.view_index = 0
        self.queue_message = None
        self.np_message = None
        self.johnson_broke = False
        self.paused = False

    """@cog_ext.cog_slash(name="start_playlist_vote",
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
                await utils.EmbedHelpers.send_message_embed(ctx, title="Playlist Vote Yes",
                                                            message=f"The vote on {track['name']} has passed! "
                                                                    f"It will be added to our playlist",
                                                            color=discord.Color.green())
                # Music.add_song_to_playlist(poll.song_url)
                poll.delete()
                return

            if not meets_vote_req:
                await utils.EmbedHelpers.send_message_embed(ctx, title="Playlist Vote Status",
                                                            message=f"{poll.current_votes} / {poll.required_votes} for "
                                                                    f"{track['name']}.")
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

            await utils.EmbedHelpers.send_message_embed(ctx, title="Playlist Vote No",
                                                        message=f"{ctx.author.mention} has voted no to adding "
                                                                f"{track['name']} to the playlist! Vote is over!",
                                                        color=discord.Color.red())
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

        await utils.EmbedHelpers.send_message_embed(ctx, title="Playlist Cancel",
                                                    message=f"{ctx.author.mention} "
                                                            f"has cancelled their poll over adding "
                                                            f"{track['name']} to the playlist! "
                                                            f"Vote is over!",
                                                    color=discord.Color.red())
        message = await ctx.channel.fetch_message(poll.poll_id)

        poll.delete()
        await message.delete()"""

    @cog_ext.cog_slash(
        name="play",
        description="Play a song!",
        options=[
            create_option(
                name="url",
                description="Valid URLS include Youtube URLS, Spotify Song URLs and Spotify Playlist URLs.",
                option_type=discord_enums.OPTION_TYPE_STRING.value,
                required=True,
            ),
            create_option(
                name="playnext",
                description="Play this song(s) after the current song is done.",
                option_type=discord_enums.OPTION_TYPE_BOOL.value,
                required=False
            )
        ],
        guild_ids=utils.Level.get_guild_ids()
    )
    @utils.Checks.rude_name_check()
    async def _play(self, ctx: SlashContext, url, playnext=False):
        await ctx.defer()

        url_type = Music.determine_url_type(url)
        if url_type == return_types.RETURN_TYPE_INVALID_URL:
            await utils.EmbedHelpers.send_message_embed(ctx, title="ERROR",
                                                        code_block="Invalid URL!",
                                                        color=discord.Color.red())
            return

        voice_client = await utils.VoiceClientManager.connect_to_member(self.client, ctx.author)

        # If we didn't connect, stop command
        if voice_client is None:
            return

        insert_index = 0
        if playnext:
            insert_index = 1

        if url_type == return_types.RETURN_TYPE_SPOTPLAYLIST_URL:
            playlist_tracks = utils.SpotifyHelpers.get_all_playlist_tracks(
                utils.SpotifyHelpers.parse_id_out_of_url(url))

            for top_track in playlist_tracks:
                track = top_track["track"]

                # fuck them
                if track["is_local"]:
                    continue

                self.add_to_queue(
                    song_url=track["external_urls"]["spotify"],
                    title=track["name"],
                    authors=utils.SpotifyHelpers.get_artist_names(track),
                    index=insert_index
                )

            await ctx.send(f"Queueing {len(playlist_tracks)} song(s).")
        else:
            try:
                utils.YoutubeHelpers.get_video_info(url)
                self.add_to_queue(url, index=insert_index)
            except Exception as e:
                await utils.EmbedHelpers.send_message_embed(ctx,
                                                            code_block=f"COULD NOT GET INFO. "
                                                                       f"PROBABLY AGE-RESTRICTED . . . SKIPPING",
                                                            color=discord.Color.red())
                return

        if voice_client.is_playing():
            await utils.EmbedHelpers.send_message_embed(ctx, message="Song currently playing. Will queue next song.")
            return

        try:
            await self.play_song(ctx, voice_client, self.queue[0])
        except Exception as e:
            await utils.EmbedHelpers.send_message_embed(ctx,
                                                        code_block=f"COULD NOT GET INFO. "
                                                                   f"PROBABLY AGE-RESTRICTED . . . SKIPPING",
                                                        color=discord.Color.red())
            await self.check_queue(ctx, voice_client)

    @cog_ext.cog_slash(
        name="connect",
        description="Have Johnson Bot connect to your voice channel. (Done automatically by /play!)",
        guild_ids=utils.Level.get_guild_ids()
    )
    @utils.Checks.rude_name_check()
    async def _connect(self, ctx: SlashContext):
        result = await self.join(ctx)

        if result == return_types.RETURN_TYPE_SUCCESSFUL_CONNECT:
            await ctx.send("Connected!", hidden=True)

    @cog_ext.cog_slash(
        name="disconnect",
        description="Disconnect the bot from a voice channel.",
        guild_ids=utils.Level.get_guild_ids()
    )
    @utils.Checks.rude_name_check()
    async def _disconnect(self, ctx: SlashContext):
        result = await utils.VoiceClientManager.disconnect(self.client)

        if result is None:
            await utils.EmbedHelpers.send_message_embed(ctx=ctx,
                                                        code_block="ERROR: Johnson Bot is not in a voice channel!",
                                                        color=discord.Color.red())
        else:
            await ctx.send("Disconnected!", hidden=True)

    @cog_ext.cog_slash(
        name="skip",
        description="Skips the song currently playing",
        guild_ids=utils.Level.get_guild_ids()
    )
    @utils.Checks.rude_name_check()
    async def _skip(self, ctx: SlashContext):
        voice_client = await utils.VoiceClientManager.get_current_vc(self.client)

        if voice_client:
            if self.paused:
                self.paused = False

            voice_client.stop()
            await ctx.send("Skipped!")
        else:
            await ctx.send("Couldn't Skip", hidden=True)

    @cog_ext.cog_slash(
        name="pause",
        description="Pauses the song currently playing",
        guild_ids=utils.Level.get_guild_ids()
    )
    async def _pause(self, ctx: SlashContext):
        voice_client = await utils.VoiceClientManager.get_current_vc(self.client)

        if voice_client and not self.paused:
            voice_client.pause()
            self.paused = True

            await ctx.send("Pausing!")
        elif voice_client and self.paused:
            await ctx.send("Song is already paused!", hidden=True)
        else:
            await ctx.send("Johnson Bot is not playing anything.", hidden=True)

    @cog_ext.cog_slash(
        name="resume",
        description="Resumes a paused song",
        guild_ids=utils.Level.get_guild_ids()
    )
    async def _resume(self, ctx: SlashContext):
        voice_client = await utils.VoiceClientManager.get_current_vc(self.client)

        if voice_client and self.paused:
            voice_client.resume()
            self.paused = False

            await ctx.send("Resuming!")
        elif voice_client and not self.paused:
            await ctx.send("Song is already resumed!", hidden=True)
        else:
            await ctx.send("Johnson Bot is not playing anything.", hidden=True)

    @cog_ext.cog_slash(
        name="queue",
        description="Show what songs are currently queued",
        options=[
            create_option(
                name="index",
                description="Shows the song at this index plus the next nine.",
                option_type=discord_enums.OPTION_TYPE_INT.value,
                required=False
            )
        ],
        guild_ids=utils.Level.get_guild_ids()
    )
    async def _queue(self, ctx: SlashContext, index=0):
        if self.queue is None or len(self.queue) == 0:
            await ctx.send("There is nothing queued", hidden=True)
            return

        if abs(index) >= len(self.queue):
            index = 0
        elif index < 0:
            index = len(self.queue) + index

        self.view_index = index

        embed = discord.Embed(
            title=F"Current Queue (Length: {len(self.queue)})",
            description=self.create_embed_description(),
        )

        embed.set_footer(text="Le Epic Queue")
        embed.set_thumbnail(url=bot_enums.BOT_AVATAR_URL.value)

        if self.queue_message is not None:
            self.queue_message = await utils.MessageHelpers.safe_message_delete(self.queue_message)

        self.queue_message = await ctx.send(embed=embed)

    @cog_ext.cog_slash(
        name="shuffle",
        description="Shuffles songs in the queue",
        guild_ids=utils.Level.get_guild_ids()
    )
    async def _shuffle(self, ctx: SlashContext):
        if self.queue is not None:
            currently_playing = self.queue.pop(0)
            random.shuffle(self.queue)
            self.queue.insert(0, currently_playing)
            await utils.EmbedHelpers.send_message_embed(ctx, message="Shuffling List")

    @cog_ext.cog_slash(
        name="clear_queue",
        description="Clears the queue.",
        guild_ids=utils.Level.get_guild_ids()
    )
    async def _clear_queue(self, ctx):
        if not self.queue == []:
            self.queue = []
            await ctx.send("Cleared.")

    @commands.command(aliases=["help_music"])
    async def music_help(self, ctx):
        help_message = ".play [song_url(Spotify, Youtube, Soundcloud)] [next]\n" \
                       "   - Play a song, type next after the url if you want to \n" \
                       "     play the song next\n" \
                       ".pause or .stop\n" \
                       "   - Pause what is playing, can be resumed with .resume or \n" \
                       "     .play\n" \
                       ".queue [index]\n" \
                       "   - View up to 10 songs that are queued\n" \
                       ".skip\n" \
                       "   - Skip\n" \
                       ".shuffle\n" \
                       "   - Shuffle\n" \
                       ".clear or .clear_queue\n" \
                       "   - Clear the queue\n" \
                       ".resume\n" \
                       "   - Resume\n" \
                       ".disconnect\n" \
                       "   - Kick Johnson Bot from the VC."

        await utils.EmbedHelpers.send_message_embed(ctx, title="Commands", code_block=help_message)

    async def join(self, ctx: SlashContext):
        if ctx.author.voice is None:
            await utils.EmbedHelpers.send_message_embed(ctx, message="You need to be in a voice channel.")
            return None

        await utils.VoiceClientManager.connect_to_member(self.client, ctx.author)
        return return_types.RETURN_TYPE_SUCCESSFUL_CONNECT

    async def play_song(self, ctx: SlashContext, voice_client, queued_song: QueuedSong):
        song_url = queued_song.url
        url_type = queued_song.url_type

        if not queued_song.props_set:
            queued_song.cache_properties()

        if url_type == return_types.RETURN_TYPE_SPOTIFY_URL:
            result = None
            tries = 5

            while True:
                result = utils.SpotifyHelpers.search_song_on_youtube(song_url)

                if result is None:
                    tries -= 1

                    # let try searching with only the title?
                    if tries <= 0:
                        await utils.EmbedHelpers.send_message_embed(ctx,
                                                                    code_block="Could not find song on youtube . . . SKIPPING")
                        await self.check_queue(ctx, voice_client)
                        return
                    else:
                        continue
                else:
                    utils.Logging.log("music_bot",
                                      f"Youtube search took {5 - tries} tries for {queued_song.title} - {queued_song.authors}")
                    break

            suffix = result["url_suffix"]

            song_url = utils.YoutubeHelpers.construct_url_from_suffix(suffix)

        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': "-vn"}
        ydl_options = {'format': 'bestaudio'}

        retries = 5

        utils.Logging.log("music_bot", f"Starting playback; url: {song_url}")
        with YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(song_url, download=False)

            # opus acodec
            # high quality

            audio_url = utils.YoutubeHelpers.find_best_audio_link(info['formats'], queued_song.url_type)

            if utils.Level.get_bot_level() == "DEBUG":
                utils.Logging.log("music_bot", f"Best Audio Link: {audio_url}")

            # url2 = info['formats'][0]['url']

            """if url2 is None:
                await ctx.send("COULD NOT PLAY MEDIA . . . SKIPPING")
                await self.check_queue(ctx)
                return

            if utils.Level.get_bot_level() == "DEBUG":
                utils.Logging.log("music_bot", f"Probe Url: {url2}")"""

            source = None

            # lots of 403 errors, don't know why
            while True:
                try:
                    source = await discord.FFmpegOpusAudio.from_probe(audio_url, method='fallback', **ffmpeg_options)
                    break
                except Exception as e:
                    retries -= 1

                    if retries <= 0:
                        break

            if source is None:
                await utils.EmbedHelpers.send_message_embed(ctx, code_block=f"COULD NOT PLAY {queued_song.title} . . . SKIPPING",
                                                            color=discord.Color.red())
                await self.check_queue(ctx, voice_client)
                return

            # we use asyncio because we can't use await in lambda
            voice_client.play(source,
                    after=lambda error: asyncio.run_coroutine_threadsafe(self.check_queue(ctx, voice_client), self.client.loop))

            if self.np_message is not None:
                self.np_message = await utils.MessageHelpers.safe_message_delete(self.np_message)

            if queued_song.url_type == return_types.RETURN_TYPE_SPOTIFY_URL:
                color = discord.Color.green()
            elif queued_song.url_type == return_types.RETURN_TYPE_SOUNDCLOUD_URL:
                color = discord.Color.orange()
            else:
                color = discord.Color.dark_red()

            self.np_message = await utils.EmbedHelpers.send_message_embed(ctx, "Now Playing",
                                                                          message=f"**{queued_song.title}** - "
                                                                                  f"_{utils.SpotifyHelpers.create_artist_string(queued_song.authors)}_",
                                                                          color=color
                                                                          )

    @staticmethod
    def add_song_to_playlist(song_url):
        utils.SpotifyHelpers.add_song_to_playlist(bot_enums.OUR_PLAYLIST_ID.value, song_url)

    @staticmethod
    def determine_url_type(song_url):
        # https://www.youtube.com/watch?v=_arqbQqq88M
        # https://youtu.be/U9qdhF7m80M
        # https://open.spotify.com/track/74wtYmeZuNS59vcNyQhLY5?si=3e55a2bd614d4e29
        # https://soundcloud.com/beanbubger/apoapsis/s-zoij7masq5J?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing
        # https://soundcloud.com/beanbubger/supersubset-v3

        segments = song_url.split("/")
        segments.reverse()

        try:
            if segments[1] == "www.youtube.com" or segments[1] == "youtu.be":
                return return_types.RETURN_TYPE_YOUTUBE_URL
            elif segments[2] == "open.spotify.com":
                if segments[1] == "track":
                    return return_types.RETURN_TYPE_SPOTIFY_URL
                elif segments[1] == "playlist":
                    return return_types.RETURN_TYPE_SPOTPLAYLIST_URL
                else:
                    return return_types.RETURN_TYPE_INVALID_URL
            elif segments[2] == "soundcloud.com" or segments[3] == "soundcloud.com":
                return return_types.RETURN_TYPE_SOUNDCLOUD_URL
            else:
                return return_types.RETURN_TYPE_INVALID_URL
        except IndexError as e:
            return return_types.RETURN_TYPE_INVALID_URL

    def add_to_queue(self, song_url, title="", authors=None, index=0):
        q_song = QueuedSong(url=song_url, url_type=Music.determine_url_type(song_url), title=title, authors=authors)

        if index == 0:
            self.queue.append(q_song)
        else:
            self.queue.insert(index, q_song)

    async def check_queue(self, ctx, voice_client):
        self.queue.pop(0)
        if len(self.queue) > 0:
            await self.play_song(ctx, voice_client, self.queue[0])
        else:
            if self.np_message is not None:
                self.np_message = await utils.MessageHelpers.safe_message_delete(self.np_message)
            if self.queue_message is not None:
                self.queue_message = await utils.MessageHelpers.safe_message_delete(self.queue_message)

            dp_message = await utils.EmbedHelpers.send_message_embed(ctx, message="Done Playing Songs.")
            await dp_message.delete(delay=10)

    def create_embed_description(self):
        max_songs = 10

        start = self.view_index
        end = self.view_index + max_songs

        if end > len(self.queue):
            end = len(self.queue)

        # grab the first ten songs and put them in a new list
        shown_songs = self.queue[self.view_index:self.view_index + max_songs]

        description_inner = ""

        i = 0
        for song in shown_songs:
            if not song.props_set:
                song.cache_properties()

            description_inner += f"{i + 1 + self.view_index}. " \
                                 f"{song.title} - {utils.SpotifyHelpers.create_artist_string(song.authors)} " \
                                 f"{'(NOW PLAYING)' if (i + self.view_index) == 0 else ''}\n"

            i += 1

        description_full = f"```fix\n{description_inner}```"

        return description_full


def setup(client):
    client.add_cog(Music(client))
