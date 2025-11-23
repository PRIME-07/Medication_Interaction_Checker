import sqlite3
from typing import List
from .config import DB_FILE

class DatabaseManager:
    """Handles low-level SQL connections and queries."""
    def __init__(self, db_file=DB_FILE):
        self.db_file = db_file

    def get_connection(self):
        # check_same_thread=False is needed for FastAPI concurrency
        conn = sqlite3.connect(self.db_file, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def query(self, sql: str, params: tuple = ()) -> List[sqlite3.Row]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()

# Global instance to be imported by services
db_manager = DatabaseManager()