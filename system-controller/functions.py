import RPi.GPIO as GPIO
import time
import cv2
import os


# ------ Pin Configuration -------
Y_DIR_PIN = 20  
Y_STEP_PIN = 21 
X_DIR_PIN = 27  
X_STEP_PIN = 4
Y_LIMIT_PIN = 23  
X_LIMIT_PIN = 17
X2_LIMIT_PIN = 18

# ------ Direction Constants -------
CW = 1   # Clockwise
CCW = 0  # Counterclockwise

# ------ Motion Parameters -------
MIN_STEP_DELAY = 0.0001  # Fastest speed
MAX_STEP_DELAY = 0.01    # Slowest speed (for start/stop)
ACCELERATION_STEPS = 50  # Steps to accelerate/decelerate

# Blade Movement Steps
BLADE_RETRACT_STEPS = 200
BLADE_ADVANCE_STEPS = 10
FACE_BLADE_RETRACT_STEPS = 200
FACE_BLADE_ADVANCE_STEPS = 230

# GPIO Setup
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




# ------Motion Handlers-------
# ------ Smooth Stepper Function -------
def step_motor(dir_pin, step_pin, direction, steps, min_delay=MIN_STEP_DELAY, max_delay=MAX_STEP_DELAY):
    GPIO.output(dir_pin, direction)

    # **Acceleration Phase**
    for i in range(ACCELERATION_STEPS):
        step_delay = max_delay - (i / ACCELERATION_STEPS) * (max_delay - min_delay)
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(step_delay)

    # **Constant Speed Phase**
    for _ in range(steps - 2 * ACCELERATION_STEPS):
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(min_delay)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(min_delay)

    # **Deceleration Phase**
    for i in range(ACCELERATION_STEPS, 0, -1):
        step_delay = max_delay - (i / ACCELERATION_STEPS) * (max_delay - min_delay)
        GPIO.output(step_pin, GPIO.HIGH)
        time.sleep(step_delay)
        GPIO.output(step_pin, GPIO.LOW)
        time.sleep(step_delay)

# ------ Homing Function -------
def home_motor():
    print("Homing X-axis...")
    step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 1000, max_delay=0.008)
    GPIO.output(X_DIR_PIN, CW)

    while GPIO.input(X_LIMIT_PIN) == GPIO.LOW:
        step_motor(X_DIR_PIN, X_STEP_PIN, CW, 10, min_delay=0.002)

    step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 10, min_delay=0.002)
    print("Homing X complete.")

    print("Homing Y-axis...")
    step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 1000, max_delay=0.008)
    GPIO.output(Y_DIR_PIN, CW)

    while GPIO.input(Y_LIMIT_PIN) == GPIO.LOW:
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 10, min_delay=0.002)

    step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 10, min_delay=0.002)
    print("Homing Y complete.")

# ------ Cutting Function -------
def cut_sections(num_sections):
    print("Starting cutting process...")
    step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 4000, min_delay=0.0005)
    step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 11000, min_delay=0.0005)

    for section in range(num_sections):
        print(f"Cutting section {section + 1}...")
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 4000, min_delay=0.0005)
        step_motor(X_DIR_PIN, X_STEP_PIN, CW, BLADE_RETRACT_STEPS, min_delay=0.0005)
        step_motor(X_DIR_PIN, X_STEP_PIN, CCW, BLADE_ADVANCE_STEPS, min_delay=0.0005)
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 4000, min_delay=0.0005)

    print("Cutting complete.")

# ------ Facing Function (Smooth) -------
def face_sample(num_sections):
    try:
        print("Starting face sample process...")
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 4000, min_delay=0.0005)
        GPIO.output(X_DIR_PIN, CW)

        while GPIO.input(X2_LIMIT_PIN) == GPIO.LOW:
            step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 10, min_delay=0.0005)

        for section in range(num_sections):
            print(f"Facing section {section + 1}...")

            # Blade advances for facing
            step_motor(X_DIR_PIN, X_STEP_PIN, CCW, FACE_BLADE_ADVANCE_STEPS, min_delay=0.0005)

            # Y-axis moves back and forth to cut
            step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 4000, min_delay=0.0005)
            step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 4000, min_delay=0.0005)

        print(f"{num_sections} sections faced.")
    finally:
        print("Facing complete.")



def sample_retract():
    try:
        print("Lowering sample holder...")
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 37000)  
    finally:
        print("Sample holder lowered.")
        

