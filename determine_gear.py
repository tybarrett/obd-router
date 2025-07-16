"""determine_gear.py - Given the RPM and speed of the car, determine the gear we're in."""


ZN6_GEAR_RATIOS = [3.538, 2.06, 1.404, 1, 0.713, 0.582]
ZN6_DIFF_GEAR_RATIO = 4100

GEAR_RATIO_DIFF_THRESHOLD = 0.1

def determine_gear(rpm, speed_mph):
    calculated_gear_ratio = rpm * (1/ZN6_DIFF_GEAR_RATIO) * (1/831.28) * 60 * speed_mph
    for gear_num, ratio in enumerate(ZN6_GEAR_RATIOS):
        diff = abs(ratio - calculated_gear_ratio)
        if diff < GEAR_RATIO_DIFF_THRESHOLD:
            return str(gear_num)
    else:
        return "N"
