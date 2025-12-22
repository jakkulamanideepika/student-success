import sqlite3
import hashlib
from datetime import datetime

DB_FILE = "students.db"

def init_db():
    """Initialize the database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT,
            role TEXT DEFAULT 'Teacher',
            institution TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            student_id TEXT,
            prediction_result TEXT,
            confidence REAL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password):
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, email, password, full_name, institution):
    """Register a new user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        cursor.execute(
            """INSERT INTO users (username, email, password, full_name, institution) 
               VALUES (?, ?, ?, ?, ?)""",
            (username, email, hashed_password, full_name, institution)
        )
        conn.commit()
        conn.close()
        return True, "Registration successful!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already exists!"
        elif "email" in str(e):
            return False, "Email already registered!"
        return False, "Registration failed!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def login_user(username, password):
    """Authenticate user"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        hashed_password = hash_password(password)
        cursor.execute(
            """SELECT id, username, email, full_name, institution, role 
               FROM users WHERE username = ? AND password = ?""",
            (username, hashed_password)
        )
        user = cursor.fetchone()
        
        if user:
            cursor.execute(
                "UPDATE users SET last_login = ? WHERE username = ?",
                (datetime.now(), username)
            )
            conn.commit()
            
            user_data = {
                'id': user[0],
                'username': user[1],
                'email': user[2],
                'full_name': user[3],
                'institution': user[4],
                'role': user[5]
            }
            conn.close()
            return True, user_data
        
        conn.close()
        return False, "Invalid username or password!"
    except Exception as e:
        return False, f"Error: {str(e)}"

def log_prediction(username, student_id, prediction_result, confidence):
    """Log prediction to database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO predictions 
               (username, student_id, prediction_result, confidence) 
               VALUES (?, ?, ?, ?)""",
            (username, student_id, prediction_result, confidence)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error logging prediction: {e}")

init_db()