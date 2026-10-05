"""Deterministic fault injection; no model or internet required."""
import json
from robust_agent import handle_tool_call

class FakeFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class FakeCall:
    def __init__(self, name, arguments, call_id="test_call"):
        self.id = call_id
        self.type = "function"
        self.function = FakeFunction(name, arguments)

FAULTS = [
    ("invalid JSON", FakeCall("get_event", '{"event_code":"DEVOPS"')),
    ("unknown tool", FakeCall("send_email", '{"to":"student@example.com"}')),
    ("missing argument", FakeCall("get_event", "{}")),
    ("wrong type", FakeCall("get_event", '{"event_code":101}')),
    ("outside enum", FakeCall("get_event", '{"event_code":"CLOUD","day":"holiday"}')),
    ("invented argument", FakeCall("get_event", '{"event_code":"CLOUD","room":"LAB-X"}')),
    ("unsafe expression", FakeCall(
        "calculate",
        json.dumps({"expression": "__import__('os').system('dir')"})
    )),
    ("array instead of object", FakeCall("calculate", '["100 + 50"]')),
    # Own design fault 1
    ("wrong-case tool name", FakeCall("GET_EVENT", '{"event_code":"DEVOPS"}')),
    # Own design fault 2
    ("empty arguments", FakeCall("calculate", "")),
]

if __name__ == "__main__":
    print("=" * 88)
    for label, call in FAULTS:
        result = handle_tool_call(call, log=False)
        print(f"{label:<24} -> {result[:100]}")
    print("=" * 88)
    print("All injected cases returned strings; no exception should stop the run.")
