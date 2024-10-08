import RPi.GPIO as GPIO
import time


DIR_PIN = 20  
STEP_PIN = 21  
CW = 1 
CCW = 0  
STEP_DELAY = 0.001  

GPIO.setmode(GPIO.BCM)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(STEP_PIN, GPIO.OUT)

def step_motor(direction, steps):
    
    GPIO.output(DIR_PIN, direction)
    
    for _ in range(steps):
        GPIO.output(STEP_PIN, GPIO.HIGH)
        time.sleep(STEP_DELAY) 
        
        GPIO.output(STEP_PIN, GPIO.LOW)
        time.sleep(STEP_DELAY)

try:
    while True:
        
        print("Rotating clockwise...")
        step_motor(CW, 200)  
        
        time.sleep(1)  

        print("Rotating counterclockwise...")
        step_motor(CCW, 200)
        
        time.sleep(1)

except KeyboardInterrupt:
    print("Program interrupted")

finally:
    GPIO.cleanup()  
