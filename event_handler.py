
# Define an event handler for the assistant responses
import json
from openai import Client, OpenAI, AssistantEventHandler
from typing_extensions import override

from calendar_service import *
from configs import *


class EventHandler(AssistantEventHandler):
    def __init__(self, openai_client, calendar_manager):
        super().__init__()
        self.openai_client = openai_client
        self.calendar_manager = calendar_manager
    @override
    def on_event(self, event):
      # Retrieve events that are denoted with 'requires_action'
      # since these will have our tool_calls
      if event.event == 'thread.run.requires_action':
        run_id = event.data.id  # Retrieve the run ID from the event data
        self.handle_requires_action(event.data, run_id)

    def handle_requires_action(self, data, run_id):
      tool_outputs = []

      for tool in data.required_action.submit_tool_outputs.tool_calls:
        
        if tool.function.name == "get_free_slots":
          parsed_data = json.loads(tool.function.arguments)
          available_slots = self.calendar_manager.get_free_slots(parsed_data['date'])
          tool_outputs.append({"tool_call_id": tool.id, "output": available_slots})

        elif tool.function.name == "book_appointment":
          parsed_data = json.loads( tool.function.arguments)
          status = self.calendar_manager.book_appointment(parsed_data['time'], parsed_data['recurrence'],parsed_data.get('recurrence_rule',None))
          tool_outputs.append({"tool_call_id": tool.id, "output": status})
        
        elif tool.function.name == "cancel_appointment":   
          parsed_data = json.loads(tool.function.arguments)
          status = self.calendar_manager.cancel_appointment(parsed_data['time'])
          tool_outputs.append({"tool_call_id": tool.id, "output": status})
        
        elif tool.function.name == "upcoming_appointments":   
          events = self.calendar_manager.upcoming_events()
          tool_outputs.append({"tool_call_id": tool.id, "output": events})
        
        elif tool.function.name == "reschedule_appointment": 
          parsed_data = json.loads(tool.function.arguments) 
          events = self.calendar_manager.reschedule_appointment(parsed_data["oldStartTime"], parsed_data["newStartTime"])
          tool_outputs.append({"tool_call_id": tool.id, "output": events})
        
        elif tool.function.name == "file_search":
          print ("file_search")
        
      # Submit all tool_outputs at the same time
      self.submit_tool_outputs(tool_outputs, run_id)

    def submit_tool_outputs(self, tool_outputs, run_id):
      # Initialize an empty string to accumulate the text deltas
      accumulated_text = ""

      # Use the submit_tool_outputs_stream helper
      with self.openai_client.beta.threads.runs.submit_tool_outputs_stream(
          thread_id=self.current_run.thread_id,
          run_id=self.current_run.id,
          tool_outputs=tool_outputs,
          event_handler=EventHandler(self.openai_client, self.calendar_manager),
      ) as stream:
          # Accumulate the text deltas
          for text in stream.text_deltas:
              accumulated_text += text

      # Print the accumulated text
      print(accumulated_text, end="", flush=True)
    @override
    def on_text_created(self, text) -> None:
        print(f"assistant: {text}", end="\n\n> ", flush=True)

    @override
    def on_text_delta(self, delta, snapshot):
        print(delta.value, end="", flush=True)

    def on_tool_call_created(self, tool_call):
        print(f"\nassistant > {tool_call.type}\n", flush=True)

    def on_tool_call_delta(self, delta, snapshot):
        if delta.type == "code_interpreter":
            if delta.code_interpreter.input:
                print(delta.code_interpreter.input, end="", flush=True)
            if delta.code_interpreter.outputs:
                print(f"\n\noutput >", flush=True)
                for output in delta.code_interpreter.outputs:
                    if output.type == "logs":
                        print(f"\n{output.logs}", flush=True)

    @override
    def on_message_done(self, message) -> None:
        # print a citation to the file searched
        message_content = message.content[0].text
        annotations = message_content.annotations
        citations = []
        for index, annotation in enumerate(annotations):
            message_content.value = message_content.value.replace(
                annotation.text, f"[{index}]"
            )
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = Client.files.retrieve(file_citation.file_id)
                citations.append(f"[{index}] {cited_file.filename}")

        print(message_content.value)
        print("\n".join(citations))