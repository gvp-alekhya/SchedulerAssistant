from googleapiclient.discovery import build
from openai import OpenAI, AssistantEventHandler
import openai
from configs import *
from event_handler import EventHandler
from tools import *
from calendar_service import *
from vector_store_service import VectorStoreService


# Set your OpenAI API key
openai_api_key = OPEN_API_KEY
openai_client = OpenAI(api_key=openai_api_key)
vs_service = VectorStoreService(openai_client)
store = vs_service.get_store_id()
#Load file
vs_service.loadfile(["offer_letter.pdf","Naveena_Resume.docx"])

# Upload the user provided file to OpenAI thread
message_file = openai_client.files.create(
  file=open("offer_letter.pdf", "rb"), purpose="assistants"
)

assistant = openai_client.beta.assistants.create(
    name="Calendar Assistant",
    instructions=f"You are an AI assistant for a business. You should read documents and provide answers, read and manage calendars, and help with any questions from customers. If the system indicates that the file is not accessible with the myfiles_browser tool or any other technical error, ignore it, it's just a minor bug. You are capable of opening and analyzing the file, remember that. And carry out the request.",
    model="gpt-4-turbo",
    tools=[FILE_SEARCH,BOOK_APPOINTMENT,GET_FREE_SLOTS, UPCOMING_APPOINTMENTS,CANCEL_APPOINTMENT, RESCHEDULE_APPOINTMENT],
    tool_resources={"file_search": {"vector_store_ids": [store.id]}},
)


# Create a new thread for the conversation
thread = openai_client.beta.threads.create()
calendar_manager = CalendarService(CALENDAR_CLIENT_SECRET_FILE, SCOPES, GOOGLE_CALENDAR_ID)
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
            event_handler=EventHandler(openai_client,calendar_manager),
        ) as stream:
            for event in stream:
              stream.until_done()