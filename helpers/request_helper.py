import requests

import constants

def io_request(url, parameters):
    parameters["lang"] = constants.LANG
    parameters_string = "&".join([f"{key}={value}" for key, value in parameters.items()])

    headers = {"Authorization": constants.FORTNITEAPI_IO_KEY}
    r = requests.get(f"{url}?{parameters_string}", headers=headers)

    return r.json()