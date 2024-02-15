import os, shutil, math, pickle, time, glob
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime, timedelta

from bot_helpers import exception_helper, image_helper, request_helper, post_helper, strings_helper, rarity_helper
import constants

class ShopModule:
    _SHOP_IMAGE_WIDTH = 3000
    _RETURNING_ITEMS_IMAGE_WIDTH = 3000

    _SHOP_MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
    _TEMP_PATH = os.path.join(_SHOP_MODULE_PATH, "temp")
    _RESULT_PATH = os.path.join(_SHOP_MODULE_PATH, "result")
    _LAST_SHOP_UID_PATH = os.path.join(_SHOP_MODULE_PATH, "last_shop_uid.p")

    _API_SHOP_URL = "https://fortniteapi.io/v2/shop"
    _RETURN_COLOR = (247, 223, 61)

    def __init__(self):
        if not os.path.exists(self._RESULT_PATH):
            os.makedirs(self._RESULT_PATH)

    def register(self, schedule):
        self.schedule = schedule
        schedule.every(1).days.at(constants.UTC_MIDNIGHT).do(self.update)

    def on_exception(self):
        self.schedule.every(5).minutes.until(timedelta(minutes=6)).do(self.update)
    
    @exception_helper.catch_exceptions(on_exception=on_exception)
    def update(self):
        shop_json = request_helper.io_request(self._API_SHOP_URL, {"fields": "id,name,shopHistory,images"})
        shop_date = self._parse_shop_date(shop_json)
        shop_uid = shop_json['lastUpdate']['uid']
        if not self._has_new_shop(shop_uid): raise Exception("No new shop detected")

        print("New shop detected!")

        shop_image_path = os.path.join(self._RESULT_PATH, f'shop_{shop_date}.jpg')

        returning_items_files = self._generate_icons(shop_json, shop_date)
        shop_image = self._merge_shop()
        image_helper.compress_image(shop_image, shop_image_path)
        
        print("Shop generated successfully!")

        post_ids = self._post_image(shop_image_path, shop_date)
        pickle.dump(shop_uid, open(self._LAST_SHOP_UID_PATH, "wb"))

        if constants.POST_RETURNING_ITEMS_AS_RESPONSE and len(returning_items_files) > 0:
            returning_items_image_path = os.path.join(self._RESULT_PATH, f'returning_items_{shop_date}.jpg')

            returning_items_image = self._merge_returning_items(returning_items_files)
            image_helper.compress_image(returning_items_image, returning_items_image_path)

            self._post_returning_items_image(returning_items_image_path, post_ids)

        # Remove temp files
        shutil.rmtree(self._TEMP_PATH)

    def _parse_shop_date(self, shop_json):
        return shop_json['lastUpdate']['date'][:10]

    def _has_new_shop(self, shop_uid):
        last_shop_uid = (pickle.load(open(self._LAST_SHOP_UID_PATH, "rb")) 
                    if os.path.exists(self._LAST_SHOP_UID_PATH)
                        else None)

        return last_shop_uid != shop_uid

    def _generate_icons(self, shop_json, shop_date):
        returning_items_files = []
        sections = list(shop_json["currentRotation"].keys())
        shop_offers_json = shop_json['shop']

        # Create temp folder
        if os.path.exists(self._TEMP_PATH):
            shutil.rmtree(self._TEMP_PATH)
        os.mkdir(self._TEMP_PATH)

        # Load assets
        overlay_image = image_helper.from_path(os.path.join(constants.ASSETS_PATH, 'overlay.png'))
        new_badge = image_helper.from_path(os.path.join(constants.ASSETS_PATH, "new_badge.png"))

        for offer_i, offer_json in enumerate(shop_offers_json):
            is_bundle = offer_json['mainType'] == "bundle"
            main_id = ("bundle_" if is_bundle else "") + offer_json['mainId']
            offer_price = offer_json['price']['finalPrice']
            offer_section = offer_json['section']['id']

            shop_history = offer_json['granted'][0]['shopHistory'] if len(offer_json['granted']) > 0 else []

            last_seen = None
            if shop_history is not None and len(shop_history) >= 2:
                if shop_history[-1] == shop_date:
                    last_seen = shop_history[-2]
                else:
                    last_seen = shop_history[-1]
            
            if last_seen is not None:
                dateloop = datetime.strptime(last_seen, "%Y-%m-%d")
                current = datetime.strptime(shop_date, "%Y-%m-%d")
                seen_diff = current.date() - dateloop.date()
                days_gone = seen_diff.days
            else:
                days_gone = None

            # Try to get the Battle Royale display asset, if not, get the first one
            display_asset = next((display_asset for display_asset in offer_json['displayAssets'] if display_asset['primaryMode'] == 'BattleRoyale'), offer_json['displayAssets'][0]) \
                                    if len(offer_json['displayAssets']) > 0 else None
            item_icon = image_helper.get_item_image(display_asset['url'], main_id)

            item_background_url = display_asset.get("background_texture")
            if item_background_url is None:
                rarity_id = offer_json['rarity']['id']
                series_id = (offer_json.get('series') or {}).get('id', None)
                item_background = rarity_helper.get_background(rarity_id, series_id)
            else:
                item_background = image_helper.from_url(item_background_url)

            #Save Background
            icon_image = image_helper.with_background(item_icon, item_background)

            #Overlay
            icon_image.paste(overlay_image, (0, 0), overlay_image)

            if days_gone is None:
                icon_image.paste(new_badge, (0, 0), new_badge)

            item_name = offer_json['displayName']
            
            #Smaller text to fit image
            font = None
            font_size = 45
            while font is None or font.getlength(item_name) > 450:
                font = ImageFont.truetype(constants.FONT_PATH, font_size)
                font_size -= 2

            draw = ImageDraw.Draw(icon_image)
            draw.text((256, 423), item_name.upper(), font=font, fill='white', anchor='ms') #Writes display name

            info_text = strings_helper.STRINGS["new_item"]
            if days_gone is not None:
                info_text = strings_helper.STRINGS["item_gone_duration"].replace("{days}", str(days_gone))
            days_gone_text_color = (255, 255, 255) \
                if days_gone is None or days_gone < constants.RETURNING_ITEM_DAY_THRESHOLD \
            else self._RETURN_COLOR

            font = ImageFont.truetype(constants.FONT_PATH, 33)
            draw = ImageDraw.Draw(icon_image)
            draw.text((256, 463), info_text, font=font, fill=days_gone_text_color, anchor='ms') #Writes info text / date last seen

            font = ImageFont.truetype(constants.FONT_PATH, 40)
            draw = ImageDraw.Draw(icon_image)
            draw.text((256, 505), str(offer_price), font=font, fill='white', anchor='ms') #Writes price of offer

            section_number = sections.index(offer_section) if offer_section in sections else len(sections)

            #Save image
            item_file_name = f'{section_number}_{offer_i}_{main_id}.png'
            icon_image.save(os.path.join(self._TEMP_PATH, item_file_name))
            icon_image.close()

            if days_gone is not None and days_gone >= constants.RETURNING_ITEM_DAY_THRESHOLD:
                returning_items_files.append(item_file_name)

        # Free memory
        overlay_image.close()
        new_badge.close()

        print(f'Generated {len(shop_offers_json)} items from the {shop_date} item shop.')
        return returning_items_files

    def _merge_shop(self):
        offer_image_paths = sorted(glob.glob(os.path.join(self._TEMP_PATH, "*.png")))
        offer_count = len(offer_image_paths)
            
        column_count = math.ceil(math.sqrt(offer_count))
        row_count = math.ceil(offer_count / column_count)

        offer_image_size = self._SHOP_IMAGE_WIDTH // column_count
        shop_image_size = (offer_image_size * column_count, offer_image_size * row_count)

        shop_image = Image.new("RGB", shop_image_size)
        shop_background = Image.open(os.path.join(constants.ASSETS_PATH, "background.png")).convert("RGBA").resize(shop_image_size)
        shop_image.paste(shop_background, (0, 0))
        shop_background.close() # Free memory

        for i, offer_image_path in enumerate(offer_image_paths):
            offer_image = image_helper.from_path(offer_image_path, size=offer_image_size)
            shop_image.paste(
                offer_image,
                ((0 + ((i % column_count) * offer_image.width)),
                    (0 + ((i // column_count) * offer_image.height)))
            )
            offer_image.close() # Free memory
        
        #Credits
        try:
            credit_images = sorted(glob.glob(os.path.join(constants.ASSETS_PATH, "ads/*.png")))
            spare_cells = column_count * row_count - offer_count
            for i in range(spare_cells):
                if i >= len(credit_images):
                    continue

                credits_image = image_helper.from_path(credit_images[i], size=offer_image_size)
                shop_image.paste(credits_image, (shop_image_size[0] - offer_image_size * (i + 1), shop_image_size[1] - offer_image_size), credits_image)
                credits_image.close() # Free memory
        except Exception as e:
            print(f"Error generating credits ({e})")

        return shop_image

    def _post_image(self, image_path, shop_date):
        split_date = shop_date.split('-')
        reformatted_date = f'{split_date[2]}/{split_date[1]}/{split_date[0]}'

        return post_helper.post(
            image_path,
            strings_helper.STRINGS["shop_post_caption"].replace('{date}', reformatted_date)
        )
    
    def _merge_returning_items(self, returning_items_files):
        column_count = math.ceil(math.sqrt(len(returning_items_files)))
        row_count = math.ceil(len(returning_items_files) / column_count)

        item_image_size = self._RETURNING_ITEMS_IMAGE_WIDTH // column_count
        returning_items_image_size = (item_image_size * column_count, item_image_size * row_count)

        returning_items_image = Image.new("RGB", returning_items_image_size)
        background = Image.open(os.path.join(constants.ASSETS_PATH, "background.png")).convert("RGBA").resize(returning_items_image_size)
        returning_items_image.paste(background, (0, 0))
        background.close() # Free memory

        for i, item_image_path in enumerate(returning_items_files):
            item_image_path = os.path.join(self._TEMP_PATH, item_image_path)
            
            item_image = image_helper.from_path(item_image_path, size=item_image_size)
            returning_items_image.paste(
                item_image,
                ((0 + ((i % column_count) * item_image.width)),
                    (0 + ((i // column_count) * item_image.height)))
            )
            item_image.close() # Free memory

        return returning_items_image
    
    def _post_returning_items_image(self, image_path, response_to):
        return post_helper.post(
            image_path,
            strings_helper.STRINGS["returning_items_caption"],
            response_to
        )
