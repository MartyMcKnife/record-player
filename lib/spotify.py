import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyOauthError
from dotenv import load_dotenv
import os

load_dotenv()

scope = (
    "user-read-playback-state user-modify-playback-state user-library-read"
)

# generate our auth instance
spOauth = SpotifyOAuth(
    client_id=os.getenv("SPOTIFY_CLIENT"),
    client_secret=os.getenv("SPOTIFY_SECRET"),
    redirect_uri=os.getenv("SPOTIFY_REDIRECT"),
    scope=scope,
    open_browser=False,
)


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
    return spOauth.get_access_token(code)
