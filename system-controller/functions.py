import RPi.GPIO as GPIO
import time
import cv2
import os
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

STEP_DELAY = 0.0000001
HOMING_STEP_DELAY = 0.01  

BLADE_RETRACT_STEPS = 200 
BLADE_ADVANCE_STEPS = 230

FACE_BLADE_RETRACT_STEPS = 200 
FACE_BLADE_ADVANCE_STEPS = 230

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


GPIO.setup(Y_DIR_PIN, GPIO.OUT)
GPIO.setup(Y_STEP_PIN, GPIO.OUT)
GPIO.setup(X_DIR_PIN, GPIO.OUT)
GPIO.setup(X_STEP_PIN, GPIO.OUT)

GPIO.setup(Y_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
GPIO.setup(X_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) 



# ------Liquid Handlers-------

def pump_A_off():
    RELAY_PIN1= 24
    GPIO.setup(RELAY_PIN1, GPIO.OUT)
    GPIO.output(RELAY_PIN1, GPIO.HIGH)
        
def pump_A_on():
    RELAY_PIN1 = 24
    GPIO.setup(RELAY_PIN1, GPIO.OUT)
    GPIO.output(RELAY_PIN1, GPIO.LOW)
        
def pump_B_off():
    RELAY_PIN2 = 25
    GPIO.setup(RELAY_PIN2, GPIO.OUT)
    GPIO.output(RELAY_PIN2, GPIO.HIGH)
        
def pump_B_on():
    RELAY_PIN2 = 25
    GPIO.setup(RELAY_PIN2, GPIO.OUT)
    GPIO.output(RELAY_PIN2, GPIO.LOW)
        

def flush_system():
    pump_A_on()
    pump_B_on()
    time.sleep(5)
    pump_A_off()
    pump_B_off()

# ------Imaging Handlers-------
def capture_image(patient_id):
  
    save_dir = "control-panel/web_interface/static/images/" + patient_id
    filename = "webcam_capture.jpg"
    
    os.makedirs(save_dir, exist_ok=True)
    
    camera_index = 0
    
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        return "Error: Could not open the camera."
    
    
    ret, frame = cap.read()
    
    cap.release()
    
    if not ret:
        return "Error: Could not capture an image from the camera."
    
    save_path = os.path.join(save_dir, filename)
    quality_params = [cv2.IMWRITE_JPEG_QUALITY, 100]  
    if cv2.imwrite(save_path, frame, quality_params):
        return f"Image saved successfully at {save_path}"
    else:
        return "Error: Failed to save the image."



# ------Motion Handlers-------
def step_motor(dir_pin, step_pin, direction, steps):
    GPIO.output(dir_pin, direction)

    for _ in range(steps):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(STEP_DELAY)

def home_motor():
    step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 1000)  
    GPIO.output(X_DIR_PIN, CW) 

    while GPIO.input(X_LIMIT_PIN) == GPIO.LOW:  
        step_motor(X_DIR_PIN, X_STEP_PIN, CW, 10 )

    step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 10)
    print("Homing X complete. Motor zeroed.")

    step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 1000)  
    GPIO.output(Y_DIR_PIN, CW) 

    while GPIO.input(Y_LIMIT_PIN) == GPIO.LOW:  
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 10)

    step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 10)
    print("Homing Y complete. Motor zeroed.")
    
    
def face_sample():
    try:
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 4000)
        step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 2000)

        for section in range(5):

            step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 4000)
            step_motor(X_DIR_PIN, X_STEP_PIN, CW, BLADE_RETRACT_STEPS)
            step_motor(X_DIR_PIN, X_STEP_PIN, CCW, BLADE_ADVANCE_STEPS)
            step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 4000)

        print(section, "sections cut.")
    finally:
        #remember to return status code to control panel
        print("Cutting complete.")



def cut_sections(num_sections):
 
    try:
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 4000)
        step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 11000)

        for section in range(num_sections):
            print(f"Cutting section {section + 1}...")

            step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 4000)
            step_motor(X_DIR_PIN, X_STEP_PIN, CW, BLADE_RETRACT_STEPS)
            step_motor(X_DIR_PIN, X_STEP_PIN, CCW, BLADE_ADVANCE_STEPS)
            step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 4000)

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
        

