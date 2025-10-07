import time
import obd
from src.MODELS.tools import DatabaseManager
from src.MODELS.tools import create_tables, DatabaseManager
from src.API.BTInteractions import BluetoothServer
from src.UTILS.config import config_instance as config
from src.API.OBDManager import OBDManager
import signal
import sys

class OpenOBD:
    custom_baudrate = config.get_obd_baudrate()
    custom_portstr = config.get_obd_portstr()

    def __init__(self, portstr=custom_portstr, baudrate=custom_baudrate):
        available_ports = obd.scan_serial()
        print("Available ports: ", available_ports)
        self.custom_portstr = portstr
        self.custom_baudrate = baudrate
        self.obd_connection = None
        self.db_connection = None
        self.bt_api = None
        self.startup()

    def init_obd_connection(self):
        print("Trying to connect to OBD...")
        print("Port: ", self.custom_portstr)
        print("Baudrate: ", self.custom_baudrate)
        self.obd_connection = OBDManager(portstr=self.custom_portstr, baudrate=self.custom_baudrate)

    def init_database_connection(self):
        print("Trying to connect to database...")
        self.db_connection = DatabaseManager.get_instance()

    def init_bluetooth_connection(self):
        self.bt_api = BluetoothServer()

    def startup(self):
        while not self.obd_connection:
            self.init_obd_connection()
            if not self.obd_connection:
                print("Connection to OBD failed. Trying again in 5 seconds...")
                time.sleep(5)
            else:
                print("Connected to OBD.")
        
        while not self.db_connection:
            self.init_database_connection()
            if not self.db_connection:
                print("Connection to DB failed. Trying again in 5 seconds...")
                time.sleep(5)
            else:
                print("Connected to DB.")

        self.init_bluetooth_connection()  # Initialize Bluetooth server

        # Use the create_tables function from your import
        create_tables()

        print("Connection established...")
        
    def shutdown(self):
        print("Shutting down server...")

        print("Server shut down successfully.")

    def run(self):
        print("Server is running. Press Ctrl+C to stop.")
        try:
            while True:
                time.sleep(1)  # Keeps the server running
        except KeyboardInterrupt:
            self.shutdown()

# Gracefully handle Ctrl+C
if __name__ == "__main__":
    server = OpenOBD()
    server.run()
