import yaml, os
import constants

with open(os.path.join(constants.ASSETS_PATH, "strings.yml"), "r") as f:
    STRINGS = yaml.load(f)