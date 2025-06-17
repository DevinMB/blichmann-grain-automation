"""
controller.py
~~~~~~~~~~~~~
Pure-logic state machine for a relay-driven filling station that uses:

* HX711 load cell (weight sensor)
* Two push-buttons
* Override toggle-switch
* Relay
* Two single-pixel NeoPixel LEDs

Call ``ScaleController.tick()`` once per main-loop iteration.  The method
    • reads the current (smoothed) weight  
    • updates the internal state machine  
    • toggles the relay / LEDs as needed  
    • returns a *label* describing the transition that happened in that tick
Nothing here sleeps or loops forever—that’s up to your application code.
"""

from __future__ import annotations

from typing import Protocol, Sequence


# --------------------------------------------------------------------------- #
# Minimal “protocol” interfaces – the real gpiozero / neopixel / HX711
# implementations satisfy these.  The protocols make unit testing with fakes
# straightforward and give editors / type-checkers something to work with.
# --------------------------------------------------------------------------- #
class _Button(Protocol):
    @property
    def is_pressed(self) -> bool: ...


class _Relay(Protocol):
    def on(self) -> None: ...
    def off(self) -> None: ...
    @property
    def is_lit(self) -> bool: ...


class _NeoPixel(Protocol):
    def __setitem__(self, index: int, value: Sequence[int]) -> None: ...


class _HX711(Protocol):
    def get_weight(self, times: int) -> float: ...


# --------------------------------------------------------------------------- #
# Main controller
# --------------------------------------------------------------------------- #
class ScaleController:
    """State-machine that drives the filling workflow."""

    HOLD_DURATION: int = 10       # *ticks* button-1 must be held to set weight
    WEIGHT_SAMPLES: int = 5       # HX711 readings averaged per tick

    def __init__(
        self,
        hx: _HX711,
        relay: _Relay,
        button_1: _Button,
        button_2: _Button,
        override_switch: _Button,
        pixel_1: _NeoPixel,
        pixel_2: _NeoPixel,
        known_weight_lbs: float = 10.0,
    ) -> None:
        # Hardware (or fakes) injected from outside
        self.hx = hx
        self.relay = relay
        self.button_1 = button_1
        self.button_2 = button_2
        self.override_switch = override_switch
        self.pixel_1 = pixel_1
        self.pixel_2 = pixel_2

        # Internal state
        self.is_job_running: bool = False
        self.target_weight: float = 0.0
        self.hold_counter: int = 0
        self.known_weight_lbs: float = known_weight_lbs

        # Initial LED colours
        self.pixel_1[0] = (255, 255, 0)  # yellow  – “ready / waiting”
        self.pixel_2[0] = (255,   0, 0)  # red     – “stopped / idle”

    # --------------------------------------------------------------------- #
    # Public API – call on every main-loop pass
    # --------------------------------------------------------------------- #
    def tick(self) -> str:
        """
        Advance the state machine by one iteration and return a label:

        ``"override" | "job_started" | "job_running" | "job_finished" |
          "weight_set" | "waiting_for_hold" | "standing_by"``
        """
        current_weight = self._get_stable_weight(self.WEIGHT_SAMPLES)

        # -- Highest-priority branch: the physical override switch -------- #
        if self.override_switch.is_pressed:
            self.relay.on()
            return "override"

        # -- A job is already running ------------------------------------ #
        if self.is_job_running:
            if current_weight >= self.target_weight:
                self.relay.off()
                self.is_job_running = False
                self.pixel_2[0] = (0, 0, 255)  # blue – finished
                return "job_finished"
            return "job_running"

        # -- Idle / standing by ------------------------------------------ #
        self.relay.off()

        # 1) Start / pause button (button 2)
        if self.button_2.is_pressed:
            self.is_job_running = True
            self.relay.on()
            self.pixel_2[0] = (0, 255, 0)  # green – running
            return "job_started"

        # 2) Weight-set button (button 1)
        if self.button_1.is_pressed:
            self.hold_counter += 1
            if self.hold_counter >= self.HOLD_DURATION:
                self.target_weight = current_weight
                self.hold_counter = 0
                self.pixel_1[0] = (0, 255, 0)  # green – target confirmed
                return "weight_set"

            # still holding…
            self.pixel_1[0] = (255, 255, 0)  # keep yellow
            return "waiting_for_hold"

        # no input; reset hold counter and stay idle
        self.hold_counter = 0
        return "standing_by"

    # --------------------------------------------------------------------- #
    # Helpers
    # --------------------------------------------------------------------- #
    def _get_stable_weight(self, samples: int) -> float:
        """Average *samples* HX711 readings to smooth out noise."""
        if samples <= 0:
            raise ValueError("samples must be positive")

        total = 0.0
        for _ in range(samples):
            total += float(self.hx.get_weight(1))
        return total / samples

    # --------------------------------------------------------------------- #
    # Optional utility for scale calibration (not used by tick())
    # --------------------------------------------------------------------- #
    def calibrate_scale(self, raw_average: float) -> float:
        """
        Given *raw_average* (the mean HX711 reading for ``known_weight_lbs``),
        return—and optionally set—the calculated reference unit.
        """
        if raw_average <= 0:
            raise ValueError("raw_average must be positive")

        reference_unit = raw_average / self.known_weight_lbs
        # If you wish, call:  self.hx.set_reference_unit(reference_unit)
        return reference_unit
