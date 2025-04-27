import time
import obd
from src.GUI.Interface import OpenOBD_Interface


class OpenOBD:
    # Default configuration
    custom_baudrate = 38400
    custom_portstr = "\\\\.\\COM6"

    def __init__(self, portstr=custom_portstr, baudrate=custom_baudrate):
        self.portstr = portstr
        self.baudrate = baudrate
        self.connection = obd.Async()
        self.startup()

    def try_connection(self):
        print("Trying to connect...")
        print("Port: ", self.portstr)
        print("Baudrate: ", self.baudrate)
        self.connection = obd.Async(portstr=self.custom_portstr, baudrate=self.custom_baudrate)

    def startup(self):
        available_ports = obd.scan_serial()
        print("Available ports: ", available_ports)
        while not self.connection.is_connected():
            self.try_connection()
            if not self.connection.is_connected():
                print("Connection failed. Trying again in 5 seconds...")
                time.sleep(5)
        
        print("Connection established...")
        self.connection.watch(obd.commands.SPEED)
        self.connection.watch(obd.commands.RPM)
        self.connection.watch(obd.commands.FUEL_STATUS)
        self.connection.watch(obd.commands.COOLANT_TEMP)
        self.connection.watch(obd.commands.GET_DTC)
        
        self.connection.start()
        self.interface = OpenOBD_Interface(self.connection)

baudrate = 38400
portstr = "\\\\.\\COM6"
OpenOBD(portstr=portstr, baudrate=baudrate)