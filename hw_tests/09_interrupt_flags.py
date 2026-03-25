# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
HW test: Verify interrupt flags fire on threshold crossings

Hardware setup:
- VCNL4030 sensor connected via I2C
- Stepper motor on DIR=D10, STEP=D9 with reflector starting in close position
- NeoPixel ring (8 pixels) on pin D7

Key insight: flags fire on TRANSITIONS. The sensor must cross from
below-low to above-high (CLOSE) or above-high to below-low (AWAY).
Start from a known state below threshold, then cross above.
"""
# ruff: noqa: PLW0603

import time

import board
import neopixel
from digitalio import DigitalInOut, Direction

from adafruit_vcnl4030 import (
    VCNL4030,
    VCNL4030_ALS_IF_H,
    VCNL4030_ALS_IF_L,
    VCNL4030_PROX_IF_AWAY,
    VCNL4030_PROX_IF_CLOSE,
    ALSIntegrationTime,
    ALSPersistence,
    ProxInterruptMode,
    ProxLEDCurrent,
    ProxPersistence,
)

NEOPIXEL_PIN = board.D7
NEOPIXEL_COUNT = 8

MICRO_MODE = 8
STEPS_PER_ROT = 200 * MICRO_MODE
HALF_ROT = STEPS_PER_ROT // 2

DIR = DigitalInOut(board.D10)
DIR.direction = Direction.OUTPUT
STEP = DigitalInOut(board.D9)
STEP.direction = Direction.OUTPUT


def step_motor(steps, direction, step_delay=0.001):
    DIR.value = direction
    for _ in range(steps):
        STEP.value = True
        time.sleep(step_delay)
        STEP.value = False
        time.sleep(step_delay)


passes = 0
fails = 0


def record_pass(msg):
    global passes
    print(f"  PASS: {msg}")
    passes += 1


def record_fail(msg, flags):
    global fails
    print(f"  FAIL: {msg} (flags=0x{flags:02X})")
    fails += 1


print("=== 09_interrupt_flags ===")
print()

pixels = neopixel.NeoPixel(NEOPIXEL_PIN, NEOPIXEL_COUNT, brightness=0.2, auto_write=True)
pixels.fill((0, 0, 0))

sensor = VCNL4030(board.I2C())
sensor.reset()
print("VCNL4030 initialized")

sensor.proximity_enabled = True
sensor.als_enabled = True
sensor.led_current = ProxLEDCurrent.MA_200
sensor.proximity_persistence = ProxPersistence.CYCLES_1
sensor.als_persistence = ALSPersistence.CYCLES_1
sensor.als_integration_time = ALSIntegrationTime.MS_100
time.sleep(0.5)

# ===== PS AWAY flag =====
# Start CLOSE (above threshold), then move FAR to trigger AWAY
print("--- PS AWAY Flag ---")
# Reflector already in close position — take close reading
time.sleep(1.0)
ps_close = sensor.proximity
print(f"  PS close: {ps_close}")

sensor.proximity_threshold_low = ps_close // 4
sensor.proximity_threshold_high = ps_close // 2
sensor.proximity_interrupt_mode = ProxInterruptMode.BOTH

print(f"  Low thresh: {ps_close // 4}  High thresh: {ps_close // 2}")

sensor.interrupt_flags  # clear
time.sleep(0.2)

# Move far — should trigger AWAY
step_motor(HALF_ROT, direction=True)
time.sleep(1.5)

ps_far = sensor.proximity
print(f"  PS far: {ps_far}")
time.sleep(0.2)

flags = sensor.interrupt_flags
if flags & VCNL4030_PROX_IF_AWAY:
    record_pass("PS AWAY flag set")
else:
    record_fail("PS AWAY flag not set", flags)

# ===== PS CLOSE flag =====
# We're now FAR (below low threshold). Move CLOSE to trigger CLOSE.
print("--- PS CLOSE Flag ---")
sensor.interrupt_flags  # clear
time.sleep(0.2)

step_motor(HALF_ROT, direction=False)
time.sleep(1.5)

ps_close = sensor.proximity
print(f"  PS close: {ps_close}")
time.sleep(0.2)

flags = sensor.interrupt_flags
if flags & VCNL4030_PROX_IF_CLOSE:
    record_pass("PS CLOSE flag set")
else:
    record_fail("PS CLOSE flag not set", flags)

# ===== ALS HIGH flag =====
# Start dark, then go bright to trigger ALS_H
print("--- ALS HIGH Flag ---")
pixels.fill((0, 0, 0))
time.sleep(1.0)

als_off = sensor.als
print(f"  ALS dark: {als_off}")

sensor.als_threshold_high = als_off + 2000
sensor.als_threshold_low = max(0, als_off - 1000)
sensor.als_interrupt_enabled = True

print(f"  Low thresh: {max(0, als_off - 1000)}  High thresh: {als_off + 2000}")

sensor.interrupt_flags  # clear
time.sleep(0.2)

# Go bright — should trigger ALS_H
pixels.fill((255, 255, 255))
time.sleep(1.5)

als_on = sensor.als
print(f"  ALS bright: {als_on}")

flags = sensor.interrupt_flags
if flags & VCNL4030_ALS_IF_H:
    record_pass("ALS HIGH flag set")
else:
    record_fail("ALS HIGH flag not set", flags)

# ===== ALS LOW flag =====
# We're now bright (above high threshold). Go dark to trigger ALS_L.

print("--- ALS LOW Flag ---")
sensor.als_threshold_low = als_off + 2000
sensor.als_threshold_high = 60000

print(f"  Low thresh: {als_off + 2000}  High thresh: 60000")

sensor.interrupt_flags  # clear
time.sleep(0.2)

# Go dark — should trigger ALS_L
pixels.fill((0, 0, 0))
time.sleep(1.5)

als_dark = sensor.als
print(f"  ALS dark: {als_dark}")

flags = sensor.interrupt_flags
if flags & VCNL4030_ALS_IF_L:
    record_pass("ALS LOW flag set")
else:
    record_fail("ALS LOW flag not set", flags)

# Cleanup
pixels.fill((0, 0, 0))

print()
print("=========================")
print(f"PASSED: {passes}  FAILED: {fails}")
if fails == 0:
    print("ALL TESTS PASSED")

print("~~END~~")
