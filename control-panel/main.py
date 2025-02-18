import customtkinter
import threading
import sys
import cv2
import socket 
from PIL import Image, ImageTk
from tkinter import messagebox
import os
import time
import glob
from pyzbar.pyzbar import decode
import numpy as np
import json


from web_interface.app import start_flask
from functions import (
    change_scaling_event, 
    sys_shutdown, 
    sys_restart, 
    get_local_ip,
)

customtkinter.set_appearance_mode("light")  
customtkinter.set_default_color_theme("blue") 


class TextWidgetStream:
    def __init__(self, text_widget):
        self.text_widget = text_widget

    def write(self, message):
        self.text_widget.after(0, self._write, message)
    
    def _write(self, message):
        self.text_widget.insert("end", message)
        self.text_widget.yview("end")  

    def flush(self):
        pass

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("HASTE CONTROL PANEL")

        self.change_scaling_event("130%")
        self.after(100, self.make_fullscreen)
      # self.config(cursor="none")
        
        self.sample_loaded = False
        self.scanning_done = False
        
        self.pump_A_state = False
        self.pump_B_state = False
    
        
        self.cap = cv2.VideoCapture(0) 
        
        self.selected_section_value = 10  
        self.selected_micron_value = 50
        self.selected_lis_number =  "N/A"
        self.selected_face_value = 10

        self.target_temp = 40
        self.actual_temp = None
        self.blade_cylce = None
        

        self.contructed_command = None


        #------Sidebar-------
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)
         
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0, fg_color="white")
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="H . A . S . T . E", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Start", hover_color="#3b8ed0", command=self.open_config_menu)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_1.configure(cursor="none")

        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="System Calibration", hover_color="#3b8ed0", command=lambda: self.send_command("SYSTEM_CALIBRATION"))
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_2.configure(cursor="none")

        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Load Sample", hover_color="#3b8ed0", command=self.open_loading_menu)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_3.configure(cursor="none")
        
        self.sidebar_button_6 = customtkinter.CTkButton(self.sidebar_frame, text="Flush System", hover_color="#3b8ed0", command=self.open_flush_menu)
        self.sidebar_button_6.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_button_6.configure(cursor="none")

        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, text="System Restart", hover_color="#3b8ed0", command=self.sys_restart)
        self.sidebar_button_4.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.sidebar_button_4.configure(cursor="none")

        self.sidebar_button_5 = customtkinter.CTkButton(self.sidebar_frame, text="Shut Down", hover_color="#3b8ed0", command=self.sys_shutdown)
        self.sidebar_button_5.grid(row=7 , column=0, padx=20, pady=(10, 10))
        self.sidebar_button_5.configure(cursor="none")
        

        local_ip = get_local_ip() 
        self.local_ip_label = customtkinter.CTkLabel(self.sidebar_frame, text=f"{local_ip}:5000", anchor="w")
        self.local_ip_label.grid(row=8, column=0, padx=20, pady=(10, 20))



        #------Video Feeds-------
        self.video_feeds_frame = customtkinter.CTkFrame(self, fg_color="white")
        self.video_feeds_frame.grid(row=1, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.video_feeds_frame.grid_columnconfigure(0, weight=1)
        self.video_feeds_frame.grid_rowconfigure(0, weight=1)

        self.video_frame = customtkinter.CTkFrame(self.video_feeds_frame, fg_color="gray")  
        self.video_frame.grid(row=0, column=0, sticky="nsew")
        self.video_frame.grid_columnconfigure(0, weight=1)
        self.video_frame.grid_rowconfigure(0, weight=1)

        self.video_label = customtkinter.CTkLabel(self.video_frame, text="", width=600, height=200)  
        self.video_label.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.video_label.grid_propagate(False)

        #------Console log-------
        self.textbox = customtkinter.CTkTextbox(self)

        self.textbox.grid(row=0, column=1, padx=(20, 20), pady=(20, 20), sticky="nsew")
        self.textbox.configure(cursor="none") 

        sys.stdout = TextWidgetStream(self.textbox)
        sys.stderr = TextWidgetStream(self.textbox)
        
        #------Tabs-------
        self.tabview = customtkinter.CTkTabview(self, fg_color="white", width=250)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(0, 0), sticky="nsew")
        self.tabview.add("Patient")
        self.tabview.add("Blade")
        self.tabview.add("Steppers")

       
        #------Patient-------
        self.tabview.tab("Patient").grid_rowconfigure((0, 1, 2), weight=1)
        self.tabview.tab("Patient").grid_columnconfigure(0, weight=1)

        
        self.start_scan = customtkinter.CTkButton(self.tabview.tab("Patient"), text="Register New LIS ID", width=30, command=self.start_lis_scan)
        self.start_scan.grid(row=0, column=0, padx=10, pady=10,sticky="nsew")
        
        self.finish_scan = customtkinter.CTkButton(self.tabview.tab("Patient"), text="Complete Scan", width=30, command=self.finish_lis_scan)
        self.finish_scan.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        
        
        self.loaded_id = customtkinter.CTkLabel(self.tabview.tab("Patient"), text="Loaded ID: --")
        self.loaded_id.grid(row=2, column=0, padx=20, pady=20, sticky="nsew")
        
        #------Blades-------
        self.tabview.tab("Blade").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Blade").grid_columnconfigure(0, weight=1)
        
        self.change_blade = customtkinter.CTkButton(self.tabview.tab("Blade"), text="Change Blade", width=30, )
        self.change_blade.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.blade_cylce_label = customtkinter.CTkLabel(self.tabview.tab("Blade"), text="Blade Cycles: ")
        self.blade_cylce_label.grid(row=1, column=0, padx=20, pady=20, sticky="nsew")
        
        try:
            with open('control-panel/config.json', 'r') as file:
                data = json.loads(file.read())
                self.blade_cylce = data.get('blade_cycles', 0)
                self.blade_cylce_label.configure(text=f"Blade Cycles: {self.blade_cylce}")
        except (FileNotFoundError, json.JSONDecodeError):
            self.blade_cylce_label.configure(text="Error Reading Config")
            
        #------Steppers-------
        self.tabview.tab("Steppers").grid_rowconfigure((0, 1, 2), weight=1)
        self.tabview.tab("Steppers").grid_columnconfigure((0, 1, 2), weight=1)

        self.up_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="↑", width=20)
        self.up_button.grid(row=0, column=1, sticky="nsew")

        self.left_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="←", width=20)
        self.left_button.grid(row=1, column=0, sticky="nsew")

        self.center_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="O", width=20)
        self.center_button.grid(row=1, column=1,  sticky="nsew")

        self.right_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="→", width=20)
        self.right_button.grid(row=1, column=2, sticky="nsew")

        self.down_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="↓", width=20)
        self.down_button.grid(row=2, column=1,  sticky="nsew")
        
       
        #------systems control-------
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, fg_color="white", label_text="System control")
        self.scrollable_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.water_temp = customtkinter.CTkLabel(self.scrollable_frame, text="Water Temp: --°C")
        self.water_temp.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        self.temp_frame = customtkinter.CTkFrame(self.scrollable_frame, fg_color="white")
        self.temp_frame.grid(row=1, column=0,  padx=5, pady=5, sticky="nsew")
        self.temp_frame.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.temp_minus_button = customtkinter.CTkButton(self.temp_frame, text="-", width=30, command=lambda: self.temp_minus())
        self.temp_minus_button.grid(row=0, column=0, sticky="ew")
        
        self.temp_entry = customtkinter.CTkEntry(self.temp_frame, width=70, justify="center")
        self.temp_entry.insert(0, "40")
        self.temp_entry.grid(row=0, column=1, padx=5, sticky="ew")
        
        self.temp_plus_button = customtkinter.CTkButton(self.temp_frame, text="+", width=30, command=lambda: self.temp_plus())
        self.temp_plus_button.grid(row=0, column=2, padx=5, sticky="ew")
        
        
        self.illuminator_label = customtkinter.CTkLabel(self.scrollable_frame, text="Illuminator")
        self.illuminator_label.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        
        self.button_frame = customtkinter.CTkFrame(self.scrollable_frame, fg_color="white")
        self.button_frame.grid(row=3, column=0, padx=5, pady=5,sticky="nsew")
        self.button_frame.grid_columnconfigure((0, 1), weight=1)
        
        
        
        self.on_button = customtkinter.CTkButton(self.button_frame, text="ON", width=30, command=lambda: self.send_command("ILLUMINATOR_ON"))
        self.on_button.grid(row=0, column=0, sticky="ew")
        
        self.off_button = customtkinter.CTkButton(self.button_frame, text="OFF", width=30, command=lambda: self.send_command("ILLUMINATOR_OFF"))
        self.off_button.grid(row=0, column=1, sticky="ew")


        self.button_frame2 = customtkinter.CTkFrame(self.scrollable_frame, fg_color="white")
        self.button_frame2.grid(row=5, column=0, padx=5, pady=5,sticky="nsew")
        self.button_frame2.grid_columnconfigure((0, 1), weight=1)

        self.valve_label = customtkinter.CTkLabel(self.scrollable_frame, text="Circulation Valve")
        self.valve_label.grid(row=4, column=0, padx=5, pady=5, sticky="nsew")

        self.open_button = customtkinter.CTkButton(self.button_frame2, text="OPEN", width=30, command=lambda: self.send_command("VALVE_OPEN"))
        self.open_button.grid(row=0, column=0, sticky="ew")
        
        self.close_button = customtkinter.CTkButton(self.button_frame2, text="CLOSE", width=30, command=lambda: self.send_command("VALVE_CLOSE"))
        self.close_button.grid(row=0, column=1, sticky="ew")
        
        self.pump_frame = customtkinter.CTkFrame(self.scrollable_frame, fg_color="white")
        self.pump_frame.grid(row=6, column=0, padx=5, pady=5,sticky="nsew")
        self.pump_frame.grid_columnconfigure((0, 1), weight=1)
        
        self.pump_A = customtkinter.CTkSwitch(self.pump_frame, text="Pump A", command=lambda: self.toggle_pump_A())
        self.pump_A.grid(row=0, column=0, padx=10, pady=(0, 20), sticky="nsew")
        
        self.pump_B = customtkinter.CTkSwitch(self.pump_frame, text="Pump B", command=lambda: self.toggle_pump_B())
        self.pump_B.grid(row=0, column=1, padx=10, pady=(0, 20), sticky="nsew")
        
        self.textbox.insert("0.0", "Developed By: Nathan Aruna & Arielle Benarroch\n\n" + "Console Log:\n\n")
        threading.Thread(target=self.update_temperature, daemon=True).start()


    #------Config menus-------
    def open_config_menu(self):
        config_window = customtkinter.CTkToplevel(self, cursor="none")

        config_window.title("Configuration Analysis Settings")
        config_window.geometry(f"{config_window.winfo_screenwidth()}x{config_window.winfo_screenheight()}+0+0")

        config_window.attributes("-fullscreen", True)
        config_window.attributes("-topmost", True)
        config_window.overrideredirect(True)

        config_window.grid_rowconfigure(6, weight=6)
        config_window.grid_columnconfigure(5, weight=5)

        label = customtkinter.CTkLabel(config_window, text="Sample Analysis Settings", font=("Arial", 14))
        label.grid(row=0, column=0, padx=20, pady=10)

        if not self.sample_loaded:
            no_sample_label = customtkinter.CTkLabel(config_window, text="Warning: No sample loaded!", font=("Arial", 12), text_color="red")
            no_sample_label.grid(row=1, column=0, padx=20, pady=10)

      

        section_slider = customtkinter.CTkSlider(config_window, from_=1, to=20, width=300, command=lambda value: self.update_section_value(value, section_value_label))
        section_slider.grid(row=0, column=1, padx=20, pady=10)

        section_value_label = customtkinter.CTkLabel(config_window, text="Selected value: 10 section(s)", font=("Arial", 14))
        section_value_label.grid(row=1, column=1, padx=20, pady=10)

        

        micron_slider = customtkinter.CTkSlider(config_window, from_=1, to=100, width=300,command=lambda value: self.update_micron_value(value, micron_value_label))
        micron_slider.grid(row=2, column=1, padx=20, pady=10)

        micron_value_label = customtkinter.CTkLabel(config_window, text="Selected value: 50 micron(s)", font=("Arial", 14))
        micron_value_label.grid(row=3, column=1, padx=20, pady=10)

        num_face_slider = customtkinter.CTkSlider(config_window, from_=1, to=20, width=300,command=lambda value: self.update_face_value(value, num_face_label))
        num_face_slider.grid(row=4, column=1, padx=20, pady=10)

        num_face_label = customtkinter.CTkLabel(config_window, text="Selected value: 10 Faces", font=("Arial", 14))
        num_face_label.grid(row=5, column=1, padx=20, pady=10)

        

        preset_options = ["Tissue Type 1", "Tissue Type 2", "Tissue Type 3", "Tissue Type 4"]
        self.preset_combobox = customtkinter.CTkComboBox(config_window, values=preset_options)
        self.preset_combobox.set("Select a Preset")  
        self.preset_combobox.grid(row=2, column=0, padx=20, pady=10)

        start_button = customtkinter.CTkButton(config_window, text_color="red", text="Start",command=lambda: self.send_command(self.contructed_command))
        start_button.grid(row=3, column=0, padx=20, pady=10)
        
        save_button = customtkinter.CTkButton(config_window,  text="Save Config", command=self.contruct_command)
        save_button.grid(row=4, column=0, padx=20, pady=10)
        
        face_button = customtkinter.CTkButton(config_window,  text="Face Sample", command=lambda: self.send_command("FACE_SAMPLE"))
        face_button.grid(row=5, column=0, padx=20, pady=10)

        close_button = customtkinter.CTkButton(config_window, text="Cancel", command=config_window.destroy)
        close_button.grid(row=6, column=0, padx=20, pady=10)

        def apply_preset():
            selected_preset = self.preset_combobox.get()
            print(f"Selected preset: {selected_preset}")
            if selected_preset == "Tissue Type 1":
                print("Applying settings...")
            elif selected_preset == "Tissue Type 2":
                print("Applying settings...")
            elif selected_preset == "Tissue Type 3":
                print("Applying settings...")
            else:
                print("Applying custom settings...")

        
        label = customtkinter.CTkLabel(config_window, text="Loaded LIS:" + (self.selected_lis_number), font=("Arial", 14))
        label.grid(row=0, column=2, padx=20, pady=10 )

        
    
    def open_loading_menu(self):
        command_thread = threading.Thread(target=lambda: self.send_command("EXTEND_SAMPLE"))
        command_thread.daemon = True
        command_thread.start()

        loading_window = customtkinter.CTkToplevel(self)
        loading_window.title("Sample Loading")
        
        loading_window.geometry(f"{loading_window.winfo_screenwidth()}x{loading_window.winfo_screenheight()}+0+0")
        loading_window.attributes("-fullscreen", True)
        loading_window.attributes("-topmost", True)

        loading_window.overrideredirect(True)

    
        content_frame = customtkinter.CTkFrame(loading_window, fg_color="#ebebeb")
        content_frame.pack(expand=True)  

        label = customtkinter.CTkLabel(content_frame, text="Ensure The Sample Is Properly Secured Before Continuing", font=("Arial", 26))
        label.pack(pady=(20, 10))  

        loader_label = customtkinter.CTkLabel(content_frame, text="Chuck Elevating...", font=("Arial", 20))
        loader_label.pack(pady=(0, 10)) 

        def on_done():
            command_thread = threading.Thread(target=lambda: self.send_command("SYSTEM_CALIBRATION"))
            command_thread.daemon = True
            command_thread.start()
            
            if not self.sample_loaded:
               self.sample_loaded = True
               self.sidebar_button_3.configure(text="Unload Sample")
               self.sidebar_button_3.configure(text_color="red")

            else:
                self.sample_loaded = False
                self.sidebar_button_3.configure(text="Load Sample")
                self.sidebar_button_3.configure(text_color="white")

            loading_window.destroy()

        done_button = customtkinter.CTkButton(content_frame, text="Continue", command=on_done)
        done_button.pack(pady=(10, 20))  
        done_button.pack_forget() 

        def remove_loader_and_show_done():
            time.sleep(5)
            loader_label.pack_forget()  
            done_button.pack(pady=(10, 20))  

        timer_thread = threading.Thread(target=remove_loader_and_show_done)
        timer_thread.daemon = True
        timer_thread.start()

       
        
        
    def open_flush_menu(self):
        command_thread = threading.Thread(target=lambda: self.send_command("SYSTEM_FLUSH"))
        command_thread.daemon = True
        command_thread.start()

        loading_window = customtkinter.CTkToplevel(self)
        loading_window.title("System Flush")
        loading_window.geometry("500x200")
        loading_window.attributes("-topmost", True)
        self.after(100, self.make_fullscreen)


        content_frame = customtkinter.CTkFrame(loading_window, fg_color="#ebebeb")
        content_frame.pack(expand=True)  

       
        loader_label = customtkinter.CTkLabel(content_frame, text="System is Flushing...", font=("Arial", 20))
        loader_label.pack(pady=(20, 10)) 

        def on_done():
            loading_window.destroy()

        done_button = customtkinter.CTkButton(content_frame, text="Done", command=on_done)
        done_button.pack(pady=(10, 20))  
        done_button.pack_forget() 

        def remove_loader_and_show_done():
            time.sleep(20)
            loader_label.pack_forget()  
            done_button.pack(pady=(10, 20))  

        timer_thread = threading.Thread(target=remove_loader_and_show_done)
        timer_thread.daemon = True
        timer_thread.start()


    
    #------Send Data to System-Controller-------
    def send_command(self, command):
      server_ip = '10.190.2.54'
      port = 5000  

      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        try:
            client_socket.connect((server_ip, port))  
            client_socket.sendall(command.encode('utf-8'))  
            print(f"Sent command: {command}")
        except ConnectionRefusedError:
            print("Connection failed. Is the server running?")
        except Exception as e:
            print(f"An error occurred: {e}")




    #------Sample Loading-------
    def handle_sample_loading(self):
        if not self.sample_loaded:
            self.open_loading_menu()
        else:
            self.sidebar_button_3.configure(text="Load Sample")
            self.sample_loaded = False
            print("Sample Unloaded")
            
    def finish_loading_sample(self, loading_window):
        self.send_command("RETRACT_SAMPLE")
        loading_window.destroy()  
        self.sidebar_button_3.configure(text="Unload Sample") 
        self.sample_loaded = True 
        
        
    #------Patient Registration-------
   
    def scan_bardcode(self):
        self.scanning_done = False  
        self.loaded_id.configure(text="Loaded ID: Searching....")
        
        while not self.scanning_done:
            ret, frame = self.cap.read()
            if ret:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                barcodes = decode(gray)

                for barcode in barcodes:
                    barcode_data = barcode.data.decode("utf-8")
                    barcode_type = barcode.type  

                    self.barcode_data = barcode_data  
                    print(f"Barcode Data: {barcode_data}, Type: {barcode_type}")
                    self.loaded_id.configure(text="Loaded ID: " + barcode_data)

                    self.selected_lis_number = barcode_data

                    pts = np.array([barcode.polygon], np.int32)
                    pts = pts.reshape((-1, 1, 2))
                    cv2.polylines(frame, [pts], True, (0, 255, 0), 3)  

                    x, y = pts[0].ravel()
                    cv2.putText(frame, barcode_data, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_image = ImageTk.PhotoImage(Image.fromarray(frame))
                self.video_label.configure(image=frame_image)
                self.video_label.image = frame_image
            else:
                self.cap = cv2.VideoCapture(0)
            time.sleep(0.01)
            
    def start_lis_scan(self):
        print("Please place the patient document under the main display.")
        self.video_label.grid(row=0, column=0)
        self.scanning_done = False  
        threading.Thread(target=self.scan_bardcode, daemon=True).start()


    def finish_lis_scan(self):
        print("Scan completed.")
        self.video_label.grid_forget()
        self.scanning_done = True  
        
        
    
         
    #------Temperature-------   
    def read_ds18b20_temp(self):
        base_dir = '/sys/bus/w1/devices/'
        device_folder = glob.glob(base_dir + '28-*')[0]  
        device_file = device_folder + '/w1_slave'

        with open(device_file, 'r') as f:
            lines = f.readlines()

        if lines[0].strip()[-3:] == 'YES':  
            temp_pos = lines[1].find('t=')
            if temp_pos != -1:
                temp_string = lines[1][temp_pos + 2:]
                temp_c = float(temp_string) / 1000.0
                return temp_c
        return None
    
    def update_temperature(self):
        temp_c = self.read_ds18b20_temp()
        if temp_c is not None:
            self.water_temp.configure(text=f"Water Temp: {temp_c:.2f}°C")
        self.after(1000, self.update_temperature)
        
    def manage_temperature(self):
        while True:
            if self.target_temp > self.actual_temp:
                self.send_commands("HEATER_ON")
            if self.target_temp == self.actual_temp:
                self.send_commands("HEATER_OFF")
            if self.target_temp < self.actual_temp:
                self.send_commands("HEATER_OFF")
            
    def temp_plus(self):
        self.target_temp += 1
        self.temp_entry.delete(0, "end")
        self.temp_entry.insert(0, self.target_temp)
        
    def temp_minus(self):
        self.target_temp -= 1
        self.temp_entry.delete(0, "end")
        self.temp_entry.insert(0, self.target_temp)
        
    
    #------Pump Toggle------- 
    def toggle_pump_A(self):
        if not self.pump_A_state:
            self.send_command("PUMP_A_ON")
            self.pump_A_state = True
            print("Pump A ON")
        else:
            self.send_command("PUMP_A_OFF")
            self.pump_A_state = False 
            print("Pump A OFF")
    
    def toggle_pump_B(self):
        if not self.pump_A_state:
            self.send_command("PUMP_A_ON")
            self.pump_B_state = True
            print("Pump B ON")
        else:
            self.send_command("PUMP_A_OFF")
            self.pump_B_state = False 
            print("Pump B OFF")

        
        
    #------Sample Settings-------  
    def update_micron_value(self, value, label):
        self.selected_micron_value = int(value)  
        label.configure(text=f"Selected value: {self.selected_micron_value} micron(s)")

    def update_section_value(self, value, label):
        self.selected_section_value = int(value)  
        label.configure(text=f"Selected value: {self.selected_section_value} section(s)")

    def update_face_value(self, value, label):
        self.selected_face_value = int(value)  
        label.configure(text=f"Selected value: {self.selected_face_value} face(s)")
      
      
    def contruct_command(self):
        self.contructed_command = f"{self.selected_section_value}|{self.selected_micron_value}|{self.selected_face_value}|{self.selected_lis_number}"
        # self.send_command(self.contructed_command)
        print(self.contructed_command)
          
          
    #------System shutdown/restart-------   
    def show_confirmation_dialog(self, action):
        response = messagebox.askyesno("Confirm Action", f"Are you sure you want to {action}?")
        return response  


    def sys_shutdown(self):

        if self.show_confirmation_dialog("Shut Down"):
           self.send_command("SYS_SHUTDOWN")
           sys_shutdown()
     
           
    def sys_restart(self):
        if self.show_confirmation_dialog("Restart"):
           sys_restart()

    def on_closing(self, event=0):
        self.cap.release()  
        self.destroy()
        
    #------Window Formatting -------   
    def make_fullscreen(self):
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        self.attributes("-fullscreen", True)  
        self.resizable(False, False)
    

    def change_scaling_event(self, new_scaling: str):
        change_scaling_event(new_scaling)

if __name__ == "__main__":
    print(os.getcwd())
    app = App()
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()
    app.mainloop()
