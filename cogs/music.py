import asyncio
import random

import discord

from yt_dlp import YoutubeDL

from discord.ext import commands
from discord import app_commands

from data_models.music import BaseSong, YDLSong, SpotifySong, SoundcloudSong
from enums.bot_enums import Enums as bot_enums
from enums.bot_enums import ReturnTypes as return_types

from utils import messaging, vcm, jspotify, youtube, jlogging, level

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

    @app_commands.command(
        name="play",
        description="Play a song!"
    )
    @app_commands.describe(url="Valid URLS include Youtube URLS, Spotify Song URLs and Spotify Playlist URLs.")
    @app_commands.describe(playnext="Play this song(s) after the current song is done.")
    async def _play(self, interaction: discord.Interaction, url: str, playnext: bool = False):

        song_type = Music.determine_song_type(url)

        if song_type == return_types.RETURN_TYPE_INVALID_URL:
            await messaging.respond_embed(interaction, title="ERROR",
                                                        code_block="Invalid URL!",
                                                        color=discord.Color.red())
            return

        await messaging.defer(interaction)

        voice_client = await vcm.connect_to_member(self.client, interaction.user)

        # If we didn't connect, stop command
        if voice_client is None:
            return

        insert_index = 0
        if playnext:
            insert_index = 1

        if Music.is_playlist_url(url):
            playlist_tracks = jspotify.get_all_playlist_tracks(
                jspotify.parse_id_out_of_url(url))

            for top_track in playlist_tracks:
                track = top_track["track"]

                # fuck them
                if track["is_local"]:
                    continue

                self.add_to_queue(
                    song_url=track["external_urls"]["spotify"],
                    title=track["name"],
                    authors=jspotify.get_artist_names(track),
                    index=insert_index
                )

            await interaction.followup.send(f"Queueing {len(playlist_tracks)} song(s).")
        else:
            self.add_to_queue(song_type, index=insert_index)

        if voice_client.is_playing():
            await messaging.respond(interaction, message="Song currently playing. Will queue next song.")
            return

        try:
            await self.play_song(interaction, voice_client, self.queue[0])
        except Exception as e:
            jlogging.error("__music__", e)
            await messaging.respond_embed(interaction,
                                                        code_block=f"COULD NOT GET INFO. "
                                                                   f"PROBABLY AGE-RESTRICTED . . . SKIPPING",
                                                        color=discord.Color.red())
            await self.check_queue(interaction, voice_client)

    @app_commands.command(
        name="connect",
        description="Have Johnson Bot connect to your voice channel. (Done automatically by /play!)"
    )
    async def _connect(self, interaction: discord.Interaction):
        result = await self.join(interaction)

        if result == return_types.RETURN_TYPE_SUCCESSFUL_CONNECT:
            await interaction.response.send_message("Connected!", ephemeral=True)

    @app_commands.command(
        name="disconnect",
        description="Disconnect the bot from a voice channel."
    )
    async def _disconnect(self, interaction: discord.Interaction):
        result = await vcm.disconnect(self.client)

        if result is None:
            await messaging.respond_embed(interaction,
                                                        code_block="ERROR: Johnson Bot is not in a voice channel!",
                                                        color=discord.Color.red())
        else:
            await messaging.respond(interaction, "Disconnected!")

    @app_commands.command(
        name="skip",
        description="Skips the song currently playing"
    )
    async def _skip(self, interaction: discord.Interaction):
        voice_client = await vcm.get_current_vc(self.client)

        if voice_client:
            if self.paused:
                self.paused = False

            voice_client.stop()
            await interaction.response.send_message("Skipped!")
        else:
            await interaction.response.send_message("Couldn't Skip", ephemeral=True)

    @app_commands.command(
        name="pause",
        description="Pauses the song currently playing"
    )
    async def _pause(self, interaction: discord.Interaction):
        voice_client = await vcm.get_current_vc(self.client)

        if voice_client and not self.paused:
            voice_client.pause()
            self.paused = True

            await interaction.response.send_message("Pausing!")
        elif voice_client and self.paused:
            await interaction.response.send_message("Song is already paused!", ephemeral=True)
        else:
            await interaction.response.send_message("Johnson Bot is not playing anything.", ephemeral=True)

    @app_commands.command(
        name="resume",
        description="Resumes a paused song"
    )
    async def _resume(self, interaction: discord.Interaction):
        voice_client = await vcm.get_current_vc(self.client)

        if voice_client and self.paused:
            voice_client.resume()
            self.paused = False

            await interaction.response.send_message("Resuming!")
        elif voice_client and not self.paused:
            await interaction.response.send_message("Song is already resumed!", ephemeral=True)
        else:
            await interaction.response.send_message("Johnson Bot is not playing anything.", ephemeral=True)

    @app_commands.command(
        name="shuffle",
        description="Shuffles songs in the queue"
    )
    async def _shuffle(self, interaction: discord.Interaction):
        if self.queue is not None:
            currently_playing = self.queue.pop(0)
            random.shuffle(self.queue)
            self.queue.insert(0, currently_playing)
            await messaging.respond(interaction, message="Shuffling List")

    @app_commands.command(
        name="queue",
        description="Show what songs are currently queued"
    )
    async def _queue(self, interaction: discord.Interaction, index: int = 0):
        if self.queue is None or len(self.queue) == 0:
            await interaction.response.send_message("There is nothing queued", ephemeral=True)
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
            self.queue_message = await messaging.safe_message_delete(self.queue_message)

        self.queue_message = await interaction.followup.send(embed=embed, wait=True)

    @app_commands.command(
        name="clear_queue",
        description="Clears the queue."
    )
    async def _clear_queue(self, interaction: discord.Interaction):
        if not self.queue == []:
            self.queue = []
            await interaction.response.send_message("Cleared.")

    @app_commands.command(
        name="jump",
        description="Jumps to a song in the queue."
    )
    async def _jump(self, interaction: discord.Interaction, index: int, skip: bool = True):
        if index == 0:
            return

        if index > len(self.queue):
            index = len(self.queue) - 1

        for i in range(index):
            self.queue.pop(i)

        vc = await vcm.get_current_vc(self.client)

        vc.stop()

    async def join(self, interaction: discord.Interaction):
        if interaction.user.voice is None:
            await messaging.respond(interaction, message="You need to be in a voice channel.")
            return None

        await vcm.connect_to_member(self.client, interaction.user)
        return return_types.RETURN_TYPE_SUCCESSFUL_CONNECT

    async def play_song(self, interaction: discord.Interaction, voice_client, queued_song: BaseSong):

        if queued_song.flagged:
            await messaging.respond_embed(interaction, code_block="Could not find song on youtube . . . SKIPPING")
            await self.check_queue(interaction, voice_client)
            return   
               
        ffmpeg_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                          'options': "-vn"}
        ydl_options = {'format': 'bestaudio'}

        jlogging.log("music_bot", f"Starting playback; url: {queued_song.url}")
        with YoutubeDL(ydl_options) as ydl:
            info = ydl.extract_info(queued_song.url, download=False)

            # opus acodec
            # high quality

            audio_url = youtube.find_best_audio_link(info['formats'], queued_song.url)

            if level.get_bot_level() == "DEBUG":
                jlogging.log("music_bot", f"Best Audio Link: {audio_url}")

            source = None

            # lots of 403 errors, don't know why
            retries = 5
            while True:
                try:
                    source = await discord.FFmpegOpusAudio.from_probe(audio_url, method='fallback', **ffmpeg_options)
                    break
                except Exception as e:
                    retries -= 1

                    if retries <= 0:
                        break

            if source is None:
                await messaging.respond_embed(interaction, code_block=f"COULD NOT PLAY {queued_song.title} . . . SKIPPING",
                                                            color=discord.Color.red())
                await self.check_queue(interaction, voice_client)
                return

            # we use asyncio because we can't use await in lambda
            voice_client.play(source,
                    after=lambda error: asyncio.run_coroutine_threadsafe(self.check_queue(interaction, voice_client), self.client.loop))

            if self.np_message is not None:
                self.np_message = await messaging.safe_message_delete(self.np_message)

            self.np_message = await messaging.respond_embed(interaction, "Now Playing",
                                                                          message=f"**{queued_song.title}** - "
                                                                                  f"_{jspotify.create_artist_string(queued_song.authors)}_",
                                                                          color=queued_song.color()
                                                                          )

    @staticmethod
    def add_song_to_playlist(song_url):
        jspotify.add_song_to_playlist(bot_enums.OUR_PLAYLIST_ID.value, song_url)

    @staticmethod
    def determine_song_type(song_url):
        # https://www.youtube.com/watch?v=_arqbQqq88M
        # https://youtu.be/U9qdhF7m80M
        # https://open.spotify.com/track/74wtYmeZuNS59vcNyQhLY5?si=3e55a2bd614d4e29
        # https://soundcloud.com/beanbubger/apoapsis/s-zoij7masq5J?utm_source=clipboard&utm_medium=text&utm_campaign=social_sharing
        # https://soundcloud.com/beanbubger/supersubset-v3

        segments = song_url.split("/")
        segments.reverse()

        try:
            if segments[1] == "www.youtube.com" or segments[1] == "youtu.be":
                return YDLSong(song_url)
            elif segments[2] == "open.spotify.com":
                if segments[1] == "track":
                    return SpotifySong(song_url)
                else:
                    return return_types.RETURN_TYPE_INVALID_URL
            elif segments[2] == "soundcloud.com" or segments[3] == "soundcloud.com":
                return SoundcloudSong(song_url)
            else:
                return return_types.RETURN_TYPE_INVALID_URL
        except IndexError as e:
            return return_types.RETURN_TYPE_INVALID_URL
        
    @staticmethod
    def is_playlist_url(url):
        segments = url.split("/")
        segments.reverse()

        try:
            if segments[2] == "open.spotify.com":
                if segments[1] == "playlist":
                    return True
        except IndexError as e:
            return False
        
        return False

    def add_to_queue(self, song: BaseSong, index):
        song.get_song_properties()

        if index == 0:
            self.queue.append(song)
        else:
            self.queue.insert(index, song)

    async def check_queue(self, interaction: discord.Interaction, voice_client):
        self.queue.pop(0)
        if len(self.queue) > 0:
            await self.play_song(interaction, voice_client, self.queue[0])
        else:
            if self.np_message is not None:
                self.np_message = await messaging.safe_message_delete(self.np_message)
            if self.queue_message is not None:
                self.queue_message = await messaging.safe_message_delete(self.queue_message)

            dp_message = await messaging.respond(interaction, message="Done Playing Songs.")
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
                                 f"{song.title} - {jspotify.create_artist_string(song.authors)} " \
                                 f"{'(NOW PLAYING)' if (i + self.view_index) == 0 else ''}\n"

            i += 1

        description_full = f"```fix\n{description_inner}```"

        return description_full


async def setup(client):
    await client.add_cog(Music(client), guilds=level.get_guild_objects())
