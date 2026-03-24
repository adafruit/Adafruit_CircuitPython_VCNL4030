# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
HW test: Verify sunlight cancellation settings work

Hardware setup:
- VCNL4030 sensor connected via I2C
- Stepper motor on DIR=D10, STEP=D9 with reflector in close position

Test: Sunlight cancellation enable/disable should work
(Hard to test actual effect indoors, just verify settings apply)
"""

import time

import board

from adafruit_vcnl4030 import VCNL4030, ProxLEDCurrent, SunlightCancelCurrent


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


print("=== 11_sunlight_cancel ===")
print("Testing sunlight cancellation settings")
print()

sensor = VCNL4030(board.I2C())
print("VCNL4030 initialized")

sensor.proximity_enabled = True
sensor.led_current = ProxLEDCurrent.MA_200
time.sleep(0.1)

all_passed = True

# Test 1: Sunlight cancellation OFF
print("--- Sunlight cancellation OFF ---")
sensor.sunlight_cancellation_enabled = False
time.sleep(0.1)

sc_off = sensor.sunlight_cancellation_enabled
print(f"  SC enabled (getter): {'YES' if sc_off else 'NO'}")

ps_off = median_read(sensor, "proximity")
print(f"  Proximity: {ps_off}")

if not sc_off:
    print("  PASS: SC reported as disabled")
else:
    print("  FAIL: SC should be disabled")
    all_passed = False
print()

# Test 2: Sunlight cancellation ON
print("--- Sunlight cancellation ON ---")
sensor.sunlight_cancellation_enabled = True
time.sleep(0.1)

sc_on = sensor.sunlight_cancellation_enabled
print(f"  SC enabled (getter): {'YES' if sc_on else 'NO'}")

ps_on = median_read(sensor, "proximity")
print(f"  Proximity: {ps_on}")

if sc_on:
    print("  PASS: SC reported as enabled")
else:
    print("  FAIL: SC should be enabled")
    all_passed = False
print()

# Test 3: Sunlight cancel current settings
print("--- SC current multiplier ---")
sc_levels = [
    ("1X", SunlightCancelCurrent.X1),
    ("2X", SunlightCancelCurrent.X2),
    ("4X", SunlightCancelCurrent.X4),
    ("8X", SunlightCancelCurrent.X8),
]
sc_names = {v: n for n, v in sc_levels}

for name, level in sc_levels:
    sensor.sunlight_cancel_current = level
    time.sleep(0.05)
    read_back = sensor.sunlight_cancel_current
    print(f"  Set {name}, read {sc_names.get(read_back, '?')}")
    if read_back != level:
        all_passed = False
print()

# Test 4: Sunlight protection settings
print("--- Sunlight protection ---")
sensor.sunlight_protection_enhanced = False
sp_off = sensor.sunlight_protection_enhanced
print(f"  SP=0 (1x): {'FAIL' if sp_off else 'OK'}")
if sp_off:
    all_passed = False

sensor.sunlight_protection_enhanced = True
sp_on = sensor.sunlight_protection_enhanced
print(f"  SP=1 (1.5x): {'OK' if sp_on else 'FAIL'}")
if not sp_on:
    all_passed = False
print()

# Cleanup
sensor.sunlight_cancellation_enabled = False

print("=========================")

if ps_off > 0 and ps_on > 0:
    print("PASS: Both readings valid")
else:
    print("FAIL: Invalid readings")
    all_passed = False

print("(Note: Indoor testing may not show SC effect)")

if all_passed:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")

print("~~END~~")
