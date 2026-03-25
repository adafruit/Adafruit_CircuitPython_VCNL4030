# SPDX-FileCopyrightText: Copyright (c) 2026 Tim Cocks for Adafruit Industries
#
# SPDX-License-Identifier: MIT
"""
HW test: Verify LED current affects proximity readings

Hardware setup:
- VCNL4030 sensor connected via I2C
- Stepper motor on DIR=D10, STEP=D9 with reflector in close position

Test: Higher LED current should give higher proximity counts
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


print("=== 04_ps_led_current ===")
print("Testing proximity at different LED currents")
print()

sensor = VCNL4030(board.I2C())
sensor.reset()
print("VCNL4030 initialized")
print("Reflector in close position")
print()

sensor.proximity_enabled = True
sensor.led_low_current = False  # Normal mode
time.sleep(0.1)

# Test different LED currents
current_configs = [
    ("50mA", ProxLEDCurrent.MA_50),
    ("100mA", ProxLEDCurrent.MA_100),
    ("200mA", ProxLEDCurrent.MA_200),
]

print("LED current vs proximity:")
readings = []
for name, current in current_configs:
    sensor.led_current = current
    time.sleep(0.1)
    val = median_read(sensor, "proximity")
    readings.append(val)
    print(f"  {name}: {val}")
print()

# Test LED_I_LOW mode (reduces to 1/10 of set current)
print("--- LED_I_LOW mode test ---")
sensor.led_current = ProxLEDCurrent.MA_200
sensor.led_low_current = False
time.sleep(0.1)
ps_normal = median_read(sensor, "proximity")
print(f"  200mA normal: {ps_normal}")

sensor.led_low_current = True  # ~20mA actual
time.sleep(0.1)
ps_low = median_read(sensor, "proximity")
print(f"  200mA + LOW mode (~20mA): {ps_low}")

# Reset
sensor.led_low_current = False

print()
print("=========================")

increasing = (readings[1] > readings[0]) and (readings[2] > readings[1])
if increasing:
    print("PASS: Higher LED current gives higher counts")
else:
    print("FAIL: Counts did not increase with LED current")

if ps_low < ps_normal / 3:
    print("PASS: LED_I_LOW mode reduces reading significantly")
else:
    print("FAIL: LED_I_LOW mode did not reduce reading enough")

print("~~END~~")
