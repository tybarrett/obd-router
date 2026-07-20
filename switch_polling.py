"""switch_polling.py - Monitors a set of GPIO pins wired to physical switches.

This is a polling-based alternative to the interrupt-driven SwitchMonitor.
Instead of relying on RPi.GPIO edge detection (which fires a callback on an
edge and then re-reads the pin - a read that can race the transition that
triggered it), a background thread samples every input pin at a fixed
interval and reports a switch as flipped only when its *settled* level
differs from the last sampled level.

Because polling always reads the current settled state, a stable switch
position can never be "missed" the way a fleeting edge can. The trade-off is
a small, bounded amount of latency (up to one poll interval) and steady but
minimal CPU use.

Each input pin is expected to read HIGH (full voltage) when its switch is
flipped up and LOW (no voltage) when flipped down. The Pi's internal
pull-down resistors are enabled so floating pins are never misread as HIGH.

Output pins are held at constant 3.3 V (HIGH) so they can act as a voltage
source for the switch circuits. A switch wired between an output pin and an
input pin will therefore drive that input HIGH when flipped up.

Usage
-----
    monitor = SwitchPoller(
        input_pins=[17, 18, 27, 22],
        output_pins=[2, 3, 4, 14],   # held at 3.3 V; one per switch
    )

    monitor.on_switch_up(0, lambda: print("Switch 0 flipped up"))
    monitor.on_switch_down(2, lambda: print("Switch 2 flipped down"))

    monitor.start()
    # ... runs in the background until monitor.stop() is called
"""

import logging
import threading
from typing import Callable

try:
    import RPi.GPIO as GPIO
except ImportError:
    # Allow the module to be imported on non-Pi hardware (e.g. for tests).
    # Any call to start() will raise clearly if GPIO is unavailable.
    GPIO = None

logger = logging.getLogger(__name__)

# How often (seconds) the background thread samples every input pin.
# 10ms is fast enough to feel instant for a human-flipped toggle while
# keeping CPU use negligible. Debouncing falls out of polling naturally:
# a switch is reported only once its settled level changes between samples.
_POLL_INTERVAL_S = 0.01


class SwitchPoller:
    """
    Monitors a fixed set of GPIO input pins wired to physical switches by
    polling them on a background thread, and dispatches registered callbacks
    when a switch's settled level changes (flipped up or down). Optionally
    holds a set of output pins at constant 3.3 V so they can act as a voltage
    source for the switch circuits.

    Parameters
    ----------
    input_pins : list[int]
        BCM-numbered GPIO pins to monitor, one per switch, in order.
        Switch indices used in on_switch_up/on_switch_down correspond
        to the position in this list (0-based).
    output_pins : list[int]
        BCM-numbered GPIO pins to configure as constant HIGH (3.3 V) outputs.
        Intended to power the switch circuits: wire each output pin to one
        side of a switch and the other side to the corresponding input pin.
        No callbacks or indices are associated with these pins.
    poll_interval_s : float
        How often, in seconds, the background thread samples every input
        pin. A switch is reported only when its level differs from the
        previous sample, so this interval also bounds the worst-case
        latency between a flip and its callback firing.
    """

    def __init__(
        self,
        input_pins: list[int],
        output_pins: list[int] = None,
        poll_interval_s: float = _POLL_INTERVAL_S,
    ):
        if len(input_pins) == 0:
            raise ValueError("At least one input pin must be provided.")

        self._pins = input_pins
        self._output_pins = output_pins or []
        self._poll_interval_s = poll_interval_s
        self._is_running = False

        # Two callback lists per switch: "up" and "down".
        # Stored as {switch_index: {"up": [callbacks], "down": [callbacks]}}
        self._callbacks: dict[int, dict[str, list[Callable]]] = {
            i: {"up": [], "down": []} for i in range(len(input_pins))
        }

        # Last-known settled state per switch (True = up, False = down),
        # seeded at start() and updated by the polling thread.
        self._last_state: dict[int, bool] = {}

        # Protects the callback dicts and _last_state so they can be modified
        # from any thread.
        self._lock = threading.Lock()

        # Background polling thread and the event used to stop it.
        self._thread: threading.Thread = None
        self._stop_event = threading.Event()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def on_switch_up(self, switch_index: int, callback: Callable) -> None:
        """Register a callback to fire when switch `switch_index` is flipped up.

        The callback receives no arguments. It is called from the background
        polling thread, so it should be thread-safe and return quickly
        (offload heavy work if needed).

        Can be called before or after start().
        """
        self._validate_index(switch_index)
        with self._lock:
            self._callbacks[switch_index]["up"].append(callback)

    def on_switch_down(self, switch_index: int, callback: Callable) -> None:
        """Register a callback to fire when switch `switch_index` is flipped down."""
        self._validate_index(switch_index)
        with self._lock:
            self._callbacks[switch_index]["down"].append(callback)

    def current_state(self, switch_index: int) -> bool:
        """Return the current state of a switch: True = up, False = down."""
        self._validate_index(switch_index)
        if not self._is_running:
            raise RuntimeError("SwitchPoller has not been started yet.")
        return bool(GPIO.input(self._pins[switch_index]))

    def start(self) -> None:
        """Set up GPIO pins and begin polling on a background thread.

        Safe to call once. Raises RuntimeError if GPIO is unavailable.
        """
        if GPIO is None:
            raise RuntimeError(
                "RPi.GPIO is not available. Install it on a Raspberry Pi "
                "or set MOCK_GPIO in the environment to use a mock."
            )
        if self._is_running:
            logger.warning("SwitchPoller.start() called more than once; ignoring.")
            return

        GPIO.setmode(GPIO.BCM)

        for pin in self._output_pins:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
            logger.info("Output pin %d (BCM) set to constant HIGH (3.3 V)", pin)

        for switch_index, pin in enumerate(self._pins):
            # Pull-down: pin reads LOW when switch is open (down).
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            # Seed the last-known state so the first poll compares against the
            # pin's actual level at startup rather than an unset value.
            with self._lock:
                self._last_state[switch_index] = bool(GPIO.input(pin))

            logger.info(
                "Polling switch %d on GPIO pin %d (BCM)", switch_index, pin
            )

        self._is_running = True
        self._stop_event.clear()
        self._thread = threading.Thread(
            target=self._poll_loop, name="SwitchPoller", daemon=True
        )
        self._thread.start()
        logger.info(
            "SwitchPoller started (poll interval %.0f ms).",
            self._poll_interval_s * 1000,
        )

    def stop(self) -> None:
        """Stop the polling thread and release GPIO resources."""
        if not self._is_running:
            return
        # Signal the loop to exit, then wait for the thread to finish so we
        # don't clean up GPIO out from under an in-progress sample.
        self._stop_event.set()
        if self._thread is not None:
            self._thread.join()
            self._thread = None
        GPIO.cleanup(self._pins + self._output_pins)
        self._is_running = False
        logger.info("SwitchPoller stopped.")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _poll_loop(self) -> None:
        """Sample every input pin at a fixed interval until stopped.

        For each switch, a callback fires only when the pin's settled level
        differs from the previous sample. Reading the settled level directly
        (rather than reacting to an edge and re-reading) means a stable switch
        position can't be missed the way a fleeting edge can.
        """
        # Event.wait() both paces the loop and returns immediately when stop()
        # is called, so shutdown is prompt regardless of the poll interval.
        while not self._stop_event.wait(self._poll_interval_s):
            for switch_index, pin in enumerate(self._pins):
                state = bool(GPIO.input(pin))

                with self._lock:
                    if self._last_state.get(switch_index) == state:
                        continue  # no change since last sample
                    self._last_state[switch_index] = state
                    direction = "up" if state else "down"
                    callbacks = list(self._callbacks[switch_index][direction])

                logger.debug(
                    "Switch %d on pin %d flipped %s", switch_index, pin, direction
                )

                for cb in callbacks:
                    try:
                        cb()
                    except Exception:
                        logger.exception(
                            "Error in %s callback for switch %d",
                            direction,
                            switch_index,
                        )

    def _validate_index(self, switch_index: int) -> None:
        if switch_index not in self._callbacks:
            raise IndexError(
                f"switch_index {switch_index} is out of range "
                f"(this monitor has {len(self._pins)} switches, indices 0–{len(self._pins) - 1})."
            )

