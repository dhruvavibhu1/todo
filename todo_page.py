"""Creates a web page to display the todo list"""
# imports the sqlite3 library, which allows us to interact with SQLite databases
import sqlite3]
from bottle import route, run

def execute_query(query, params=(), fetch=False):
    with sqlite3.connect('todo.db') as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.fetchall() if fetch else None

@route('/')
def todo_list():
    rows = execute_query("SELECT category, item FROM todo", fetch=True)

    table_rows = ""
    for row in rows:
        row_id, catagory, item = row

run(host='localhost', port=8080)
