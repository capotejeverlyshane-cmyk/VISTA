import sqlite3
import os
from contextlib import contextmanager

# Ensure the data directory exists
DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'vista.db')

def init_db():
    """Initializes the SQLite database with the necessary tables."""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Chat Logs Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                intent TEXT,
                language TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Feedback Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                answer TEXT NOT NULL,
                intent TEXT,
                helpful BOOLEAN,
                language TEXT,
                comment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Add comment column to existing feedback table if it doesn't exist
        try:
            cursor.execute("ALTER TABLE feedback ADD COLUMN comment TEXT")
        except sqlite3.OperationalError:
            pass # Column already exists
        
        # Unresolved Queries Table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS unresolved_queries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                question TEXT NOT NULL,
                predicted_intent TEXT,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()

@contextmanager
def get_db():
    """Context manager for SQLite database connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row # Allows accessing columns by name
    try:
        yield conn
    finally:
        conn.close()

# Initialize the database when this module is imported
init_db()

if __name__ == '__main__':
    print(f"Database initialized at {DB_PATH}")
