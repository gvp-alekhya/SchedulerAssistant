import datetime
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2 import service_account
from datetime import timedelta

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
    def book_appointment(self, start_time):
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
                    'dateTime': (datetime.datetime.fromisoformat(start_time) + timedelta(hours=1)).isoformat(),
                    'timeZone': 'PST',
                },
            }
            event = self.calendar_service.events().insert(calendarId=self.calendar_id, body=event).execute()
            return 'Appointment created: ' + event.get('htmlLink')
        except Exception as e:
            return f"Error booking appointment: {str(e)}"

    def get_free_slots(self, start):
        try:
            start_time = datetime.datetime.fromisoformat(start)
            end_time = start_time + timedelta(days=3)
            start_time_iso_format = start_time.isoformat() + 'Z'
            end_time_iso_format = end_time.isoformat() + 'Z'
            events_result = self._get_event_list(start_time_iso_format, end_time_iso_format, None)
            events = events_result.get('items', [])
            free_slots = []

            current_time = datetime.datetime.fromisoformat(start_time_iso_format)
            end_time = datetime.datetime.fromisoformat(end_time_iso_format)

            for event in events:
                event_start = event['start'].get('dateTime', event['start'].get('date'))
                event_end = event['end'].get('dateTime', event['end'].get('date'))
                event_start_time = datetime.datetime.fromisoformat(event_start)
                event_end_time = datetime.datetime.fromisoformat(event_end)

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
            date_time = datetime.datetime.fromisoformat(date_time)
            event = self.find_event_by_datetime(date_time)
            if not event: 
                return 'No appointment matched for this date'
            
            self.calendar_service.events().delete(calendarId=self.calendar_id, eventId=event["id"]).execute()
            return "Appointment canceled successfully."
        except Exception as e:
            return f"Error canceling appointment: {str(e)}"

    def reschedule_appointment(self, old_start_time, new_start_time):
        try:
            old_start_time = datetime.datetime.fromisoformat(old_start_time)
            event = self.find_event_by_datetime(old_start_time)
            if not event:
                return 'No appointment found'
            
            event['start']['dateTime'] = new_start_time
            event['end']['dateTime'] = (datetime.datetime.fromisoformat(new_start_time) + timedelta(hours=1)).isoformat()

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