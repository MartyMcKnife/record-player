import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError
from dotenv import load_dotenv
import os
import time

load_dotenv()

scope = "user-read-playback-state user-modify-playback-state user-library-read"

# generate our auth instance
spOauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT"),
    client_secret=os.getenv("SPOTIFY_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT"),
    scope=scope,
    open_browser=False,
)


class spotifyError(Exception):
    pass


def validateUser():
    tokenInfo = spOauth.get_cached_token()
    if tokenInfo:
        # already authenticated - return our spotify class
        # passing it like this means the library will do the heaving lifting of reauthentication
        try:
            return spotipy.Spotify(auth_manager=spOauth)
        except SpotifyOauthError:
            return False
            # something has gone reallly wrong - best to just try again
    else:
        return False


# get url to authorize ourselves
def getUrl():
    return spOauth.get_authorize_url()


# return our authorized token and store our code in cache
def authUser(returnUrl: str):
    code = spOauth.parse_auth_response_url(returnUrl)
    auth = spOauth.get_access_token(code)
    return spotipy.Spotify(auth=auth["access_token"])


def getSongInfo(sp):
    count = 0
    playing = None
    # keep looping until we have data to play from
    # if it has been 10 seconds, something has probably gone wrong so we throw an error to restart
    while not playing:
        if count >= 20:
            raise spotifyError("Unexpected error when reading from spotify")
        playing = sp.current_playback()
        time.sleep(0.5)
        count += 1

    track_name = playing["item"]["name"]
    artist_name = ", ".join([item["name"] for item in playing["item"]["artists"]])
    album_name = playing["item"]["album"]["name"]
    # send our processed data back
    return {
        "song_id": playing["item"]["id"],
        "track": {"name": track_name, "cur": track_name},
        "artists": {"name": artist_name, "cur": artist_name},
        "album": {"name": album_name, "cur": album_name},
        "total_duration": int(playing["item"]["duration_ms"]),
        "current_duration": int(playing["progress_ms"]),
    }
