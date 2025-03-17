import RPi.GPIO as GPIO
import time
import cv2
import os
import math
import pigpio

# ------ Pin Configuration -------
Y_DIR_PIN = 20  
Y_STEP_PIN = 21 

X_DIR_PIN = 27  
X_STEP_PIN = 4

Y_LIMIT_PIN = 23  
X_LIMIT_PIN = 17
X2_LIMIT_PIN = 18

# ------ Inits -------
CW = 1   
CCW = 0  

# Step Delays (Default)
STEP_FREQ = 2000  # Frequency in Hz (Adjust for speed/smoothness)
ACCEL_STEPS = 100  # Number of steps to accelerate/decelerate

pi = pigpio.pi()

if not pi.connected:
    print("pigpio daemon not running. Start it with 'sudo pigpiod'")
    exit()


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
    base_dir = os.path.join('web_interface', 'static', 'images')  
    save_dir = os.path.join(base_dir, patient_id)  

    if not os.path.exists(save_dir):
        print(f"Patient folder {patient_id} does not exist. Creating folder.")
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
    





# Set direction pins as outputs
pi.set_mode(Y_DIR_PIN, pigpio.OUTPUT)
pi.set_mode(X_DIR_PIN, pigpio.OUTPUT)

# Function to send steps using PWM (smoother than bit-banging)
def step_motor(dir_pin, step_pin, direction, steps, frequency=STEP_FREQ):
    """Moves the stepper motor using pigpio PWM for smooth motion."""
    
    pi.write(dir_pin, direction)  # Set motor direction
    pi.hardware_PWM(step_pin, frequency, 500000)  # 50% duty cycle

    time.sleep(steps / frequency)  # Wait for the required number of steps

    pi.hardware_PWM(step_pin, 0, 0)  # Stop PWM after motion

# Homing function using pigpio
def home_motor():
    """Home the X and Y axes using limit switches."""
    
    # Move X axis to home position
    pi.write(X_DIR_PIN, CCW)
    while pi.read(X_LIMIT_PIN) == 0:
        step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 10)
    
    print("Homing X complete. Motor zeroed.")

    # Move Y axis to home position
    pi.write(Y_DIR_PIN, CCW)
    while pi.read(Y_LIMIT_PIN) == 0:
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 10)

    print("Homing Y complete. Motor zeroed.")

# Function for smooth cutting
def cut_sections(num_sections):
    """Perform smooth section cutting using PWM control."""
    try:
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 4000)  # Move to start position
        step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 11000)

        for section in range(num_sections):
            print(f"Cutting section {section + 1}...")

            step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 4000)
            step_motor(X_DIR_PIN, X_STEP_PIN, CW, 200)  # Retract smoothly
            step_motor(X_DIR_PIN, X_STEP_PIN, CCW, 10)   # Advance blade
            step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 4000)

            print(f"Section {section + 1} complete.\n")

        print(f"{num_sections} sections cut.")

    finally:
        print("Cutting complete.")

def sample_extend():
    """Extend sample smoothly."""
    try:
        print("Raising sample holder...")
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CCW, 33000)  # Adjust steps for height
    finally:
        print("Sample holder raised.")

# Retract Sample Holder
def sample_retract():
    """Retract sample smoothly."""
    try:
        print("Lowering sample holder...")
        step_motor(Y_DIR_PIN, Y_STEP_PIN, CW, 37000)  # Adjust steps for lowering
    finally:
        print("Sample holder lowered.")

# Cleanup function
def cleanup():
    """Stops pigpio and releases GPIOs."""
    pi.stop()
    print("GPIO cleanup done.")

