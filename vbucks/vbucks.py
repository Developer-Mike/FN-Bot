import requests, pickle, os
from datetime import datetime, timedelta

from helpers import exception_helper, post_helper, strings_helper
import constants

class VBucksModule:
    _VBUCKS_MODULE_PATH = os.path.dirname(os.path.abspath(__file__))
    _LAST_POST_PATH = os.path.join(_VBUCKS_MODULE_PATH, "last_post.p")

    _STW_WORLD_INFO_URL = "https://fortnite-public-service-prod11.ol.epicgames.com/fortnite/api/game/v2/world/info"
    _TOKEN_AUTH_URL = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
    _FORTNITE_PC_BASE = "ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ="

    def register(self, schedule):
        self.schedule = schedule
        schedule.every(1).days.at(constants.UTC_MIDNIGHT).do(self.update)
    
    def on_exception(self):
        self.schedule.every(5).minutes.until(timedelta(minutes=6)).do(self.update)
    
    @exception_helper.catch_exceptions(on_exception=on_exception)
    def update(self):
        date = datetime.now().strftime("%d%m%Y")
        if self._has_posted_today(date): return

        stw_json = self._get_stw_json()
        vbucks_missions = self._get_vbucks_missions(stw_json)

        if sum(vbucks_missions.values()) > 0:
            self._post_vbucks_missions(vbucks_missions)

        pickle.dump(date, open(self._LAST_POST_PATH, "wb"))

    def _has_posted_today(self, date):
        if not os.path.exists(self._LAST_POST_PATH): 
            return False
        else: 
            return pickle.load(open(self._LAST_POST_PATH, "rb")) == date

    def _get_stw_json(self):
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"basic {self._FORTNITE_PC_BASE}"
        }
        body = {
            "grant_type": "client_credentials"
        }
        r = requests.post(self._TOKEN_AUTH_URL, headers=headers, data=body)
        token = r.json()["access_token"]

        headers = {
            "Accept-Language": "en-US",
            "Authorization": f"bearer {token}"
        }
        r = requests.get(self._STW_WORLD_INFO_URL, headers=headers)

        return r.json()
    
    def _get_vbucks_missions(self, stw_json):
        vbucks_missions = {}

        for mission_alert_group in stw_json["missionAlerts"]:
            theather_name, is_hidden = self._get_theater_info(stw_json, mission_alert_group["theaterId"])
            if is_hidden: continue

            for mission_alert in mission_alert_group["availableMissionAlerts"]:
                for mission_reward in mission_alert["missionAlertRewards"]["items"]:
                    if mission_reward["itemType"] == "AccountResource:currency_mtxswap":
                        if theather_name not in vbucks_missions:
                            vbucks_missions[theather_name] = 0

                        vbucks_missions[theather_name] += mission_reward["quantity"]
        
        return vbucks_missions


    def _get_theater_info(self, stw_json, theater_id):
        for theater in stw_json["theaters"]:
            if theater["uniqueId"] == theater_id:
                return theater["displayName"], theater["bHideLikeTestTheater"]
    
    def _post_vbucks_missions(self, vbucks_missions):
        vbucks_list = [f"{theater_name}: {vbucks_amount}" for theater_name, vbucks_amount in vbucks_missions.items()]
        text = strings_helper.STRINGS["vbucks_text"].replace("{missions}", "\\n".join(vbucks_list))

        post_helper.post(None, text)