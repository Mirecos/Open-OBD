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
    def get_bluetooth_mac_address(self):
        return self.config.get('Bluetooth server', 'mac_address')
    
    def get_bluetooth_channel(self):
        return self.config.getint('Bluetooth server', 'channel')
    
    def get_buffer_size(self):
        return self.config.getint('Bluetooth server', 'buffer_size')
    
    def get_timeout(self):
        return self.config.getint('Bluetooth server', 'timeout')
    
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