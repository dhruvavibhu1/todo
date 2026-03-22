"""Creates the todo database"""
# imports the sqlite3 library, which allows us to interact with SQLite databases
import sqlite3

# prints a message indicating that the process of creating the todo database has started
print("Started creating the todo database")

# python will create a new file called 'todo.db'
conn = sqlite3.connect('todo.db')

# creates a table called "todo" with three columns
conn.execute("CREATE TABLE todo (category VARCHAR (50), item VARCHAR(100))")

# adds 5 records to the todo table, each with a category and an item
conn.execute("INSERT INTO todo (category, item) VALUES ('shopping', 'eggs')")
conn.execute("INSERT INTO todo (category, item) VALUES ('shopping', 'milk')")
conn.execute("INSERT INTO todo (category, item) VALUES ('shopping', 'flour')")
conn.execute("INSERT INTO todo (category, item) VALUES ('activity', 'Clean the house')")
conn.execute("INSERT INTO todo (category, item) VALUES ('activity', 'Do homework')")

# commits the changes to the database, ensuring that the new table and records are saved
conn.commit()

# prints a message to the console indicating that the database has been created successfully
print("Database has been created")
