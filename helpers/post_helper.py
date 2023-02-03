import constants

def post_image(image, caption):
    if constants.TWITTER_ENABLED:
        print("Posting to Twitter.")
        _post_twitter(image, caption)

def _post_twitter(image, caption):
    media = constants.TWITTER_API.media_upload(image)
    constants.TWITTER_API.update_status(caption, media_ids=[media.media_id])