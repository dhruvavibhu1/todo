"""Creates a webserver for interacting with the database"""
#Imports required modules
import sqlite3
from bottle import route, run, redirect, request

def execute_query(query, params=(), fetch=False):
    """Handles database interactions"""
    #Connects to the database
    with sqlite3.connect('todo.db') as conn:
        #Executes SQL query and returns result
        cur = conn.execute(query, params)
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
                <form action="/delete", method='POST'>
                    <input type="hidden" name="delitem" value='{row_id}'>
                    <button type='submit'>Delete</button>
                </form>
            </td>
        </tr>
        """

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Todo List</title>
        </head>
        <body>
        <h1>Todo List</h1> 
        <form action="/new", method="POST">
            <input type="text", name="newcategory" placeholder="Category" required>
            <input type="text", name="item" placeholder="New item" required>
            <button type='submit'>Add</button>
        </form>
        <table>
            <tr>
                <th>Category</th>
                <th>Item</th>
                <th>Action</th>
            </tr>
            {table_rows}
        </body>
        </html>
        """

    return html

@route('/delete', method='POST')
def delete_item():
    """Handle deletion of items"""
    delid = request.forms.get('delitem')
    #checks if 'delid' is valid
    if delid:
        #deleted the record
        execute_query("DELETE FROM todo WHERE id = ?", (delid,))
    #redirects to the home page
    redirect('/')

@route('/new', method='POST')    
def new_item():
    newcat, item = request.forms.get('newcat'), request.forms.get('item')
    if newcat and item:
        execute_query("INSERT INTO todo (category, item) VALUES (?, ?)", (newcat, item))
    redirect('/')

#Starts the webserver
run(host = 'localhost', port = 8080)