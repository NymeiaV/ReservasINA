import os
import sqlite3

# Get the database path from the app
db_path = os.path.join(os.path.abspath('.'), 'instance', 'app.db')
print(f"Connecting to database: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check current table structure
cursor.execute("PRAGMA table_info(prestamos)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]
print(f"Current columns: {column_names}")

# Add the column if it doesn't exist
if 'hora_devolucion_final' not in column_names:
    print("Adding hora_devolucion_final column...")
    cursor.execute("ALTER TABLE prestamos ADD COLUMN hora_devolucion_final DATETIME")
    conn.commit()
    print("Column added successfully!")
else:
    print("Column hora_devolucion_final already exists.")

# Close connection
conn.close()