import obd
import threading
from ..UTILS.logger import Logger

logger = Logger("OBD Manager")

class OBDManager:
    _instance = None
    _lock = threading.Lock()

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
        if not self.obd_connection:
            logger.error("OBD manager was not initialized.")
            return None
        try:
            response = self.obd_connection.query(cmd)
            return response.value
        except Exception as e:
            logger.error(f"Query failed: {e}")
            return None


    def get_speed(self):
        return self.query(obd.commands.SPEED)

    def get_rpm(self):
        return self.query(obd.commands.RPM)

    def get_coolant_temp(self):
        return self.query(obd.commands.COOLANT_TEMP)

    def get_throttle_pos(self):
        return self.query(obd.commands.THROTTLE_POS)

    def main(self):
        self.obd_connection.watch(obd.commands.SPEED)
        self.obd_connection.watch(obd.commands.RPM)
        self.obd_connection.watch(obd.commands.FUEL_STATUS)
        self.obd_connection.watch(obd.commands.COOLANT_TEMP)
        self.obd_connection.watch(obd.commands.GET_DTC)
        self.obd_connection.start()

