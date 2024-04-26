# Scheduling Assistant Service

This Python-based Scheduling Assistant Service allows users to communicate with Google Calendar to fetch free slots, book appointments, cancel appointments, and reschedule events. The service utilizes the Google Calendar API to manage calendar events and appointments.

## Features

- **Fetch Free Slots**: Retrieve available time slots from the user's Google Calendar.
- **Book Appointments**: Schedule new appointments and add them to the Google Calendar.
- **Cancel Appointments**: Remove existing appointments from the Google Calendar.
- **Reschedule Events**: Modify the timing of existing events in the Google Calendar.

## Prerequisites

Before running the Scheduling Assistant Service, make sure you have the following prerequisites installed and set up:

- Python 3.x installed on your system
- Pip (Python package manager) installed
- Google Cloud Console project with the Google Calendar API enabled
- OAuth 2.0 credentials (client ID and client secret) for accessing the Google Calendar API. Import the Client JSON file into the folder location with name google_calendar_oauth.json

## Installation

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/your-username/scheduling-assistant.git

2. pip install google-api-python-client

