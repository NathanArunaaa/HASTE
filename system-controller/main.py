import json
import socket
import RPi.GPIO as GPIO

from functions import sample_extend, sample_retract, cut_sections, home_motor

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

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

                command_data = data.decode('utf-8').strip()

                # Parse the JSON command
                try:
                    command_obj = json.loads(command_data)
                    command = command_obj.get("command")
                    parameters = command_obj.get("parameters", {})
                except json.JSONDecodeError:
                    response = {
                        "status": "error",
                        "code": 400,
                        "message": "Invalid JSON received."
                    }
                    connection.sendall(json.dumps(response).encode('utf-8'))
                    continue

                print(f"Received command: {command} with parameters: {parameters}")

                # Process commands and respond
                if command == "EXTEND_SAMPLE":
                    sample_extend()
                    response = {
                        "status": "success",
                        "code": 200,
                        "message": "Sample extended successfully."
                    }
                elif command == "RETRACT_SAMPLE":
                    sample_retract()
                    response = {
                        "status": "success",
                        "code": 200,
                        "message": "Sample retracted successfully."
                    }
                elif command == "SECTION_SAMPLE":
                    sections = parameters.get("sections", 3)
                    speed = parameters.get("speed", 100)
                    cut_sections(sections, speed)
                    response = {
                        "status": "success",
                        "code": 200,
                        "message": f"Cut {sections} sections at speed {speed}."
                    }
                elif command == "SYSTEM_CALIBRATION":
                    home_motor()
                    response = {
                        "status": "success",
                        "code": 200,
                        "message": "System calibrated successfully."
                    }
                else:
                    response = {
                        "status": "error",
                        "code": 404,
                        "message": f"Unknown command: {command}"
                    }

                # Send response back to client
                connection.sendall(json.dumps(response).encode('utf-8'))

            except Exception as process_error:
                print(f"Error processing command: {process_error}")
                response = {
                    "status": "error",
                    "code": 500,
                    "message": f"Internal server error: {process_error}"
                }
                connection.sendall(json.dumps(response).encode('utf-8'))
                break

        connection.close()

    except Exception as e:
        print(f"An error occurred: {e}")
