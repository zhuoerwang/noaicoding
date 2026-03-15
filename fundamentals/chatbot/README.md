# Project 18: AI Chatbot

**Builds on:** BPE Tokenizer (Project 9), Transformer (Project 13), RAG (Project 14)

**Model is pluggable** — `model_fn: Callable` can be:
1. Your numpy Transformer from Project 13 (full from-scratch stack, but gibberish output)
2. A mock function (for testing the pipeline)
3. An API wrapper (for useful output — only if you want to demo)

This project teaches the **application layer**: conversation, streaming, tools, context management.

## Level 1: Conversation Manager

**Implement the conversation layer that sits on top of a language model:**

```
class Message:
    role: str          # "system", "user", "assistant"
    content: str
    timestamp: float

class Conversation:
    __init__(system_prompt: str = "")
    add_message(role: str, content: str) -> None
    get_messages() -> list[Message]
    format_prompt() -> str              # format full conversation into a prompt string
    clear() -> None
```

**Requirements:**
- Track multi-turn conversation history with roles
- System prompt is always the first message
- `format_prompt()` formats the full conversation into a single string for the model:
  ```
  System: You are a helpful assistant.
  User: What is Python?
  Assistant: Python is a programming language.
  User: Who created it?
  Assistant:
  ```
- Handle the chat template format (roles + content)
- Validate roles: only "system", "user", "assistant" allowed
- Prevent consecutive same-role messages (merge them)

**Test Cases:**
```python
conv = Conversation(system_prompt="You are a helpful assistant.")
conv.add_message("user", "Hello")
conv.add_message("assistant", "Hi! How can I help?")
conv.add_message("user", "What is Python?")

messages = conv.get_messages()
assert len(messages) == 4  # system + 3 messages
assert messages[0].role == "system"

prompt = conv.format_prompt()
assert "You are a helpful assistant" in prompt
assert prompt.endswith("Assistant:")  # ready for model to complete
```

---

## Level 2: Streaming Token Generation

**Implement streaming inference with a generate function:**

```
class ChatEngine:
    __init__(model_fn: Callable, tokenizer, max_tokens: int = 256)
    generate(conversation: Conversation) -> str           # full response
    generate_stream(conversation: Conversation) -> Iterator[str]  # token by token

class StopCriteria:
    __init__(stop_sequences: list[str], max_tokens: int)
    should_stop(generated_text: str, token_count: int) -> bool
```

**Requirements:**
- `model_fn`: any function that takes token IDs and returns logits (pluggable)
- `generate_stream()`: yield one token at a time (generator)
  - Tokenize prompt -> feed to model -> sample next token -> decode -> yield
  - Enables real-time streaming output like ChatGPT
- Stop criteria: stop on EOS token, max tokens, or stop sequences (e.g., `"User:"`)
- Temperature sampling: divide logits by temperature before softmax
- Top-k and top-p (nucleus) sampling
- Implement top-p from scratch: sort by probability, cumulative sum, cut off at p

**Test Cases:**
```python
# Mock model that always predicts the next token deterministically
def mock_model(token_ids):
    # Returns logits, simple predictable behavior
    logits = [0.0] * 100
    logits[42] = 10.0  # always predict token 42
    return logits

engine = ChatEngine(mock_model, tokenizer, max_tokens=5)
conv = Conversation()
conv.add_message("user", "Hi")

tokens = list(engine.generate_stream(conv))
assert len(tokens) <= 5  # respects max_tokens

# Stop sequence
stop = StopCriteria(stop_sequences=["User:"], max_tokens=100)
assert stop.should_stop("Hello User:", 5) is True
assert stop.should_stop("Hello", 5) is False
assert stop.should_stop("Hello", 100) is True  # max tokens
```

---

## Level 3: Tool Use / Function Calling

**Add the ability for the chatbot to call external tools:**

```
class Tool:
    __init__(name: str, description: str, parameters: dict,
             function: Callable)

class ToolRegistry:
    register(tool: Tool) -> None
    get_tool(name: str) -> Tool | None
    format_tool_descriptions() -> str     # for the system prompt

class ToolCallParser:
    parse(text: str) -> list[dict] | None   # extract tool calls from model output
    format_result(tool_name: str, result: Any) -> str
```

**Requirements:**
- Tools are defined with name, description, parameter schema, and a callable
- Tool descriptions are injected into the system prompt so the model knows about them
- Parse tool calls from model output using a structured format:
  ```
  <tool_call>{"name": "calculator", "arguments": {"expression": "2+2"}}</tool_call>
  ```
- Execute the tool, format the result, and feed it back into the conversation
- Handle tool errors gracefully (return error message to model)
- Support multiple tool calls in a single response
- The conversation flow: user -> model (tool call) -> tool result -> model (final answer)

**Test Cases:**
```python
def calculator(expression: str) -> str:
    return str(eval(expression))  # simplified

tools = ToolRegistry()
tools.register(Tool(
    name="calculator",
    description="Evaluate a math expression",
    parameters={"expression": "str"},
    function=calculator
))

parser = ToolCallParser()
text = 'Let me calculate that. <tool_call>{"name": "calculator", "arguments": {"expression": "2+2"}}</tool_call>'
calls = parser.parse(text)
assert len(calls) == 1
assert calls[0]["name"] == "calculator"

result = tools.get_tool("calculator").function(**calls[0]["arguments"])
assert result == "4"
```

---

## Level 4: Context Window Management

**Handle conversations that exceed the model's context window:**

```
class ContextManager:
    __init__(max_context_tokens: int, tokenizer,
             strategy: str = "sliding_window")
    fit_conversation(conversation: Conversation) -> list[Message]
    summarize(messages: list[Message]) -> Message

class ChatBot:
    __init__(engine: ChatEngine, tools: ToolRegistry | None = None,
             context_manager: ContextManager | None = None)
    chat(user_input: str) -> str
    chat_stream(user_input: str) -> Iterator[str]
    reset() -> None
```

**Requirements:**
- `ContextManager` trims conversation to fit within token budget
- Strategies:
  - `"sliding_window"`: keep system prompt + last N messages that fit
  - `"summarize"`: summarize older messages, keep recent ones verbatim
- System prompt is always preserved (never trimmed)
- Token counting: use tokenizer to count actual tokens, not characters
- `ChatBot`: full end-to-end chatbot wiring everything together
  - Manages conversation state
  - Calls context manager before each generation
  - Handles tool calls automatically (loop until final text response)
  - Supports streaming output

**Test Cases:**
```python
cm = ContextManager(max_context_tokens=100, tokenizer=mock_tokenizer,
                    strategy="sliding_window")
conv = Conversation(system_prompt="You are helpful.")
for i in range(50):
    conv.add_message("user", f"Message {i}")
    conv.add_message("assistant", f"Reply {i}")

trimmed = cm.fit_conversation(conv)
assert trimmed[0].role == "system"  # system prompt preserved
# Total tokens should be <= 100

# Full chatbot
bot = ChatBot(engine, tools, cm)
response = bot.chat("What is 2+2?")
assert isinstance(response, str)
assert len(response) > 0
```
