"""spotify_status_fetcher.py - fetches the current state of my Spotify player."""


import requests
import json

from models.spotify_status import SpotifyStatus


class SpotifyStatusFetcher:
    def __init__(self):
        self.client_id = "12b6af9d6af24d38abcb1c987f3a7bae"
        self.client_secret = "6c69993a2c64482b8beb286732758f76"

        self.access_token = self.generate_access_token()


    def generate_access_token(self):
        access_token_resp = requests.post("https://accounts.spotify.com/api/token",
                                         headers={"Content-Type": "application/x-www-form-urlencoded"},
                                         json=f"grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}")
        print(access_token_resp.content)

        json_obj = json.loads(access_token_resp.content)
        return json_obj["access_token"]


    def fetch_player_state(self):
        response = requests.get("https://api.spotify.com/v1/me/player", headers={"Authorization": "Bearer " + self.access_token})
        print(response.content)

        response_obj = json.loads(response.content)

        spotify_state = SpotifyStatus(response_obj["item"])