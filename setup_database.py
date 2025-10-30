import sqlite3

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('seating_system.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Create the users table
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    role TEXT NOT NULL
);
''')

# Create the reservations table
cursor.execute('''
CREATE TABLE IF NOT EXISTS reservations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    seat_number INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);
''')

# Insert some example users
cursor.execute("INSERT INTO users (name, role) VALUES ('Alice', 'Admin')")
cursor.execute("INSERT INTO users (name, role) VALUES ('Bob', 'User')")

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully!")
