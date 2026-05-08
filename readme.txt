# todo
This is my 'to do' list database for CT03 course

## Google Calendar Integration Setup

To enable Google Calendar integration:

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google Calendar API:
   - Go to "APIs & Services" > "Library"
   - Search for "Google Calendar API" and enable it
4. Create credentials:
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth 2.0 Client IDs"
   - Choose "Desktop application"
   - Download the credentials JSON file and rename it to `credentials.json`
   - Place it in the same directory as the Python files
5. Run the app and click "Sync All to Calendar" to authenticate

## Features
- Add todo items with categories
- Delete todo items
- Sync all todos to Google Calendar as events
- View upcoming calendar events