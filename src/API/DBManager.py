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


        def start_session(self, vehicle_info="Unknown Vehicle"):
            """Start a new driving session"""
            try:
                start_time = datetime.datetime.now()
                self.cursor.execute('''
                    INSERT INTO sessions (start_time, vehicle_info)
                    VALUES (?, ?)
                ''', (start_time, vehicle_info))
                self.connection.commit()
                self.session_id = self.cursor.lastrowid
                logger.info(f"Started new session with ID: {self.session_id}")
            except sqlite3.Error as e:
                logger.error(f"Error starting session: {e}")

        def end_session(self):
            """End the current driving session"""
            try:
                if self.session_id is None:
                    logger.warning("No active session to end")
                    return
                end_time = datetime.datetime.now()
                self.cursor.execute('''
                    UPDATE sessions
                    SET end_time = ?
                    WHERE id = ?
                ''', (end_time, self.session_id))
                self.connection.commit()
                logger.info(f"Ended session with ID: {self.session_id}")
                self.session_id = None
            except sqlite3.Error as e:
                logger.error(f"Error ending session: {e}")

        def insert_reading(self, speed, rpm, fuel_status, coolant_temp, dtc):
            """Insert a new OBD reading into the database"""
            try:
                if self.session_id is None:
                    logger.warning("No active session. Cannot insert reading.")
                    return
                timestamp = datetime.datetime.now()
                self.cursor.execute('''
                    INSERT INTO readings (session_id, timestamp, speed, rpm, fuel_status, coolant_temp, dtc)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (self.session_id, timestamp, speed, rpm, fuel_status, coolant_temp, dtc))
                self.connection.commit()
                logger.debug(f"Inserted reading at {timestamp} for session ID: {self.session_id}")
            except sqlite3.Error as e:
                logger.error(f"Error inserting reading: {e}")

# Function to initialize database tables
def create_tables():
    """Initialize database tables - standalone function for easy import"""
    db_manager = DatabaseManager.get_instance()
    db_manager.create_tables()