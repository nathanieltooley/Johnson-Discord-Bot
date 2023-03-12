import utils.jlogging as jlogging
import spotipy
import datetime

from youtube_search import YoutubeSearch
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

def create_spotify_object():
    scope = "playlist-modify-public"

    sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
    jlogging.log(__name__, "Spotify Client Created!")

    return sp


def create_auth_spotify_object():
    scope = "playlist-modify-private"
    cache = ".spotipyoauthcache"

    sp_oauth = SpotifyOAuth(scope=scope, cache_path=cache)
    url = sp_oauth.get_authorize_url()
    # code = sp_oauth.parse_response_code(url)

    jlogging.log(__name__, f"url: {url}")
    # Logging.log(__name__, f"code: {code}")
    jlogging.log(__name__, f"auth: {sp_oauth.get_authorize_url()}")

    token = sp_oauth.get_access_token(url)
    sp = spotipy.Spotify(auth=token['access_token'])

    return sp

class SpotifyClient:    
    spotify = create_spotify_object()
    auth_spotify = None # SpotifyCreator.create_auth_spotify_object()

    
def get_all_playlist_tracks(playlist_id='6yO77cQ0JTMKuNxLh47oLX'):
    my_user_id = "yallmindifiyeet"

    results = SpotifyClient.spotify.user_playlist_tracks(my_user_id, playlist_id)
    tracks = results['items']

    while results['next']:
        results = SpotifyClient.spotify.next(results)
        tracks.extend(results['items'])

    return tracks


def get_track(id):
    return SpotifyClient.spotify.track(id)


def get_length_of_playlist():
    my_user_id = "yallmindifiyeet"
    playlist_id = '6yO77cQ0JTMKuNxLh47oLX'

    results = SpotifyClient.spotify.user_playlist_tracks(my_user_id, playlist_id)
    return results['total']


def parse_date(date_string):
    return datetime.datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%SZ")


def determine_diff(tracks, songs, check_updated):
    songs_in_tracks = []
    songs_gone = []

    for song in songs:
        found = False
        for track in tracks:
            if song == track['track']['id']: # song.name == track['track']['name'] and song.artists[0] == track['track']['artists'][0]['name']:
                songs_in_tracks.append(song)
                found = True

                break

        if not found:
            songs_gone.append(song)

    tracks_added = []

    for track in tracks:
        parsed_date = parse_date(track['added_at'])

        td = check_updated - parsed_date

        if td.total_seconds() < 0:
            tracks_added.append(track)

    return songs_gone, tracks_added


def create_artist_string(artists):
    artist_string = ""

    for artist in artists:
        if artist == artists[-1]:
            artist_string += artist
        else:
            artist_string += f"{artist}, "

    return artist_string


def verify_spotify_url(url, desired_type):
    # ex. "https://open.spotify.com/track/33i4H7iDxIes1d8Nd0S3QF?si=aa73a3fc629140c1"

    # remove https://
    pre_split = url[8: len(url)]

    sections = pre_split.split('/')

    # three responses: correct form, incorrect type, not a spotify link (in that order)
    try:
        domain_name = sections[0]
        spotify_type = sections[1]

        if spotify_type == desired_type:
            return True
        else:
            return False

    except IndexError:
        return None


def parse_id_out_of_url(song_url):
    # https://open.spotify.com/track/1bt443XPmX5ZG5DjhMJ8Rh?si=f6f953ba6c594500
    sections = song_url.split('/')
    end = sections[-1]

    if "?" in end:
        q_pos = end.find("?")
        return end[0: q_pos]
    else:
        return end


def get_album_art_url(track):
    return track['album']['images'][0]['url']


def add_song_to_playlist(playlist_id, song_url):
    SpotifyClient.auth_spotify.user_playlist_add_tracks("yallmindifiyeet", playlist_id, [SpotifyClient.parse_id_out_of_url(song_url)])


def is_song_in_playlist(playlist_id, song_url):
    tracks = SpotifyClient.get_all_playlist_tracks(playlist_id)

    for track in tracks:
        if SpotifyClient.parse_id_out_of_url(song_url) == track['track']['id']:
            return True

    return False


def get_artist_names(track_info):
    artist_names = []

    for artist in track_info['artists']:
        artist_names.append(artist['name'])

    return artist_names


def search_song_on_youtube(song_url, just_title=False):
    track_info = get_track(parse_id_out_of_url(song_url))

    artists = get_artist_names(track_info)

    search_query = ""

    if just_title:
        search_query = f"{track_info['name']}"
    else:
        search_query = f"{track_info['name']} {create_artist_string(artists)}"

    search_results = YoutubeSearch(search_query).to_dict()

    return determine_best_search_result(search_results)


def determine_best_search_result(search_results: dict):
    if search_results is None or len(search_results) == 0:
        return None

    return search_results[0]


def get_all_album_tracks(album_id):
    album_page = SpotifyClient.spotify.album_tracks(album_id)
    tracks = album_page['items']

    while album_page['next']:
        t = SpotifyClient.spotify.next(album_page)
        tracks.extend(t)