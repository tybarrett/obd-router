"""spotify_status.py - a data model that captures the status of the user's spotify account."""


import json


class SpotifyStatus:
    def __init__(self, song_name, artist_name, album_name, song_length, time_in_song):
        self.song_name = song_name
        self.artist_name = artist_name
        self.album_name = album_name
        self.song_length = song_length
        self.time_in_song = time_in_song

    def to_json(self):
        d = {"song_name": self.song_name,
             "artist_name": self.artist_name,
             "album_name": self.album_name,
             "song_length": self.song_length,
             "time_in_song": self.time_in_song}

        return json.dumps(d)
