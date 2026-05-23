"""data_pipeline.py - Generic scheduler that fans out registered data sources to registered receivers.

The pipeline has no knowledge of any specific data source or receiver. It only
depends on the DataSource interface. New inputs (GPS, engine temp, etc.) can be
added in main.py without touching this file at all.

Threading model
---------------
Each DataSource runs on its own daemon thread. Threads are started when spin()
is called and run until stop() is called (or the process exits, since they are
daemon threads). A single lock serialises calls to receivers so individual
receiver implementations do not need to be thread-safe themselves.
"""

import threading
import time
import logging
from data_sources.data_source import DataSource

logger = logging.getLogger(__name__)


class DataPipeline:

    def __init__(self):
        self._sources: list[DataSource] = []
        self._receivers: list = []
        self._receiver_lock = threading.Lock()
        self._running = False
        self._threads: list[threading.Thread] = []

    # ------------------------------------------------------------------
    # Registration API — called before spin()
    # ------------------------------------------------------------------

    def register_source(self, source: DataSource) -> None:
        """Add a data source. Each source gets its own background thread."""
        self._sources.append(source)

    def register_receiver(self, receiver) -> None:
        """Add a receiver. Receivers are called (under a lock) from source threads."""
        self._receivers.append(receiver)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def spin(self) -> None:
        """Start all source threads and block until stop() is called."""
        self._running = True
        for source in self._sources:
            t = threading.Thread(
                target=self._run_source,
                args=(source,),
                name=type(source).__name__,
                daemon=True,
            )
            self._threads.append(t)
            t.start()
            logger.info("Started thread for %s at %.1f Hz", type(source).__name__, source.rate_limit_hz)

        for t in self._threads:
            t.join()

    def stop(self) -> None:
        """Signal all source threads to exit after their current cycle."""
        self._running = False

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _run_source(self, source: DataSource) -> None:
        """Main loop for a single source thread."""
        interval = 1.0 / source.rate_limit_hz

        while self._running:
            cycle_start = time.time()

            try:
                data = source.fetch()
            except Exception:
                logger.exception("Error fetching from %s", type(source).__name__)
                data = None

            if data is not None:
                with self._receiver_lock:
                    for receiver in self._receivers:
                        try:
                            receiver.ingest(data)
                        except Exception:
                            logger.exception("Error in receiver %s", type(receiver).__name__)

            elapsed = time.time() - cycle_start
            sleep_time = interval - elapsed
            if sleep_time > 0:
                time.sleep(sleep_time)
