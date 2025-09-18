import obd
import tkinter as tk
from tkinter import StringVar

from ..API.OBDInteractions import query_command


class OpenOBD_Interface:
    
    def __init__(self, connection: obd.OBD):
        self.root = tk.Tk()
        self.root.title("Vehicle Dashboard")
        self.root.geometry("500x300")
        self.root.configure(bg="#2c3e50")  # Set background color
        self.connection = connection

        # Create variables to hold values
        self.speed_var = StringVar(value="Loading...")
        self.rpm_var = StringVar(value="Loading...")
        self.fuel_var = StringVar(value="Loading...")
        self.temp_var = StringVar(value="Loading...")
        self.DTC_codes = StringVar(value="Loading...")


        # Creating the GUI elements
        self.create_label("Speed:", self.speed_var, 0)
        self.create_label("RPM:", self.rpm_var, 1)
        self.create_label("Fuel Level:", self.fuel_var, 2)
        self.create_label("Engine Temp:", self.temp_var, 3)
        self.create_label("DTC Codes:", self.DTC_codes, 4)

        # Start updating functions
        self.update_simple_data()

        self.root.mainloop()

    def create_label(self, text, variable, row):
        """Helper function to create styled labels."""
        label = tk.Label(self.root, text=text, font=("Helvetica", 14), bg="#2c3e50", fg="#ecf0f1")
        label.grid(row=row, column=0, padx=10, pady=10, sticky="w")
        value_label = tk.Label(self.root, textvariable=variable, font=("Helvetica", 14), bg="#2c3e50", fg="#1abc9c")
        value_label.grid(row=row, column=1, padx=10, pady=10, sticky="w")

    def update_simple_data(self):
        # Update speed
        speed = query_command(self.connection, obd.commands.SPEED)
        if speed.value is not None:
            self.speed_var.set(f"{speed.value.to('kph')}")
        else:
            self.speed_var.set("N/A")

        # Update RPM
        rpm = query_command(self.connection, obd.commands.RPM)
        if rpm.value is not None:
            self.rpm_var.set(f"{rpm.value}")
        else:
            self.rpm_var.set("N/A")

        # Update fuel level
        fuel = query_command(self.connection, obd.commands.FUEL_STATUS)
        if fuel.value is not None:
            self.fuel_var.set(f"{fuel.value}%")
        else:
            self.fuel_var.set("N/A")

        # Update engine temperature
        temp = query_command(self.connection, obd.commands.COOLANT_TEMP)
        if temp.value is not None:
            self.temp_var.set(f"{temp.value}°C")
        else:
            self.temp_var.set("N/A")
            
        dtcs = query_command(self.connection, obd.commands.GET_DTC)
        print(dtcs.value)
        temporary = ""
        if dtcs.value is not None:
            for item in dtcs.value:
                temporary += f"{item[0]} "
        self.DTC_codes.set(temporary)

        # Schedule the next update
        self.root.after(1000, self.update_simple_data)