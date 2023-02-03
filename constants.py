import os, dotenv, tweepy

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_PATH, "assets")
FONT_PATH = os.path.join(ASSETS_PATH, "Burbank.otf")

dotenv.load_dotenv(os.path.join(BASE_PATH, ".env"))

LANG = os.getenv("LANG")
FORTNITEAPI_IO_KEY = os.getenv("FORTNITEAPI_IO_KEY")

TWITTER_ENABLED = os.getenv("TWITTER") in ("true", "1")
if TWITTER_ENABLED:
    _TWITTER_AUTH = tweepy.OAuthHandler(os.getenv("TWITTER_CONSUMER_KEY"), os.getenv("TWITTER_CONSUMER_SECRET"))
    _TWITTER_AUTH.set_access_token(os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_SECRET"))

    TWITTER_API = tweepy.API(_TWITTER_AUTH)