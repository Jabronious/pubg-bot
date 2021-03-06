import requests
import pdb

class PubgBotWrapper(object):
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://mr-pubg.herokuapp.com/api/v1/"

    def matches(self, id=''):
        url = self.base_url + "matches/" + id
        header = {"api-key": self.api_key}
        response = requests.get(url, headers=header)
        if response.ok:
            return response.json()
        else:
            return False

    def participants(self, match_id, player_id=''):
        url = self.base_url + "matches/" + match_id +"/participants/" + player_id.replace('account.', '')
        header = {"api-key": self.api_key}
        response = requests.get(url, headers=header)
        if response.ok:
            return response.json()
        else:
            return False