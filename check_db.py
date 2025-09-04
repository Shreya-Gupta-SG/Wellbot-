import sqlite3

# Connect to your database
conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Show all tables
print("\nTables in DB:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print(cursor.fetchall())

# Show structure of 'users' table (if exists)
print("\nSchema of users table:")
cursor.execute("PRAGMA table_info(users);")
print(cursor.fetchall())

# Show all rows in 'users'
print("\nData in users table:")
cursor.execute("SELECT * FROM users;")
print(cursor.fetchall())

conn.close()
