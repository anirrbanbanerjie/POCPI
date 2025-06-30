# db.py
import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("claims.db")
    c = conn.cursor()
    c.execute("""
    CREATE TABLE IF NOT EXISTS decisions (
        claim_id TEXT,
        decision TEXT,
        reviewer_role TEXT,
        timestamp TEXT
    )
    """)
    conn.commit()
    conn.close()

def log_decision(claim_id, decision, role):
    conn = sqlite3.connect("claims.db")
    c = conn.cursor()
    c.execute("INSERT INTO decisions (claim_id, decision, reviewer_role, timestamp) VALUES (?, ?, ?, ?)",
              (claim_id, decision, role, datetime.now().isoformat()))
    conn.commit()
    conn.close()