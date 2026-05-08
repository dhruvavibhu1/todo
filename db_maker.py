"""Creates the todo data base"""
#Imports the sqlite library
import sqlite3

#Prints text to the screen
print("Started creating the todo database")

#Creates the database in the current folder
conn = sqlite3.connect('todo.db')

#Creates the tables with 3 fields
conn.execute("CREATE TABLE todo (category VARCHAR(50), item VARCHAR(100),id INTEGER PRIMARY KEY)")

#Adds 5 records to the table
conn.execute("INSERT INTO todo (category, item) VALUES ('shopping', 'eggs')")
conn.execute("INSERT INTO todo (category, item) VALUES ('Shopping', 'milk')")
conn.execute("INSERT INTO todo (category, item) VALUES ('Shopping', 'flour')")
conn.execute("INSERT INTO todo (category, item) VALUES ('Activity', 'Clean house')")
conn.execute("INSERT INTO todo (category, item) VALUES ('Activity', 'Do homework')")

#Saves changes
conn.commit()

#Print text to the screen
print("Database has been created.")
