"""spotify_status_fetcher.py - fetches the current state of my Spotify player."""
import os
import dotenv

import requests
import json
import base64
import time

from models.spotify_status import SpotifyStatus


class SpotifyStatusFetcher:

    KICKSTART_MY_HEART_URI = "spotify:track:4Yqy0GpeDEXLibWJCZyQew"
    HEARTBEAT_URI = "spotify:track:4uWrIclvxHbzEQodrPmX7p"

    EUROBEAT_PLAYLIST_URI = "spotify:playlist:1Bq37SrRJiygFAm7BO0hmm"
    WRONG_GENERATION_PLAYLIST_URI = "spotify:playlist:65P2b3ITkgnKiHr7EBaDHO"

    # Playback is sent to this device even when it is idle.
    TARGET_DEVICE_ID = "130a9601826a011b0cf013e1372cbebd9c8ab80e"

    def __init__(self):
        self.access_token = None
        dotenv.load_dotenv()
        self.auth_token = os.getenv("SPOTIFY_AUTH_TOKEN")
        self.client_id = os.getenv("SPOTIFY_CLIENT_ID")
        self.client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")

        with open("spotify/refresh_token.txt", "r") as refresh_token_fp:
            self.refresh_token = refresh_token_fp.read()


    def __encode_client_creds(self):
        sample_string = self.client_id + ":" + self.client_secret
        sample_string_bytes = sample_string.encode("ascii")

        base64_bytes = base64.b64encode(sample_string_bytes)
        return base64_bytes.decode("ascii")


    def __generate_access_token(self):
        access_token_resp = requests.post("https://accounts.spotify.com/api/token",
                                          headers={"Content-Type": "application/x-www-form-urlencoded",
                                                   "Authorization": f"Basic {self.__encode_client_creds()}"},
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


    def __wait_for_context(self, context_uri, headers, timeout_s=5.0, interval_s=0.25):
        """Poll until the player reports context_uri, since a shuffle sent before it loads is discarded."""
        deadline = time.monotonic() + timeout_s
        while time.monotonic() < deadline:
            player_resp = requests.get("https://api.spotify.com/v1/me/player", headers=headers)
            if player_resp.status_code == 200 and player_resp.content:
                if (player_resp.json().get("context") or {}).get("uri") == context_uri:
                    return
            time.sleep(interval_s)


    def play_playlist_shuffled(self, playlist_uri):
        """Start a playlist from its first track on the target device, then enable shuffle for the rest."""
        headers = {"Authorization": "Bearer " + self.__generate_access_token()}
        play_body = {"context_uri": playlist_uri, "offset": {"position": 0}, "position_ms": 0}
        device_params = {"device_id": self.TARGET_DEVICE_ID}
        play_resp = requests.put("https://api.spotify.com/v1/me/player/play",
                                 params=device_params, json=play_body, headers=headers)
        if play_resp.status_code == 404:
            # Target device is unavailable, so fall back to the active device.
            device_params = {}
            play_resp = requests.put("https://api.spotify.com/v1/me/player/play",
                                     json=play_body, headers=headers)
        self.__wait_for_context(playlist_uri, headers)
        shuffle_resp = requests.put("https://api.spotify.com/v1/me/player/shuffle",
                                    params={"state": "true", **device_params},
                                    headers=headers)
        print(f"play: {play_resp}, shuffle: {shuffle_resp}")


if __name__ == "__main__":
    s = SpotifyStatusFetcher()
    print(s.fetch_player_state())
    time.sleep(5)
    s.change_player_state(SpotifyStatusFetcher.HEARTBEAT_URI)
    time.sleep(5)
    print(s.fetch_player_state())
