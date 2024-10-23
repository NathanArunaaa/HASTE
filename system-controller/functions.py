import RPi.GPIO as GPIO
import time

# Pin Definitions
DIR_PIN = 20   # Direction pin
STEP_PIN = 21  # Step pin

# Direction Constants
CW = GPIO.HIGH   # Clockwise
CCW = GPIO.LOW   # Counter-Clockwise

# Configuration
STEP_DELAY = 0.001  # Adjust delay for precise stepping (1ms)
STEPS_PER_REV = 200  # Change based on your motor (e.g., 200 for 1.8°/step)

# GPIO Setup
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Suppress warnings
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)

def step_motor(direction, steps):
    """
    Control the stepper motor by sending precise pulses.
    
    Args:
        direction: CW or CCW (GPIO.HIGH or GPIO.LOW)
        steps: Number of steps to execute
    """
    GPIO.output(DIR_PIN, direction)  # Set rotation direction
    print(f"Starting motor in {'CW' if direction == CW else 'CCW'} direction")

    for step in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)  # Pulse step pin
        time.sleep(STEP_DELAY)  # Wait for motor to respond
        GPIO.output(STEP_PIN, GPIO.LOW)  # Reset step pin
        time.sleep(STEP_DELAY)  # Delay between steps

        # Debugging output to monitor progress every 100 steps
        if step % 100 == 0:
            print(f"Step {step}/{steps}")

    print("Movement complete")

def sample_extend():
    """
    Move the motor upwards (extend) for a precise number of steps.
    """
    try:
        print("Extending...")
        step_motor(CCW, 5000)  # Adjust step count for your needs
    except KeyboardInterrupt:
        print("Process interrupted")
    finally:
        print("GPIO cleaned up, program ended")

def sample_retract():
    """
    Move the motor downwards (retract) for a precise number of steps.
    """
    try:
        print("Retracting...")
        step_motor(CW, 5000)  # Adjust step count for your needs
    except KeyboardInterrupt:
        print("Process interrupted")
    finally:
        print("GPIO cleaned up, program ended")

# Main Execution
