import datetime
import json
from googleapiclient.discovery import build
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from datetime import datetime, timedelta
from googleapiclient.errors import HttpError


# Set up Google Calendar API
API_KEY = 'AIzaSyD751ptKOdLw5a3OKBprw9gIrW8ctcKlp8'
CLIENT_SECRETS_FILE = 'google_calendar_oauth.json'
SCOPES = ['https://www.googleapis.com/auth/calendar']
GOOGLE_CALENDAR_ID = "f6e57b46f9b8d75338685c0977256c06714de28ccf4bc3bfd67efbdb97f61a79@group.calendar.google.com"

# Perform OAuth 2.0 authorization
flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
credentials = flow.run_local_server()
SERVICE_NAME = 'calendar'
SERVICE_VERSION = 'v3'
calendar_service = build(SERVICE_NAME, SERVICE_VERSION, credentials=credentials)

def book_appointment(start_time):
    
    event = {
        'summary': 'Taxwise appointment',
        'location': '',
        'description': '',
        'start': {
            'dateTime': start_time,
            'timeZone': 'PST', 
        },
        'end': {
            'dateTime': datetime.isoformat(datetime.fromisoformat(start_time) + timedelta(hours=1)),
            'timeZone': 'PST',  
        },
    }
    event = calendar_service.events().insert(calendarId= GOOGLE_CALENDAR_ID, body=event).execute()
    print('Appointment created: %s' % event.get('htmlLink'))
    return 'Appointment created:' + event.get('htmlLink')


def get_free_slots(start):
    start_time = datetime.fromisoformat(start)
    end_time = start_time + timedelta(days=1)
    print(start_time.isoformat() + 'Z', end_time.isoformat() + 'Z')
    # Retrieve events for the specified day
    events_result = calendar_service.events().list(
        calendarId=GOOGLE_CALENDAR_ID,
        timeMin=start_time.isoformat() +'Z',
        timeMax=end_time.isoformat()+'Z',
        singleEvents=True,
        orderBy='startTime',
        timeZone="PST"
    ).execute()
    events = events_result.get('items', [])
    free_slots = []

    # Determine free slots based on retrieved events
    current_time = datetime.fromisoformat(start_time.isoformat() +'Z' )
    end_time = datetime.fromisoformat(end_time.isoformat() +'Z')
    for event in events:
        event_start = event['start'].get('dateTime', event['start'].get('date'))
        event_end = event['end'].get('dateTime', event['end'].get('date'))

        # Convert event_start and event_end to datetime objects
        event_start_time = datetime.fromisoformat(event_start)
        event_end_time = datetime.fromisoformat(event_end)

        # Check for free slots before the current event
        if current_time < event_start_time:
            free_slots.append({'start': current_time.isoformat(), 'end': event_start_time.isoformat()})

        current_time = event_end_time

    # Check for free slots after the last event
    if current_time <  end_time:
        free_slots.append({'start': current_time.isoformat(), 'end': end_time.isoformat()})
    
    formatted_slots = ''
    for slot in free_slots:
              # Extract start and end times
              start_time = slot['start']
              end_time = slot['end']
              
              # Format the slot nicely
              formatted_slot = f"{start_time} to {end_time}\n"
              
              # Append the formatted slot to the final string
              formatted_slots += formatted_slot
    
    return (formatted_slots)

# Function to retrieve and display upcoming events
def upcoming_events():

    # Define the current datetime to use as the start time
    now = datetime.utcnow().isoformat() + 'Z'  
    print(now)
    try:
        # Make a request to list upcoming events
        events_result = calendar_service.events().list(calendarId=GOOGLE_CALENDAR_ID, timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])
        print (events)
        upcomingEvents = ''
        if not events:
            return ('No upcoming events found.')
        else:
            upcomingEvents += 'Upcoming events:\n'
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                summary =  'Taxwise'
                upcomingEvents += f"- {start} - {summary}\n"

            return upcomingEvents

    except Exception as e:
        return f"An error occurred while fetching events: {str(e)}"

def find_event_by_datetime( start_time):

    # Define the end datetime by adding a small delta (e.g., 1 minute) to the start datetime
    end_datetime = start_time + timedelta(hours=1)  
    time_min = start_time.isoformat()
    time_max = end_datetime.isoformat()
    print (time_max , time_min)
    try:
        # Make a request to list events within the specified time range
        events_result = calendar_service.events().list(
            calendarId=GOOGLE_CALENDAR_ID,
            timeMin=time_min,
            timeMax=time_max,
            singleEvents=True,
        ).execute()
        print (events_result)
        events = events_result.get('items', [])
        
        if not events:
            return None  # No events found at the specified datetime
        else:
            # Filter events to find the exact event matching the start datetime
            for event in events:
                event_start = event['start'].get('dateTime')
                print (event_start)
                if event_start == start_time.isoformat():
                    return event  # Return the matching event

        return None  # No exact match found

    except Exception as e:
        return f"An error occurred while fetching events: {str(e)}"


# Function to cancel an appointment
def cancel_appointment(date_time):
   
    date_time = datetime.fromisoformat(date_time)
    event = find_event_by_datetime(date_time)
    print( event)
    if not event: 
        return 'No appointment matched for this date'
    # Delete the event
    
    calendar_service.events().delete(calendarId=GOOGLE_CALENDAR_ID, eventId=event["id"]).execute()
    return "Appointment canceled successfully."

# Function to reschedule an appointment
def reschedule_appointment( old_start_time,new_start_time):
    print (old_start_time)
    old_start_time = datetime.fromisoformat(old_start_time)
    print (old_start_time)  
    event = find_event_by_datetime(old_start_time)
    print (event)
    if not event:
        return 'No appointment found'
    # Update the event with new start and end times
    event = calendar_service.events().get(calendarId=GOOGLE_CALENDAR_ID, eventId=event["id"]).execute()
    event['start']['dateTime'] = new_start_time
    event['end']['dateTime'] = datetime.isoformat(datetime.fromisoformat(new_start_time) + timedelta(hours =1))

    updated_event = calendar_service.events().update(calendarId=GOOGLE_CALENDAR_ID, eventId=event['id'], body=event).execute()
    return "Appointment rescheduled successfully."
