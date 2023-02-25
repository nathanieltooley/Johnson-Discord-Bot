import discord

from enums.bot_enums import ReturnTypes as return_types
from utils import jspotify, youtube
from abc import ABC, abstractmethod
from typing import List

class BaseSong(ABC):

    def __init__(self, url: str) -> None:
        self.url = url

    @abstractmethod
    def get_song_properties(self) -> None:
        raise NotImplementedError
    
    @abstractmethod
    def color(self) -> discord.Color:
        raise NotImplementedError
    
class YDLSong(BaseSong):

    def get_song_properties(self) -> None:
        info = youtube.get_video_info(self.url)

        self.title = info["title"]

        # I put them in a tuple because otherwise the author string function will count each character as an author
        # ex. If the uploader's name is Johnson then it would be displayed "J, o, h, n, s, o, n" if not in a tuple
        try:
            self.authors = (info["creator"],)
        except KeyError:
            self.authors = (info["uploader"],)

    def color(self) -> discord.Color:
        return discord.Color.red()
    
class SoundcloudSong(YDLSong):
    
    def color(self) -> discord.Color:
        return discord.Color.orange()
    
class SpotifySong(BaseSong):
    
    def get_song_properties(self) -> None:
        track_info = jspotify.get_track(jspotify.parse_id_out_of_url(self.url))

        self.title = track_info["name"]
        self.authors = jspotify.get_artist_names(track_info)

    def color(self) -> discord.Color:
        return discord.Color.green()