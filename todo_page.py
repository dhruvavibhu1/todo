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
    """Ensure the todo table has due_date, priority, and completed columns."""
    with sqlite3.connect('todo.db') as conn:
        try:
            columns = [row[1] for row in conn.execute("PRAGMA table_info(todo)").fetchall()]
        except sqlite3.OperationalError:
            return

        if 'due_date' not in columns:
            conn.execute("ALTER TABLE todo ADD COLUMN due_date TEXT DEFAULT ''")
        if 'completed' not in columns:
            conn.execute("ALTER TABLE todo ADD COLUMN completed INTEGER DEFAULT 0")
        if 'priority' not in columns:
            conn.execute("ALTER TABLE todo ADD COLUMN priority TEXT DEFAULT 'Normal'")


@route('/')
def todo_list():
    """Set path to the home page"""
    search_query = request.query.get('search', '').strip()
    priority_filter = request.query.get('priority', 'all')

    query = "SELECT id, category, item, due_date, priority, completed FROM todo"
    conditions = []
    params = []

    if search_query:
        conditions.append("(category LIKE ? OR item LIKE ? OR due_date LIKE ? OR priority LIKE ?)")
        params.extend([f"%{search_query}%"] * 4)

    if priority_filter != 'all':
        conditions.append("priority = ?")
        params.append(priority_filter)

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    query += " ORDER BY completed, due_date, category, item"
    rows = execute_query(query, params, fetch=True)

    table_rows = ""
    for row in rows:
        row_id, category, item, due_date, priority, completed = row
        due_text = due_date if due_date else 'No due date'
        priority_text = priority or 'Normal'
        priority_class = f'priority-{priority_text.lower()}'
        row_class = 'completed' if completed else ''
        toggle_label = 'Undo' if completed else 'Complete'

        table_rows += f"""
        <tr class='{row_class}'>
            <td>{category}</td>
            <td>{item}</td>
            <td>{due_text}</td>
            <td><span class='priority-pill {priority_class}'>{priority_text}</span></td>
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
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Lora:wght@400;700&family=Open+Sans:wght@400;600;700&family=Poppins:wght@400;600;700&display=swap');
                :root {{
                    --ui-font: 'Inter', sans-serif;
                    --body-text: #2f3e56;
                    --bg-image: url('https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=1500&q=80');
                    --panel-bg: rgba(255, 255, 255, 0.94);
                    --card-bg: rgba(255, 255, 255, 0.92);
                    --button-bg: #4a76ff;
                    --button-hover: #2f5dd8;
                    --accent: #ff8b3d;
                    --priority-low-bg: #e8efff;
                    --priority-low-text: #0557c3;
                    --priority-normal-bg: #edf2ff;
                    --priority-normal-text: #2f6be3;
                    --priority-high-bg: #ffedd5;
                    --priority-high-text: #b45309;
                    --priority-urgent-bg: #ffe3eb;
                    --priority-urgent-text: #881337;
                }}
                body {{
                    font-family: var(--ui-font);
                    color: var(--body-text);
                    background-image: var(--bg-image);
                    background-size: cover;
                    background-position: center;
                    background-repeat: no-repeat;
                    background-attachment: fixed;
                    margin: 0;
                    min-height: 100vh;
                    display: flex;
                    justify-content: center;
                    align-items: flex-start;
                    padding: 40px 20px 20px;
                }}
                .container {{
                    width: min(100%, 920px);
                    background: var(--card-bg);
                    margin-top: 10px;
                    border-radius: 28px;
                    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.12);
                    padding: 30px;
                    backdrop-filter: blur(12px);
                }}
                h1 {{
                    margin: 0 0 10px;
                    color: var(--body-text);
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
                .new-item-form input[type='date'],
                .settings-row input,
                .settings-row select {{
                    border-radius: 16px;
                    border: 1px solid #d8dee8;
                    padding: 12px 14px;
                    font-size: 0.95rem;
                    font-family: var(--ui-font);
                    outline: none;
                    min-width: 180px;
                }}
                .new-item-form button,
                .actions-row button,
                .actions-row a button,
                td form button,
                .settings-actions button {{
                    border: none;
                    border-radius: 16px;
                    padding: 11px 18px;
                    cursor: pointer;
                    transition: background 0.2s ease, transform 0.2s ease;
                    background: var(--button-bg);
                    color: white;
                    font-weight: 600;
                }}
                .new-item-form button:hover,
                .actions-row button:hover,
                td form button:hover,
                .settings-actions button.save:hover {{
                    transform: translateY(-1px);
                    background: var(--button-hover);
                }}
                .actions-row a button {{
                    background: var(--accent);
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
                .priority-pill {{
                    display: inline-flex;
                    padding: 6px 12px;
                    border-radius: 999px;
                    font-size: 0.85rem;
                    font-weight: 700;
                }}
                .priority-low {{
                    color: var(--priority-low-text);
                    background: var(--priority-low-bg);
                }}
                .priority-normal {{
                    color: var(--priority-normal-text);
                    background: var(--priority-normal-bg);
                }}
                .priority-high {{
                    color: var(--priority-high-text);
                    background: var(--priority-high-bg);
                }}
                .priority-urgent {{
                    color: var(--priority-urgent-text);
                    background: var(--priority-urgent-bg);
                }}
                a {{
                    color: #4a76ff;
                    text-decoration: none;
                }}
                .settings-panel {{
                    margin-bottom: 20px;
                    display: flex;
                    flex-direction: column;
                    gap: 12px;
                }}
                .settings-panel button.toggle {{
                    background: #3548a3;
                    color: white;
                    width: fit-content;
                }}
                .settings-content {{
                    background: rgba(255, 255, 255, 0.92);
                    border: 1px solid rgba(74, 118, 255, 0.18);
                    border-radius: 20px;
                    padding: 18px;
                    display: grid;
                    gap: 14px;
                }}
                .settings-content.hidden {{
                    display: none;
                }}
                .settings-row {{
                    display: grid;
                    grid-template-columns: repeat(2, minmax(140px, 1fr));
                    gap: 10px;
                }}
                .settings-row label {{
                    display: flex;
                    flex-direction: column;
                    gap: 6px;
                    font-size: 0.95rem;
                    color: #374151;
                }}
                .settings-actions {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                    justify-content: flex-end;
                }}
                .settings-actions button.reset {{
                    background: #f1f5f9;
                    color: #334155;
                }}
            </style>
                    <script>
                const storageKey = 'todoAppSettings';
                const defaultSettings = {{
                    fontFamily: 'Inter',
                    fontColor: '#2f3e56',
                    backgroundImageUrl: 'https://images.unsplash.com/photo-1518837695005-2083093ee35b?auto=format&fit=crop&w=1500&q=80',
                    lowColor: '#0557c3',
                    lowBg: '#e8efff',
                    normalColor: '#2f6be3',
                    normalBg: '#edf2ff',
                    highColor: '#b45309',
                    highBg: '#ffedd5',
                    urgentColor: '#881337',
                    urgentBg: '#ffe3eb'
                }};
                const fontMap = {{
                    Inter: "'Inter', sans-serif",
                    Lora: "'Lora', serif",
                    'Open Sans': "'Open Sans', sans-serif",
                    Poppins: "'Poppins', sans-serif"
                }};
                function applySettings(settings) {{
                    const root = document.documentElement;
                    root.style.setProperty('--ui-font', fontMap[settings.fontFamily] || fontMap.Inter);
                    root.style.setProperty('--body-text', settings.fontColor || defaultSettings.fontColor);
                    const bgUrl = settings.backgroundImageUrl && settings.backgroundImageUrl.trim() ? settings.backgroundImageUrl.trim() : defaultSettings.backgroundImageUrl;
                    root.style.setProperty('--bg-image', `url("${{bgUrl}}")`);
                    root.style.setProperty('--priority-low-text', settings.lowColor || defaultSettings.lowColor);
                    root.style.setProperty('--priority-low-bg', settings.lowBg || defaultSettings.lowBg);
                    root.style.setProperty('--priority-normal-text', settings.normalColor || defaultSettings.normalColor);
                    root.style.setProperty('--priority-normal-bg', settings.normalBg || defaultSettings.normalBg);
                    root.style.setProperty('--priority-high-text', settings.highColor || defaultSettings.highColor);
                    root.style.setProperty('--priority-high-bg', settings.highBg || defaultSettings.highBg);
                    root.style.setProperty('--priority-urgent-text', settings.urgentColor || defaultSettings.urgentColor);
                    root.style.setProperty('--priority-urgent-bg', settings.urgentBg || defaultSettings.urgentBg);
                }}
                function loadSettings() {{
                    try {{
                        const saved = localStorage.getItem(storageKey);
                        return saved ? JSON.parse(saved) : defaultSettings;
                    }} catch (error) {{
                        return defaultSettings;
                    }}
                }}
                function saveSettings(settings) {{
                    localStorage.setItem(storageKey, JSON.stringify(settings));
                    applySettings(settings);
                }}
                function populateForm(settings) {{
                    document.getElementById('font-select').value = settings.fontFamily;
                    document.getElementById('font-color').value = settings.fontColor;
                    document.getElementById('background-url').value = settings.backgroundImageUrl;
                    document.getElementById('low-color').value = settings.lowColor;
                    document.getElementById('low-bg').value = settings.lowBg;
                    document.getElementById('normal-color').value = settings.normalColor;
                    document.getElementById('normal-bg').value = settings.normalBg;
                    document.getElementById('high-color').value = settings.highColor;
                    document.getElementById('high-bg').value = settings.highBg;
                    document.getElementById('urgent-color').value = settings.urgentColor;
                    document.getElementById('urgent-bg').value = settings.urgentBg;
                }}
                function getFormSettings() {{
                    return {{
                        fontFamily: document.getElementById('font-select').value,
                        fontColor: document.getElementById('font-color').value,
                        backgroundImageUrl: document.getElementById('background-url').value,
                        lowColor: document.getElementById('low-color').value,
                        lowBg: document.getElementById('low-bg').value,
                        normalColor: document.getElementById('normal-color').value,
                        normalBg: document.getElementById('normal-bg').value,
                        highColor: document.getElementById('high-color').value,
                        highBg: document.getElementById('high-bg').value,
                        urgentColor: document.getElementById('urgent-color').value,
                        urgentBg: document.getElementById('urgent-bg').value
                    }};
                }}
                function resetSettings() {{
                    localStorage.removeItem(storageKey);
                    populateForm(defaultSettings);
                    applySettings(defaultSettings);
                }}
                document.addEventListener('DOMContentLoaded', () => {{
                    const settings = loadSettings();
                    populateForm(settings);
                    applySettings(settings);
                    document.getElementById('settings-form').addEventListener('submit', event => {{
                        event.preventDefault();
                        saveSettings(getFormSettings());
                    }});
                    document.getElementById('toggle-settings').addEventListener('click', () => {{
                        document.getElementById('settings-content').classList.toggle('hidden');
                    }});
                    document.getElementById('reset-settings').addEventListener('click', resetSettings);
                }});
            </script>
        </head>
        <body>
            <div class="container">
                <div class="settings-panel">
                    <button type="button" id="toggle-settings" class="toggle">Show / Hide Settings</button>
                    <div id="settings-content" class="settings-content hidden">
                        <form id="settings-form">
                            <div class="settings-row">
                                <label>
                                    Font family
                                    <select id="font-select" name="font_select">
                                        <option value="Inter">Inter</option>
                                        <option value="Lora">Lora</option>
                                        <option value="Open Sans">Open Sans</option>
                                        <option value="Poppins">Poppins</option>
                                    </select>
                                </label>
                                <label>
                                    Font color
                                    <input id="font-color" type="color" name="font_color" value="#2f3e56">
                                </label>
                                <label>
                                    Background image URL
                                    <input id="background-url" type="url" name="background_url" placeholder="https://...">
                                </label>
                                <label>
                                    Low priority text color
                                    <input id="low-color" type="color" name="low_color" value="#0557c3">
                                </label>
                                <label>
                                    Low priority background
                                    <input id="low-bg" type="color" name="low_bg" value="#e8efff">
                                </label>
                                <label>
                                    Normal priority text color
                                    <input id="normal-color" type="color" name="normal_color" value="#2f6be3">
                                </label>
                                <label>
                                    Normal priority background
                                    <input id="normal-bg" type="color" name="normal_bg" value="#edf2ff">
                                </label>
                                <label>
                                    High priority text color
                                    <input id="high-color" type="color" name="high_color" value="#b45309">
                                </label>
                                <label>
                                    High priority background
                                    <input id="high-bg" type="color" name="high_bg" value="#ffedd5">
                                </label>
                                <label>
                                    Urgent priority text color
                                    <input id="urgent-color" type="color" name="urgent_color" value="#881337">
                                </label>
                                <label>
                                    Urgent priority background
                                    <input id="urgent-bg" type="color" name="urgent_bg" value="#ffe3eb">
                                </label>
                            </div>
                            <div class="settings-actions">
                                <button type="button" id="reset-settings" class="reset">Reset defaults</button>
                                <button type="submit" class="save">Save settings</button>
                            </div>
                        </form>
                    </div>
                </div>
                <h1>To-do list</h1>
                <p class="subheading">Search, filter by priority, add due dates, and mark tasks complete from one centered view.</p>
                <form class="search-filter" action="/" method="GET">
                    <input type="text" name="search" placeholder="Search category, item, due date, or priority" value="{search_query}">
                    <select name="priority">
                        <option value="all" {'selected' if priority_filter == 'all' else ''}>All</option>
                        <option value="Low" {'selected' if priority_filter == 'Low' else ''}>Low</option>
                        <option value="Normal" {'selected' if priority_filter == 'Normal' else ''}>Normal</option>
                        <option value="High" {'selected' if priority_filter == 'High' else ''}>High</option>
                        <option value="Urgent" {'selected' if priority_filter == 'Urgent' else ''}>Urgent</option>
                    </select>
                    <button type="submit">Search / Filter</button>
                </form>
                <form class="new-item-form" action="/new" method="POST">
                    <input type="text" name="newcat" placeholder="Category" required>
                    <input type="text" name="item" placeholder="New item" required>
                    <select name="priority" required>
                        <option value="Normal">Normal</option>
                        <option value="Low">Low</option>
                        <option value="High">High</option>
                        <option value="Urgent">Urgent</option>
                    </select>
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
                            <th>Priority</th>
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
    priority = request.forms.get("priority") or 'Normal'
    if newcat and item:
        execute_query(
            "INSERT INTO todo (category, item, due_date, priority) VALUES (?, ?, ?, ?)",
            (newcat, item, due_date or '', priority)
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
