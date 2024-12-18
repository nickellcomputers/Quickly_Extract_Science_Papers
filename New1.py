import os
import zipfile
import re
from datetime import datetime
import sqlite3

# Define the zip file and the directory to extract it to
zip_file = "Sort Conv.zip"
extract_dir = "/created"

# Create the directory to extract to if it doesn't exist
os.makedirs(extract_dir, exist_ok=True)

# Unzip the file
with zipfile.ZipFile(zip_file, 'r') as zip_ref:
    zip_ref.extractall(extract_dir)

# Get a list of the extracted files
extracted_files = [os.path.join(root, file) for root, dirs, files in os.walk(extract_dir) for file in files]
txt_files = [file for file in extracted_files if file.endswith(".txt")]

def parse_line(line):
    pattern = re.compile(r"(?P<user>\w+) \((?P<time>[\d:]+)\): (?P<message>.*)")
    match = pattern.match(line)
    if match:
        return match.group("user"), match.group("time"), match.group("message")
    else:
        return None, None, None

def parse_chat_file(file_path):
    chats = []
    with open(file_path, "r") as file:
        for line in file.readlines():
            user, time, message = parse_line(line)
            if user and time and message:
                time_obj = datetime.strptime(time, "%H:%M:%S")
                chats.append({
                    "user": user,
                    "time": time_obj,
                    "message": message,
                })
    return chats

# Check if the database exists, if it does, delete it
db_path = "chatconv.db"
if os.path.exists(db_path):
    os.remove(db_path)

# Create a SQLite database
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Create tables
c.execute("""
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE
)
""")
c.execute("""
CREATE TABLE user_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file TEXT,
    user_id INTEGER,
    time TEXT,
    message TEXT,
    conversation_id INTEGER
)
""")
c.execute("""
CREATE TABLE conversations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file TEXT UNIQUE
)
""")

# Parse each txt file and insert the chats into the database
for txt_file in txt_files:
    chats = parse_chat_file(txt_file)
    for chat in chats:
        # Insert each user into the users table (ignore if user already exists)
        c.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (chat["user"],))
        # Get the user_id of the user
        c.execute("SELECT id FROM users WHERE username = ?", (chat["user"],))
        user_id = c.fetchone()[0]
        # Insert the chat into the user_messages table
        c.execute("INSERT INTO user_messages (file, user_id, time, message) VALUES (?, ?, ?, ?)", 
                  (txt_file, user_id, chat["time"].strftime("%H:%M:%S"), chat["message"]))
    # Insert the conversation into the conversations table
    c.execute("INSERT INTO conversations (file) VALUES (?)", (txt_file,))

# Update the conversation_id field in the user_messages table
c.execute("""
UPDATE user_messages 
SET conversation_id = (
    SELECT id 
    FROM conversations 
    WHERE conversations.file = user_messages.file
)
""")

# Commit the changes
conn.commit()

