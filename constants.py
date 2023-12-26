import os, dotenv, tweepy
from datetime import datetime

BASE_PATH = os.path.realpath(os.path.abspath(os.path.dirname(__file__)))
ASSETS_PATH = os.path.join(BASE_PATH, "assets")
print(f"Assets path: {ASSETS_PATH}")
FONT_PATH = os.path.join(ASSETS_PATH, "Burbank.otf")

UTC_MIDNIGHT = datetime.fromisoformat(f"1970-01-01 00:01:00.000+00:00").astimezone().strftime("%H:%M")

dotenv.load_dotenv(os.path.join(BASE_PATH, ".env"))

LANG = os.getenv("LANGUAGE")
FORTNITEAPI_IO_KEY = os.getenv("FORTNITEAPI_IO_KEY")
CONTINUE_ON_CORRUPTED_IMAGE = os.getenv("CONTINUE_ON_CORRUPTED_IMAGE") in ("true", "1")
FALLBACK_IMAGE_FROM_FORTNITE_API = os.getenv("FALLBACK_IMAGE_FROM_FORTNITE_API") in ("true", "1")

TWITTER_ENABLED = os.getenv("TWITTER_ENABLED") in ("true", "1")
TWITTER_API = tweepy.Client(
    bearer_token=os.getenv("TWITTER_BEARER_TOKEN"),
    consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
    consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
    access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
    access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
)
TWITTER_API_V1 = tweepy.API(
    auth=tweepy.OAuthHandler(
        consumer_key=os.getenv("TWITTER_CONSUMER_KEY"),
        consumer_secret=os.getenv("TWITTER_CONSUMER_SECRET"),
        access_token=os.getenv("TWITTER_ACCESS_TOKEN"),
        access_token_secret=os.getenv("TWITTER_ACCESS_TOKEN_SECRET")
    )
)
        