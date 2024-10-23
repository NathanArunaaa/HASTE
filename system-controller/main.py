import socket
import RPi.GPIO as GPIO

from functions import (
    sample_extend, 
    sample_retract
)
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False) 

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
                    break  # Exit the inner loop on disconnection

                command = data.decode('utf-8').strip()
                print(f"Received command: {command}")

                if command == "EXTEND_SAMPLE":
                    print("Extending sample...")
                    sample_extend()
                elif command == "RETRACT_SAMPLE":
                    print("Retracting sample...")
                    sample_retract()
                else:
                    print(f"Unknown command: {command}")

            except Exception as process_error:
                print(f"Error processing command: {process_error}")
                break  # Ensure the inner loop exits on error

        connection.close()  # Close connection after handling

    except Exception as e:
        print(f"An error occurred: {e}")
