# Day 6 Task — Reliable Tool Calling

## Scenario

I chose a **Campus Event Assistant**. The assistant can look up a campus event and calculate fees. The two tools are `get_event` and `calculate`. The event data is intentionally small so the important part of the task remains reliability rather than application size.

The available event codes are PYTHON, CLOUD and DEVOPS. The event lookup also has a `day` field whose allowed values are `weekday` and `weekend`. The schemas use `required`, `additionalProperties: false`, and an enum.

## 1. Explanation of Concepts

### Chat Completions format

Chat Completions sends a request containing a model, a list of messages and, when tools are available, a tools list. Other controls used in this project include temperature and max_tokens. A response contains choices; each choice has a message and a finish_reason.

In this project, `finish_reason` is important. `stop` means the model completed its answer normally, so the code can return the content. `tool_calls` means the model wants the program to execute one or more functions, so the loop processes the calls and sends tool messages back. `length` means generation stopped because the token limit was reached. The agent responds by increasing max_tokens and retrying, up to its limit.

`message.content` can be empty when the model wants a tool because the useful output is represented by `message.tool_calls` rather than ordinary natural-language content.

### OpenAI-compatible servers

An OpenAI-compatible server exposes an API shape that the OpenAI Python client can communicate with. The same client can therefore be pointed at different providers by changing the base URL and API key/configuration. In this project `config.py` selects Ollama, Groq or Hugging Face from `.env`.

Compatibility does not promise that every model or server supports every feature equally. In particular, tool calling and strict schema response formats can vary between providers and models.

### Streaming and Responses API

Streaming sends generated output incrementally instead of waiting for the complete response. This improves responsiveness and lets a user see output sooner. Inside an agent loop, streaming is usually switched off because the program needs the complete tool-call information before it can reliably validate and execute the call.

The Responses API style uses a different response/event structure and is designed around response items rather than the exact Chat Completions message format used here. This course stays on Chat Completions because the lab and earlier agent are built around that format and it clearly exposes messages, tool calls and finish reasons.

### Five steps of a tool call

1. The program sends messages and the tool definitions to the model.
2. The model returns a tool call containing a tool name and generated argument text.
3. The program parses the argument text and checks the tool name and schema.
4. The program executes the Python function and creates a tool message containing the result.
5. The program sends that result back to the model, which can make another tool call or produce the final answer.

The **code**, not the model, actually runs the function. This matters because the arguments arriving from the model are generated text and must never be treated as trusted input.

### Tool-definition parts

The description tells the model what the tool does and helps it choose the tool. `properties` describes individual arguments and their types. `enum` restricts a value to an allowed list. `required` prevents an important argument from being omitted. `additionalProperties: false` rejects invented arguments.

The scenario uses all of these. For example, `day` can only be `weekday` or `weekend`, so a value such as `holiday` is rejected. An extra `room` argument is rejected because the schema does not define it.

The strict setting is useful when supported because it asks the provider to follow the schema more strictly. Validation in our own Python code is still required.

For `tool_choice`, `auto` lets the model decide whether to call a tool, `none` prevents tool calls, `required` requires a tool call, and a named function asks for a particular function. For this assistant, `auto` is the best default because some questions need a tool and some, such as a greeting, do not.

### JSON mode vs schema mode

JSON mode asks for valid JSON but does not necessarily enforce the exact fields and types required by the application. Schema mode provides a specified JSON schema, so the result is constrained to the requested shape when the provider supports it.

In this scenario I use tools when the assistant needs to fetch event information or perform a calculation. I use structured output when the task is to extract fields from a user's sentence, such as `event_code`, `wants_discount` and `needs_tool`.

Even perfectly shaped JSON does not guarantee a correct answer. A model can put a wrong but correctly typed value into a valid field. Shape validation is not the same thing as factual correctness.

### Parallel tool calls

Parallel tool calls happen when one model response contains two or more tool calls. The loop must process every call and append exactly one tool message for every `tool_call_id`.

A useful parallel question in this scenario is: **"What are the DevOps and Cloud event fees together?"** The model can request both event lookups in the same response and then use the calculator.

If one tool-call ID is left unanswered, the conversation can become invalid for APIs that require every call to receive a corresponding tool result.

### Failures handled

The project handles invalid JSON, unknown tools, missing arguments, wrong argument types, values outside an enum, invented arguments, truncated replies, repeated identical calls, and tool execution errors.

Invalid JSON is returned as an argument error. An unknown tool produces a message listing available tools. A missing argument is reported by the validator. A wrong type is rejected. An enum violation shows the allowed values. An invented argument is rejected because `additionalProperties` is false. A truncated response causes a retry with a larger token limit. Repeated identical calls are counted and stopped after three occurrences.

### Repair pattern

The repair pattern is to convert failures into useful messages that the model can read and potentially correct. Every stage returns a string instead of raising because an exception would stop the agent loop and prevent the model from receiving the information needed to repair its call.

A truncated response is retried with more tokens because the problem is insufficient generation space. A malformed tool call is instead sent back as an error message because the model needs to generate a corrected call.

### Fault injection

Fault injection means deliberately constructing bad tool calls and passing them directly to the handler. It needs no model and no internet because the test is checking our Python validation and execution boundary rather than model generation.

This shows that many important agent bugs live in the application/tool boundary: parsing, validation, routing, execution and message bookkeeping.

A stricter schema can prevent an invented argument such as `room="LAB-X"` or an enum value such as `day="holiday"`. A schema cannot by itself guarantee that the model selected the correct event or that a tool's external data is factually correct.

## 2. Tool Calling vs Structured Outputs

| Basis for comparison | Tool calling | Structured outputs |
|---|---|---|
| What the model is asked to do | Request a function/action | Return data in a defined shape |
| Who performs the action or produces the final data | Python code performs the tool action | Model produces the structured data |
| How the shape of the result is controlled | Tool parameters are defined by schema and validated by code | JSON mode or JSON schema controls response shape |
| What can still go wrong | Bad JSON, wrong tool, bad arguments, repeated calls, tool failure | Correct shape but incorrect values; provider may not support strict schema |
| How your code guards against it | Parse, lookup, validate, execute, retry and repeat detection | Parse JSON and validate/use the extracted fields |
| Support across servers and models | Varies by provider/model | JSON/schema support also varies |
| Your choice if the task is to fetch or calculate something, and why | **Tool calling** — Python must perform the lookup/calculation | Structured output alone cannot perform the action |
| Your choice if the task is to pull fields out of a sentence, and why | Tool is unnecessary | **Structured output** — the application needs predictable fields |

## 3. Observation

### Fault table

| Injected fault | Message returned | Did the run continue? |
|---|---|---|
| Invalid JSON | `Argument error: invalid JSON ...` | Y |
| Unknown tool | `Unknown tool: send_email. Available tools: get_event, calculate.` | Y |
| Missing argument | `Argument error: Missing required argument 'event_code'...` | Y |
| Wrong type | `Argument error: Argument 'event_code' must be a string...` | Y |
| Value outside enum | `Argument error: Argument 'day' must be one of ['weekday', 'weekend']...` | Y |
| Invented argument | `Argument error: Unexpected argument(s): room...` | Y |
| Unsafe expression | `Calculator error: Unsupported expression...` | Y |
| JSON array instead of object | `Argument error: Arguments must be a JSON object.` | Y |
| Own fault 1: wrong-case tool | `Unknown tool: GET_EVENT...` | Y |
| Own fault 2: empty arguments | Missing required `expression` | Y |

### Agent behaviour

The exact number of steps and the exact wording are model/provider-dependent, so these are recorded after running the scripts against the configured provider.

| Question | Expected observation |
|---|---|
| What is the fee for the DevOps bootcamp? | One `get_event` call, then final answer |
| What are DevOps and Cloud fees together? | Two event calls may arrive in parallel, followed by `calculate` |
| What is the fee for HOLIDAY? | Invalid/unknown value is handled without crashing |
| Write a one-line welcome message | No tool should be necessary |
| Parallel calls | Possible on models that support parallel tool calling |
| `finish_reason = length` | Only occurs if the provider/model actually truncates a response |

### Before and after guards

Without guards, malformed tool arguments can reach Python execution and an unexpected exception can terminate the agent. With the guards, the same failure becomes a model-readable error string and the loop can continue.

The guarded version also has explicit repeat detection and a maximum step count, so a model cannot remain in an endless identical-call loop.

### Structured outputs

The `structured_demo.py` script runs three cases:
1. No response constraint.
2. JSON mode.
3. Strict JSON schema mode.

The actual result is provider-dependent. The script records the raw response, parsed JSON, or the provider error. This is intentional because the task asks for an observation of what the selected provider really supports.

## 4. Suitability and Conclusion

The most important distinction is that a model's tool call is generated text, not a trusted function invocation. The model proposes the function name and arguments; the application decides whether the proposal is valid and whether the function should actually run.

Every tool-calling loop should therefore inspect every reply, parse every argument payload, verify that the tool exists, validate its arguments, execute the tool safely, return one tool message per call ID, and stop or retry when progress is impossible.

Schemas prevent structural mistakes such as missing required fields, invented fields, incorrect types and invalid enum values. They cannot guarantee that the model understood the user's intent or that the underlying tool result is correct.

Deliberate fault injection is stronger than simply waiting for a model to fail because it is deterministic, repeatable and does not require a model or internet connection. The same guard can be tested every time code changes.

For this campus-event scenario, **tool calling** is the correct choice for event lookups and calculations because the program needs to perform those operations. **Structured outputs** are better when the job is only to extract predictable fields from a sentence.

The single most important guard is validation before execution. It creates a clear trust boundary between model-generated text and application code. Combined with retry, repeat detection and fault injection, it turns an agent from a loop that works only when the model behaves into a system that is designed to recover when the model does not.
