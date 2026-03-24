"""
HW test: Verify proximity responds to stepper-positioned reflector

Hardware setup:
- VCNL4030 sensor connected via I2C
- Stepper motor on DIR=D10, STEP=D9 (1/8 microstep mode)
  with a reflective surface attached
- Start position: reflector in front of (close to) sensor
- After quarter rotation (400 steps): reflector moves away from sensor
"""

import time
import board
from digitalio import DigitalInOut, Direction
from adafruit_vcnl4030 import VCNL4030, ProxLEDCurrent

# Stepper config from sensor_neopixel_servo_test.py
DIR = DigitalInOut(board.D10)
DIR.direction = Direction.OUTPUT
STEP = DigitalInOut(board.D9)
STEP.direction = Direction.OUTPUT

MICRO_MODE = 8  # 1/8 microstep
STEPS_PER_ROT = 200 * MICRO_MODE  # 1600 steps per full rotation
QUARTER_ROT = STEPS_PER_ROT // 4  # 400 steps = 90 degrees
HALF_ROT = STEPS_PER_ROT // 2  # 400 steps = 90 degrees


def step_motor(steps, direction, step_delay=0.001):
    DIR.value = direction
    for _ in range(steps):
        STEP.value = True
        time.sleep(step_delay)
        STEP.value = False
        time.sleep(step_delay)


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


print("=== 01_proximity_servo ===")
print("Verify proximity with stepper-positioned reflector")
print()

sensor = VCNL4030(board.I2C())
print("VCNL4030 initialized")

sensor.proximity_enabled = True
sensor.led_current = ProxLEDCurrent.MA_200
time.sleep(0.2)

# CLOSE: starting position, reflector in front of sensor
print("--- CLOSE (start position) ---")
time.sleep(1.0)
ps_close = median_read(sensor, "proximity")
print(f"  Proximity: {ps_close}")

# FAR: quarter rotation moves reflector away from sensor
print("--- FAR (quarter rotation) ---")
step_motor(HALF_ROT, direction=True)
time.sleep(1.0)
ps_far = median_read(sensor, "proximity")
print(f"  Proximity: {ps_far}")

# Return to close position
step_motor(HALF_ROT, direction=False)
time.sleep(1.0)

print()
print("=========================")
print(f"  Far: {ps_far}  Close: {ps_close}  Diff: {ps_close - ps_far}")
if ps_close > ps_far + 50:
    print("PASS: Close reading significantly higher than far")
else:
    print("FAIL: Close reading not significantly higher")

print("~~END~~")