import sqlite3

# Connect to the database (it will create if it doesn't exist)
conn = sqlite3.connect('equipment.db')
cursor = conn.cursor()

# Create the table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS equipment (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        rental_price REAL NOT NULL
    )
''')

# Insert sample data into the table
cursor.executemany('''
    INSERT INTO equipment (name, rental_price) VALUES (?, ?)
''', [
    ('Projector', 500),
    ('Microphone', 200),
    ('Speakers', 300),
    ('Laptop', 1000),
    ('LED Screen', 1500)
])

# Commit the changes and close the connection
conn.commit()
conn.close()

print("Database and table created successfully with sample data.")