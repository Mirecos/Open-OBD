import time
import obd
from src.API.DBManager import DatabaseManager
from src.API.DBManager import create_tables, DatabaseManager
from src.API.BTInteractions import BluetoothServer
from src.UTILS.config import config_instance as config
from src.API.OBDManager import OBDManager
from src.UTILS.logger import Logger

logger = Logger("Car Doctor")

class OpenOBD:
    custom_baudrate = config.get_obd_baudrate()
    custom_portstr = config.get_obd_portstr()

    def __init__(self, portstr=custom_portstr, baudrate=custom_baudrate):
        available_ports = obd.scan_serial()
        logger.info(f"Available ports: {available_ports}")
        self.custom_portstr = portstr
        self.custom_baudrate = baudrate
        self.obd_connection = None
        self.db_connection = None
        self.bt_api = None
        self.startup()

    def init_obd_connection(self):
        logger.info("Trying to connect to OBD...")
        logger.info(f"Port: {self.custom_portstr}")
        logger.info(f"Baudrate: {self.custom_baudrate}")
        self.obd_connection = OBDManager(portstr=self.custom_portstr, baudrate=self.custom_baudrate)

    def init_database_connection(self):
        logger.info("Trying to connect to database...")
        self.db_connection = DatabaseManager.get_instance()

    def init_bluetooth_connection(self):
        self.bt_api = BluetoothServer()

    def startup(self):
        while not self.obd_connection:
            self.init_obd_connection()
            if not self.obd_connection:
                logger.error("Connection to OBD failed. Trying again in 5 seconds...")
                time.sleep(5)
            else:
                logger.info("Connected to OBD.")
        
        while not self.db_connection:
            self.init_database_connection()
            if not self.db_connection:
                logger.error("Connection to DB failed. Trying again in 5 seconds...")
                time.sleep(5)
            else:
                logger.info("Connected to DB.")

        while not self.bt_api:
            self.init_bluetooth_connection()
            if not self.bt_api:
                logger.error("Connection to Bluetooth API failed. Trying again in 5 seconds...")
                time.sleep(5)
            else:
                logger.info("Connected to Bluetooth API.")

        # Use the create_tables function from your import
        create_tables()

        logger.info("Connection established...")


    async def shutdown(self):
        logger.info("Shutting down server...")
        # Bluetooth
        await self.bt_api.shutdown()
        logger.info("Server shut down successfully.")


    def run(self):
        logger.info("Server is running. Press Ctrl+C to stop.")

        logger.info("Starting new session in database...")
        DatabaseManager.get_instance().start_session()
        logger.info("Session started.")

        try:
            while True:
                logger.info("Running")
                speed = self.obd_connection.get_speed()
                print(f"Speed: {speed}")
                rpm = self.obd_connection.get_rpm()
                print(f"RPM: {rpm}")
                coolant_temp = self.obd_connection.get_coolant_temp()
                print(f"Coolant Temp: {coolant_temp}")
                fuel_status = self.obd_connection.get_fuel_status()
                print(f"Fuel Status: {fuel_status}")
                dtc = self.obd_connection.get_dtc()
                print(f"DTC: {dtc}")

                DatabaseManager.get_instance().insert_reading(
                    speed=speed,
                    rpm=rpm,
                    coolant_temp=coolant_temp,
                    fuel_status=fuel_status,
                    dtc=dtc
                )

                time.sleep(5)
        except KeyboardInterrupt:
            logger.info("Ctrl+C detected. Shutting down...")
            DatabaseManager.get_instance().end_session()
            self.shutdown()

# Gracefully handle Ctrl+C
if __name__ == "__main__":
    server = OpenOBD()
    server.run()
