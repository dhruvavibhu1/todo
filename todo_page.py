"""Creates a webserver for interacting with the todo database"""
#Imports required modules
import sqlite3
from bottle import route, run, request, redirect
from calendar_integration import add_todo_to_calendar, get_calendar_events

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
                <form action='/delete', method='POST'>
                    <input type='hidden' name=delitem value='{row_id}'>
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
            <style>
                body {{
                    font-family: Inter, sans-serif;
                    margin: 15px;
                }}
                h1 {{
                    color: #ffdd00;
                }}
                table {{
                    border-collapse: collapse;
                    width: 100%;
                }}
                th, td {{
                    border: 1px solid #ddd;
                    padding: 8px;
                    text-align: left;
                }}
                th {{
                    background-color: ##ff0088;
                }}
                button {{
                    background-color: #4CAF50;
                    color: white;
                    border: 1px solid #4CAF50;
                    border-radius: 10px; 
                    padding: 3px 10px;
                    cursor: crosshair;
                    font-family: Inter, sans-serif;
                }}
                button:hover {{
                    background-color: #45a049;
                }}
            </style>
        </head>
        <body>
            <h1>To-do list</h1>
            <h1 style="color:blue">Add new item</h1>
            <form action="/new", method="POST">
                <input type="text" name="newcat" placeholder="Category" required>
                <input type="text" name="item" placeholder="New item" required>
                <button type="submit">Add</button>
            </form>
            <div style="margin: 20px 0;">
                <form action="/sync_to_calendar", method="POST" style="display: inline;">
                    <button type="submit" style="background-color: #2196F3;">Sync All to Calendar</button>
                </form>
                <a href="/calendar_events" style="margin-left: 10px;">
                    <button style="background-color: #FF9800;">View Calendar Events</button>
                </a>
            </div>
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

@route('/delete', method='POST')
def delete_item():
    """Used for deleting items from the to do list"""
    #Gets the ID of the item to delete
    delid = request.forms.get("delitem")
    #Checks if 'delid' is valid
    if delid:
        #Deletes the record
        execute_query("DELETE FROM todo WHERE id = ?", (delid,))
        #Redirects to the home page
    redirect('/')

@route('/new', method='POST')
def new_item():
    newcat, item = request.forms.get("newcat"), request.forms.get("item")
    if newcat and item:
        execute_query("INSERT INTO todo (category, item) VALUES (?, ?)", (newcat, item))
    redirect('/')


@route('/sync_to_calendar', method='POST')
def sync_to_calendar():
    """Sync all todo items to Google Calendar"""
    rows = execute_query("SELECT category, item FROM todo", fetch=True)
    results = []
    for row in rows:
        category, item = row
        result = add_todo_to_calendar(category, item)
        results.append(f"{category}: {item} - {result}")
    # For now, just redirect. In a real app, you'd show results
    redirect('/')

@route('/calendar_events')
def calendar_events():
    """Show upcoming calendar events"""
    events = get_calendar_events()

    if isinstance(events, str):  # Error message
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Calendar Events</title>
        </head>
        <body>
            <h1>Calendar Events</h1>
            <p>Error: {events}</p>
            <a href="/">Back to Todo List</a>
        </body>
        </html>
        """
    else:
        event_list = ""
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            event_list += f"<li>{event['summary']} - {start}</li>"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Calendar Events</title>
        </head>
        <body>
            <h1>Upcoming Calendar Events</h1>
            <ul>{event_list}</ul>
            <a href="/">Back to Todo List</a>
        </body>
        </html>
        """

    return html


#Starts the webserver
if __name__ == '__main__':
    run(host = 'localhost', port = 8080)
