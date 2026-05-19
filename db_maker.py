"""Creates the todo data base"""
#Imports the sqlite library
import sqlite3

#Prints text to the screen
print("Started creating the todo database")

#Creates the database in the current folder
conn = sqlite3.connect('todo.db')

#Creates the table with schema including due date and completed status
conn.execute(
    "CREATE TABLE todo (category VARCHAR(50), item VARCHAR(100), due_date TEXT DEFAULT '', completed INTEGER DEFAULT 0, id INTEGER PRIMARY KEY)"
)

#Adds 5 records to the table
conn.execute("INSERT INTO todo (category, item, due_date) VALUES ('shopping', 'eggs', '')")
conn.execute("INSERT INTO todo (category, item, due_date) VALUES ('Shopping', 'milk', '')")
conn.execute("INSERT INTO todo (category, item, due_date) VALUES ('Shopping', 'flour', '')")
conn.execute("INSERT INTO todo (category, item, due_date) VALUES ('Activity', 'Clean house', '')")
conn.execute("INSERT INTO todo (category, item, due_date) VALUES ('Activity', 'Do homework', '')")

#Saves changes
conn.commit()

#Print text to the screen
print("Database has been created.")
