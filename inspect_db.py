import sqlite3
conn = sqlite3.connect('/c/Users/Usuario/Desktop/Proyecto Computadoras - Prestamos/instance/app.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print('Tables:')
for t in tables:
    print(t[0])
conn.close()