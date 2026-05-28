"""spotify_data_source.py - DataSource adapter for the Spotify player."""

from data_sources.data_source import DataSource
from spotify.spotify_status_fetcher import SpotifyStatusFetcher


class SpotifyDataSource(DataSource):
    """
    Wraps SpotifyStatusFetcher and exposes it as a DataSource.

    Spotify is polled at a much lower rate than OBD data since it involves
    an external HTTPS round-trip and the underlying data changes slowly.
    Returns None when the player is inactive so receivers are not called.
    """

    def __init__(self, rate_limit_hz: float = 0.2):  # default: once every 5 s
        super().__init__(rate_limit_hz)
        self.spotify = SpotifyStatusFetcher()

    def fetch(self) -> dict | None:
        state = self.spotify.fetch_player_state()

        if state is None:
            return None

        data = state.to_dict()
        data["__TYPE"] = "spotify"
        return data
