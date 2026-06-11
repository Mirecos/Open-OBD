import sqlite3
import os
import datetime
import threading
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
            # The connection is shared between the main loop (readings) and
            # the BLE server thread (queries), so guard every access to it.
            self._lock = threading.RLock()
            self.connect()

        def connect(self):
            """Connect to the SQLite database"""
            try:
                self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
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
                with self._lock:
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
                with self._lock:
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
                with self._lock:
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
                with self._lock:
                    self.cursor.execute('''
                        INSERT INTO readings (session_id, timestamp, speed, rpm, fuel_status, coolant_temp, dtc)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (self.session_id, timestamp, speed, rpm, fuel_status, coolant_temp, dtc))
                    self.connection.commit()
                logger.debug(f"Inserted reading at {timestamp} for session ID: {self.session_id}")
            except sqlite3.Error as e:
                logger.error(f"Error inserting reading: {e}")

        def count_sessions(self):
            """Count the total number of stored driving sessions"""
            try:
                with self._lock:
                    self.cursor.execute('SELECT COUNT(*) FROM sessions')
                    return self.cursor.fetchone()[0] or 0
            except sqlite3.Error as e:
                logger.error(f"Error counting sessions: {e}")
                return 0

        def get_sessions(self, offset=0, limit=20):
            """Fetch a page of driving sessions, most recent first"""
            try:
                with self._lock:
                    self.cursor.execute('''
                        SELECT id, start_time, end_time, vehicle_info
                        FROM sessions
                        ORDER BY start_time DESC
                        LIMIT ? OFFSET ?
                    ''', (limit, offset))
                    rows = self.cursor.fetchall()
                return [
                    {
                        "id": row[0],
                        # Drop the microseconds, not useful for a session list
                        "start_time": row[1].split('.')[0] if row[1] else None,
                        "end_time": row[2].split('.')[0] if row[2] else None,
                        "vehicle_info": row[3],
                    }
                    for row in rows
                ]
            except sqlite3.Error as e:
                logger.error(f"Error fetching sessions: {e}")
                return []

        def get_session_summary(self, session_id):
            """Fetch metadata and aggregated readings stats for a single session"""
            try:
                with self._lock:
                    self.cursor.execute('''
                        SELECT id, start_time, end_time, vehicle_info
                        FROM sessions WHERE id = ?
                    ''', (session_id,))
                    session_row = self.cursor.fetchone()
                    if session_row is None:
                        return None

                    self.cursor.execute('''
                        SELECT
                            COUNT(*),
                            AVG(speed), MAX(speed),
                            AVG(rpm), MAX(rpm),
                            MAX(coolant_temp)
                        FROM readings WHERE session_id = ?
                    ''', (session_id,))
                    stats_row = self.cursor.fetchone()

                return {
                    "id": session_row[0],
                    "start_time": session_row[1],
                    "end_time": session_row[2],
                    "vehicle_info": session_row[3],
                    "reading_count": stats_row[0] or 0,
                    "avg_speed": round(stats_row[1], 1) if stats_row[1] is not None else 0,
                    "max_speed": round(stats_row[2], 1) if stats_row[2] is not None else 0,
                    "avg_rpm": round(stats_row[3], 1) if stats_row[3] is not None else 0,
                    "max_rpm": round(stats_row[4], 1) if stats_row[4] is not None else 0,
                    "max_coolant_temp": round(stats_row[5], 1) if stats_row[5] is not None else 0,
                }
            except sqlite3.Error as e:
                logger.error(f"Error fetching session summary: {e}")
                return None

        def fetch_current_session(self):
            """Fetch the current active session details"""
            try:
                if self.session_id is None:
                    logger.warning("No active session to fetch")
                    return None
                with self._lock:
                    self.cursor.execute('''
                        SELECT * FROM readings WHERE session_id = ?
                    ''', (self.session_id,))
                    session = self.cursor.fetchone()
                return session
            except sqlite3.Error as e:
                logger.error(f"Error fetching current session: {e}")
                return None

# Function to initialize database tables
def create_tables():
    """Initialize database tables - standalone function for easy import"""
    db_manager = DatabaseManager.get_instance()
    db_manager.create_tables()