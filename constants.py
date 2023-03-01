import os, dotenv, tweepy
from datetime import datetime

BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ASSETS_PATH = os.path.join(BASE_PATH, "assets")
FONT_PATH = os.path.join(ASSETS_PATH, "Burbank.otf")

UTC_MIDNIGHT = datetime.fromisoformat(f"1970-01-01 00:10:00.000+00:00").astimezone().strftime("%H:%M")

dotenv.load_dotenv(os.path.join(BASE_PATH, ".env"))

LANG = os.getenv("LANG")
FORTNITEAPI_IO_KEY = os.getenv("FORTNITEAPI_IO_KEY")
CONTINUE_ON_CORRUPTED_IMAGE = os.getenv("CONTINUE_ON_CORRUPTED_IMAGE") in ("true", "1")

VIRTUAL_DISPLAY = os.getenv("VIRTUAL_DISPLAY") in ("true", "1")
CHROMEDRIVER_PATH = os.path.join(BASE_PATH, os.getenv("CHROMEDRIVER_PATH"))

TWITTER_ENABLED = os.getenv("TWITTER") in ("true", "1")
USE_TWITTER_API = os.getenv("USE_TWITTER_API") in ("true", "1")
if TWITTER_ENABLED:
    if USE_TWITTER_API:
        _TWITTER_AUTH = tweepy.OAuthHandler(os.getenv("TWITTER_CONSUMER_KEY"), os.getenv("TWITTER_CONSUMER_SECRET"))
        _TWITTER_AUTH.set_access_token(os.getenv("TWITTER_ACCESS_TOKEN"), os.getenv("TWITTER_ACCESS_SECRET"))

        TWITTER_API = tweepy.API(_TWITTER_AUTH)
    else:
        TWITTER_USERNAME = os.getenv("TWITTER_USERNAME")
        TWITTER_EMAIL = os.getenv("TWITTER_EMAIL")
        TWITTER_PASSWORD = os.getenv("TWITTER_PASSWORD")
        