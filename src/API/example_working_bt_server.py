import time
import obd
import sqlite3
from src.MODELS.tools import DatabaseManager
from src.GUI.Interface import OpenOBD_Interface
from src.MODELS.tools import create_tables, DatabaseManager
from src.API.BTInteractions import BluetoothServer

# Initialize tables
class OpenOBD:
    # Default configuration
    custom_baudrate = 38400
    custom_portstr = "/dev/pts/2"

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
        self.obd_connection = obd.Async(portstr=self.custom_portstr, baudrate=self.custom_baudrate)

    def init_database_connection(self):
        print("Trying to connect to database...")
        self.db_connection = DatabaseManager.get_instance()

    def init_bluetooth_connection(self):
        self.bt_api = BluetoothServer()
        self.bt_api._start_server()

    def startup(self):
        while not self.obd_connection:
            self.init_obd_connection()
            if not self.obd_connection:
                print("Connection to OBD failed. Trying again in 5 seconds...")
                time.sleep(5)
        
        while not self.db_connection:
            self.init_database_connection()
            if not self.db_connection:
                print("Connection to DB failed. Trying again in 5 seconds...")
                time.sleep(5)

        self.init_bluetooth_connection()  # Initialize Bluetooth server

        # Use the create_tables function from your import
        create_tables()

        print("Connection established...")
        self.obd_connection.watch(obd.commands.SPEED)
        self.obd_connection.watch(obd.commands.RPM)
        self.obd_connection.watch(obd.commands.FUEL_STATUS)
        self.obd_connection.watch(obd.commands.COOLANT_TEMP)
        self.obd_connection.watch(obd.commands.GET_DTC)
        
        self.obd_connection.start()
        self.interface = OpenOBD_Interface(self.obd_connection)

baudrate = 38400
portstr = "/dev/pts/3"
OpenOBD(portstr=portstr, baudrate=baudrate)
