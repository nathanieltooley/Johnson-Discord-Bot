import svc.utils as utils

from enums.bot_enums import ReturnTypes as return_types


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
            track_info = utils.SpotifyHelpers.get_track(utils.SpotifyHelpers.parse_id_out_of_url(self.url))

            self.title = track_info["name"]
            self.authors = utils.SpotifyHelpers.get_artist_names(track_info)

            self.props_set = True
        elif self.url_type == return_types.RETURN_TYPE_YOUTUBE_URL:
            info = utils.YoutubeHelpers.get_video_info(self.url)

            self.title = info["title"]
            self.authors = (info["creator"],)

            self.props_set = True

    def clear_props(self):
        self.title = ""
        self.authors = None
        self.props_set = False

