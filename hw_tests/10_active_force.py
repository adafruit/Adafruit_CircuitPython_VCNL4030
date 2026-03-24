# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
HW test: Verify active force mode for triggered readings

Hardware setup:
- VCNL4030 sensor connected via I2C
- Stepper motor on DIR=D10, STEP=D9 with reflector in close position

Test: In AF mode, readings should only update after trigger
"""

import time

import board

from adafruit_vcnl4030 import VCNL4030, ProxLEDCurrent

print("=== 10_active_force ===")
print("Testing PS active force mode")
print()

sensor = VCNL4030(board.I2C())
print("VCNL4030 initialized")

sensor.proximity_enabled = True
sensor.led_current = ProxLEDCurrent.MA_200
time.sleep(0.1)

all_passed = True

# Test 1: Normal continuous mode
print("--- Continuous mode (AF=0) ---")
sensor.proximity_active_force_mode = False
time.sleep(0.1)

ps1 = sensor.proximity
time.sleep(0.1)
ps2 = sensor.proximity
print(f"  Reading 1: {ps1}")
print(f"  Reading 2: {ps2}")

if ps1 > 0 and ps2 > 0:
    print("  PASS: Continuous readings work")
else:
    print("  FAIL: Continuous readings not working")
    all_passed = False
print()

# Test 2: Active force mode
print("--- Active force mode (AF=1) ---")
sensor.proximity_active_force_mode = True
time.sleep(0.1)

# First reading might be stale from before AF mode
ps_stale = sensor.proximity
print(f"  Stale reading (before trigger): {ps_stale}")

# Trigger a new reading
print("  Triggering PS reading...")
sensor.trigger_proximity()
time.sleep(0.1)  # Wait for reading to complete

ps_triggered = sensor.proximity
print(f"  Triggered reading: {ps_triggered}")

if ps_triggered > 0:
    print("  PASS: Triggered reading is valid")
else:
    print("  FAIL: Triggered reading is zero")
    all_passed = False
print()

# Test 3: Verify AF mode is actually engaged
print("--- Verify AF mode engaged ---")
af_enabled = sensor.proximity_active_force_mode
print(f"  AF mode enabled: {'YES' if af_enabled else 'NO'}")
if af_enabled:
    print("  PASS: AF mode getter works")
else:
    print("  FAIL: AF mode not reported as enabled")
    all_passed = False
print()

# Test 4: Disable AF mode, verify continuous readings resume
print("--- Disabling AF mode ---")
sensor.proximity_active_force_mode = False
time.sleep(0.1)

ps_resumed = sensor.proximity
print(f"  Reading after AF disabled: {ps_resumed}")

if ps_resumed > 0:
    print("  PASS: Continuous readings resumed")
else:
    print("  FAIL: Readings not resumed after AF disabled")
    all_passed = False

print()
print("=========================")
if all_passed:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")

print("~~END~~")
