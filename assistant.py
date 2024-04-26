from googleapiclient.discovery import build
from openai import OpenAI, AssistantEventHandler
from EventHandler import EventHandler
from Tools import *
from calendarEvents import *


# Set your OpenAI API key
openai_api_key = "YOUR_API_KEY"
openai_client = OpenAI(api_key=openai_api_key)
assistant = openai_client.beta.assistants.create(
    name="Calendar Assistant",
    instructions="You are an AI assistant for a business. You should read documents and provide answers, read and manage calendars, and help with any questions from customers.",
    model="gpt-4-turbo",
    tools=[BOOK_APPOINTMENT,GET_FREE_SLOTS, UPCOMING_APPOINTMENTS,CANCEL_APPOINTMENT, RESCHEDULE_APPOINTMENT]
)
# Create a new thread for the conversation
thread = openai_client.beta.threads.create()

# Start an interactive chat session
print("Welcome to the Calendar Assistant! You can ask me anything. Type 'exit' to end the conversation.")
while True:
    user_input = input("> ")
    if user_input.lower() == "exit":
        break
    else:
        # Send user input to the assistant
        message = openai_client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=user_input,
        )

        # Stream responses from the assistant
        with openai_client.beta.threads.runs.stream(
            thread_id=thread.id,
            assistant_id=assistant.id,
            instructions="Please address the user as Jane Doe. The user has a premium account.",
            event_handler=EventHandler(openai_client),
        ) as stream:
            for event in stream:
              stream.until_done()