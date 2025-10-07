import obd
import threading

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
        print(f"[OBD Service] Connecting to {self.port or 'auto'}...")
        try:
            self.obd_connection = obd.Async(portstr=self.port, baudrate=self.baudrate)
            print(self.obd_connection)
        except Exception as e:
            print(f"[OBD Service] Connection error: {e}")
            self.connection = None
        self.main()


    def query(self, cmd):
        if not self.obd_connection:
            print("[OBD Service] : OBD manager was not initialized.")
            return None
        try:
            response = self.obd_connection.query(cmd)
            return response.value
        except Exception as e:
            print(f"[OBD Service] Query failed: {e}")
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



# from obd_manager import OBDManager
# import time

# def main():
#     obd_mgr = OBDManager()  # Singleton instance
#     while True:
#         rpm = obd_mgr.get_rpm()
#         speed = obd_mgr.get_speed()
#         print(f"RPM: {rpm}, Speed: {speed}")
#         time.sleep(2)