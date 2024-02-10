import os, dotenv, tweepy
from datetime import datetime

def _get_env_bool(env_name):
    return os.getenv(env_name) in ("true", "1")

BASE_PATH = os.path.realpath(os.path.abspath(os.path.dirname(__file__)))
ASSETS_PATH = os.path.join(BASE_PATH, "assets")
print(f"Assets path: {ASSETS_PATH}")
FONT_PATH = os.path.join(ASSETS_PATH, "Burbank.otf")

UTC_MIDNIGHT = datetime.fromisoformat(f"1970-01-01 00:01:00.000+00:00").astimezone().strftime("%H:%M")

dotenv.load_dotenv(os.path.join(BASE_PATH, ".env"))

LANG = os.getenv("LANGUAGE")
FORTNITEAPI_IO_KEY = os.getenv("FORTNITEAPI_IO_KEY")
CONTINUE_ON_CORRUPTED_IMAGE = _get_env_bool("CONTINUE_ON_CORRUPTED_IMAGE")
FALLBACK_IMAGE_FROM_FORTNITE_API = _get_env_bool("FALLBACK_IMAGE_FROM_FORTNITE_API")

POST_RETURNING_ITEMS_AS_RESPONSE = _get_env_bool("POST_RETURNING_ITEMS_AS_RESPONSE")
RETURNING_ITEM_DAY_THRESHOLD = int(os.getenv("RETURNING_ITEM_DAY_THRESHOLD"))

TWITTER_ENABLED = _get_env_bool("TWITTER_ENABLED")
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
        