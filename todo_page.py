"""Creates a webserver for interacting with the todo database"""
# Imports required modules
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
    rows = execute_query("SELECT id, category, item FROM todo ORDER BY category, item", fetch=True)

    table_rows = ""
    for row in rows:
        row_id, category, item = row
        
        table_rows += f"""
        <tr>
            <td>{category}</td>
            <td>{item}</td>
            <td>
                <form action='/delete', method='POST'>
                    <input type='hidden', name=delitem, value='{row_id}'>
                    <button type='submit'>Delete</button>
                </form>
            </td>
        </tr>
        """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>To-do list</title>
        </head>
        <body>
            <h1>To-do list</h1>
            <table>
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
