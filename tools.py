"""Day 6 Task: Campus event assistant tools and schemas."""
import ast
import operator

EVENTS = {
    "PYTHON": {"name": "Python Workshop", "room": "LAB-A", "fee": 100},
    "CLOUD": {"name": "Cloud Basics", "room": "LAB-B", "fee": 150},
    "DEVOPS": {"name": "DevOps Bootcamp", "room": "LAB-C", "fee": 200},
}

_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.USub: operator.neg,
}

def get_event(event_code: str, day: str = "weekday") -> str:
    """Look up a campus event."""
    event = EVENTS.get(event_code.strip().upper())
    if event is None:
        return f"Unknown event code: {event_code}. Valid codes: {', '.join(EVENTS)}."
    return f"{event['name']} | room={event['room']} | fee={event['fee']}"

def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _OPS:
        return _OPS[type(node.op)](_evaluate(node.operand))
    raise ValueError("Unsupported expression")

def calculate(expression: str) -> str:
    """Safely calculate a basic arithmetic expression without eval()."""
    try:
        return str(_evaluate(ast.parse(expression, mode="eval").body))
    except Exception as error:
        return f"Calculator error: {error}. Use only numbers and + - * / ( )."

TOOL_FUNCTIONS = {
    "get_event": get_event,
    "calculate": calculate,
}

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_event",
            "description": (
                "Look up one campus event. Valid codes: PYTHON, CLOUD, DEVOPS."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "event_code": {
                        "type": "string",
                        "description": "Event code such as DEVOPS",
                    },
                    "day": {
                        "type": "string",
                        "enum": ["weekday", "weekend"],
                        "description": "Whether the event is on a weekday or weekend",
                    },
                },
                "required": ["event_code"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Calculate one arithmetic expression using numbers, + - * / and brackets."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Arithmetic expression",
                    },
                },
                "required": ["expression"],
                "additionalProperties": False,
            },
        },
    },
]

SCHEMAS = {
    tool["function"]["name"]: tool["function"]["parameters"]
    for tool in TOOLS
}
