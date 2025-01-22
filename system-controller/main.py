import socket
import RPi.GPIO as GPIO
import time
from functions import (
    sample_extend, 
    sample_retract,
    cut_sections,
    home_motor,
    face_sample,
    flush_system,
    pump_A_on,
    pump_A_off,
    pump_B_on,
    pump_B_off,
    illuminator_off,
    illuminator_on
)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

pump_A_off()
pump_B_off()

home_motor()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5000)) 
server_socket.listen(1)


print("Waiting for a connection...")

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
                    print("Retracting sample...")
                    cut_sections(3)
                
                elif command == "FACE_SAMPLE":
                    print("Retracting sample...")
                    face_sample()
                
                elif command == "SYSTEM_CALIBRATION":
                    print("Retracting sample...")
                    home_motor()

                elif command == "SYSTEM_FLUSH":
                    print("Flushing system...")
                    flush_system()

                elif command == "ILLUMINATOR_ON":
                    print("Turning illuminator on...")
                    illuminator_on()
                    
                elif command == "ILLUMINATOR_OFF":
                    print("Turning illuminator off...")
                    illuminator_off()
                    
                    
                    
                else:
                    print(f"Unknown command: {command}")

            except Exception as process_error:
                print(f"Error processing command: {process_error}")
                break  

        connection.close()  

    except Exception as e:
        print(f"An error occurred: {e}")
