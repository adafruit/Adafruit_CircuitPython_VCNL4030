# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
HW test: Verify active force mode for triggered readings

Hardware setup:
- VCNL4030 sensor connected via I2C
- Stepper motor on DIR=D10, STEP=D9 (1/8 microstep mode)
  with a reflective surface attached
- Start position: reflector in front of (close to) sensor

Test: In AF mode, readings should only update after trigger.
- Trigger with reflector CLOSE -> expect high reading
- Move reflector FAR without triggering -> reading should NOT change
- Trigger with reflector FAR -> expect low reading
"""

import time

import board
from digitalio import DigitalInOut, Direction

from adafruit_vcnl4030 import VCNL4030, ProxLEDCurrent

# Stepper config
DIR = DigitalInOut(board.D10)
DIR.direction = Direction.OUTPUT
STEP = DigitalInOut(board.D9)
STEP.direction = Direction.OUTPUT

MICRO_MODE = 8  # 1/8 microstep
STEPS_PER_ROT = 200 * MICRO_MODE  # 1600 steps per full rotation
HALF_ROT = STEPS_PER_ROT // 2  # 800 steps = 180 degrees


def step_motor(steps, direction, step_delay=0.001):
    DIR.value = direction
    for _ in range(steps):
        STEP.value = True
        time.sleep(step_delay)
        STEP.value = False
        time.sleep(step_delay)


print("=== 10_active_force ===")
print("Testing PS active force mode with stepper-positioned reflector")
print()

sensor = VCNL4030(board.I2C())
sensor.reset()
print("VCNL4030 initialized")

sensor.proximity_enabled = True
sensor.led_current = ProxLEDCurrent.MA_200
time.sleep(0.2)

all_passed = True

# Test 1: Continuous mode baseline — confirm stepper positions work
print("--- Continuous mode baseline (AF=0) ---")
sensor.proximity_active_force_mode = False
time.sleep(0.1)

# CLOSE: starting position
time.sleep(1.0)
ps_close_continuous = sensor.proximity
print(f"  Proximity (close): {ps_close_continuous}")

# FAR: half rotation moves reflector away
step_motor(HALF_ROT, direction=True)
time.sleep(1.0)
ps_far_continuous = sensor.proximity
print(f"  Proximity (far):   {ps_far_continuous}")

if ps_close_continuous > ps_far_continuous + 50:
    print("  PASS: Continuous mode shows close > far")
else:
    print("  FAIL: Continuous mode close/far difference too small")
    all_passed = False
print()

# Return reflector to close position
step_motor(HALF_ROT, direction=False)
time.sleep(1.0)

# Test 2: Active force mode — triggered reading with reflector CLOSE
print("--- AF mode: trigger with reflector CLOSE ---")
sensor.proximity_active_force_mode = True
time.sleep(0.1)

sensor.trigger_proximity()
time.sleep(0.1)
ps_af_close = sensor.proximity
print(f"  Triggered reading (close): {ps_af_close}")
print()

# Test 3: Move reflector FAR without triggering — reading should NOT change
print("--- AF mode: move to FAR without triggering ---")
step_motor(HALF_ROT, direction=True)
time.sleep(1.0)

ps_af_no_trigger = sensor.proximity
print(f"  Reading without trigger (reflector far): {ps_af_no_trigger}")

if ps_af_no_trigger == ps_af_close:
    print("  PASS: Reading unchanged without trigger (AF mode holding last value)")
else:
    print("  FAIL: Reading changed without trigger (AF mode not holding value)")
    all_passed = False
print()

# Test 4: Trigger with reflector FAR — reading should now update to low value
print("--- AF mode: trigger with reflector FAR ---")
sensor.trigger_proximity()
time.sleep(0.1)
ps_af_far = sensor.proximity
print(f"  Triggered reading (far): {ps_af_far}")

if ps_af_close > ps_af_far + 50:
    print("  PASS: Triggered close reading significantly higher than triggered far")
else:
    print("  FAIL: Triggered close/far difference too small")
    all_passed = False
print()

# Test 5: Disable AF mode, return to close, verify continuous readings resume
print("--- Disabling AF mode, returning to CLOSE ---")
sensor.proximity_active_force_mode = False
step_motor(HALF_ROT, direction=False)
time.sleep(1.0)

ps_resumed = sensor.proximity
print(f"  Reading after AF disabled (close): {ps_resumed}")

if ps_resumed > ps_far_continuous + 50:
    print("  PASS: Continuous readings resumed with expected close value")
else:
    print("  FAIL: Readings not resumed correctly after AF disabled")
    all_passed = False

print()
print("=========================")
if all_passed:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")

print("~~END~~")
