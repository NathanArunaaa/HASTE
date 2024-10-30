import socket
import RPi.GPIO as GPIO

from functions import (
    sample_extend, 
    sample_retract,
    cut_sections,
    home_motor
)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('0.0.0.0', 5000)) 
server_socket.listen(1)

home_motor()

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
                elif command == "SYSTEM_CALIBRATION":
                    print("Retracting sample...")
                    home_motor()
                else:
                    print(f"Unknown command: {command}")

            except Exception as process_error:
                print(f"Error processing command: {process_error}")
                break  

        connection.close()  

    except Exception as e:
        print(f"An error occurred: {e}")
