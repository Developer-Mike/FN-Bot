import os, shutil, math, pickle, time, glob
from PIL import Image, ImageFont, ImageDraw
from datetime import datetime, timedelta

from bot_helpers import exception_helper, image_helper, request_helper, post_helper, strings_helper, rarity_helper
import constants

class ShopModule:
    _SHOP_IMAGE_WIDTH = 3000

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

        self._generate_icons(shop_json, shop_date)
        shop_image = self._merge_shop()
        self._compress_image(shop_image, shop_date)
        
        print("Shop generated successfully!")
        shutil.rmtree(self._TEMP_PATH)

        self._post_image(shop_date)
        
        pickle.dump(shop_uid, open(self._LAST_SHOP_UID_PATH, "wb"))
        
    def _parse_shop_date(self, shop_json):
        return shop_json['lastUpdate']['date'][:10]

    def _has_new_shop(self, shop_uid):
        last_shop_uid = (pickle.load(open(self._LAST_SHOP_UID_PATH, "rb")) 
                    if os.path.exists(self._LAST_SHOP_UID_PATH)
                        else None)

        return last_shop_uid != shop_uid

    def _generate_icons(self, shop_json, shop_date):
        sections = {section:i for i, section in enumerate(shop_json["currentRotation"].keys())}
        shop_offers_json = shop_json['shop']

        # Create temp folder
        if os.path.exists(self._TEMP_PATH):
            shutil.rmtree(self._TEMP_PATH)
        os.mkdir(self._TEMP_PATH)

        # Load assets
        overlay_image = image_helper.from_path(os.path.join(constants.ASSETS_PATH, 'overlay.png'))
        new_badge = image_helper.from_path(os.path.join(constants.ASSETS_PATH, "new_badge.png"))

        for offer_i, offer_json in enumerate(shop_offers_json):
            display_asset = offer_json['displayAssets'][0]
            item_icon = image_helper.from_url(display_asset['url'])

            item_background_url = display_asset.get("background_texture")
            if item_background_url is None:
                rarity_id = offer_json['rarity']['id']
                if offer_json['series'] is not None: rarity_id = offer_json['series']['id']
                item_background = rarity_helper.get_background(rarity_id)
            else:
                item_background = image_helper.from_url(item_background_url)

            is_bundle = offer_json['mainType'] == "bundle"
            main_id = ("bundle_" if is_bundle else "") + offer_json['mainId']
            offer_price = offer_json['price']['finalPrice']
            offer_section = offer_json['section']['id']

            shop_history = offer_json['granted'][0]['shopHistory']

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

            font = ImageFont.truetype(constants.FONT_PATH, 33)
            draw = ImageDraw.Draw(icon_image)
            draw.text((256, 463), info_text, font=font, fill=((255, 255, 255) if days_gone is None or days_gone < 100 else self._RETURN_COLOR), anchor='ms') #Writes info text / date last seen

            font = ImageFont.truetype(constants.FONT_PATH, 40)
            draw = ImageDraw.Draw(icon_image)
            draw.text((256, 505), str(offer_price), font=font, fill='white', anchor='ms') #Writes price of offer

            section_number = sections[offer_section] if offer_section in sections else len(sections)

            #Save image
            icon_image.save(os.path.join(self._TEMP_PATH, f'{section_number}_{offer_i}_{main_id}.png'))
            icon_image.close()

        # Free memory
        overlay_image.close()
        new_badge.close()

        print(f'Generated {len(shop_offers_json)} items from the {shop_date} item shop.')

    def _merge_shop(self):
        offer_image_paths = glob.glob(os.path.join(self._TEMP_PATH, "*.png"))
        offer_count = len(offer_image_paths)
            
        column_count = math.ceil(math.sqrt(offer_count))
        row_count = math.ceil(offer_count / column_count)

        offer_image_size = self._SHOP_IMAGE_WIDTH // column_count
        shop_image_size = (offer_image_size * column_count, offer_image_size * row_count)

        shop_image = Image.new("RGB", shop_image_size)
        shop_background = Image.open(os.path.join(constants.ASSETS_PATH, "background.png")).convert("RGBA").resize(shop_image_size)
        shop_image.paste(shop_background, (0, 0))
        shop_background.close() # Free memory

        for i, offer_image_path in enumerate(sorted(offer_image_paths)):
            offer_image = image_helper.from_path(offer_image_path, size=offer_image_size)
            shop_image.paste(
                offer_image,
                ((0 + ((i % column_count) * offer_image.width)),
                    (0 + ((i // column_count) * offer_image.height)))
            )
            offer_image.close() # Free memory
        
        #Credits
        try:
            credit_images = glob.glob(os.path.join(constants.ASSETS_PATH, "ads/*.png"))
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

    def _compress_image(self, image, shop_date):
        save_path = os.path.join(self._RESULT_PATH, f'shop_{shop_date}.jpg')
        image.save(save_path, optimize=True, quality=85)

        current_size = (image.width, image.height)
        size_step = 250
        size_limit = 3000000

        start_time = time.time()
        while os.path.getsize(save_path) > size_limit:
            image = image.resize(current_size, Image.Resampling.LANCZOS)
            image.save(save_path, optimize=True, quality=85)

            current_size[0] -= size_step
            current_size[1] -= size_step

        image.close() # Free memory
        print(f"Compressed image to {os.path.getsize(save_path)} bytes. Took {round(time.time() - start_time, 2)} seconds.")

    def _post_image(self, shop_date):
        split_date = shop_date.split('-')
        reformatted_date = f'{split_date[2]}/{split_date[1]}/{split_date[0]}'

        post_helper.post(
            os.path.join(self._RESULT_PATH, f'shop_{shop_date}.jpg'),
            strings_helper.STRINGS["shop_post_caption"].replace('{date}', reformatted_date)
        )
