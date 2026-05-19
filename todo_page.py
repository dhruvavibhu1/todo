"""Creates a webserver for interacting with the todo database"""
#Imports required modules
import datetime
import sqlite3
from bottle import route, run, request, redirect
from calendar_integration import add_todo_to_calendar, get_calendar_events

def execute_query(query, params=(), fetch=False):
    """Handles database interactions"""
    with sqlite3.connect('todo.db') as conn:
        cur = conn.execute(query, params)
        return cur.fetchall() if fetch else None


def ensure_db_schema():
    """Ensure the todo table has due_date and completed columns."""
    with sqlite3.connect('todo.db') as conn:
        try:
            columns = [row[1] for row in conn.execute("PRAGMA table_info(todo)").fetchall()]
        except sqlite3.OperationalError:
            return

        if 'due_date' not in columns:
            conn.execute("ALTER TABLE todo ADD COLUMN due_date TEXT DEFAULT ''")
        if 'completed' not in columns:
            conn.execute("ALTER TABLE todo ADD COLUMN completed INTEGER DEFAULT 0")


@route('/')
def todo_list():
    """Set path to the home page"""
    search_query = request.query.get('search', '').strip()
    status_filter = request.query.get('status', 'all')

    query = "SELECT id, category, item, due_date, completed FROM todo"
    conditions = []
    params = []

    if search_query:
        conditions.append("(category LIKE ? OR item LIKE ? OR due_date LIKE ?)")
        params.extend([f"%{search_query}%"] * 3)

    if status_filter == 'pending':
        conditions.append("completed = 0")
    elif status_filter == 'done':
        conditions.append("completed = 1")

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY completed, due_date, category, item"
    rows = execute_query(query, params, fetch=True)

    table_rows = ""
    for row in rows:
        row_id, category, item, due_date, completed = row
        due_text = due_date if due_date else 'No due date'
        status_text = 'Completed' if completed else 'Pending'
        status_class = 'status-completed' if completed else 'status-pending'
        row_class = 'completed' if completed else ''
        toggle_label = 'Undo' if completed else 'Complete'

        table_rows += f"""
        <tr class='{row_class}'>
            <td>{category}</td>
            <td>{item}</td>
            <td>{due_text}</td>
            <td><span class='status-pill {status_class}'>{status_text}</span></td>
            <td>
                <form action='/toggle_complete' method='POST' style='display:inline;'>
                    <input type='hidden' name='todo_id' value='{row_id}'>
                    <button type='submit'>{toggle_label}</button>
                </form>
                <form action='/delete' method='POST' style='display:inline;'>
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
            <title>To-do List</title>
            <style>
                body {{
                    font-family: 'Inter', sans-serif;
                    background-image: url('https://cdn.britannica.com/17/83817-050-67C814CD/Mount-Everest.jpg');
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    padding: 20px;
                }}
                .container {{
                    width: min(100%, 920px);
                    background: #ffffff;
                    border-radius: 28px;
                    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.08);
                    padding: 30px;
                }}
                h1 {{
                    margin: 0 0 10px;
                    color: #2f3e56;
                    text-align: center;
                }}
                .subheading {{
                    color: #556477;
                    text-align: center;
                    margin-bottom: 24px;
                }}
                .search-filter,
                .new-item-form,
                .actions-row {{
                    display: flex;
                    flex-wrap: wrap;
                    justify-content: center;
                    gap: 12px;
                    margin-bottom: 18px;
                }}
                .search-filter input,
                .search-filter select,
                .new-item-form input,
                .new-item-form input[type='date'] {{
                    border-radius: 16px;
                    border: 1px solid #d8dee8;
                    padding: 12px 14px;
                    font-size: 0.95rem;
                    font-family: 'Inter', sans-serif;
                    outline: none;
                    min-width: 180px;
                }}
                .new-item-form button,
                .actions-row button,
                .actions-row a button,
                td form button {{
                    border: none;
                    border-radius: 16px;
                    padding: 11px 18px;
                    cursor: pointer;
                    transition: background 0.2s ease, transform 0.2s ease;
                    background: #4a76ff;
                    color: white;
                    font-weight: 600;
                }}
                .new-item-form button:hover,
                .actions-row button:hover,
                td form button:hover {{
                    transform: translateY(-1px);
                    background: #2f5dd8;
                }}
                .actions-row a button {{
                    background: #ff8b3d;
                }}
                .actions-row a button:hover {{
                    background: #e56f17;
                }}
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    border-radius: 18px;
                    overflow: hidden;
                    box-shadow: inset 0 0 0 1px rgba(74, 118, 255, 0.08);
                }}
                th, td {{
                    padding: 14px 16px;
                    text-align: left;
                }}
                thead {{
                    background: linear-gradient(135deg, #4a76ff, #3a56d6);
                    color: white;
                }}
                tbody tr:nth-child(even) {{
                    background: #fbfbfd;
                }}
                tbody tr.completed {{
                    background: #f3f5fa;
                    color: #6b7280;
                    text-decoration: line-through;
                }}
                tbody tr.completed td button {{
                    background: #8b98c9;
                }}
                .status-pill {{
                    display: inline-flex;
                    padding: 6px 12px;
                    border-radius: 999px;
                    font-size: 0.85rem;
                    font-weight: 700;
                }}
                .status-pending {{
                    color: #db9856;
                    background: #edf2ff;
                }}
                .status-completed {{
                    color: #1a4b2f;
                    background: #e6f5ea;
                }}
                a {{
                    color: #4a76ff;
                    text-decoration: none;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>To-do list</h1>
                <p class="subheading">Search, filter, add due dates, and mark tasks complete from one centered view.</p>
                <form class="search-filter" action="/" method="GET">
                    <input type="text" name="search" placeholder="Search category, item, or due date" value="{search_query}">
                    <select name="status">
                        <option value="all" {'selected' if status_filter == 'all' else ''}>All</option>
                        <option value="pending" {'selected' if status_filter == 'pending' else ''}>Pending</option>
                        <option value="done" {'selected' if status_filter == 'done' else ''}>Completed</option>
                    </select>
                    <button type="submit">Search / Filter</button>
                </form>
                <form class="new-item-form" action="/new" method="POST">
                    <input type="text" name="newcat" placeholder="Category" required>
                    <input type="text" name="item" placeholder="New item" required>
                    <input type="date" name="due_date" placeholder="Due date">
                    <button type="submit">Add item</button>
                </form>
                <div class="actions-row">
                    <form action="/sync_to_calendar" method="POST" style="margin: 0;">
                        <button type="submit">Sync All to Calendar</button>
                    </form>
                    <a href="/calendar_events"><button type="button">View Calendar Events</button></a>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Item</th>
                            <th>Due date</th>
                            <th>Status</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
        </body>
        </html>
        """

    return html

@route('/delete', method='POST')
def delete_item():
    """Used for deleting items from the to do list"""
    delid = request.forms.get("delitem")
    if delid:
        execute_query("DELETE FROM todo WHERE id = ?", (delid,))
    redirect('/')


@route('/toggle_complete', method='POST')
def toggle_complete():
    todo_id = request.forms.get('todo_id')
    if todo_id:
        execute_query("UPDATE todo SET completed = 1 - completed WHERE id = ?", (todo_id,))
    redirect('/')


@route('/new', method='POST')
def new_item():
    newcat = request.forms.get("newcat")
    item = request.forms.get("item")
    due_date = request.forms.get("due_date")
    if newcat and item:
        execute_query(
            "INSERT INTO todo (category, item, due_date) VALUES (?, ?, ?)",
            (newcat, item, due_date or '')
        )
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

    if not results:
        result_html = "<li>No todo items found to sync.</li>"
    else:
        result_html = ''.join(f"<li>{result}</li>" for result in results)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sync Results</title>
    </head>
    <body>
        <h1>Sync Results</h1>
        <ul>{result_html}</ul>
        <a href="/">Back to Todo List</a>
    </body>
    </html>
    """

    return html

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


# Starts the webserver
if __name__ == '__main__':
    ensure_db_schema()
    run(host='localhost', port=8080)
