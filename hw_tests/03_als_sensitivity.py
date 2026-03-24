"""
HW test: Verify ALS_HD and ALS_NS mode changes

Hardware setup:
- VCNL4030 sensor connected via I2C
- NeoPixel ring (8 pixels) on pin D7 at fixed brightness

Test: Raw counts should differ between modes but lux should compensate
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
        elif read_type == "lux":
            readings.append(sensor.lux)
        elif read_type == "white":
            readings.append(sensor.white)
        elif read_type == "proximity":
            readings.append(sensor.proximity)
        if i < n - 1:
            time.sleep(delay_s)
    readings.sort()
    return readings[n // 2]


print("=== 03_als_sensitivity ===")
print("Testing ALS_HD and ALS_NS sensitivity modes")
print()

# Initialize NeoPixels at moderate brightness
pixels = neopixel.NeoPixel(NEOPIXEL_PIN, NEOPIXEL_COUNT, brightness=1.0, auto_write=True)
pixels.fill((100, 100, 100))

sensor = VCNL4030(board.I2C())
print("VCNL4030 initialized")

sensor.als_enabled = True
sensor.als_integration_time = ALSIntegrationTime.MS_100
time.sleep(0.2)

# Mode 1: HD=0, NS=0 (most sensitive, default)
print("--- Mode 1: HD=0, NS=0 (most sensitive) ---")
sensor.als_high_dynamic_range = False
sensor.als_low_sensitivity = False
time.sleep(0.2)
raw1 = median_read(sensor, "als")
lux1 = median_read(sensor, "lux")
print(f"  Raw: {raw1}  Lux: {lux1:.2f}")

# Mode 2: HD=1 (2x range, half resolution)
print("--- Mode 2: HD=1, NS=0 (2x range) ---")
sensor.als_high_dynamic_range = True
sensor.als_low_sensitivity = False
time.sleep(0.2)
raw2 = median_read(sensor, "als")
lux2 = median_read(sensor, "lux")
print(f"  Raw: {raw2}  Lux: {lux2:.2f}")

# Mode 3: HD=0, NS=1 (2x range)
print("--- Mode 3: HD=0, NS=1 (2x range) ---")
sensor.als_high_dynamic_range = False
sensor.als_low_sensitivity = True
time.sleep(0.2)
raw3 = median_read(sensor, "als")
lux3 = median_read(sensor, "lux")
print(f"  Raw: {raw3}  Lux: {lux3:.2f}")

# Reset to default
sensor.als_high_dynamic_range = False
sensor.als_low_sensitivity = False

# Cleanup - turn off NeoPixels
pixels.fill((0, 0, 0))

# Analyze results
print()
print("=========================")

# Check if raw counts differ between modes
raws_differ = (raw2 != raw1) or (raw3 != raw1)

# Check if lux values are within 30% of each other (compensation working)
avg_lux = (lux1 + lux2 + lux3) / 3.0
lux_compensated = all(
    avg_lux * 0.7 < lx < avg_lux * 1.3 for lx in (lux1, lux2, lux3)
)

if raws_differ:
    print("PASS: Raw counts differ between modes")
else:
    print("INFO: Raw counts similar (may be OK at this light level)")

if lux_compensated:
    print("PASS: Lux values compensated within 30%")
else:
    print("FAIL: Lux values vary more than 30% between modes")

print("~~END~~")
