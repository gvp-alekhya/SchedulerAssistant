from datetime import datetime

from date_time_util import getISOString
GET_FREE_SLOTS = {
      "type": "function",
      "function": {
        "name": "get_free_slots",
        "description": "Get free slots for an appointment from a calendar. Business hours are only between 9AM to 6PM pST. And each appointment is for 45 minutes. As response you need to show time slots only between the business hours (9AM to 5PM) and later than the current user time",
        "parameters": {
          "type": "object",
          "properties": {
            "date": {
              "type": "string",
              "description": "For which date. Infer this as date time in ISO format based on the user input and his timezone. You should consider today as "+getISOString(datetime.now())
            },
          },
          "required": ["date"]
        }
      }
    }
BOOK_APPOINTMENT = {
    "type": "function",
    "function": {
        "name": "book_appointment",
        "description": "Book an appointment with optional recurrence.",
        "parameters": {
            "type": "object",
            "properties": {
                "time": {
                    "type": "string",
                    "description": "Time slot for the appointment. Should be in ISO format."
                },
                "recurrence": {
                    "type": "boolean",
                    "description": "Indicates whether the appointment is recurring."
                },
                "recurrence_rule": {
                    "type": "string",
                    "description": "Recurrence rule in iCalendar (RFC 5545) format. Required if 'recurrence' is true.USe the following example for reference 'FREQ=WEEKLY;BYDAY=MO;UNTIL=20240605T170000Z;'"
                },
                "days_of_week": {
                    "type": "array",
                    "items": {
                        "type": "string"
                    },
                    "description": "Days of the week for recurring appointments (e.g., ['MO', 'WE'] for Mondays and Wednesdays). Required if 'recurrence' is true."
                }
            },
            "required": ["time", "recurrence"]
        }
    }
}

UPCOMING_APPOINTMENTS = {
      "type": "function",
      "function": {
        "name": "upcoming_appointments",
        "description": "Show upcoming events for a calendar",
        "parameters": {
          "type": "object",
          "properties": {
            "upcoming_events": {
              "type": "string",
              "description": "show list of upcoming events. Display each event in a new line"
            },
          },
          "required": []}
      }
    }
CANCEL_APPOINTMENT = {
      "type": "function",
      "function": {
        "name": "cancel_appointment",
        "description": "Cancel an appointment for a calendar",
        "parameters": {
          "type": "object",
          "properties": {
            "time": {
              "type": "string",
              "description": "Date and Time slot for the appointment to be cancelled. Infer this as a date time in ISO based on the user input and his timezone"
            },

          },
          "required": ["time","timezone"]
        }
      }
    }
RESCHEDULE_APPOINTMENT = {
      "type": "function",
      "function": {
        "name": "reschedule_appointment",
        "description": "Reschedule an appointment for a later date on the calendar",
        "parameters": {
          "type": "object",
          "properties": {
            "newStartTime": {
              "type": "string",
              "description": "Rescheduled Date and Time slot for the new appointment. Infer this as a date time in ISO based on the user input and his timezone"
            },
              "oldStartTime": {
              "type": "string",
              "description": "Old Date and Time slot for the appointment to be rescheduled. Infer this as a date time in ISO based on the user input and his timezone"
            },

          },
          "required": ["newStartTime","oldStartTime"]
        }
      }
    }

FILE_SEARCH = {
    "type": "file_search",
}