"""spotify_status_fetcher.py - fetches the current state of my Spotify player."""


import requests
import json

from models.spotify_status import SpotifyStatus

"""
Plan for getting spotify auth details:
- generate the "request User Authorization" url ourselves
- go there in a browser
- when we try (and fail) the redirect, grab the url it tried to use
  - we will fail because we don't actually have a server that cares about this redirect
  - save the `code` parameter in an environment variable (or smth) for safekeeping
- request an access token `accounts.spotify.com/api/token`
"""


class SpotifyStatusFetcher:

    KICKSTART_MY_HEART_URI = "spotify:track:4Yqy0GpeDEXLibWJCZyQew"
    HEARTBEAT_URI = "spotify:track:4uWrIclvxHbzEQodrPmX7p"

    def __init__(self):


    def generate_access_token(self):
        access_token_resp = requests.post("https://accounts.spotify.com/api/token",
                                         headers={"Content-Type": "application/x-www-form-urlencoded"},
                                         json=f"grant_type=client_credentials&client_id={self.client_id}&client_secret={self.client_secret}")
        print(access_token_resp.content)

        json_obj = json.loads(access_token_resp.content)
        return json_obj["access_token"]


    def fetch_player_state(self):
        response = requests.get("https://api.spotify.com/v1/me/player", headers={"Authorization": "Bearer " + self.access_token})

        if not response.content:
            return None

        response_obj = json.loads(response.content)

        spotify_state = SpotifyStatus(response_obj["item"]["name"],
                                      ", ".join([artist["name"] for artist in response_obj["item"]["artists"]]),
                                      response_obj["item"]["album"]["name"],
                                      int(response_obj["item"]["duration_ms"] / 1000),
                                      int(response_obj["progress_ms"] / 1000))
        return spotify_state


    def change_player_state(self, spotify_uri):
        response = requests.put("https://api.spotify.com/v1/me/player/play",
                                json.dumps({"uris": [spotify_uri]}),
                                headers={"Authorization": "Bearer " + self.access_token})
        print(response)


if __name__ == "__main__":
    s = SpotifyStatusFetcher()
    state = s.fetch_player_state()
    print(state)
    s.change_player_state(SpotifyStatusFetcher.KICKSTART_MY_HEART_URI)
    print(s.fetch_player_state())
