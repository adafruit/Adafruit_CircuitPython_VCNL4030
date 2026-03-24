# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
HW test: Verify PS duty cycle settings work

Hardware setup:
- VCNL4030 sensor connected via I2C
- Stepper motor on DIR=D10, STEP=D9 with reflector in close position

Test: All duty cycles should return valid (non-zero) readings
"""

import time

import board

from adafruit_vcnl4030 import VCNL4030, ProxDuty, ProxLEDCurrent


def median_read(sensor, read_type, n=3, delay_s=0.05):
    readings = []
    for i in range(n):
        if read_type == "proximity":
            readings.append(sensor.proximity)
        elif read_type == "als":
            readings.append(sensor.als)
        elif read_type == "white":
            readings.append(sensor.white)
        elif read_type == "lux":
            readings.append(sensor.lux)
        if i < n - 1:
            time.sleep(delay_s)
    readings.sort()
    return readings[n // 2]


print("=== 07_ps_duty ===")
print("Testing proximity at different duty cycles")
print()

sensor = VCNL4030(board.I2C())
print("VCNL4030 initialized")

sensor.proximity_enabled = True
sensor.led_current = ProxLEDCurrent.MA_200
time.sleep(0.1)

# Test each duty cycle
duty_configs = [
    ("1/40", ProxDuty.RATIO_40),
    ("1/80", ProxDuty.RATIO_80),
    ("1/160", ProxDuty.RATIO_160),
    ("1/320", ProxDuty.RATIO_320),
]

print("Duty cycle vs proximity:")
print("(Lower duty = less power, similar readings expected)")
readings = []
for name, duty in duty_configs:
    sensor.proximity_duty = duty
    time.sleep(0.1)
    val = median_read(sensor, "proximity")
    readings.append(val)
    print(f"  {name}: {val}")

print()
print("=========================")

all_valid = all(r > 0 for r in readings)
if all_valid:
    print("PASS: All duty cycles return valid readings")
else:
    print("FAIL: Some duty cycles returned zero")

min_val = min(readings)
max_val = max(readings)
if max_val < min_val * 3:
    print("PASS: Readings are within expected range")
else:
    print("INFO: Large variation between duty cycles")

print("~~END~~")
