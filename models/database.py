import sqlite3
import os
from datetime import datetime

# เปลี่ยนจาก /tmp มาใช้โฟลเดอร์ปัจจุบันแทน
DB_PATH = os.path.join(os.getcwd(), "bot.db")

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        user_id TEXT PRIMARY KEY,
        display_name TEXT,
        role TEXT DEFAULT "member",
        warn_count INTEGER DEFAULT 0,
        is_blacklisted INTEGER DEFAULT 0,
        blacklist_reason TEXT,
        created_at TEXT,
        updated_at TEXT
    )''')
    c.execute('''CREATE TABLE IF NOT EXISTS violations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id TEXT,
        group_id TEXT,
        violation_type TEXT,
        detail TEXT,
        action_taken TEXT,
        created_at TEXT
    )''')
    conn.commit()
    conn.close()

def add_to_blacklist(user_id, reason=""):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('INSERT INTO users (user_id, is_blacklisted, blacklist_reason, created_at, updated_at) VALUES (?, 1, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET is_blacklisted=1, blacklist_reason=?, updated_at=?', (user_id, reason, now, now, reason, now))
    conn.commit()
    conn.close()

def is_blacklisted(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT is_blacklisted FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return bool(row and row["is_blacklisted"])

def remove_from_blacklist(user_id):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute("UPDATE users SET is_blacklisted=0, blacklist_reason=NULL, updated_at=? WHERE user_id=?", (now, user_id))
    conn.commit()
    conn.close()

def add_warn(user_id):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('INSERT INTO users (user_id, warn_count, created_at, updated_at) VALUES (?, 1, ?, ?) ON CONFLICT(user_id) DO UPDATE SET warn_count=warn_count+1, updated_at=?', (user_id, now, now, now))
    c.execute("SELECT warn_count FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.commit()
    conn.close()
    return row["warn_count"] if row else 1

def set_role(user_id, role):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('INSERT INTO users (user_id, role, created_at, updated_at) VALUES (?, ?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET role=?, updated_at=?', (user_id, role, now, now, role, now))
    conn.commit()
    conn.close()

def get_role(user_id):
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row["role"] if row else "member"

def log_violation(user_id, group_id, violation_type, detail, action_taken):
    conn = get_connection()
    c = conn.cursor()
    now = datetime.now().isoformat()
    c.execute('INSERT INTO violations (user_id, group_id, violation_type, detail, action_taken, created_at) VALUES (?, ?, ?, ?, ?, ?)', (user_id, group_id, violation_type, detail, action_taken, now))
    conn.commit()
    conn.close()
