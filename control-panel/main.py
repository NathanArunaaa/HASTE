
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


from web_interface.app import start_flask
from functions import (
    change_scaling_event, 
    sys_shutdown, 
    sys_restart, 
    get_local_ip,
)

customtkinter.set_appearance_mode("light")  
customtkinter.set_default_color_theme("blue") 

CONTROL_PANEL_IP = '192.168.2.126'
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
        self.running = True

        self.after(100, self.make_fullscreen)

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
        self.video_feeds_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.video_feeds_frame.grid_columnconfigure(0, weight=1)
        self.video_feeds_frame.grid_rowconfigure(4, weight=1)
        self.textbox = customtkinter.CTkTextbox(self, width=2530)

       
        
        self.video_frame = customtkinter.CTkFrame(self.video_feeds_frame, fg_color="white")
        self.video_frame.grid(row=1, column=0, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.video_label = customtkinter.CTkLabel(self.video_frame, text="", anchor="center")
        self.video_label.grid(row=0, column=0, padx=20, pady=20)
        
   

        #------Console log-------
        self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.textbox.configure(cursor="none") 

        sys.stdout = TextWidgetStream(self.textbox)
        sys.stderr = TextWidgetStream(self.textbox)
        
        #------Tabs-------
        self.tabview = customtkinter.CTkTabview(self, fg_color="white", width=250)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(0, 0), sticky="nsew")
        self.tabview.add("Blade")
        self.tabview.add("Debug")
        self.tabview.add("Steppers")

        #------Blades-------
        self.tabview.tab("Blade").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Blade").grid_columnconfigure(0, weight=1)

        self.blade_cylce = customtkinter.CTkLabel(self.tabview.tab("Blade"), text="Blade Cycles: 182")
        self.blade_cylce.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        #------Debug-------
        self.tabview.tab("Debug").grid_rowconfigure(0, weight=1)
        self.tabview.tab("Debug").grid_columnconfigure(0, weight=1)
        
        self.spacer = customtkinter.CTkLabel(self.tabview.tab("Debug"), text="", width=20, )
        self.spacer.grid(row=0, column=0, padx=40, pady=2, sticky="nsew") 

        self.debug_button1 = customtkinter.CTkButton(self.tabview.tab("Debug"), text="Pump A", width=20, command=lambda: self.send_command("DEBUG_PUMP_A"))
        self.debug_button1.grid(row=1, column=0, padx=40, pady=2, sticky="nsew")  
         
        self.debug_button2 = customtkinter.CTkButton(self.tabview.tab("Debug"), text="Pump B", width=20,command=lambda: self.send_command("DEBUG_PUMP_B"))
        self.debug_button2.grid(row=2, column=0, padx=40, pady=2, sticky="nsew")   
        
        self.debug_button3 = customtkinter.CTkButton(self.tabview.tab("Debug"), text="Illuminator", width=20)
        self.debug_button3.grid(row=3, column=0, padx=40, pady=2, sticky="nsew")   
        #------Steppers-------
        self.tabview.tab("Steppers").grid_rowconfigure((0, 1, 2), weight=1)
        self.tabview.tab("Steppers").grid_columnconfigure((0, 1, 2), weight=1)

        self.up_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="↑", width=20)
        self.up_button.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.left_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="←", width=20)
        self.left_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.center_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="O", width=20)
        self.center_button.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        self.right_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="→", width=20)
        self.right_button.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")

        self.down_button = customtkinter.CTkButton(self.tabview.tab("Steppers"), text="↓", width=20)
        self.down_button.grid(row=2, column=1, padx=10, pady=10, sticky="nsew")
        
       
        #------Temp Monitoring-------
        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, fg_color="white", label_text="Temperatures")
        self.scrollable_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        
        self.water_temp = customtkinter.CTkLabel(self.scrollable_frame, text="Water Temp: --°C")
        self.water_temp.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")   
        

        #------Default values-------
        self.textbox.insert("0.0", "Developed By: Nathan Aruna & Arielle Benarroch\n\n" + "Console Log:\n\n" )
        threading.Thread(target=self.update_temperature, daemon=True).start()
        threading.Thread(target=self.update_video_feed, daemon=True).start() 

    #------Config menus-------
    def open_config_menu(self):
        config_window = customtkinter.CTkToplevel(self, cursor="none")

        config_window.title("Configuration Analysis Settings")
        config_window.geometry(f"{config_window.winfo_screenwidth()}x{config_window.winfo_screenheight()}+0+0")

        config_window.attributes("-fullscreen", True)
        config_window.attributes("-topmost", True)
        config_window.overrideredirect(True)

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
        
        face_button = customtkinter.CTkButton(config_window,  text="Face Sample", command=lambda: self.send_command("FACE_SAMPLE"))
        face_button.grid(row=4, column=0, padx=20, pady=10)

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

        input_value = customtkinter.StringVar()  

        input_entry = customtkinter.CTkEntry(config_window, textvariable=input_value, justify="right", width=100, font=("Arial", 18))
        input_entry.grid(row=0, column=2, padx=20, pady=10, sticky="e")

        def on_number_click(num):
            current = input_value.get()
            input_value.set(current + str(num))

        def clear_input():
            input_value.set("")

        number_pad = customtkinter.CTkFrame(config_window, fg_color="white")
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
        command_thread = threading.Thread(target=lambda: self.send_command(""))
        command_thread.daemon = True
        command_thread.start()

        loading_window = customtkinter.CTkToplevel(self)
        loading_window.title("Load Sample")
        loading_window.geometry("500x200")
        loading_window.attributes("-topmost", True)
        self.after(100, self.make_fullscreen)


    
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


    
    #------Functions-------
    
    def make_fullscreen(self):
        self.geometry(f"{self.winfo_screenwidth()}x{self.winfo_screenheight()}+0+0")
        self.attributes("-fullscreen", True)  
        self.resizable(False, False)

    def send_command(self, command):
      server_ip = '192.168.2.126'
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
   
    def update_video_feed(self):
        while self.running:
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                frame_image = ImageTk.PhotoImage(Image.fromarray(frame))
                self.video_label.configure(image=frame_image)
                self.video_label.image = frame_image
            else:
                self.cap = cv2.VideoCapture(0) 
            time.sleep(0.01)

        
    
         
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
        
          
    def update_micron_value(self, value, label):
        label.configure(text=f"Selected value: {int(value)} micron(s)")
        
    def update_section_value(self, value, label):
        label.configure(text=f"Selected value: {int(value)} section(s)")
        
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
