import configparser
import os

class Config:
    def __init__(self):
        self.config = configparser.ConfigParser()
        
        # Find the config file relative to the project root
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.join(current_dir, '..', '..')
        config_path = os.path.join(project_root, 'config.ini')
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at {config_path}")
        
        self.config.read(config_path)


    # Bluetooth server configuration
    def get_bluetooth_server_name(self):
        return self.config.get('Bluetooth server', 'server_name')

    def get_bluetooth_service_uuid(self):
        return self.config.get('Bluetooth server', 'service_uuid')

    def get_bluetooth_char_uuid(self):
        return self.config.get('Bluetooth server', 'char_uuid')

    # OBD connection configuration
    def get_obd_portstr(self):
        return self.config.get('OBD connection', 'obd_portstr')

    def get_obd_baudrate(self):
        return self.config.getint('OBD connection', 'obd_baudrate')


    # Generic getter methods
    def get(self, section, key, fallback=None):
        return self.config.get(section, key, fallback=fallback)
    
    def getint(self, section, key, fallback=None):
        return self.config.getint(section, key, fallback=fallback)
    
    def getfloat(self, section, key, fallback=None):
        return self.config.getfloat(section, key, fallback=fallback)
    
    def getboolean(self, section, key, fallback=None):
        return self.config.getboolean(section, key, fallback=fallback)

# Create a global instance
config_instance = Config()