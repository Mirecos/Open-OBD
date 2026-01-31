import obd
import threading
from ..UTILS.logger import Logger
import json
import time

obd.logger.setLevel(obd.logging.DEBUG)  # Suppress obd library logs

logger = Logger("OBD Manager")

class OBDManager:
    _instance = None
    _lock = threading.Lock()
    obd_connection = None

    def __new__(cls, portstr=None, baudrate=None):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._init_connection(portstr, baudrate)
            return cls._instance


    def _init_connection(self, portstr, baudrate):
        self.port = portstr
        self.baudrate = baudrate
        logger.debug(f"Initializing OBD connection on port: {self.port or 'auto'} with baudrate: {self.baudrate or 'default'}")
        try:
            self.obd_connection = obd.Async(portstr=self.port, baudrate=self.baudrate)
            if not self.obd_connection.is_connected():
                logger.error("❌ OBD connection failed")
                raise Exception("OBD connection failed")
            logger.debug("✅ OBD connection established")
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.connection = None
        self.main()


    def query(self, cmd):
        if self.obd_connection is None:
            logger.error("OBD manager was not initialized.")
            return None
        try:
            response = self.obd_connection.query(cmd)
            return response.value
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return None


    def get_speed(self):
        return 50.0
        value = self.query(obd.commands.SPEED)
        return float(value.magnitude) if value is not None else 0.0

    def get_rpm(self):
        value = self.query(obd.commands.RPM)
        return float(value.magnitude) if value is not None else 0.0

    def get_coolant_temp(self):
        value = self.query(obd.commands.COOLANT_TEMP)
        return float(value.magnitude) if value is not None else 0.0

    def get_fuel_status(self):
        value = self.query(obd.commands.FUEL_STATUS)
        return str(value) if value is not None else None

    def get_throttle_pos(self):
        value = self.query(obd.commands.THROTTLE_POS)
        return float(value.magnitude) if value is not None else 0.0
    
    def get_dtc(self):
        dtcs = self.query(obd.commands.GET_DTC)
        if not dtcs:
            return json.dumps([])
        
        dtc_list = []
        for code, desc in dtcs:
            dtc_list.append({
                "code": str(code),
                "description": str(desc)
            })
        
        return json.dumps(dtc_list) 

    def main(self):
        self.obd_connection.watch(obd.commands.SPEED)
        self.obd_connection.watch(obd.commands.RPM)
        self.obd_connection.watch(obd.commands.COOLANT_TEMP)
        self.obd_connection.watch(obd.commands.FUEL_STATUS)
        self.obd_connection.watch(obd.commands.THROTTLE_POS)
        self.obd_connection.watch(obd.commands.GET_DTC)
        self.obd_connection.start()

