
import customtkinter
import threading
import sys
import cv2
import socket 
from PIL import Image, ImageTk
from tkinter import messagebox
import os



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

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('192.168.x.x', 5000)) 

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

        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="HASTE", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Start", hover_color="#3b8ed0", command=self.open_config_menu)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        #self.sidebar_button_1.configure(cursor="none")

        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="System Calibration", hover_color="#3b8ed0")
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        #self.sidebar_button_2.configure(cursor="none")

        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Load Sample", hover_color="#3b8ed0", command=lambda: self.send_command("EXTEND_SAMPLE") )
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        #self.sidebar_button_3.configure(cursor="none")
        
        self.sidebar_button_6 = customtkinter.CTkButton(self.sidebar_frame, text="Flush System", hover_color="#3b8ed0", command=lambda: self.send_command("start_sensors"))
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
        
    

        self.update_video_feed()


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
        config_window.grid_rowconfigure(1, weight=1)
        config_window.grid_columnconfigure(1, weight=1)

        label = customtkinter.CTkLabel(config_window, text="Sample Analysis Settings", font=("Arial", 14))
        label.grid(row=0, column=0, padx=20, pady=10)

        if not self.sample_loaded:
            no_sample_label = customtkinter.CTkLabel(config_window, text="Warning: No sample loaded!", font=("Arial", 12), text_color="red")
            no_sample_label.grid(row=1, column=0, padx=20, pady=10)

        micron_value_label = customtkinter.CTkLabel(config_window, text="Selected value: 50 microns", font=("Arial", 14))
        micron_value_label.grid(row=3, column=1, padx=20, pady=10)

        scale = customtkinter.CTkSlider(config_window, from_=1, to=100, width=300, command=lambda value: self.update_micron_value(value, micron_value_label))
        scale.grid(row=2, column=1, padx=20, pady=10)

        preset_options = ["Tissue Type 1", "Tissue Type 2", "Tissue Type 3", "Tissue Type 4"]
        self.preset_combobox = customtkinter.CTkComboBox(config_window, values=preset_options)
        self.preset_combobox.set("Select a Preset")  
        self.preset_combobox.grid(row=2, column=0, padx=20, pady=10)

      
        start_button = customtkinter.CTkButton(config_window, text="Start", command=lambda: print(f"Starting analysis with {int(scale.get())} microns"))
        start_button.grid(row=3, column=0, padx=20, pady=10)
        
        close_button = customtkinter.CTkButton(config_window, text="Cancel", command=config_window.destroy)
        close_button.grid(row=4, column=0, padx=20, pady=10)

        def apply_preset():
            selected_preset = self.preset_combobox.get()
            print(f"Selected preset: {selected_preset}")
            if selected_preset == "Low Resolution":
                print("Applying low resolution settings...")
            elif selected_preset == "Medium Resolution":
                print("Applying medium resolution settings...")
            elif selected_preset == "High Resolution":
                print("Applying high resolution settings...")
            else:
                print("Applying custom settings...")
        buzzer_thread = threading.Thread(target=play_buzzer)
        buzzer_thread.daemon = True
        buzzer_thread.start()

   

        
    
    def open_loading_menu(self):
        self.send_command("EXTEND_SAMPLE")
        loading_window = customtkinter.CTkToplevel(self)
        loading_window.title("Load Sample")
        loading_window.geometry("500x200")
        loading_window.attributes("-topmost", True)

        label = customtkinter.CTkLabel(loading_window, text="Ensure The Sample Is Properly Secured Before Continuing", font=("Arial", 14))
        label.pack(pady=20)

        done_button = customtkinter.CTkButton(loading_window, text="Done", command=lambda: self.finish_loading_sample(loading_window))
        done_button.pack(pady=20)

        buzzer_thread = threading.Thread(target=play_buzzer)
        buzzer_thread.daemon = True
        buzzer_thread.start()

    
    #------Functions-------

    def send_command(self, command):
       client_socket.send(command.encode('utf-8'))

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
        
    def update_micron_value(self, value, label):
        label.configure(text=f"Selected value: {int(value)} microns")
        
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
