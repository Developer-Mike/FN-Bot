import constants

def post(image, caption, response_to={}):
    print(f"Posting. ({image}, {caption}, {response_to})")
    caption = caption.replace("\\n", "\n")

    post_ids = {}

    if constants.TWITTER_ENABLED:
        print("Posting to Twitter.")
        post_ids["twitter"] = _post_twitter_api(image, caption, response_to.get("twitter"))
    
    print("Post complete.")
    return post_ids

def _post_twitter_api(image, caption, response_to=None):
    media_ids = [constants.TWITTER_API_V1.media_upload(image).media_id] if image != None else None
    tweet = constants.TWITTER_API.create_tweet(text=caption, media_ids=media_ids, in_reply_to_tweet_id=response_to)

    return tweet.data.get("id")