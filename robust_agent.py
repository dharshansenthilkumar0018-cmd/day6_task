"""Reliable tool-calling agent for a campus event scenario."""
import json
from config import client, MODEL, banner
from tools import TOOLS, TOOL_FUNCTIONS, SCHEMAS
from validate import validate_arguments

SYSTEM_PROMPT = (
    "You are a campus event assistant. Use get_event to look up event details. "
    "Use calculate for every arithmetic step. Valid event codes are PYTHON, CLOUD, DEVOPS. "
    "If no tool is needed, answer directly."
)

MAX_TOKENS = 500
REPEAT_LIMIT = 3

def handle_tool_call(call, log=True):
    name = call.function.name
    raw = call.function.arguments or "{}"

    try:
        arguments = json.loads(raw)
    except json.JSONDecodeError as error:
        return f"Argument error: invalid JSON ({error}). Send valid JSON for '{name}'."

    function = TOOL_FUNCTIONS.get(name)
    if function is None:
        return f"Unknown tool: {name}. Available tools: {', '.join(TOOL_FUNCTIONS)}."

    problem = validate_arguments(arguments, SCHEMAS[name])
    if problem:
        return f"Argument error: {problem}"

    try:
        result = str(function(**arguments))
    except Exception as error:
        result = f"Tool error in {name}: {type(error).__name__}: {error}"

    if log:
        print(f"      {name}({arguments}) -> {result[:120]}")
    return result

def agent(question, max_steps=6, verbose=True):
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    seen = {}
    max_tokens = MAX_TOKENS

    for step in range(1, max_steps + 1):
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=TOOLS,
            temperature=0,
            max_tokens=max_tokens,
        )

        choice = response.choices[0]
        message = choice.message

        if choice.finish_reason == "length":
            if max_tokens >= 2000:
                return "Stopped: reply was still truncated at 2000 tokens."
            max_tokens *= 2
            if verbose:
                print(f"   step {step}: truncated; retrying with max_tokens={max_tokens}")
            continue

        if not message.tool_calls:
            return (message.content or "").strip()

        messages.append({
            "role": "assistant",
            "content": message.content or "",
            "tool_calls": [
                {
                    "id": c.id,
                    "type": "function",
                    "function": {
                        "name": c.function.name,
                        "arguments": c.function.arguments,
                    },
                }
                for c in message.tool_calls
            ],
        })

        if verbose:
            print(f"   step {step}: {len(message.tool_calls)} tool call(s)")

        for call in message.tool_calls:
            signature = (call.function.name, call.function.arguments)
            seen[signature] = seen.get(signature, 0) + 1

            if seen[signature] >= REPEAT_LIMIT:
                return (
                    f"Stopped: {call.function.name} was called {REPEAT_LIMIT} "
                    "times with the same arguments and made no progress."
                )

            result = handle_tool_call(call, log=verbose)
            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": result,
            })

    return "Stopped: maximum steps reached without a final answer."

if __name__ == "__main__":
    banner("CAMPUS EVENT AGENT")
    questions = [
        "What is the fee for the DevOps bootcamp?",
        "What are the DevOps and Cloud event fees together?",
        "What is the fee for HOLIDAY?",
        "Write a one-line welcome message for event participants.",
    ]

    for q in questions:
        print("\nQ:", q)
        try:
            print("A:", agent(q))
        except Exception as error:
            print(f"Agent error: {type(error).__name__}: {error}")
