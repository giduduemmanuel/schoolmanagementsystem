import sqlite3
import hashlib

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def setup_users():
    conn = sqlite3.connect('school_management.db')
    cursor = conn.cursor()
    
    # Create users table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Clear existing users
    cursor.execute('DELETE FROM users')
    
    # Insert default users with hashed passwords
    users = [
        ('admin', 'admin123', 'System Administrator', 'admin'),
        ('teacher1', 'teacher123', 'Opio Moses', 'teacher'),
        ('librarian1', 'library123', 'Mary Librarian', 'librarian'),
        ('bursar1', 'bursar123', 'Achola Jackie', 'bursar'),
        ('headteacher', 'head123', 'Dr. Smith Head', 'headteacher')
    ]
    
    for user_id, password, full_name, role in users:
        hashed_password = hash_password(password)
        cursor.execute('''
            INSERT INTO users (user_id, password, full_name, role, is_active)
            VALUES (?, ?, ?, ?, 1)
        ''', (user_id, hashed_password, full_name, role))
        print(f"Created user: {user_id} with role: {role}")
    
    conn.commit()
    conn.close()
    print("Users setup completed successfully!")

if __name__ == '__main__':
    setup_users()
