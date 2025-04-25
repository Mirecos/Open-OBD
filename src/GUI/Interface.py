import obd
import tkinter as tk
from tkinter import StringVar

from API.Interactions import query_command

class OpenOBD_Interface:
    
    def __init__(self, connection: obd.OBD):
        self.root = tk.Tk()
        self.root.title("Vehicle Dashboard")
        self.root.geometry("400x200")
        self.connection = connection

        # Create variables to hold values
        self.speed_var = StringVar()
        self.speed_var.set("Loading...")
        self.rpm_var = StringVar()
        self.rpm_var.set("Loading...")

        # Creating the GUI elements
        self.speed_label = tk.Label(self.root, textvariable=self.speed_var, font=("Helvetica", 16))
        self.speed_label.pack(pady=20)
        
        self.rpm_label = tk.Label(self.root, textvariable=self.rpm_var, font=("Helvetica", 16))
        self.rpm_label.pack(pady=20)

        # Start updating functions
        self.update_simple_data()

        self.root.mainloop()

    def update_simple_data(self):
        speed = query_command(self.connection, obd.commands.SPEED)
        if speed.value is not None:
            self.speed_var.set(f"Speed: {speed.value.to('kph')}")
        else:
            self.speed_var.set("Speed: N/A")

        rpm = query_command(self.connection,obd.commands.RPM)
        if rpm.value is not None:
            self.rpm_var.set(f"RPM: {rpm.value}")
        else:
            self.rpm_var.set("RPM: N/A")

        self.root.after(1000, self.update_simple_data)
