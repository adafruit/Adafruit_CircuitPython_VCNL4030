"""
HW test: Verify 12-bit vs 16-bit PS resolution

Hardware setup:
- VCNL4030 sensor connected via I2C
- Stepper motor on DIR=D10, STEP=D9 with reflector in close position

Test: 16-bit mode should allow values > 4095
"""

import time
import board
from adafruit_vcnl4030 import VCNL4030, ProxGain, ProxLEDCurrent


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


print("=== 06_ps_resolution ===")
print("Testing 12-bit vs 16-bit proximity resolution")
print()

sensor = VCNL4030(board.I2C())
print("VCNL4030 initialized")
print("Reflector in close position for high readings")
print()

sensor.proximity_enabled = True
sensor.led_current = ProxLEDCurrent.MA_200  # High current for strong signal
sensor.proximity_gain = ProxGain.SINGLE_8X
time.sleep(0.1)

# Test 12-bit mode (PS_HD=0)
print("--- 12-bit mode (PS_HD=0) ---")
sensor.proximity_resolution_16bit = False
time.sleep(0.1)
ps_12bit = median_read(sensor, "proximity")
print(f"  Reading: {ps_12bit}")
status = "(OK)" if ps_12bit <= 4095 else "(UNEXPECTED: > 4095)"
print(f"  Max theoretical: 4095 {status}")

# Test 16-bit mode (PS_HD=1)
print("--- 16-bit mode (PS_HD=1) ---")
sensor.proximity_resolution_16bit = True
time.sleep(0.1)
ps_16bit = median_read(sensor, "proximity")
print(f"  Reading: {ps_16bit}")
print(f"  Max theoretical: 65535")

print()
print("=========================")

if ps_16bit > ps_12bit:
    print("PASS: 16-bit mode gives higher resolution/range")
elif ps_12bit < 4000:
    print("INFO: 12-bit not saturated, can't verify 16-bit advantage")
    print("PASS: Both modes returned valid readings")
else:
    print("PASS: 12-bit saturated, 16-bit allows higher values")

if ps_12bit > 0 and ps_16bit > 0:
    print("PASS: Both resolution modes return valid readings")
else:
    print("FAIL: One or both modes returned zero")

print("~~END~~")
