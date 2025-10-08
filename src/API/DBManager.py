import sqlite3
import os
import datetime
from src.UTILS.logger import Logger

logger = Logger("DB Manager")

class DatabaseManager:
    _instance = None
    
    @staticmethod
    def get_instance(db_path="obd_data.db"):
        """Static method to get or create the singleton instance"""
        if DatabaseManager._instance is None:
            DatabaseManager._instance = DatabaseManager.__DatabaseManager(db_path)
        return DatabaseManager._instance
    
    class __DatabaseManager:
        """Private class that holds the actual implementation"""
        def __init__(self, db_path):
            self.db_path = db_path
            self.connection = None
            self.cursor = None
            self.session_id = None
            self.connect()
        
        def connect(self):
            """Connect to the SQLite database"""
            try:
                self.connection = sqlite3.connect(self.db_path)
                self.cursor = self.connection.cursor()
                logger.info(f"Connected to database: {self.db_path}")
            except sqlite3.Error as e:
                logger.error(f"Database connection error: {e}")
        
        def close(self):
            """Close the database connection"""
            if self.connection:
                self.connection.close()
                logger.info("Database connection closed")
        
        # Move this method inside the inner class
        def create_tables(self):
            """Create necessary tables if they don't exist"""
            try:
                # Create sessions table to track different driving sessions
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        start_time TIMESTAMP,
                        end_time TIMESTAMP,
                        vehicle_info TEXT
                    )
                ''')
                
                # Create readings table to store OBD data
                self.cursor.execute('''
                    CREATE TABLE IF NOT EXISTS readings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id INTEGER,
                        timestamp TIMESTAMP,
                        speed REAL,
                        rpm REAL,
                        fuel_status TEXT,
                        coolant_temp REAL,
                        dtc TEXT,
                        FOREIGN KEY (session_id) REFERENCES sessions (id)
                    )
                ''')
                
                self.connection.commit()
                logger.info("Database tables created or verified successfully")
            except sqlite3.Error as e:
                logger.error(f"Error creating tables: {e}")

# Function to initialize database tables
def create_tables():
    """Initialize database tables - standalone function for easy import"""
    db_manager = DatabaseManager.get_instance()
    db_manager.create_tables()