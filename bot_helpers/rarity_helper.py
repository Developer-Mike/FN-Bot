from bot_helpers import image_helper

RARITY_COLORS = {
    "Common": "https://media.fortniteapi.io/images/rarities/v2/rarity_common.png",
    "Epic": "https://media.fortniteapi.io/images/rarities/v2/rarity_epic.png",
    "Legendary": "https://media.fortniteapi.io/images/rarities/v2/rarity_legendary.png",
    "Mythic": "https://media.fortniteapi.io/images/rarities/v2/rarity_mythic.png",
    "Rare": "https://media.fortniteapi.io/images/rarities/v2/rarity_rare.png",
    "Transcendent": "https://media.fortniteapi.io/images/rarities/v2/rarity_transcendent.png",
    "Uncommon": "https://media.fortniteapi.io/images/rarities/v2/rarity_uncommon.png",

    "CUBESeries": "https://media.fortniteapi.io/images/rarities/v2/T-Cube-Background.png",
    "DCUSeries": "https://media.fortniteapi.io/images/rarities/v2/T-BlackMonday-Background.png",
    "FrozenSeries": "https://media.fortniteapi.io/images/rarities/v2/T_Ui_LavaSeries_Frozen.png",
    "CreatorCollabSeries": "https://media.fortniteapi.io/images/rarities/v2/T_Ui_CreatorsCollab_Bg.png",
    "LavaSeries": "https://media.fortniteapi.io/images/rarities/v2/T_Ui_LavaSeries_Bg.png",
    "MarvelSeries": "https://media.fortniteapi.io/images/rarities/v2/Marvel.png",
    "PlatformSeries": "https://media.fortniteapi.io/images/rarities/v2/platformseries.png",
    "ShadowSeries": "https://media.fortniteapi.io/images/rarities/v2/T_Ui_LavaSeries_Shadow.png",
    "SlurpSeries": "https://media.fortniteapi.io/images/rarities/v2/Slurp.png",
    "ColumbusSeries": "https://media.fortniteapi.io/images/rarities/v2/ColumbusSeries.png"
}

def get_background(rarity_id, series_id):
    background_url = RARITY_COLORS.get(series_id, None)

    if background_url is None:
        background_url = RARITY_COLORS.get(rarity_id, None)

        if background_url is None:
            background_url = RARITY_COLORS[RARITY_COLORS.keys()[0]]

    return image_helper.from_url(background_url, mode='RGB')