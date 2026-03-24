"""
HW test: Verify PS gain modes affect sensitivity

Hardware setup:
- VCNL4030 sensor connected via I2C
- Stepper motor on DIR=D10, STEP=D9 with reflector in close position

Gain modes (most to least sensitive):
  TWO_STEP > SINGLE_1X > SINGLE_8X
The "8X" means 8x extended range, NOT 8x more gain.
"""

import time
import board
from adafruit_vcnl4030 import VCNL4030, ProxGain, ProxLEDCurrent


def read_gain(sensor, gain):
    sensor.proximity_gain = gain
    time.sleep(0.2)
    sensor.proximity  # Discard first reading
    time.sleep(0.05)
    return sensor.proximity


print("=== 05_ps_gain ===")
print("Testing PS gain modes")
print()

sensor = VCNL4030(board.I2C())
print("VCNL4030 initialized")

sensor.proximity_enabled = True
sensor.led_current = ProxLEDCurrent.MA_200
time.sleep(0.2)

two_step = read_gain(sensor, ProxGain.TWO_STEP)
single_1x = read_gain(sensor, ProxGain.SINGLE_1X)
single_8x = read_gain(sensor, ProxGain.SINGLE_8X)

print("Gain mode vs proximity (most to least sensitive):")
print(f"  TWO_STEP:  {two_step}")
print(f"  SINGLE_1X: {single_1x}")
print(f"  SINGLE_8X: {single_8x}")

print()
print("=========================")

pass_all = True
if two_step > single_1x:
    print("PASS: TWO_STEP > SINGLE_1X")
else:
    print("FAIL: TWO_STEP should be > SINGLE_1X")
    pass_all = False

if single_1x > single_8x:
    print("PASS: SINGLE_1X > SINGLE_8X")
else:
    print("FAIL: SINGLE_1X should be > SINGLE_8X")
    pass_all = False

if pass_all:
    print("ALL TESTS PASSED")

print("~~END~~")
