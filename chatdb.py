# chatdb.py
import sqlite3

db_path = "chatconv.db"

def open_conn():
    return sqlite3.connect(db_path)

