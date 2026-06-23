"""switch_monitor.py - Monitors a set of GPIO pins wired to physical switches.

Each input pin is expected to read HIGH (full voltage) when its switch is
flipped up and LOW (no voltage) when flipped down. The Pi's internal pull-down
resistors are enabled so floating pins are never misread as HIGH.

Output pins are held at constant 3.3 V (HIGH) so they can act as a voltage
source for the switch circuits. A switch wired between an output pin and an
input pin will therefore drive that input HIGH when flipped up.

Monitoring uses RPi.GPIO's interrupt-driven edge detection rather than polling.
The kernel notifies us via epoll when a pin transitions, so no CPU cycles are
spent between switch events.

Usage
-----
    monitor = SwitchMonitor(
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

# How long (ms) to ignore subsequent edges after the first one fires.
# Typical mechanical switches settle within 10-50ms.
_DEBOUNCE_MS = 50


class SwitchMonitor:
    """
    Monitors a fixed set of GPIO input pins wired to physical switches and
    dispatches registered callbacks when a switch is flipped up or down.
    Optionally holds a set of output pins at constant 3.3 V so they can
    act as a voltage source for the switch circuits.

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
    debounce_ms : int
        Edge events within this many milliseconds of a prior event on the
        same pin are ignored. Prevents mechanical bounce from firing
        callbacks multiple times per flip.
    """

    def __init__(
        self,
        input_pins: list[int],
        output_pins: list[int] = None,
        debounce_ms: int = _DEBOUNCE_MS,
    ):
        if len(input_pins) == 0:
            raise ValueError("At least one input pin must be provided.")

        self._pins = input_pins
        self._output_pins = output_pins or []
        self._debounce_ms = debounce_ms
        self._is_running = False

        # Two callback lists per switch: index 0 = on_up, index 1 = on_down.
        # Stored as {switch_index: {"up": [callbacks], "down": [callbacks]}}
        self._callbacks: dict[int, dict[str, list[Callable]]] = {
            i: {"up": [], "down": []} for i in range(len(input_pins))
        }

        # Protects the callback dicts so they can be modified from any thread.
        self._lock = threading.Lock()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def on_switch_up(self, switch_index: int, callback: Callable) -> None:
        """Register a callback to fire when switch `switch_index` is flipped up.

        The callback receives no arguments. It is called from a background
        thread managed by RPi.GPIO, so it should be thread-safe and return
        quickly (offload heavy work if needed).

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
            raise RuntimeError("SwitchMonitor has not been started yet.")
        return bool(GPIO.input(self._pins[switch_index]))

    def start(self) -> None:
        """Set up GPIO pins and begin listening for edge events.

        Safe to call once. Raises RuntimeError if GPIO is unavailable.
        """
        if GPIO is None:
            raise RuntimeError(
                "RPi.GPIO is not available. Install it on a Raspberry Pi "
                "or set MOCK_GPIO in the environment to use a mock."
            )
        if self._is_running:
            logger.warning("SwitchMonitor.start() called more than once; ignoring.")
            return

        GPIO.setmode(GPIO.BCM)

        for pin in self._output_pins:
            GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
            logger.info("Output pin %d (BCM) set to constant HIGH (3.3 V)", pin)

        for switch_index, pin in enumerate(self._pins):
            # Pull-down: pin reads LOW when switch is open (down).
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

            # Capture switch_index in a default arg so each lambda closes over
            # the correct value (classic Python loop-closure gotcha).
            GPIO.add_event_detect(
                pin,
                GPIO.BOTH,
                callback=lambda channel, idx=switch_index: self._on_edge(channel, idx),
                bouncetime=self._debounce_ms,
            )
            logger.info(
                "Monitoring switch %d on GPIO pin %d (BCM)", switch_index, pin
            )

        self._is_running = True

    def stop(self) -> None:
        """Remove edge detection and release GPIO resources."""
        if not self._is_running:
            return
        for pin in self._pins:
            GPIO.remove_event_detect(pin)
        GPIO.cleanup(self._pins + self._output_pins)
        self._is_running = False
        logger.info("SwitchMonitor stopped.")

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _on_edge(self, channel: int, switch_index: int) -> None:
        """Called by RPi.GPIO on any edge for the given channel.

        Reads the pin to determine direction (RPi.GPIO delivers BOTH edges via
        one callback; reading the pin tells us which way it settled).
        """
        state = GPIO.input(channel)
        direction = "up" if state == GPIO.HIGH else "down"

        logger.debug("Switch %d on pin %d flipped %s", switch_index, channel, direction)

        with self._lock:
            callbacks = list(self._callbacks[switch_index][direction])

        for cb in callbacks:
            try:
                cb()
            except Exception:
                logger.exception(
                    "Error in %s callback for switch %d", direction, switch_index
                )

    def _validate_index(self, switch_index: int) -> None:
        if switch_index not in self._callbacks:
            raise IndexError(
                f"switch_index {switch_index} is out of range "
                f"(this monitor has {len(self._pins)} switches, indices 0–{len(self._pins) - 1})."
            )