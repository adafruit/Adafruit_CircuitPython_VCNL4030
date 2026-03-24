"""
HW test: Verify ALS responds to NeoPixel light changes

Hardware setup:
- VCNL4030 sensor connected via I2C
- NeoPixel ring (16 pixels) on pin D6, facing the sensor

Test: ALS reading should increase when NeoPixels turn ON
"""

import time
import board
import neopixel
from adafruit_vcnl4030 import VCNL4030, ALSIntegrationTime

NEOPIXEL_PIN = board.D7
NEOPIXEL_COUNT = 8


def set_all_pixels(pixels, r, g, b):
    pixels.fill((r, g, b))


def median_read(sensor, read_type, n=3, delay_s=0.05):
    """Take n readings of the given type and return the median."""
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


print("=== 00_als_neopixel ===")
print("Testing ALS response to NeoPixel light")
print()

# Initialize NeoPixels - start OFF
pixels = neopixel.NeoPixel(NEOPIXEL_PIN, NEOPIXEL_COUNT, brightness=1.0, auto_write=True)
set_all_pixels(pixels, 0, 0, 0)

# Initialize sensor
sensor = VCNL4030(board.I2C())
print("VCNL4030 initialized")

# Enable ALS and white channel, set integration time
sensor.als_enabled = True
sensor.white_channel_enabled = True
sensor.als_integration_time = ALSIntegrationTime.MS_100
time.sleep(0.2)  # Wait for first reading

all_passed = True

# Test 1: ALS raw value increases with NeoPixels
print("--- Test 1: ALS raw value ---")
set_all_pixels(pixels, 0, 0, 0)
time.sleep(0.3)
als_off = median_read(sensor, "als")
print(f"  ALS OFF: {als_off}")

set_all_pixels(pixels, 255, 255, 255)
time.sleep(0.3)
als_on = median_read(sensor, "als")
print(f"  ALS ON:  {als_on}")

if als_on > als_off + 10:
    print("  PASS: ALS increased with NeoPixels ON")
else:
    print("  FAIL: ALS did not increase significantly")
    all_passed = False
print()

# Test 2: Lux value increases with NeoPixels
print("--- Test 2: Lux calculation ---")
set_all_pixels(pixels, 0, 0, 0)
time.sleep(0.3)
lux_off = median_read(sensor, "lux")
print(f"  Lux OFF: {lux_off:.2f}")

set_all_pixels(pixels, 255, 255, 255)
time.sleep(0.3)
lux_on = median_read(sensor, "lux")
print(f"  Lux ON:  {lux_on:.2f}")

if lux_on > lux_off + 0.5:
    print("  PASS: Lux increased with NeoPixels ON")
else:
    print("  FAIL: Lux did not increase significantly")
    all_passed = False
print()

# Test 3: White channel responds
print("--- Test 3: White channel ---")
set_all_pixels(pixels, 0, 0, 0)
time.sleep(0.3)
white_off = median_read(sensor, "white")
print(f"  White OFF: {white_off}")

set_all_pixels(pixels, 255, 255, 255)
time.sleep(0.3)
white_on = median_read(sensor, "white")
print(f"  White ON:  {white_on}")

if white_on > white_off + 10:
    print("  PASS: White channel increased with NeoPixels ON")
else:
    print("  FAIL: White channel did not increase significantly")
    all_passed = False
print()

# Cleanup - turn off NeoPixels
set_all_pixels(pixels, 0, 0, 0)

# Final result
print("=========================")
if all_passed:
    print("ALL TESTS PASSED")
else:
    print("SOME TESTS FAILED")

print("~~END~~")
