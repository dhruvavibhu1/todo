import sqlite3

print("Started creating the todo database")

conn = sqlite3.connect('todo.db')

conn.execute("CREATE TABLE todo (category VARCHAR (50), item VARCHAR(100), id INTEGER PRIMARY KEY)")

conn.execute("INSERT INTO todo (category, item) VALUES ('shopping', 'eggs')")
conn.execute("INSERT INTO todo (category, item) VALUES ('shopping', 'milk')")
conn.execute("INSERT INTO todo (category, item) VALUES ('shopping', 'flour')")
conn.execute("INSERT INTO todo (category, item) VALUES ('activity', 'Clean the house')")
conn.execute("INSERT INTO todo (category, item) VALUES ('activity', 'Do homework')")

conn.commit()

print("Database has been created")
