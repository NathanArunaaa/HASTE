import RPi.GPIO as GPIO
import time
import cv2
import os
import shutil

# ------Pin Configuration-------
Y_DIR_PIN = 20  
Y_STEP_PIN = 21 

X_DIR_PIN = 27  
X_STEP_PIN = 4

Y_LIMIT_PIN = 23  
X_LIMIT_PIN = 17
X2_LIMIT_PIN = 18

# ------Inits-------
CW = 1   
CCW = 0  

STEP_DELAY = 0.00001

DEFAULT_MIN_DELAY = 0.00005 
DEFAULT_MAX_DELAY = 0.0001     
DEFAULT_ACCEL_STEPS = 1000  
HOMING_STEP_DELAY = 0.01  

BLADE_ADVANCE_STEPS = 20



GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


GPIO.setup(Y_DIR_PIN, GPIO.OUT)
GPIO.setup(Y_STEP_PIN, GPIO.OUT)
GPIO.setup(X_DIR_PIN, GPIO.OUT)
GPIO.setup(X_STEP_PIN, GPIO.OUT)

GPIO.setup(Y_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)  
GPIO.setup(X_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
GPIO.setup(X2_LIMIT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)



def system_shutdown():
    pump_B_on()
    time.sleep(10)
    GPIO.cleanup()
    os.system("sudo shutdown now")

# ------Liquid Handlers-------

def valve_close():
    RELAY_B_PIN1= 6
    GPIO.setup(RELAY_B_PIN1, GPIO.OUT)
    GPIO.output(RELAY_B_PIN1, GPIO.HIGH)
        
def valve_open():
    RELAY_B_PIN1 = 6
    GPIO.setup(RELAY_B_PIN1, GPIO.OUT)
    GPIO.output(RELAY_B_PIN1, GPIO.LOW)


def pump_A_off():
    RELAY_A_PIN1= 24
    GPIO.setup(RELAY_A_PIN1, GPIO.OUT)
    GPIO.output(RELAY_A_PIN1, GPIO.HIGH)
        
def pump_A_on():
    RELAY_A_PIN1 = 24
    GPIO.setup(RELAY_A_PIN1, GPIO.OUT)
    GPIO.output(RELAY_A_PIN1, GPIO.LOW)
        
def pump_B_off():
    RELAY_A_PIN2 = 25
    GPIO.setup(RELAY_A_PIN2, GPIO.OUT)
    GPIO.output(RELAY_A_PIN2, GPIO.HIGH)
        
def pump_B_on():
    RELAY_A_PIN2 = 25
    GPIO.setup(RELAY_A_PIN2, GPIO.OUT)
    GPIO.output(RELAY_A_PIN2, GPIO.LOW)

def heater_off():
    RELAY_B_PIN1 = 16
    GPIO.setup(RELAY_B_PIN1, GPIO.OUT)
    GPIO.output(RELAY_B_PIN1, GPIO.HIGH)
        
def heater_on():
    RELAY_B_PIN1 = 16
    GPIO.setup(RELAY_B_PIN1, GPIO.OUT)
    GPIO.output(RELAY_B_PIN1, GPIO.LOW)
    
        

def flush_system():
    pump_A_on()
    pump_B_on()
    time.sleep(20)
    pump_A_off()
    pump_B_off()

# ------Imaging Handlers-------

def illuminator_off():
    RELAY_B_PIN4= 12
    GPIO.setup(RELAY_B_PIN4, GPIO.OUT)
    GPIO.output(RELAY_B_PIN4, GPIO.HIGH)
        
def illuminator_on():
    RELAY_B_PIN4 = 12
    GPIO.setup(RELAY_B_PIN4, GPIO.OUT)
    GPIO.output(RELAY_B_PIN4, GPIO.LOW)



def capture_image(patient_id):
    illuminator_on()
    time.sleep(1)
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    base_dir = os.path.join(script_dir, 'web_interface', 'static', 'images')  
    save_dir = os.path.join(base_dir, str(patient_id))  

    if not os.path.exists(save_dir):
        print(f"Patient folder {save_dir} does not exist. Creating folder.")
        os.makedirs(save_dir, exist_ok=True)  

    existing_files = [f for f in os.listdir(save_dir) if f.endswith('.jpg')]
    section_ids = []

    for file in existing_files:
        try:
            section_id = int(file.split('.')[0])  
            section_ids.append(section_id)
        except ValueError:
            continue  

    next_section_id = max(section_ids, default=0) + 1  
    filename = f"{next_section_id}.jpg"  
    camera_index = 0
    cap = cv2.VideoCapture(camera_index)

    if not cap.isOpened():
        print("Error: Could not open the camera.")
        return
    
    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
    print(f"Camera opened with resolution: {width}x{height}")
 
    time.sleep(2)
    ret, frame = cap.read()
    cap.release()

    if not ret:
        print("Error: Could not capture an image from the camera.")
        return
    
    text = f"{patient_id}-#: {next_section_id}"
    font = cv2.FONT_HERSHEY_DUPLEX
    font_scale = 0.6
    font_thickness = 1
    text_color = (0, 0, 0)  
    position = (10, 30)  

    cv2.putText(frame, text, position, font, font_scale, text_color, font_thickness, cv2.LINE_AA)

    save_path = os.path.join(save_dir, filename)
    print(f"Saving image to: {save_path}")

    quality_params = [cv2.IMWRITE_JPEG_QUALITY, 100]  
    if cv2.imwrite(save_path, frame, quality_params):
        print(f"Image saved successfully at {save_path}")
    else:
        print("Error: Failed to save the image.")

    illuminator_off()


def clear_database():
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    base_dir = os.path.join(script_dir, 'web_interface', 'static', 'images')  

    if not os.path.exists(base_dir):
        print(f"Image directory {base_dir} does not exist.")
        return
    
    for folder in os.listdir(base_dir):
        folder_path = os.path.join(base_dir, folder)
        if os.path.isdir(folder_path):
            print(f"Deleting folder {folder_path}...")
            shutil.rmtree(folder_path)  

    print("All image folders have been deleted.")



# ------Motion Handlers-------
def step_motor(dir_pin, step_pin, direction, steps, 
               min_delay=DEFAULT_MIN_DELAY, 
               max_delay=DEFAULT_MAX_DELAY, 
               accel_steps=DEFAULT_ACCEL_STEPS):
    GPIO.output(dir_pin, direction)

    def get_step_delay(i):
        """ Compute delay dynamically based on acceleration profile """
        if i < accel_steps: 
            return max_delay - (i / accel_steps) * (max_delay - min_delay)
        elif i > steps - accel_steps:  
            return min_delay + ((i - (steps - accel_steps)) / accel_steps) * (max_delay - min_delay)
        return min_delay 

    for i in range(steps):
        step_delay = get_step_delay(i)
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(step_delay)
        
def step_motor_no_accel(dir_pin, step_pin, direction, steps):
    GPIO.output(dir_pin, direction)

    for _ in range(steps):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(STEP_DELAY)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(STEP_DELAY)

def home_motor():
    step_motor_no_accel(X_DIR_PIN, X_STEP_PIN, CCW, 1000)  
    GPIO.output(X_DIR_PIN, CW) 

    while GPIO.input(X_LIMIT_PIN) == GPIO.LOW:  
        step_motor_no_accel(X_DIR_PIN, X_STEP_PIN, CW, 10 )

    step_motor_no_accel(X_DIR_PIN, X_STEP_PIN, CCW, 10)
    print("Homing X complete. Motor zeroed.")

    step_motor_no_accel(Y_DIR_PIN, Y_STEP_PIN, CCW, 1000)  
    GPIO.output(Y_DIR_PIN, CW) 

    while GPIO.input(Y_LIMIT_PIN) == GPIO.LOW:  
        step_motor_no_accel(Y_DIR_PIN, Y_STEP_PIN, CW, 10)

    step_motor_no_accel(Y_DIR_PIN, Y_STEP_PIN, CCW, 10)
    print("Homing Y complete. Motor zeroed.")
    
    
def face_sample(num_sections):
    try:
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 8000)
        GPIO.output(X_DIR_PIN, CW) 

        while GPIO.input(X2_LIMIT_PIN) == GPIO.LOW:  
            step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 10 )


        for section in range(num_sections):
            step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 6000)
            step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 6000)
            step_motor(X_DIR_PIN, X_STEP_PIN, CCW, BLADE_ADVANCE_STEPS)


        print(section, "sections cut.")
    finally:
        print("Cutting complete.")



def cut_sections(num_sections, section_thickness, patient_id):
 
    try:
        for section in range(num_sections):
            print(f"Cutting section {section + 1}...")

            step_motor(X_DIR_PIN, X_STEP_PIN, CCW, BLADE_ADVANCE_STEPS)
            step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 6000)
            step_motor(X_DIR_PIN, X_STEP_PIN, CW, BLADE_ADVANCE_STEPS)
            step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 6000)
            step_motor(X_DIR_PIN, X_STEP_PIN, CCW, BLADE_ADVANCE_STEPS)

            capture_image(patient_id)

            print(f"Section {section + 1} complete.\n")

        print(section, "sections cut.")
        
    finally:
        print("Cutting complete.")
        home_motor()
        

def sample_extend():
    try:
        print("Raising sample holder...")
        step_motor_no_accel(Y_DIR_PIN, Y_STEP_PIN, CCW, 33000)  
    finally:
        print("Sample holder raised.")



def sample_retract():
    try:
        print("Lowering sample holder...")
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 37000)  
    finally:
        print("Sample holder lowered.")
        

