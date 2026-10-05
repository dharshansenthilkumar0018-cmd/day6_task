"""Schema validator for the Day 6 campus-event scenario."""

TYPES = {
    "string": str,
    "number": (int, float),
    "integer": int,
    "boolean": bool,
    "array": list,
    "object": dict,
}

def validate_arguments(arguments, schema):
    if not isinstance(arguments, dict):
        return "Arguments must be a JSON object."

    properties = schema.get("properties", {})

    for name in schema.get("required", []):
        if name not in arguments:
            return (
                f"Missing required argument '{name}'. "
                f"Expected: {', '.join(properties)}."
            )

    if schema.get("additionalProperties") is False:
        extra = [key for key in arguments if key not in properties]
        if extra:
            return (
                f"Unexpected argument(s): {', '.join(extra)}. "
                f"Allowed: {', '.join(properties)}."
            )

    for name, value in arguments.items():
        rule = properties.get(name, {})
        expected = TYPES.get(rule.get("type"))

        if rule.get("type") in {"number", "integer"} and isinstance(value, bool):
            return f"Argument '{name}' must be a {rule['type']}, but got bool."

        if expected and not isinstance(value, expected):
            return (
                f"Argument '{name}' must be a {rule['type']}, "
                f"but got {type(value).__name__}: {value!r}."
            )

        if "enum" in rule and value not in rule["enum"]:
            return (
                f"Argument '{name}' must be one of {rule['enum']}, "
                f"got {value!r}."
            )

    return None

if __name__ == "__main__":
    from tools import SCHEMAS
    schema = SCHEMAS["get_event"]

    cases = [
        {"event_code": "DEVOPS"},
        {"event_code": "CLOUD", "day": "weekend"},
        {},
        {"event_code": 101},
        {"event_code": "CLOUD", "day": "holiday"},
        {"event_code": "CLOUD", "room": "LAB-X"},
    ]

    print("=== VALIDATOR TESTS ===")
    for case in cases:
        print(f"{case!r:<55} -> {validate_arguments(case, schema) or 'OK'}")
