"""Creates a webserver for interacting with the todo database"""
# Imports required modules
import datetime
import sqlite3
from bottle import route, run, request, redirect


def execute_query(query, params=(), fetch=False):
    """Handles database interactions."""
    with sqlite3.connect('todo.db') as conn:
        cur = conn.execute(query, params)
        return cur.fetchall() if fetch else None


def ensure_db_schema():
    """Ensure the todo table includes the right tracking columns."""
    with sqlite3.connect('todo.db') as conn:
        try:
            columns = [row[1] for row in conn.execute("PRAGMA table_info(todo)").fetchall()]
        except sqlite3.OperationalError:
            return

        if 'due_date' not in columns:
            conn.execute("ALTER TABLE todo ADD COLUMN due_date TEXT DEFAULT ''")
        if 'completed' not in columns:
            conn.execute("ALTER TABLE todo ADD COLUMN completed INTEGER DEFAULT 0")
        if 'completed_date' not in columns:
            conn.execute("ALTER TABLE todo ADD COLUMN completed_date TEXT DEFAULT ''")
        if 'priority' not in columns:
            conn.execute("ALTER TABLE todo ADD COLUMN priority TEXT DEFAULT 'Normal'")


def get_total_completed():
    """Return the number of completed todo tasks."""
    result = execute_query("SELECT COUNT(*) FROM todo WHERE completed = 1", fetch=True)
    return result[0][0] if result else 0


def get_completed_dates():
    """Return the distinct completed dates for streak calculations."""
    rows = execute_query(
        "SELECT DISTINCT completed_date FROM todo WHERE completed = 1 AND completed_date != '' ORDER BY completed_date DESC",
        fetch=True,
    )
    dates = []
    for row in rows:
        try:
            dates.append(datetime.datetime.strptime(row[0], "%Y-%m-%d").date())
        except (TypeError, ValueError):
            continue
    return sorted(set(dates), reverse=True)


def calculate_streak():
    """Calculate the current consecutive completion streak."""
    dates = get_completed_dates()
    if not dates:
        return 0

    streak = 1
    previous = dates[0]
    for current in dates[1:]:
        if current == previous - datetime.timedelta(days=1):
            streak += 1
            previous = current
        else:
            break
    return streak


def get_reward_level(points):
    if points >= 200:
        return 'Platinum'
    if points >= 100:
        return 'Gold'
    if points >= 50:
        return 'Silver'
    if points > 0:
        return 'Bronze'
    return 'Newbie'


@route('/')
def todo_list():
    """Render the home page with statistics and the task list."""
    search_query = request.query.get('search', '').strip()
    priority_filter = request.query.get('priority', 'all')

    total_completed = get_total_completed()
    reward_points = total_completed * 10
    streak_days = calculate_streak()
    current_time = datetime.datetime.now().strftime('%H:%M:%S')
    reward_level = get_reward_level(reward_points)

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
                <div class='action-buttons'>
                    <form class='inline-action' action='/toggle_complete' method='POST'>
                        <input type='hidden' name='todo_id' value='{row_id}'>
                        <button type='submit'>{toggle_label}</button>
                    </form>
                    <form class='inline-action' action='/delete' method='POST'>
                        <input type='hidden' name='delitem' value='{row_id}'>
                        <button type='submit'>Delete</button>
                    </form>
                </div>
            </td>
        </tr>
        """

    html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>To-do List</title>
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

                :root {{
                    color-scheme: light;
                    --font-family: 'Inter', sans-serif;
                    --body-text: #263147;
                    --page-background: radial-gradient(circle at top, #eef3ff 0%, #f3f5f9 40%, #f8fafc 100%);
                    --bg-image: none;
                    --surface: #ffffff;
                    --surface-strong: #f8fafc;
                    --border: #e5e9f0;
                    --primary: #4056ff;
                    --accent: #f97316;
                    --muted: #64748b;
                    --shadow: 0 16px 40px rgba(24, 39, 75, 0.08);
                    --streak-card-bg: #fffbf7;
                    --streak-card-border: #f59e0b;
                    --streak-card-height: auto;
                }}

                .metric-card.streak-card {{
                    background: var(--streak-card-bg);
                    border-color: var(--streak-card-border);
                    height: var(--streak-card-height, auto);
                }}

                *, *::before, *::after {{
                    box-sizing: border-box;
                }}

                html, body {{
                    margin: 0;
                    min-height: 100%;
                }}

                body {{
                    background-color: #f3f5f9;
                    background-image: var(--bg-image), var(--page-background);
                    background-position: center;
                    background-size: cover;
                    color: var(--body-text);
                    font-family: var(--font-family);
                    line-height: 1.5;
                    display: flex;
                    justify-content: center;
                    padding: 30px 16px 40px;
                }}

                .page-shell {{
                    width: min(100%, 1080px);
                }}

                .hero {{
                    display: grid;
                    gap: 24px;
                    margin-bottom: 26px;
                }}

                .summary-grid {{
                    display: grid;
                    grid-template-columns: repeat(3, minmax(0, 1fr));
                    gap: 16px;
                }}

                .metric-card {{
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: 24px;
                    padding: 22px 24px;
                    box-shadow: var(--shadow);
                }}

                .metric-title {{
                    margin: 0 0 12px;
                    color: var(--muted);
                    font-size: 0.95rem;
                    font-weight: 600;
                    text-transform: uppercase;
                    letter-spacing: 0.08em;
                }}

                .metric-value {{
                    margin: 0;
                    font-size: 2rem;
                    font-weight: 700;
                    color: #17202a;
                }}

                .metric-time {{
                    margin: 8px 0 0;
                    color: #334155;
                    font-size: 0.95rem;
                    font-weight: 600;
                }}

                .metric-subtext {{
                    margin-top: 8px;
                    color: #52606d;
                    font-size: 0.92rem;
                }}

                .page-card {{
                    background: var(--surface);
                    border: 1px solid var(--border);
                    border-radius: 30px;
                    box-shadow: var(--shadow);
                    overflow: hidden;
                }}

                .page-card header {{
                    padding: 26px 30px 0;
                }}

                .page-card h1 {{
                    margin: 0 0 8px;
                    font-size: clamp(2rem, 2.4vw, 2.5rem);
                    letter-spacing: -0.03em;
                }}

                .page-card p {{
                    margin: 0;
                    color: var(--muted);
                    font-size: 1rem;
                }}

                .top-actions {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                    align-items: center;
                    justify-content: space-between;
                    margin: 24px 30px 0;
                }}

                .top-actions button, .top-actions form button, .top-actions .settings-button, .search-filter button, .new-item-form button, .todo-table button {{
                    border: 1px solid transparent;
                    border-radius: 14px;
                    padding: 10px 14px;
                    font-size: 0.95rem;
                    font-family: Inter, sans-serif;
                    cursor: pointer;
                    transition: transform 0.18s ease, box-shadow 0.18s ease, background 0.18s ease, border-color 0.18s ease;
                    font-weight: 600;
                    min-height: 40px;
                }}

                .top-actions button.primary, .top-actions form button.primary {{
                    background: var(--primary);
                    color: white;
                    box-shadow: 0 12px 24px rgba(64, 86, 255, 0.14);
                }}

                .top-actions button.secondary {{
                    background: var(--surface-strong);
                    color: #334155;
                    box-shadow: inset 0 0 0 1px rgba(100, 116, 139, 0.12);
                }}

                .settings-button {{
                    background: #ffffff;
                    color: #334155;
                    border: 1px solid var(--border);
                    box-shadow: none;
                    padding: 10px 14px;
                    border-radius: 14px;
                    font-weight: 700;
                    min-height: 38px;
                }}

                .settings-button:hover {{
                    background: #f8fafc;
                }}

                .top-actions button:hover, .top-actions .settings-button:hover, .top-actions form button:hover, .search-filter button:hover, .new-item-form button:hover, .todo-table button:hover {{
                    transform: translateY(-1px);
                }}

                .search-filter, .new-item-form {{
                    display: grid;
                    gap: 12px;
                    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                    padding: 0 30px 24px;
                }}

                .search-filter {{
                    align-items: flex-end;
                }}

                .search-filter input,
                .search-filter select,
                .new-item-form input,
                .new-item-form input[type='date'],
                .new-item-form select {{
                    width: 100%;
                    border: 1px solid var(--border);
                    border-radius: 14px;
                    padding: 12px 14px;
                    font-size: 0.95rem;
                    color: #1f2937;
                    background: #fff;
                }}

                .search-filter button {{
                    width: auto;
                    justify-self: start;
                    min-width: 100px;
                    padding: 10px 14px;
                    background: #334155;
                    color: white;
                    box-shadow: 0 12px 20px rgba(51, 65, 85, 0.14);
                }}

                .new-item-form button {{
                    width: fit-content;
                    justify-self: start;
                    background: #14b8a6;
                    color: white;
                }}

                .action-buttons {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 8px;
                    align-items: center;
                }}

                .inline-action {{
                    display: inline-block;
                    margin: 0;
                }}

                .inline-action button {{
                    min-width: 88px;
                    padding: 8px 12px;
                    background: #f8fafc;
                    color: #334155;
                    border-color: #d1d5db;
                    box-shadow: none;
                }}

                .inline-action button:hover {{
                    background: #eef2ff;
                }}

                .todo-table {{
                    width: 100%;
                    border: 1px solid var(--border);
                    border-collapse: collapse;
                    border-spacing: 0;
                    box-shadow: 0 14px 38px rgba(15, 23, 42, 0.06);
                    background: #fff;
                }}

                .todo-table th,
                .todo-table td {{
                    padding: 14px 16px;
                    text-align: left;
                    border: 1px solid var(--border);
                }}

                .todo-table th:nth-child(3),
                .todo-table td:nth-child(3) {{
                    width: 130px;
                }}

                .todo-table th:nth-child(4),
                .todo-table td:nth-child(4) {{
                    width: 110px;
                }}

                .todo-table th:nth-child(5),
                .todo-table td:nth-child(5) {{
                    width: 180px;
                }}

                .todo-table thead th {{
                    background: #eef2ff;
                    color: #1f2937;
                    font-weight: 700;
                    font-size: 0.95rem;
                }}

                .todo-table tbody tr {{
                    background: #ffffff;
                }}

                .todo-table tbody tr:nth-child(even) {{
                    background: #f8f9ff;
                }}

                .todo-table tbody tr:hover {{
                    background: #eef2ff;
                }}

                .todo-table tbody tr.completed {{
                    color: #64748b;
                    background: #f3f4f6;
                }}

                .todo-table tbody tr.completed td {{
                    text-decoration: line-through;
                }}

                .priority-pill {{
                    display: inline-flex;
                    align-items: center;
                    padding: 8px 12px;
                    border-radius: 999px;
                    font-size: 0.85rem;
                    font-weight: 700;
                }}

                .priority-low {{
                    background: #eef2ff;
                    color: #2563eb;
                }}

                .priority-normal {{
                    background: #f0f9ff;
                    color: #0c4a6e;
                }}

                .priority-high {{
                    background: #fff7ed;
                    color: #c2410c;
                }}

                .priority-urgent {{
                    background: #fef2f2;
                    color: #b91c1c;
                }}

                .settings-panel {{
                    padding: 0 30px 24px;
                }}

                .settings-content {{
                    background: #ffffff;
                    border: 1px solid var(--border);
                    border-radius: 22px;
                    padding: 22px;
                    display: grid;
                    gap: 16px;
                }}

                .settings-content.hidden {{
                    display: none;
                }}

                .settings-row {{
                    display: grid;
                    gap: 16px;
                    grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
                }}

                .settings-row label {{
                    display: grid;
                    gap: 8px;
                    font-size: 0.95rem;
                    color: #334155;
                }}

                .settings-actions {{
                    display: flex;
                    flex-wrap: wrap;
                    gap: 12px;
                    justify-content: flex-end;
                }}

                .settings-actions button {{
                    border-radius: 16px;
                    padding: 12px 18px;
                }}

                .settings-actions button.reset {{
                    background: #f1f5f9;
                    color: #334155;
                }}

                .settings-actions button.save {{
                    background: var(--primary);
                    color: white;
                }}

                @media (max-width: 760px) {{
                    .summary-grid {{
                        grid-template-columns: 1fr;
                    }}

                    .top-actions {{
                        flex-direction: column;
                        align-items: stretch;
                    }}
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
                    Garmond: "'Garmond', serif",
                    'Lucida Console': "'Lucida Console', monospace",
                    Arial: "'Arial', sans-serif"
                }};
                function applySettings(settings) {{
                    const root = document.documentElement;
                    root.style.setProperty('--font-family', fontMap[settings.fontFamily] || fontMap.Inter);
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
            <div class="page-shell">
                <div class="page-card">
                    <header>
                        <h1>To-do list</h1>
                    </header>
                    <div class="hero">
                        <div class="summary-grid">
                            <div class="metric-card">
                                <p class="metric-title">Tasks completed</p>
                                <p class="metric-value">{total_completed}</p>
                                <p class="metric-subtext">Total tasks finished so far.</p>
                            </div>
                            <div class="metric-card">
                                <p class="metric-title">Reward points</p>
                                <p class="metric-value">{reward_points}</p>
                                <p class="metric-subtext">Current reward level: {reward_level}</p>
                            </div>
                            <div class="metric-card streak-card">
                                <p class="metric-title">Current streak</p>
                                <p class="metric-value">{streak_days} day{'s' if streak_days != 1 else ''}</p>
                                <p class="metric-time">Current time: {current_time}</p>
                                <p class="metric-subtext">Consecutive completion days.</p>
                            </div>
                        </div>
                    </div>
                    <div class="settings-panel">
                        <button type="button" id="toggle-settings" class="settings-button">Show / Hide Settings</button>
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
                    <table class="todo-table">
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
            </div>
        </body>
        </html>
        """

    return html


@route('/delete', method='POST')
def delete_item():
    """Used for deleting items from the to do list."""
    delid = request.forms.get('delitem')
    if delid:
        execute_query("DELETE FROM todo WHERE id = ?", (delid,))
    redirect('/')


@route('/toggle_complete', method='POST')
def toggle_complete():
    todo_id = request.forms.get('todo_id')
    if todo_id:
        row = execute_query("SELECT completed FROM todo WHERE id = ?", (todo_id,), fetch=True)
        if row:
            completed = row[0][0]
            if completed == 0:
                execute_query(
                    "UPDATE todo SET completed = 1, completed_date = ? WHERE id = ?",
                    (datetime.date.today().isoformat(), todo_id),
                )
            else:
                execute_query(
                    "UPDATE todo SET completed = 0, completed_date = '' WHERE id = ?",
                    (todo_id,),
                )
    redirect('/')


@route('/new', method='POST')
def new_item():
    newcat = request.forms.get('newcat')
    item = request.forms.get('item')
    due_date = request.forms.get('due_date')
    priority = request.forms.get('priority') or 'Normal'
    if newcat and item:
        execute_query(
            "INSERT INTO todo (category, item, due_date, priority, completed_date) VALUES (?, ?, ?, ?, '')",
            (newcat, item, due_date or '', priority),
        )
    redirect('/')


if __name__ == '__main__':
    ensure_db_schema()
    run(host='localhost', port=8080)
