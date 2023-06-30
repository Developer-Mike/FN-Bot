import yaml, os
import constants

with open(os.path.join(constants.ASSETS_PATH, "strings.yml"), "r", encoding="utf-8") as f:
    STRINGS = yaml.safe_load(f)