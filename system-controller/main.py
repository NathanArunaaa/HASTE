import time
import threading
import serial
from functions import (
    sample_extend,
    sample_retract
)

# Function to ensure the serial connection is initialized
def initialize_serial_connection():
    try:
        ser = serial.Serial('/dev/serial0', 9600, timeout=1)
        ser.flush()  # Flush any initial junk data
        print("Serial port opened successfully.")
        return ser
    except serial.SerialException as e:
        print(f"Error initializing serial port: {e}")
        exit(1)

# Function to filter out non-printable characters
def clean_command(raw_command):
    return ''.join(c for c in raw_command if c.isprintable())

# Function to process commands
def process_command(ser, command):
    if command == "EXTEND_SAMPLE":
        sample_extend()
        response = "extended sample"
        ser.write(response.encode('utf-8'))  
        print(f"Sent: {response}")
    elif command == "RETRACT_SAMPLE":
        sample_retract()
        response = "retracted sample"
        ser.write(response.encode('utf-8'))  
        print(f"Sent: {response}")
    else:
        response = "Unknown command"
        ser.write(f"{response}\n".encode('utf-8'))
        print(f"Received unknown command: {command}")

# Function to listen for commands in a separate thread
def listen_for_commands(ser):
    while True:
        try:
            if ser.in_waiting > 0:
                raw_data = ser.readline()
                print(f"Raw Data: {raw_data}")

                # First try decoding with UTF-8 and ignore errors
                command = raw_data.decode('utf-8', errors='ignore').rstrip()

                # Clean command to remove non-printable characters
                cleaned_command = clean_command(command)
                print(f"Received cleaned command: {cleaned_command}")

                if cleaned_command:
                    process_command(ser, cleaned_command)
                else:
                    print("No valid command found after cleaning")

            time.sleep(0.5)  # Adjust this delay to prevent CPU overuse

        except UnicodeDecodeError as e:
            print(f"Error decoding command: {e}")
            print(f"Raw data (hex): {raw_data.hex()}")
        except serial.SerialException as e:
            print(f"Serial communication error: {e}")
            time.sleep(2)  # Wait before retrying
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

def main():
    ser = initialize_serial_connection()

    # Start the thread for listening to serial commands
    listener_thread = threading.Thread(target=listen_for_commands, args=(ser,), daemon=True)
    listener_thread.start()

    try:
        while True:
            time.sleep(1)  # Keep the main thread alive
    except KeyboardInterrupt:
        print("Exiting program.")
        ser.close()  # Close the serial port before exiting
        exit(0)

if __name__ == "__main__":
    main()
