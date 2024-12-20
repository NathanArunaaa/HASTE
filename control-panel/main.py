
import customtkinter
import threading
import sys
import cv2
import socket 
from PIL import Image, ImageTk
from tkinter import messagebox
import os
import time
import json

from web_interface.app import start_flask
from functions import (
    change_scaling_event, 
    sys_shutdown, 
    sys_restart, 
    get_local_ip,
    play_buzzer
)

customtkinter.set_appearance_mode("light")  
customtkinter.set_default_color_theme("blue") 

CONTROL_PANEL_IP = '192.168.1.10'
CONTROL_PANEL_PORT = 5000



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
        
        self.sample_loaded = False

        #------inits-------     
        self.title("HASTE CONTROL PANEL")
        self.config(cursor="none")
        self.cap = cv2.VideoCapture(0) 

        self.section_value = 10  # Default section value
        self.micron_value = 50  # Default micron value
        self.selected_preset = None  # Default preset selection

        self.attributes("-fullscreen", True)
        #self.config(cursor="none")
        self.change_scaling_event("130%")

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        #------Sidebar------- 
        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0, fg_color="white")
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="H . A . S . T . E", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Start", hover_color="#3b8ed0", command=self.open_config_menu)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        #self.sidebar_button_1.configure(cursor="none")

        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="System Calibration", hover_color="#3b8ed0", command=lambda: self.send_command("SYSTEM_CALIBRATION"))
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        #self.sidebar_button_2.configure(cursor="none")

        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Load Sample", hover_color="#3b8ed0", command=self.open_loading_menu)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        #self.sidebar_button_3.configure(cursor="none")
        
        self.sidebar_button_6 = customtkinter.CTkButton(self.sidebar_frame, text="Flush System", hover_color="#3b8ed0", command=self.open_flush_menu)
        self.sidebar_button_6.grid(row=4, column=0, padx=20, pady=10)
        #self.sidebar_button_6.configure(cursor="none")

        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, text="System Restart", hover_color="#3b8ed0", command=self.sys_restart)
        self.sidebar_button_4.grid(row=6, column=0, padx=20, pady=(10, 10))
        #self.sidebar_button_4.configure(cursor="none")

        self.sidebar_button_5 = customtkinter.CTkButton(self.sidebar_frame, text="Shut Down", hover_color="#3b8ed0", command=self.sys_shutdown)
        self.sidebar_button_5.grid(row=7 , column=0, padx=20, pady=(10, 10))
        #self.sidebar_button_5.configure(cursor="none")
        

        local_ip = get_local_ip() 
        self.local_ip_label = customtkinter.CTkLabel(self.sidebar_frame, text=f"{local_ip}:5000", anchor="w")
        self.local_ip_label.grid(row=8, column=0, padx=20, pady=(10, 20))



        #------Video Feeds-------
        self.video_feeds_frame = customtkinter.CTkFrame(self, fg_color="white")
        self.video_feeds_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.video_feeds_frame.grid_columnconfigure(0, weight=1)
        self.video_feeds_frame.grid_rowconfigure(4, weight=1)
        self.textbox = customtkinter.CTkTextbox(self, width=250)

        self.cam_buttons = customtkinter.CTkSegmentedButton(
            self.video_feeds_frame, 
            values=["Microscope", "CAM-1", "CAM-2"],
            command=self.on_camera_change 
        )
        self.cam_buttons.grid(row=0, column=0, padx=20, pady=10)
        
        self.video_frame = customtkinter.CTkFrame(self.video_feeds_frame, fg_color="white")
        self.video_frame.grid(row=1, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.video_label = customtkinter.CTkLabel(self.video_frame, text="")
        self.video_label.grid(row=0, column=0, padx=20, pady=20) 
        
    
        #self.update_video_feed()


        #------Console log-------
        self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.textbox.configure(cursor="none") 

        sys.stdout = TextWidgetStream(self.textbox)
        sys.stderr = TextWidgetStream(self.textbox)
        
        #------Tabs-------
        self.tabview = customtkinter.CTkTabview(self, fg_color="white", width=250)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(0, 0), sticky="nsew")
        self.tabview.add("Blade")
        self.tabview.add("Sensors")
        self.tabview.add("Steppers")

        #------Blades-------
        self.blade_health = customtkinter.CTkLabel(self.tabview.tab("Blade"), text="Blade Health:")
        self.blade_health.grid(row=0, column=0, padx=20, pady=20)
        self.blade_cylce = customtkinter.CTkLabel(self.tabview.tab("Blade"), text="Blade Cylces: 182")
        self.blade_cylce.grid(row=1, column=0, padx=20, pady=20)
        self.blade_progressbar_1 = customtkinter.CTkProgressBar(self.tabview.tab("Blade"))
        self.blade_progressbar_1.grid(row=2, column=0, padx=20, pady=20)

        #------Sensors-------
        self.label_tab_2 = customtkinter.CTkLabel(self.tabview.tab("Sensors"), text="Sensor info here")
        self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)
        
        #------Steppers-------
        self.up_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="↑", width=20)
        self.up_button.grid(row=0, column=1, padx=10, pady=10)

        self.left_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="←", width=20)
        self.left_button.grid(row=1, column=0, padx=10, pady=10)
        
        self.left_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="O", width=20)
        self.left_button.grid(row=1, column=1, padx=10, pady=10)

        self.right_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="→", width=20)
        self.right_button.grid(row=1, column=2, padx=10, pady=10)

        self.down_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="↓", width=20)
        self.down_button.grid(row=2, column=1, padx=10, pady=10)
        
        
        #------Switch buttons-------
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, fg_color="white", label_text="Active Indicators")
        self.scrollable_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_switches = []
        for i in range(4):
            switch = customtkinter.CTkSwitch(master=self.scrollable_frame, text=f"Indicator {i}")
            switch.grid(row=i, column=0, padx=10, pady=(0, 20))
            self.scrollable_frame_switches.append(switch)
            
            
        #------Default values-------
        self.textbox.insert("0.0", "Developed By: Nathan Aruna & Arielle Benarroch\n\n" + "Console Log:\n\n" )
        self.cam_buttons.set("Microscope")
 
    #------Config menus-------
    def open_config_menu(self):
        config_window = customtkinter.CTkToplevel(self)

        config_window.title("Configuration Analysis Settings")
        config_window.geometry("700x400")
        config_window.attributes("-fullscreen", True)
        config_window.attributes("-topmost", True)

        config_window.grid_rowconfigure(5, weight=5)
        config_window.grid_columnconfigure(5, weight=5)

        label = customtkinter.CTkLabel(config_window, text="Sample Analysis Settings", font=("Arial", 14))
        label.grid(row=0, column=0, padx=20, pady=10)

        if not self.sample_loaded:
            no_sample_label = customtkinter.CTkLabel(config_window, text="Warning: No sample loaded!", font=("Arial", 12), text_color="red")
            no_sample_label.grid(row=1, column=0, padx=20, pady=10)

        section_value_label = customtkinter.CTkLabel(config_window, text="Selected value: 10 section(s)", font=("Arial", 14))
        section_value_label.grid(row=1, column=1, padx=20, pady=10)

        section_slider = customtkinter.CTkSlider(
            config_window, from_=1, to=20, width=300,
            command=lambda value: self.update_section_value(value, section_value_label))
        section_slider.grid(row=0, column=1, padx=20, pady=10)

        micron_value_label = customtkinter.CTkLabel(config_window, text="Selected value: 50 micron(s)", font=("Arial", 14))
        micron_value_label.grid(row=3, column=1, padx=20, pady=10)

        scale = customtkinter.CTkSlider(config_window, from_=1, to=100, width=300,command=lambda value: self.update_micron_value(value, micron_value_label))
        scale.grid(row=2, column=1, padx=20, pady=10)

        preset_options = ["Tissue Type 1", "Tissue Type 2", "Tissue Type 3", "Tissue Type 4"]
        self.preset_combobox = customtkinter.CTkComboBox(config_window, values=preset_options)
        self.preset_combobox.set("Select a Preset")  
        self.preset_combobox.grid(row=2, column=0, padx=20, pady=10)

        start_button = customtkinter.CTkButton(config_window, text_color="red", text="Start",command=lambda: self.send_command("SECTION_SAMPLE"))
        start_button.grid(row=3, column=0, padx=20, pady=10)
        
        start_button = customtkinter.CTkButton(config_window,  text="Face Sample", command=lambda: self.send_command(""))
        start_button.grid(row=4, column=0, padx=20, pady=10)

        close_button = customtkinter.CTkButton(config_window, text="Cancel", command=config_window.destroy)
        close_button.grid(row=5, column=0, padx=20, pady=10)

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

        buzzer_thread = threading.Thread(target=play_buzzer)
        buzzer_thread.daemon = True
        buzzer_thread.start()

        input_value = customtkinter.StringVar()  

        input_entry = customtkinter.CTkEntry(config_window, textvariable=input_value, justify="right", width=100, font=("Arial", 18))
        input_entry.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        def on_number_click(num):
            current = input_value.get()
            input_value.set(current + str(num))

        def clear_input():
            input_value.set("")

        number_pad = customtkinter.CTkFrame(config_window)
        number_pad.grid(row=1, column=2, rowspan=5, padx=20, pady=10, sticky="nsew")

        buttons = [
            ('1', 0, 0), ('2', 0, 1), ('3', 0, 2),
            ('4', 1, 0), ('5', 1, 1), ('6', 1, 2),
            ('7', 2, 0), ('8', 2, 1), ('9', 2, 2),
            ('0', 3, 1), ('C', 3, 0), ('-', 3, 2)
        ]

        for (text, row, col) in buttons:
            if text == 'C':
                btn = customtkinter.CTkButton(number_pad, text=text, command=clear_input, width=50)
            else:
                btn = customtkinter.CTkButton(number_pad, text=text, command=lambda t=text: on_number_click(t), width=50)
            btn.grid(row=row, column=col, padx=5, pady=5)

   

        
    
    def open_loading_menu(self):
        command_thread = threading.Thread(target=lambda: self.send_command("EXTEND_SAMPLE"))
        command_thread.daemon = True
        command_thread.start()

        loading_window = customtkinter.CTkToplevel(self)
        loading_window.title("Flush System")
        loading_window.geometry("500x200")
        loading_window.attributes("-topmost", True)
        loading_window.attributes("-fullscreen", True)

    
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

        buzzer_thread = threading.Thread(target=play_buzzer)
        buzzer_thread.daemon = True
        buzzer_thread.start()
        
        
        
    def open_flush_menu(self):
        command_thread = threading.Thread(target=lambda: self.send_command(""))
        command_thread.daemon = True
        command_thread.start()

        loading_window = customtkinter.CTkToplevel(self)
        loading_window.title("Load Sample")
        loading_window.geometry("500x200")
        loading_window.attributes("-topmost", True)
        loading_window.attributes("-fullscreen", True)

    
        content_frame = customtkinter.CTkFrame(loading_window, fg_color="#ebebeb")
        content_frame.pack(expand=True)  

       
        loader_label = customtkinter.CTkLabel(content_frame, text="System is Flushing...", font=("Arial", 20))
        loader_label.pack(pady=(20, 10)) 

        def on_done():
            command_thread = threading.Thread(target=lambda: self.send_command(""))
            command_thread.daemon = True
            command_thread.start()
            self.sample_loaded = True
            loading_window.destroy()

        done_button = customtkinter.CTkButton(content_frame, text="Done", command=on_done)
        done_button.pack(pady=(10, 20))  
        done_button.pack_forget() 

        def remove_loader_and_show_done():
            time.sleep(4)
            loader_label.pack_forget()  
            done_button.pack(pady=(10, 20))  

        timer_thread = threading.Thread(target=remove_loader_and_show_done)
        timer_thread.daemon = True
        timer_thread.start()

        buzzer_thread = threading.Thread(target=play_buzzer)
        buzzer_thread.daemon = True
        buzzer_thread.start()



       

    
    #------Functions-------

    def send_command(self, command):
      server_ip = '192.168.1.20'
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
        
        
    #------Video-------
    def on_camera_change(self, event):
        selected_camera = self.cam_buttons.get()
        print(f"Selected camera: {selected_camera}")  
        camera_index = 0  

        if selected_camera == "Microscope":
            camera_index = 0  
        elif selected_camera == "CAM-1":
            camera_index = 1
        elif selected_camera == "CAM-2":
            camera_index = 2 
        
        self.cap.release() 
        self.cap = cv2.VideoCapture(camera_index)  
        if not self.cap.isOpened():
            messagebox.showerror("Error", f"Unable to access camera: {camera_index}")
   
    def update_video_feed(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)  
            img = Image.fromarray(frame)  
            imgtk = ImageTk.PhotoImage(image=img) 
            self.video_label.configure(image=imgtk)
            self.video_label.imgtk = imgtk  

        self.after(10, self.update_video_feed)
                 
    def buzzer_thread(self):
        buzzer_thread = threading.Thread(target=play_buzzer)
        buzzer_thread.daemon = True
        buzzer_thread.start()  
        
    def update_section_value(self, value, label):
        self.section_value = int(value)
        label.config(text=f"Selected value: {self.section_value} section(s)")
        print(f"Section value updated to: {self.section_value}")

    def update_micron_value(self, value, label):
        self.micron_value = int(value)
        label.config(text=f"Selected value: {self.micron_value} micron(s)")
        print(f"Micron value updated to: {self.micron_value}")

    def apply_preset(self):
        self.selected_preset = self.preset_combobox.get()
        print(f"Selected preset: {self.selected_preset}")

    def send_config_data(self):
        data = {
            "section_value": self.section_value,
            "micron_value": self.micron_value,
            "selected_preset": self.selected_preset,
        }
        print(f"Sending data: {data}")

        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((CONTROL_PANEL_IP, CONTROL_PANEL_PORT))
                s.sendall(json.dumps(data).encode('utf-8'))
            print("Data sent successfully!")
        except Exception as e:
            print(f"Error sending data: {e}")
            
    def show_confirmation_dialog(self, action):
        response = messagebox.askyesno("Confirm Action", f"Are you sure you want to {action}?")
        return response
    
    
    def apply_settings(self, speed, max_value):
        print(f"Speed set to: {speed}")
        print(f"Max Value set to: {max_value}")


    def change_scaling_event(self, new_scaling: str):
        change_scaling_event(new_scaling)


    def sys_shutdown(self):
        if self.show_confirmation_dialog("Shut Down"):
           sys_shutdown()
     
           
    def sys_restart(self):
        if self.show_confirmation_dialog("Restart"):
           sys_restart()


    def on_closing(self, event=0):
        self.cap.release()  
        self.destroy()
    
 

if __name__ == "__main__":
    print(os.getcwd())
    app = App()
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()
    app.mainloop()
