import RPi.GPIO as GPIO
import time


DIR_PIN = 20  
STEP_PIN = 21  
CW = 1 
CCW = 0  
STEP_DELAY = 0.001  
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 

GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)

def step_motor(direction, steps):
    
    GPIO.output(DIR_PIN, direction)
    
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(STEP_DELAY) 
        
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(STEP_DELAY)

def sample_extend():
    try:
        print("Goin up...")
        step_motor(CCW, 5000)
        step_motor(CCW, 500)  
  
        

    except KeyboardInterrupt:
        print("Program interrupted")

    finally:
        print("done")

def sample_retract():
    try:
        print("Goin down...")
        step_motor(CCW, 5000)  
        
    except KeyboardInterrupt:
        print("Program interrupted")

    finally:
        print("done")

