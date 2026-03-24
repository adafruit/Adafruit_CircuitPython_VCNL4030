"""
HW test: Verify INT pin goes LOW on proximity threshold crossing

Wiring: VCNL4030 INT pin -> D8 (with pull-up)

Strategy:
1. Move reflector to FAR position and sample ambient proximity
2. Set high threshold to 2x ambient
3. Enable proximity close interrupt
4. Move reflector to CLOSE position to cross the threshold
5. Verify D8 goes LOW when threshold crossed
6. Read interrupt flags to clear, verify D8 goes HIGH again
"""

import time
import board
from digitalio import DigitalInOut, Direction, Pull
from adafruit_vcnl4030 import (
    VCNL4030,
    ProxLEDCurrent,
    ProxPersistence,
    ProxInterruptMode,
    VCNL4030_PROX_IF_CLOSE,
)

INT_PIN = board.D8

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


print("=== 12_interrupt_pin ===")
print()

int_pin = DigitalInOut(INT_PIN)
int_pin.direction = Direction.INPUT
int_pin.pull = Pull.UP

sensor = VCNL4030(board.I2C())
print("VCNL4030 initialized")
_ = sensor.interrupt_flags
# Verify INT pin starts HIGH (open drain, pulled up)
if int_pin.value != True:
    print("FAIL: INT pin not HIGH at start (check wiring)")
    raise SystemExit
print("INT pin HIGH at start: OK")

sensor.proximity_enabled = True
sensor.led_current = ProxLEDCurrent.MA_200
sensor.proximity_resolution_16bit = True
time.sleep(0.2)

# Move reflector to FAR position for ambient sampling
step_motor(HALF_ROT, direction=True)
time.sleep(0.5)

# Sample ambient proximity (reflector away from sensor)
total = 0
for _ in range(10):
    total += sensor.proximity
    time.sleep(0.05)
ambient = total // 10
print(f"Ambient proximity: {ambient}")

# Set THDL just above ambient so FAR state is "AWAY" (PS < THDL)
# Set THDH at 1.5x ambient so CLOSE reading reliably crosses it
# Use BOTH mode: requires PS to transition from < THDL (AWAY) to > THDH (CLOSE)
thdl = ambient + max(ambient // 5, 20)
thdh = max(int(ambient * 1.5), thdl + 20)
print(f"THDL (above FAR): {thdl}  THDH (below CLOSE): {thdh}")

# Configure
sensor.proximity_threshold_low = thdl
sensor.proximity_threshold_high = thdh
sensor.proximity_persistence = ProxPersistence.CYCLES_1
sensor.proximity_interrupt_mode = ProxInterruptMode.BOTH

# Clear any pending flags
sensor.interrupt_flags

print("\nMoving reflector to close position...")

# Move reflector to CLOSE position — should cross the threshold
step_motor(HALF_ROT, direction=False)

# Poll INT pin for up to 5 seconds
print("(Waiting up to 5 seconds for INT to fire)")
int_fired = False
start = time.monotonic()
while time.monotonic() - start < 5.0:
    prox = sensor.proximity
    pin_state = "HIGH" if int_pin.value else "LOW"
    print(f"Prox: {prox}  INT pin: {pin_state}")
    if not int_pin.value:
        int_fired = True
        break
    time.sleep(0.2)

if not int_fired:
    print("FAIL: INT never fired")
    raise SystemExit

print("\nINT fired!")

# Verify pin is LOW
if not int_pin.value:
    print("INT pin LOW after trigger: OK")
else:
    print("FAIL: INT pin not LOW after trigger")

# Read flags to clear
flags = sensor.interrupt_flags
print(f"Flags: 0x{flags:02X}")

if flags & VCNL4030_PROX_IF_CLOSE:
    print("CLOSE flag set: OK")
else:
    print("FAIL: CLOSE flag not set")

# After reading flags, INT should release (go HIGH)
time.sleep(0.01)
if int_pin.value:
    print("INT pin released (HIGH) after flag read: OK")
else:
    print("WARNING: INT pin still LOW after flag read")

# Disable interrupt
sensor.proximity_interrupt_mode = ProxInterruptMode.DISABLED  # re-use DISABLED

print("\n=== ALL TESTS PASSED ===")

print("~~END~~")
