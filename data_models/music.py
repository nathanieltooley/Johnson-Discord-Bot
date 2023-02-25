from enums.bot_enums import ReturnTypes as return_types
from utils import jspotify, youtube
from abc import ABC, abstractmethod

class QueuedSong:

    def __init__(self, url, url_type, title="", authors=None):
        self.url = url
        self.url_type = url_type
        self.title = title
        self.authors = authors

        if not title == "" and authors is not None:
            self.props_set = True
        else:
            self.props_set = False

    def cache_properties(self):
        if self.url_type == return_types.RETURN_TYPE_SPOTIFY_URL:
            track_info = jspotify.get_track(jspotify.parse_id_out_of_url(self.url))

            self.title = track_info["name"]
            self.authors = jspotify.get_artist_names(track_info)

            self.props_set = True
        else:
            info = youtube.get_video_info(self.url)

            self.title = info["title"]

            # I put them in a tuple because otherwise the author string function will count each character as an author
            # ex. If the uploader's name is Johnson then it would be displayed "J, o, h, n, s, o, n" if not in a tuple
            try:
                self.authors = (info["creator"],)
            except KeyError:
                self.authors = (info["uploader"],)

            self.props_set = True

    def clear_props(self):
        self.title = ""
        self.authors = None
        self.props_set = False