# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
HW test: Verify PS cancellation reduces baseline

Hardware setup:
- VCNL4030 sensor connected via I2C
- Stepper motor on DIR=D10, STEP=D9 with reflector in close position

Test: Setting cancellation value should reduce proximity reading
"""

import time

import board

from adafruit_vcnl4030 import VCNL4030, ProxLEDCurrent


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


print("=== 08_ps_cancellation ===")
print("Testing PS crosstalk cancellation")
print()

sensor = VCNL4030(board.I2C())
sensor.reset()
print("VCNL4030 initialized")

sensor.proximity_enabled = True
sensor.led_current = ProxLEDCurrent.MA_200
sensor.proximity_cancellation = 0  # Start with no cancellation
time.sleep(0.1)

# Read baseline with no cancellation
print("--- No cancellation ---")
baseline = median_read(sensor, "proximity")
print(f"  Baseline reading: {baseline}")

# Set cancellation to half the baseline
cancel_val = baseline // 2
print(f"--- Setting cancellation to {cancel_val} ---")
sensor.proximity_cancellation = cancel_val
time.sleep(0.1)

cancelled = median_read(sensor, "proximity")
print(f"  Cancelled reading: {cancelled}")

expected = max(0, baseline - cancel_val)
print(f"  Expected ~{expected}")

# Reset cancellation
sensor.proximity_cancellation = 0

print()
print("=========================")

if cancelled < baseline:
    print("PASS: Cancellation reduced the reading")
else:
    print("FAIL: Cancellation did not reduce reading")

diff = abs(cancelled - expected)
if diff < baseline // 4:
    print("PASS: Cancelled value close to expected")
else:
    print("INFO: Cancelled value differs from expected")
    print(f"  Difference: {diff}")

print("~~END~~")
