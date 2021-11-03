import discord
import svc.utils as utils

from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option, create_choice


class Music(commands.Cog):

    def __init__(self, client):
        self.client = client

    @cog_ext.cog_slash(name="start_playlist_vote",
                       description="Start a vote to add a song to Our Playlist :) "
                                   "(Must have a link to song on spotify).",
                       options=[
                           create_option(
                               name="songurl",
                               description="A link to a song on spotify that you wish to add (ex. https://open.spotify.com/track/[track_id])",
                               option_type=3,
                               required=True
                           )
                       ],
                       guild_ids=utils.Level.get_guild_ids())
    async def _add_to_playlist(self, ctx: SlashContext, song_url):

        await ctx.defer()
        does_url_pass = utils.SpotifyHelpers.verify_spotify_url(song_url, "track")

        if does_url_pass is None:
            await ctx.send("Make sure you submit a spotify link. For example: *https://open.spotify.com/track/33i4H7iDxIes1d8Nd0S3QF?si=aa73a3fc629140c1*")

        if does_url_pass:
            embed = discord.Embed(
                title="PLAYLIST VOTE",
                description="Those who are eligible: vote on this song to be in 'our playlist :)'",
                color=discord.Color.green()
            )



            await ctx.send(song_url)

        elif not does_url_pass:
            await ctx.send("Make sure you submit a song link and not a playlist link. For example: https://open.spotify.com/**track**/")


def setup(client):
    client.add_cog(Music(client))
