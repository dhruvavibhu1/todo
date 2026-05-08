"""
Google Calendar integration for Todo app
"""
import os
import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Get authenticated Google Calendar service"""
    creds = None
    # The file token.json stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # You need to download credentials.json from Google Cloud Console
            if not os.path.exists('credentials.json'):
                raise FileNotFoundError("credentials.json not found. Please download it from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    service = build('calendar', 'v3', credentials=creds)
    return service

def add_todo_to_calendar(category, item):
    """Add a todo item as a calendar event"""
    try:
        service = get_calendar_service()

        # Create event for tomorrow at 9 AM
        tomorrow = datetime.datetime.now() + datetime.timedelta(days=1)
        start_time = tomorrow.replace(hour=9, minute=0, second=0, microsecond=0)
        end_time = start_time + datetime.timedelta(hours=1)

        event = {
            'summary': f'{category}: {item}',
            'description': f'Todo item from {category} category',
            'start': {
                'dateTime': start_time.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_time.isoformat(),
                'timeZone': 'UTC',
            },
        }

        event = service.events().insert(calendarId='primary', body=event).execute()
        return f"Event created: {event.get('htmlLink')}"
    except Exception as e:
        return f"Error adding to calendar: {str(e)}"

def get_calendar_events():
    """Get upcoming calendar events"""
    try:
        service = get_calendar_service()

        # Get events from now to next week
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        week_later = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat() + 'Z'

        events_result = service.events().list(
            calendarId='primary', timeMin=now, timeMax=week_later,
            singleEvents=True, orderBy='startTime'
        ).execute()
        events = events_result.get('items', [])

        return events
    except Exception as e:
        return f"Error getting calendar events: {str(e)}"