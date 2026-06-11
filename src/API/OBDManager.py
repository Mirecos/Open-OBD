import obd
import threading
from ..UTILS.logger import Logger
import json
import time

obd.logger.setLevel(obd.logging.FATAL)  # Suppress obd library logs

logger = Logger("OBD Manager")

class OBDManager:
    _instance = None
    _lock = threading.Lock()
    obd_connection = None

    # Mode 01 PIDs polled for the realtime dashboard. Each entry maps the key
    # exposed in get_realtime_data()'s response to the corresponding OBD
    # command. Values are reported in the units defined by the OBD-II
    # standard (km/h, rpm, °C, %).
    REALTIME_COMMANDS = [
        ("speed", obd.commands.SPEED),
        ("rpm", obd.commands.RPM),
        ("coolant_temp", obd.commands.COOLANT_TEMP),
        ("engine_load", obd.commands.ENGINE_LOAD),
        ("throttle_pos", obd.commands.THROTTLE_POS),
        ("fuel_level", obd.commands.FUEL_LEVEL),
    ]

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


    def get_value(self, cmd):
        """Query a numeric command and return its magnitude as a float
        rounded to 1 decimal, or None if the vehicle doesn't support it."""
        value = self.query(cmd)
        if value is None:
            return None
        magnitude = getattr(value, "magnitude", value)
        try:
            return round(float(magnitude), 1)
        except (TypeError, ValueError):
            return None

    def get_speed(self):
        return self.get_value(obd.commands.SPEED) or 0.0

    def get_rpm(self):
        return self.get_value(obd.commands.RPM) or 0.0

    def get_coolant_temp(self):
        return self.get_value(obd.commands.COOLANT_TEMP) or 0.0

    def get_realtime_data(self):
        return {key: self.get_value(cmd) for key, cmd in self.REALTIME_COMMANDS}

    def get_fuel_status(self):
        value = self.query(obd.commands.FUEL_STATUS)
        return str(value) if value is not None else None

    def get_throttle_pos(self):
        return self.get_value(obd.commands.THROTTLE_POS) or 0.0
    
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
        for _, cmd in self.REALTIME_COMMANDS:
            self.obd_connection.watch(cmd)
        self.obd_connection.watch(obd.commands.FUEL_STATUS)
        self.obd_connection.watch(obd.commands.GET_DTC)
        self.obd_connection.start()

