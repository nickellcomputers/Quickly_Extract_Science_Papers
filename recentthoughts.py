import sqlite3
from datetime import datetime, timedelta
import os

# Database file path
database = "D:\\Users\\Gong Creation\\Desktop\\Global Desktop\\OneDrive\\Programming\\Thought Bounce\\Project1.NET\\bin\\newthoughts.db"

# Establish a connection to the database
conn = sqlite3.connect(database)

# Create a cursor object
cur = conn.cursor()

# Get date 7 days ago
week_ago_date = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')

# Prepare query
query = f"SELECT ThoughtDateNow, ThoughtName, ThoughtTime FROM Thoughts WHERE ThoughtDateNow >= '{week_ago_date}' AND isHide = 0"

# Execute the query
cur.execute(query)

# Fetch all results
rows = cur.fetchall()


if not rows:
    # Get date 14 days ago
    two_weeks_ago_date = (datetime.now() - timedelta(days=14)).strftime('%Y-%m-%d')
    
    # Prepare query for 14 days
    query = f"SELECT ThoughtDateNow, ThoughtName, ThoughtTime FROM Thoughts WHERE ThoughtDateNow >= '{two_weeks_ago_date}' AND isHide = 0"
    
    # Execute the query
    cur.execute(query)

    # Fetch all results
    rows = cur.fetchall()

# Specify the full path to the output file


output_dir = ".\\output\\recent_thoughts"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_file = f"{output_dir}\\thoughts_this_week.txt"


# Open a text file in write mode
with open(output_file, 'w') as f:
    # Write each row to the text file
    for row in rows:
        # Parse date and time
        date = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S").strftime("%m/%d/%Y")
        time = datetime.strptime(row[2], "1/1/0001 %I:%M:%S %p").strftime("%I:%M:%S %p")
        f.write(f'{date} {time} - {row[1]}\n')

# Close the connection
conn.close()

