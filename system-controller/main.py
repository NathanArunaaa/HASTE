import socket
import RPi.GPIO as GPIO
import json
import threading

from functions import (
    sample_extend, 
    sample_retract,
    cut_sections,
    home_motor,
    face_sample,
    flush_system,
    illuminator_on,
    illuminator_off,
    pump_A_off,
    pump_B_off,
    pump_A_on,
    pump_B_on,
    valve_close,
    valve_open,
    heater_off,
    heater_on,
    capture_image,
    system_shutdown,
    clear_database
   
)

from web_interface.app import start_flask


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

home_motor()

pump_A_off()
pump_B_off()

file_path = "./config.json"

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5000)) 
server_socket.listen(1)


print("Waiting for a connection...")

flask_thread = threading.Thread(target=start_flask)
flask_thread.daemon = True
flask_thread.start()

def read_config():
    try:
        with open(file_path, 'r') as json_file:
            config = json.load(json_file)
        return config
    except Exception as e:
        print(f"Error reading config file: {e}")
        return None

while True:
    try:
        connection, address = server_socket.accept()
        print(f"Connected to {address}")

        while True:
            try:
                data = connection.recv(1024)  
                if not data:
                    print("Connection closed by client.")
                    break  
                command = data.decode('utf-8').strip()
                print(f"Received command: {command}")

                if command == "EXTEND_SAMPLE":
                    print("Extending sample...")
                    sample_extend()
                    
                elif command == "RETRACT_SAMPLE":
                    print("Retracting sample...")
                    sample_retract()
                    
                elif command == "SECTION_SAMPLE":
                    print("Cutting sections...")
                    config = read_config()
                    if config:
                        section_value = config.get("section_value")  
                        micron_value = config.get("micron_value")
                        lis_number = config.get("lis_number")  
  

                        cut_sections(section_value, micron_value, lis_number)
                    else:
                        print("Error: Could not read section_value and micron_value from config.")
                
                elif command == "FACE_SAMPLE":
                    print("Facing sample...")
                    config = read_config()  
                    if config:
                        face_value = config.get("face_value")  
                        face_sample(face_value)
                    else:
                        print("Error: Could not read face_value from config.")
                
                elif command == "SYSTEM_CALIBRATION":
                    print("Calibrating system...")
                    home_motor()

                elif command == "SYSTEM_FLUSH":
                    print("Flushing system...")
                    flush_system()
                    
                elif command == "SYS_SHUTDOWN":
                    print("Shutting down system...")
                    system_shutdown()

                elif command == "ILLUMINATOR_ON":
                    print("Turning illuminator on...")
                    illuminator_on()
                    
                elif command == "ILLUMINATOR_OFF":
                    print("Turning illuminator off...")
                    illuminator_off()
                   
                elif command == "VALVE_OPEN":
                    print("Opening valve...")
                    valve_open()

                elif command == "VALVE_CLOSE":
                    print("Closing valve...")
                    valve_close()
                    
                elif command == "PUMP_A_ON":
                    print("Turning pump A on...")
                    pump_A_on()

                elif command == "PUMP_A_OFF":
                    print("Turning pump A off...")
                    pump_A_off()
                
                elif command == "PUMP_B_ON":
                    print("Turning pump B on...")
                    pump_B_on()

                elif command == "PUMP_B_OFF":
                    print("Turning pump B off...")
                    pump_B_off()

                elif command == "HEATER_ON":
                    print("Turning heater on...")
                    heater_on()
                    pump_A_on()
                    
                elif command == "HEATER_OFF":
                    print("Turning heater off...")
                    heater_off()
                    pump_A_off()

                elif command == "DEBUG_CAMERA":
                    print("Capturing image...")
                    config = read_config()  
                    if config:
                        lis_number = config.get("lis_number", "default_lis")  
                        capture_image(lis_number)
                    else:
                        print("Error: Could not read lis_number from config.")

                elif command == "CLEAR_DATABASE":
                    print("Clearing database...")
                    clear_database()
                    
                    
                    
                else:
                    print(command)
                    section_value, micron_value, face_value, lis_number = command.split("|")
                    
                    section_value = int(section_value)  
                    micron_value = int(micron_value)  
                    face_value = int(face_value)  
                    lis_number = lis_number
                    
                    data_dict = {
                        "section_value": section_value,
                        "micron_value": micron_value,
                        "face_value": face_value,
                        "lis_number": lis_number
                    }  
                    
                    file_path = "./config.json"
                    
                    with open(file_path, 'w') as json_file:
                        json.dump(data_dict, json_file, indent=4)

            except Exception as process_error:
                print(f"Error processing command: {process_error}")
                break  

        connection.close()  

    except Exception as e:
        print(f"An error occurred: {e}")
