
# Define an event handler for the assistant responses
import json
from openai import OpenAI, AssistantEventHandler
from typing_extensions import override

from calendarEvents import *


class EventHandler(AssistantEventHandler):
    def __init__(self, openai_client):
        super().__init__()
        self.openai_client = openai_client
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
          available_slots = get_free_slots(parsed_data['date'])
          tool_outputs.append({"tool_call_id": tool.id, "output": available_slots})

        if tool.function.name == "book_appointment":   
          parsed_data = json.loads(tool.function.arguments)
          status = book_appointment(parsed_data['time'])
          tool_outputs.append({"tool_call_id": tool.id, "output": status})
        
        if tool.function.name == "cancel_appointment":   
          parsed_data = json.loads(tool.function.arguments)
          status = cancel_appointment(parsed_data['time'])
          tool_outputs.append({"tool_call_id": tool.id, "output": status})
        
        if tool.function.name == "upcoming_appointments":   
          events = upcoming_events()
          tool_outputs.append({"tool_call_id": tool.id, "output": events})
        
        if tool.function.name == "reschedule_appointment": 
          parsed_data = json.loads(tool.function.arguments) 
          print (parsed_data) 
          events = reschedule_appointment(parsed_data["oldStartTime"], parsed_data["newStartTime"])
          tool_outputs.append({"tool_call_id": tool.id, "output": events})
        
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
          event_handler=EventHandler(self.openai_client),
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
