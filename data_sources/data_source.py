"""data_source.py - Abstract base class for all data sources."""

from abc import ABC, abstractmethod


class DataSource(ABC):
    """
    Represents a single input to the data pipeline.

    Each concrete subclass encapsulates one external system (OBD, Spotify, etc.)
    and is responsible for fetching a snapshot of its state as a plain dict.
    The pipeline calls fetch() on a background thread at the specified rate.
    """

    def __init__(self, rate_limit_hz: float = 2.0):
        self.rate_limit_hz = rate_limit_hz

    @abstractmethod
    def fetch(self) -> dict | None:
        """
        Fetch the latest data from this source.

        Returns a dict ready to hand to receivers, or None if no data is
        available right now (e.g. Spotify player is inactive). Returning None
        causes the pipeline to skip this cycle without calling any receiver.
        """
        pass
