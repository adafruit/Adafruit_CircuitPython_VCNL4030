# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
HW test: Verify ALS integration time affects raw counts

Hardware setup:
- VCNL4030 sensor connected via I2C
- NeoPixel ring (8 pixels) on pin D7 at fixed moderate brightness

Test: Longer integration times should give higher raw counts
"""

import time

import board
import neopixel

from adafruit_vcnl4030 import VCNL4030, ALSIntegrationTime

NEOPIXEL_PIN = board.D7
NEOPIXEL_COUNT = 8


def median_read(sensor, read_type, n=3, delay_s=0.05):
    readings = []
    for i in range(n):
        if read_type == "als":
            readings.append(sensor.als)
        elif read_type == "white":
            readings.append(sensor.white)
        elif read_type == "lux":
            readings.append(sensor.lux)
        elif read_type == "proximity":
            readings.append(sensor.proximity)
        if i < n - 1:
            time.sleep(delay_s)
    readings.sort()
    return readings[n // 2]


print("=== 02_als_integration_time ===")
print("Testing ALS at different integration times")
print()

# Initialize NeoPixels at moderate brightness
pixels = neopixel.NeoPixel(NEOPIXEL_PIN, NEOPIXEL_COUNT, brightness=1.0, auto_write=True)
pixels.fill((64, 64, 64))

sensor = VCNL4030(board.I2C())
sensor.reset()
print("VCNL4030 initialized")

sensor.als_enabled = True
time.sleep(0.1)

# Test each integration time
it_configs = [
    ("50ms", ALSIntegrationTime.MS_50, 0.10),
    ("100ms", ALSIntegrationTime.MS_100, 0.15),
    ("200ms", ALSIntegrationTime.MS_200, 0.30),
    ("400ms", ALSIntegrationTime.MS_400, 0.50),
    ("800ms", ALSIntegrationTime.MS_800, 0.90),
]

print("Integration time vs raw counts:")
readings = []
for name, it, settle in it_configs:
    sensor.als_integration_time = it
    time.sleep(settle)
    val = median_read(sensor, "als")
    readings.append(val)
    print(f"  {name}: {val}")
print()

# Verify trend: longer IT should give higher counts
increasing = all(readings[i] >= readings[i - 1] for i in range(1, len(readings)))

# Cleanup - turn off NeoPixels
pixels.fill((0, 0, 0))

print("=========================")
if increasing:
    print("PASS: Longer integration times give higher counts")
else:
    print("FAIL: Counts did not increase with integration time")
    print("(Note: May saturate at high brightness)")

print("~~END~~")
