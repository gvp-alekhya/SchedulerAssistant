import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from datetime import timedelta,datetime

from configs import GOOGLE_CALENDAR_ID

class CalendarService:
    def __init__(self, client_secret_file, scopes, calendar_id):
        self.client_secret_file = client_secret_file
        self.scopes = scopes
        self.calendar_id = calendar_id
        self.calendar_service = self._build_calendar_service()

    def _build_calendar_service(self):
        flow = InstalledAppFlow.from_client_secrets_file(self.client_secret_file, self.scopes)
        credentials = flow.run_local_server()
        return build('calendar', 'v3', credentials=credentials)

    # TODO : Read summary,descritpion for every business form backend
    def book_appointment(self, start_time, recurrence=False, recurrence_rule=None):
        try:
            event = {
                'summary': 'Taxwise appointment',
                'location': '',
                'description': '',
                'start': {
                    'dateTime': start_time,
                    'timeZone': 'PST',
                },
                'end': {
                    'dateTime': (datetime.fromisoformat(start_time) + timedelta(hours=1)).isoformat(),
                    'timeZone': 'PST',
                },
            }

            if recurrence and recurrence_rule:
                event['recurrence'] = [f'RRULE:{recurrence_rule}']
       
            created_event = self.calendar_service.events().insert(calendarId=self.calendar_id, body=event).execute()
            return 'Appointment created: ' + created_event.get('htmlLink')

        except Exception as e:
            return f"Error booking appointment: {str(e)}"

    def get_free_slots(self, start):
        try:
            start_time = datetime.fromisoformat(start)
            end_time = start_time + timedelta(days=3)
            start_time_iso_format = start_time.isoformat() + 'Z'
            end_time_iso_format = end_time.isoformat() + 'Z'
            events_result = self._get_event_list(start_time_iso_format, end_time_iso_format, None)
            events = events_result.get('items', [])
            free_slots = []

            current_time = datetime.fromisoformat(start_time_iso_format)
            end_time = datetime.fromisoformat(end_time_iso_format)

            for event in events:
                event_start = event['start'].get('dateTime', event['start'].get('date'))
                event_end = event['end'].get('dateTime', event['end'].get('date'))
                event_start_time = datetime.fromisoformat(event_start)
                event_end_time = datetime.fromisoformat(event_end)

                if current_time < event_start_time:
                    free_slots.append({'start': current_time.isoformat(), 'end': event_start_time.isoformat()})

                current_time = event_end_time

            if current_time < end_time:
                free_slots.append({'start': current_time.isoformat(), 'end': end_time.isoformat()})
            
            formatted_slots = '\n'.join(f"{slot['start']} to {slot['end']}" for slot in free_slots)
            return formatted_slots
        except Exception as e:
            return f"Error retrieving free slots: {str(e)}"

    def find_event_by_datetime(self, start_time):
        end_datetime = start_time + timedelta(hours=1) 
        time_min = start_time.isoformat()
        time_max = end_datetime.isoformat() 
        try:
            events_result = self._get_event_list(time_min, time_max, None)
            events = events_result.get('items', [])
            
            if not events:
                return None
            else:
                for event in events:
                    event_start = event['start'].get('dateTime')
                    if event_start == start_time.isoformat():
                        return event

            return None
        except Exception as e:
            return f"An error occurred while fetching events: {str(e)}"

    def cancel_appointment(self, date_time):
        try:
            date_time = datetime.fromisoformat(date_time)
            event = self.find_event_by_datetime(date_time)
            if not event: 
                return 'No appointment matched for this date'
            
            self.calendar_service.events().delete(calendarId=self.calendar_id, eventId=event["id"]).execute()
            return "Appointment canceled successfully."
        except Exception as e:
            return f"Error canceling appointment: {str(e)}"

    def reschedule_appointment(self, old_start_time, new_start_time):
        try:
            old_start_time = datetime.fromisoformat(old_start_time)
            event = self.find_event_by_datetime(old_start_time)
            if not event:
                return 'No appointment found'
            
            event['start']['dateTime'] = new_start_time
            event['end']['dateTime'] = (datetime.fromisoformat(new_start_time) + timedelta(hours=1)).isoformat()

            updated_event = self.calendar_service.events().update(calendarId=self.calendar_id, eventId=event['id'], body=event).execute()
            return "Appointment rescheduled successfully."
        except Exception as e:
            return f"Error rescheduling appointment: {str(e)}"

    def _get_event_list(self, time_min, time_max, max_results):
        try:
            request_params = {
                'calendarId': self.calendar_id,
                'timeMin': time_min,
                'singleEvents': True,
                'orderBy': 'startTime'
            }
            if time_max:
                request_params["timeMax"] = time_max
            if max_results:
                request_params["maxResults"] = max_results
            return self.calendar_service.events().list(**request_params).execute()
        except Exception as e:
            return f"Error retrieving events list: {str(e)}"
             
    def build_recurrence_rule(user_input):
        # Example user input: "Schedule a weekly meeting every Monday and Wednesday at 10 AM for the next 4 weeks."

        # Default values (if not specified by user)
        frequency = 'WEEKLY'
        days_of_week = []  # List to store selected days of the week
        duration = 4  # Default duration (e.g., 4 occurrences)

        # Parse user input to extract recurrence-related details
        if 'daily' in user_input:
            frequency = 'DAILY'
        elif 'weekly' in user_input:
            frequency = 'WEEKLY'
        elif 'monthly' in user_input:
            frequency = 'MONTHLY'

        # Extract days of the week (e.g., "every Monday and Wednesday")
        if 'Monday' in user_input:
            days_of_week.append('MO')
        if 'Tuesday' in user_input:
            days_of_week.append('TU')
        if 'Wednesday' in user_input:
            days_of_week.append('WE')
        # Add more days as needed...

        # Determine recurrence end (e.g., "for the next 4 weeks")
        if 'weeks' in user_input:
            duration = 4  # Number of occurrences
        # Add logic to parse other duration formats (e.g., end date)

        # Construct recurrence rule in RFC 5545 format
        if days_of_week:
            recurrence_rule = f'RRULE:FREQ={frequency};BYDAY={",".join(days_of_week)};COUNT={duration}'
        else:
            recurrence_rule = f'RRULE:FREQ={frequency};COUNT={duration}'

        return recurrence_rule

    # Function to retrieve and display upcoming events
    def upcoming_events(self):
    
        # Define the current datetime to use as the start time
        now = datetime.now().isoformat() + 'Z'  # 'Z' indicates UTC time
        upcomingEvents = ''
        try:
            # Make a request to list upcoming events
            events_result = self.calendar_service.events().list(calendarId= self.calendar_id, timeMin=now,
                                                maxResults=10, singleEvents=True,
                                                orderBy='startTime').execute()
            events = events_result.get('items', [])
           
            if not events:
                return 'No upcoming events found.'
            else:
                for event in events:
                    start = event['start'].get('dateTime', event['start'].get('date'))
                    upcomingEvents += f"- {start} - {event['summary'] if event.get('summary') else 'Taxwise'}"

                return upcomingEvents
        except Exception as e:
            print(f"An error occurred: {e}")
            return upcomingEvents