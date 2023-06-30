import constants

def post(image, caption):
    print(f"Posting. ({image}, {caption})")
    caption = caption.replace("\\n", "\n")

    if constants.TWITTER_ENABLED:
        print("Posting to Twitter.")
        _post_twitter_api(image, caption)
    
    print("Post complete.")

def _post_twitter_api(image, caption):
    if image != None:
        media = constants.TWITTER_API_V1.media_upload(image)

    constants.TWITTER_API.create_tweet(text=caption, media_ids=[media.media_id] if image != None else [])