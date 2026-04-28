"""Creates a web page to display the todo list"""
# imports the sqlite3 library, which allows us to interact with SQLite databases
import sqlite3
from bottle import route, run

def execute_query(query, params=(), fetch=False):
    """Handles database interactions"""
    with sqlite3.connect('todo.db') as conn:
        cur = conn.cursor()
        # Executes the provided SQL query with optional parameters and fetches results if specified
        cur.execute(query, params)
        return cur.fetchall() if fetch else None

@route('/')
def todo_list():
    """Set path to the home page"""
    rows = execute_query("SELECT category, item FROM todo", fetch=True)

    table_rows = ""
    for row in rows:
        row_id, category, item = row

        table_rows += f"""
        # html code
        <tr>
            <td>{category}</td>
            <td>{item}</td>
            <td>
                <form action = "/delete" method='POST'>
                    <input type='hidden' name='delitem' value='{row_id}'>
                    <button type='submit'>Delete</button>
                </form>
            </td>
        </tr>
        """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>To-Do List</title>
        </head>
        <body>
            <h1>To-Do List</h1>
            <table border="1">
                <tr>
                    <th>Category</th>
                    <th>Item</th>
                    <th>Action</th>
                </tr>
                {table_rows}
            </table>
        </body>
        </html>
        """

        return html

# Starts the webserver
run(host= 'localhost', port=8080)
