"""spotify_status_fetcher.py - fetches the current state of my Spotify player."""
import os
import dotenv

import requests
import json

from models.spotify_status import SpotifyStatus


class SpotifyStatusFetcher:

    KICKSTART_MY_HEART_URI = "spotify:track:4Yqy0GpeDEXLibWJCZyQew"
    HEARTBEAT_URI = "spotify:track:4uWrIclvxHbzEQodrPmX7p"

    def __init__(self):
        self.access_token = None
        dotenv.load_dotenv()
        self.auth_token = os.getenv("SPOTIFY_AUTH_TOKEN")
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        with open("refresh_token.txt", "r") as refresh_token_fp:
            self.refresh_token = refresh_token_fp.read()


    def __generate_access_token(self):
        access_token_resp = requests.post("https://accounts.spotify.com/api/token",
                                          headers={"Content-Type": "application/x-www-form-urlencoded",
                                         json=f"grant_type=authorization_code&code={self.auth_token}&redirect_uri=http://localhost:3000")
                                          data={"grant_type": "refresh_token",
                                                "refresh_token": self.refresh_token,
                                                },
                                          )
        print("Response: " + access_token_resp.content.decode("utf-8"))

        json_obj = json.loads(access_token_resp.content)
        return json_obj["access_token"]


    def fetch_player_state(self):
        access_token = self.__generate_access_token()
        response = requests.get("https://api.spotify.com/v1/me/player",
                                headers={"Authorization": "Bearer " + access_token})

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
        access_token = self.__generate_access_token()
        response = requests.put("https://api.spotify.com/v1/me/player/play",
                                json.dumps({"uris": [spotify_uri]}),
                                headers={"Authorization": "Bearer " + access_token})
        print(response)


if __name__ == "__main__":
    s = SpotifyStatusFetcher()
    print(s.generate_access_token())
    # state = s.fetch_player_state()
    # print(state)
    # s.change_player_state(SpotifyStatusFetcher.KICKSTART_MY_HEART_URI)
    # print(s.fetch_player_state())
