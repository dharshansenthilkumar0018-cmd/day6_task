"""Compare free text, JSON mode and strict schema mode."""
import json
from config import client, MODEL, banner

SCHEMA = {
    "type": "object",
    "properties": {
        "event_code": {"type": "string"},
        "wants_discount": {"type": "boolean"},
        "needs_tool": {"type": "boolean"},
    },
    "required": ["event_code", "wants_discount", "needs_tool"],
    "additionalProperties": False,
}

QUESTION = "I want the DevOps bootcamp with a student discount. What event is that?"

def ask(response_format, label):
    print(f"\n--- {label} ---")
    try:
        reply = client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "Extract the request as JSON with keys event_code, "
                        "wants_discount and needs_tool. Reply with JSON only."
                    ),
                },
                {"role": "user", "content": QUESTION},
            ],
            temperature=0,
            response_format=response_format,
        )
        text = (reply.choices[0].message.content or "").strip()
        print("raw   :", text)
        print("parsed:", json.loads(text))
    except Exception as error:
        print(f"not supported / failed ({type(error).__name__}: {error})")

if __name__ == "__main__":
    banner("STRUCTURED OUTPUTS")
    ask(None, "1. No constraint")
    ask({"type": "json_object"}, "2. JSON mode")
    ask(
        {
            "type": "json_schema",
            "json_schema": {
                "name": "event_query",
                "schema": SCHEMA,
                "strict": True,
            },
        },
        "3. Schema mode (strict)",
    )
