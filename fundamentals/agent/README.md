# Project 24: Coding Agent

**Requires:** One API call to an LLM (Anthropic/OpenAI). Everything else is pure Python.

**Builds on:** AI Chatbot (Project 18), Sandbox (Project 15), RAG (Project 14)

**The lesson:** Everyone uses LangChain/CrewAI. The agent is just a while loop with tool dispatch. Build it from scratch to understand what's underneath.

## Level 1: Tool System

**Implement a tool definition and dispatch system:**

```
class Tool:
    name: str
    description: str
    parameters: dict          # JSON schema for parameters
    function: Callable

class ToolRegistry:
    register(tool: Tool) -> None
    get_tool(name: str) -> Tool | None
    to_api_format() -> list[dict]       # format for LLM API's tool parameter

class ToolCallParser:
    parse_response(response: dict) -> list[ToolCall]   # extract tool calls from LLM response
    format_result(tool_name: str, result: str) -> dict  # format result for next API call
```

**Requirements:**
- Define tools with name, description, parameter schema (JSON Schema format)
- `to_api_format()`: convert tools into the format the LLM API expects
- Parse tool calls from the LLM response (the API returns structured tool_use blocks)
- Execute the matching function with parsed arguments
- Format tool results to feed back into the conversation
- Handle tool not found, wrong arguments, execution errors
- No magic — you see exactly what goes to and from the API

**Test Cases:**
```python
registry = ToolRegistry()
registry.register(Tool(
    name="read_file",
    description="Read a file from disk",
    parameters={"path": {"type": "string", "description": "File path"}},
    function=lambda path: open(path).read()
))

api_tools = registry.to_api_format()
assert api_tools[0]["name"] == "read_file"

tool = registry.get_tool("read_file")
assert tool is not None
result = tool.function(path="/tmp/test.txt")

# Parse a mock LLM response with tool calls
parser = ToolCallParser()
mock_response = {"type": "tool_use", "name": "read_file", "input": {"path": "/tmp/test.txt"}}
calls = parser.parse_response(mock_response)
assert calls[0].name == "read_file"
```

---

## Level 2: Agent Loop (ReAct)

**Implement the core agent loop:**

```
class Agent:
    __init__(api_client, tools: ToolRegistry, system_prompt: str,
             max_turns: int = 10)
    run(task: str) -> AgentResult

class AgentResult:
    final_response: str
    tool_calls: list[dict]    # history of all tool calls made
    turns: int
    total_tokens: int
```

**Requirements:**
- The agent loop:
  1. Send messages + tools to LLM API
  2. If response is text → done, return final answer
  3. If response is tool_use → execute tool, append result, go to step 1
  4. Repeat until text response or max_turns reached
- This is the entire ReAct pattern — observe, think, act, repeat
- Track full conversation history (messages in, tool calls, tool results)
- Token counting: track usage per turn and total
- Max turns guard: prevent infinite loops
- Handle API errors: retry with backoff
- Log every turn: what the agent thought, what tool it called, what it got back

**Test Cases:**
```python
agent = Agent(api_client, tools, system_prompt="You are a helpful coding assistant.")

# Simple task that requires reading a file
result = agent.run("What's in /tmp/test.txt?")
assert result.final_response is not None
assert result.turns >= 1
assert any(tc["name"] == "read_file" for tc in result.tool_calls)

# Task that requires no tools
result2 = agent.run("What is 2+2?")
assert "4" in result2.final_response
assert result2.turns == 1  # no tools needed
```

---

## Level 3: Coding Tools

**Build the tools that make it a coding agent:**

```
class FileReadTool(Tool):     # read a file
class FileWriteTool(Tool):    # write/create a file
class FileEditTool(Tool):     # edit specific lines in a file
class RunCodeTool(Tool):      # execute code in sandbox (Project 15)
class GlobTool(Tool):         # find files by pattern
class GrepTool(Tool):         # search file contents
class BashTool(Tool):         # run shell commands (restricted)
```

**Requirements:**
- `FileReadTool`: read file contents, handle not found, support line ranges
- `FileWriteTool`: write content to file, create parent directories
- `FileEditTool`: find-and-replace in a file (like sed but safer)
  - Takes old_string and new_string, replaces exact match
  - Fails if old_string not found or not unique
- `RunCodeTool`: execute Python code using your Sandbox (Project 15)
  - Return stdout, stderr, exit code
  - Enforce timeout and memory limits
- `GlobTool`: find files matching a pattern (e.g., `**/*.py`)
- `GrepTool`: search for text across files
- `BashTool`: run shell commands with allowlist (no rm -rf, no sudo)
- Each tool has clear error messages the agent can understand and retry

**Test Cases:**
```python
# Setup a temp project directory
tools = build_coding_tools(workspace="/tmp/test-project")

# Write a file
write_tool = tools.get_tool("write_file")
write_tool.function(path="hello.py", content="print('hello')")

# Read it back
read_tool = tools.get_tool("read_file")
content = read_tool.function(path="hello.py")
assert "print('hello')" in content

# Run it
run_tool = tools.get_tool("run_code")
result = run_tool.function(code="print('hello')")
assert result["stdout"].strip() == "hello"

# Edit it
edit_tool = tools.get_tool("edit_file")
edit_tool.function(path="hello.py", old_string="hello", new_string="world")
content = read_tool.function(path="hello.py")
assert "print('world')" in content
```

---

## Level 4: Planning + Error Recovery

**Make the agent smarter with planning and self-correction:**

```
class PlanningAgent(Agent):
    __init__(..., planning: bool = True)
    run(task: str) -> AgentResult

class ErrorRecovery:
    __init__(max_retries: int = 3)
    wrap_tool_call(tool: Tool, args: dict) -> str   # execute with retry
    analyze_error(error: str, context: list[dict]) -> str  # suggest fix
```

**Requirements:**
- **Planning**: before executing, agent creates a step-by-step plan
  - Inject a planning prompt: "First, outline your approach. Then execute step by step."
  - Agent outputs a plan, then follows it
- **Error recovery**: when a tool call fails, agent gets the error and tries to fix it
  - Syntax error in generated code → agent reads the error, fixes the code
  - File not found → agent searches for the right file
  - Test failure → agent reads the test output, debugs the issue
- **Workspace awareness**: agent knows the project structure
  - On start, glob the workspace and provide a file tree
  - Agent can explore before coding
- **Conversation summary**: when context gets long, summarize earlier turns
- **Diff output**: after all changes, show a summary of what was modified

**Test Cases:**
```python
agent = PlanningAgent(api_client, tools,
    system_prompt="You are a coding agent. Plan before you act.")

# Task: create a function and test it
result = agent.run("""
Create a file called fizzbuzz.py with a fizzbuzz function,
then create test_fizzbuzz.py with tests, then run the tests.
""")

# Agent should have:
# 1. Created fizzbuzz.py
# 2. Created test_fizzbuzz.py
# 3. Run the tests
# 4. Fixed any failures
assert result.final_response is not None
assert any("write_file" in str(tc) for tc in result.tool_calls)
assert any("run_code" in str(tc) for tc in result.tool_calls)

# Error recovery: give it broken code to fix
result2 = agent.run("Fix the syntax error in /tmp/test-project/broken.py and run it")
assert result2.turns > 1  # needed multiple turns to diagnose and fix
```
