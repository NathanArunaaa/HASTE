import RPi.GPIO as GPIO
import time

# ------Pin Configuration-------
Y_DIR_PIN = 20  
Y_STEP_PIN = 21 

X_DIR_PIN = 19  
X_STEP_PIN = 27 


# ------Inits-------
CW = 1   
CCW = 0  

STEP_DELAY = 0.0005  
BLADE_RETRACT_STEPS = 50  
BLADE_ADVANCE_STEPS = 60   

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


GPIO.setup(Y_DIR_PIN, GPIO.OUT)
GPIO.setup(Y_STEP_PIN, GPIO.OUT)
GPIO.setup(X_DIR_PIN, GPIO.OUT)
GPIO.setup(X_STEP_PIN, GPIO.OUT)

# ------Motion Handlers-------
def step_motor(dir_pin, step_pin, direction, steps):
    GPIO.output(dir_pin, direction)

    for _ in range(steps):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(STEP_DELAY)

def cut_sections(num_sections, y_steps_per_section):

    try:
        for section in range(num_sections):
            print(f"Cutting section {section + 1}...")

            step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, y_steps_per_section)
            step_motor(X_DIR_PIN, X_STEP_PIN, CW, BLADE_RETRACT_STEPS)
            step_motor(X_DIR_PIN, X_STEP_PIN, CCW, BLADE_ADVANCE_STEPS)

            print(f"Section {section + 1} complete.\n")

        print(section, "sections cut.")

    finally:
        #remember to return status code to control panel
        print("Cutting complete.")

def sample_extend():
    try:
        print("Raising sample holder...")
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 37000)  
    finally:
        print("Sample holder raised.")


def sample_retract():
    try:
        print("Lowering sample holder...")
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 37000)  
    finally:
        print("Sample holder lowered.")