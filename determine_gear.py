"""determine_gear.py - Given the RPM and speed of the car, determine the gear we're in."""


ZN6_GEAR_RATIOS = [0.0046, 0.0084, 0.0124, 0.0175, 0.0246, 0.03]
GEAR_RATIO_DIFF_THRESHOLD = 0.001


def determine_gear(rpm, speed_mph):
    # The speed-to-rpm ratio is constant at each gear.
    # We will calculate that ratio, try to relate it to our list of known ratios.
    # If it is close to a known ratio, we return that gear. Otherwise, "N".
    speed_over_rpm = speed_mph / rpm
    for i, ratio in enumerate(ZN6_GEAR_RATIOS):
        if abs(speed_over_rpm - ratio) < GEAR_RATIO_DIFF_THRESHOLD:
            return str(i + 1)

    return "N"
