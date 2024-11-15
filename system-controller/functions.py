import RPi.GPIO as GPIO
import time

# ------Pin Configuration-------
Y_DIR_PIN = 20  
Y_STEP_PIN = 21 

X_DIR_PIN = 27  
X_STEP_PIN = 4

Y_LIMIT_PIN = 23  
X_LIMIT_PIN = 17

# ------Inits-------
CW = 1   
CCW = 0  

STEP_DELAY = 0.00000000000001 
HOMING_STEP_DELAY = 0.01  

BLADE_RETRACT_STEPS = 2000  
BLADE_ADVANCE_STEPS = 2000   

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


GPIO.setup(Y_DIR_PIN, GPIO.OUT)
GPIO.setup(Y_STEP_PIN, GPIO.OUT)
GPIO.setup(X_DIR_PIN, GPIO.OUT)
GPIO.setup(X_STEP_PIN, GPIO.OUT)

GPIO.setup(Y_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
GPIO.setup(X_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) 




# ------Motion Handlers-------
def step_motor(dir_pin, step_pin, direction, steps):
    GPIO.output(dir_pin, direction)

    for _ in range(steps):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(STEP_DELAY)


def home_motor():
   
    step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 1000)  
    GPIO.output(Y_DIR_PIN, CW) 

    while GPIO.input(Y_LIMIT_PIN) == GPIO.LOW:  
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 10)

    step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 10)
    print("Homing Y complete. Motor zeroed.")


    step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 1000)  
    GPIO.output(X_DIR_PIN, CW) 

    while GPIO.input(X_LIMIT_PIN) == GPIO.LOW:  
        step_motor(X_DIR_PIN, X_STEP_PIN, CW, 10 )

    step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 10)
    print("Homing X complete. Motor zeroed.")

def cut_sections(num_sections):

    try:
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 30000)
        for section in range(num_sections):
            print(f"Cutting section {section + 1}...")

            step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 15000)
            step_motor(X_DIR_PIN, X_STEP_PIN, CW, BLADE_RETRACT_STEPS)
            step_motor(X_DIR_PIN, X_STEP_PIN, CCW, BLADE_ADVANCE_STEPS)
            step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 15000)

            print(f"Section {section + 1} complete.\n")

        print(section, "sections cut.")

    finally:
        #remember to return status code to control panel
        print("Cutting complete.")

def sample_extend():
    try:
        print("Raising sample holder...")
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 36000)  
    finally:
        print("Sample holder raised.")


def sample_retract():
    try:
        print("Lowering sample holder...")
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 37000)  
    finally:
        print("Sample holder lowered.")