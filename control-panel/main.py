import tkinter
import tkinter.messagebox
import customtkinter

import threading
import sys
import traceback

from web_interface.app import start_flask
from functions import (
    open_input_dialog_event, 
    change_appearance_mode_event, 
    change_scaling_event, 
    sidebar_button_event, 
    sys_shutdown, 
    sys_restart, 
    get_local_ip,
    play_buzzer_sound,
    
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

        self.title("")
        self.config(cursor="none")

        self.attributes("-fullscreen", True)
        self.config(cursor="none")
        self.change_scaling_event("130%")

        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2), weight=1)

        self.sidebar_frame = customtkinter.CTkFrame(self, width=140, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, rowspan=4, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.logo_label = customtkinter.CTkLabel(self.sidebar_frame, text="AMSS ", font=customtkinter.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Start", hover_color="#3b8ed0", command=play_buzzer_sound)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_1.configure(cursor="none")  

        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="System Calibration",hover_color="#3b8ed0", command=play_buzzer_sound)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_2.configure(cursor="none") 
        
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Load Sample", hover_color="#3b8ed0", command=play_buzzer_sound)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_3.configure(cursor="none") 
        
        self.sidebar_button_4 = customtkinter.CTkButton(self.sidebar_frame, text="System Restart", hover_color="#3b8ed0", command=self.sys_restart)
        self.sidebar_button_4.grid(row=5, column=0, padx=20, pady=(10, 10))
        self.sidebar_button_4.configure(cursor="none") 
        
        self.sidebar_button_5 = customtkinter.CTkButton(self.sidebar_frame, text="Shut Down", hover_color="#3b8ed0", command=self.sys_shutdown)
        self.sidebar_button_5.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.sidebar_button_5.configure(cursor="none") 
        
        local_ip = get_local_ip() 
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text=f"{local_ip}:5000", anchor="w")
        self.appearance_mode_label.grid(row=7, column=0, padx=20, pady=(10, 20))
       
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=0, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.textbox.configure(cursor="none") 

        sys.stdout = TextWidgetStream(self.textbox)
        sys.stderr = TextWidgetStream(self.textbox)

        
        self.tabview = customtkinter.CTkTabview(self, width=250)
        self.tabview.grid(row=0, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.tabview.add("CTkTabview")
        self.tabview.add("Tab 2")
        self.tabview.add("Tab 3")
        self.tabview.tab("CTkTabview").grid_columnconfigure(0, weight=1) 
        self.tabview.tab("Tab 2").grid_columnconfigure(0, weight=1)
        self.tabview.configure(cursor="none") 
        
        self.optionmenu_1 = customtkinter.CTkOptionMenu(self.tabview.tab("CTkTabview"), dynamic_resizing=False,
                                                        values=["Value 1", "Value 2", "Value Long Long Long"])
        self.optionmenu_1.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.combobox_1 = customtkinter.CTkComboBox(self.tabview.tab("CTkTabview"),
                                                    values=["Value 1", "Value 2", "Value Long....."])
        self.combobox_1.grid(row=1, column=0, padx=20, pady=(10, 10))
        self.string_input_button = customtkinter.CTkButton(self.tabview.tab("CTkTabview"), text="Open CTkInputDialog",
                                                           command=self.open_input_dialog_event)
        self.string_input_button.grid(row=2, column=0, padx=20, pady=(10, 10))
        self.label_tab_2 = customtkinter.CTkLabel(self.tabview.tab("Tab 2"), text="CTkLabel on Tab 2")
        self.label_tab_2.grid(row=0, column=0, padx=20, pady=20)

      

        self.slider_progressbar_frame = customtkinter.CTkFrame(self, fg_color="transparent")
        self.slider_progressbar_frame.grid(row=1, column=1, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.slider_progressbar_frame.grid_columnconfigure(0, weight=1)
        self.slider_progressbar_frame.grid_rowconfigure(4, weight=1)
        self.seg_button_1 = customtkinter.CTkSegmentedButton(self.slider_progressbar_frame)
        self.seg_button_1.grid(row=0, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_1 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_1.grid(row=1, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.progressbar_2 = customtkinter.CTkProgressBar(self.slider_progressbar_frame)
        self.progressbar_2.grid(row=2, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.slider_1 = customtkinter.CTkSlider(self.slider_progressbar_frame, from_=0, to=1, number_of_steps=4)
        self.slider_1.grid(row=3, column=0, padx=(20, 10), pady=(10, 10), sticky="ew")
        self.slider_2 = customtkinter.CTkSlider(self.slider_progressbar_frame, orientation="vertical")
        self.slider_2.grid(row=0, column=1, rowspan=5, padx=(10, 10), pady=(10, 10), sticky="ns")
        self.progressbar_3 = customtkinter.CTkProgressBar(self.slider_progressbar_frame, orientation="vertical")
        self.progressbar_3.grid(row=0, column=2, rowspan=5, padx=(10, 20), pady=(10, 10), sticky="ns")

        self.scrollable_frame = customtkinter.CTkScrollableFrame(self, label_text="CTkScrollableFrame")
        self.scrollable_frame.grid(row=1, column=2, padx=(20, 0), pady=(20, 0), sticky="nsew")
        self.scrollable_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_frame_switches = []
        for i in range(100):
            switch = customtkinter.CTkSwitch(master=self.scrollable_frame, text=f"CTkSwitch {i}")
            switch.grid(row=i, column=0, padx=10, pady=(0, 20))
            self.scrollable_frame_switches.append(switch)

        
      
        self.optionmenu_1.set("CTkOptionmenu")
        self.combobox_1.set("CTkComboBox")
        self.slider_1.configure(command=self.progressbar_2.set)
        self.slider_2.configure(command=self.progressbar_3.set)
        self.progressbar_1.configure(mode="indeterminnate")
        self.progressbar_1.start()
        self.textbox.insert("0.0", "Developed By: Nathan Aruna & Arielle Benarroch\n\n" + "Console Log:\n\n" +  "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed diam nonumy eirmod tempor invidunt ut labore et dolore magna aliquyam erat, sed diam voluptua.\n\n" * 20)
        self.seg_button_1.configure(values=["CTkSegmentedButton", "Value 2", "Value 3"])
        self.seg_button_1.set("Value 2")
        
        

    def open_input_dialog_event(self):
        open_input_dialog_event()

    def change_appearance_mode_event(self, new_appearance_mode: str):
        change_appearance_mode_event(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        change_scaling_event(new_scaling)

    def sidebar_button_event(self):
        sidebar_button_event()

    def sys_shutdown(self):
        play_buzzer_sound()
        if tkinter.messagebox.askyesno("Shutdown Confirmation", "Are you sure you want to shut down the system?"):
            sys_shutdown()

    def sys_restart(self):

        play_buzzer_sound()
        if tkinter.messagebox.askyesno("Restart Confirmation", "Are you sure you want to restart the system?"):
            sys_restart()
        
    def handle_exception(self, exc_type, exc_value, exc_traceback):
        formatted_exception = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        sys.stderr.write(formatted_exception)
        self.textbox.insert("end", formatted_exception)
        self.textbox.yview("end")  
        



if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.daemon = True
    flask_thread.start()
    app = App()
    app.mainloop()

