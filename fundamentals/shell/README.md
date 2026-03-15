# Project 21: Shell

## Level 1: REPL + Built-in Commands

**Implement a basic shell (command-line interpreter):**

```
class Shell:
    __init__()
    run() -> None                           # start the REPL loop
    execute(command_line: str) -> str | None  # parse and execute a command

class CommandParser:
    parse(line: str) -> list[list[str]]     # split into commands + args
```

**Requirements:**
- Read-eval-print loop: display prompt, read input, execute, print output
- Parse command line into program + arguments: `ls -la /tmp` → `["ls", "-la", "/tmp"]`
- Handle quoted strings: `echo "hello world"` → `["echo", "hello world"]`
- Handle single quotes: `echo 'hello "world"'` preserves double quotes
- Built-in commands (implemented in Python, not via subprocess):
  - `cd <dir>` — change directory
  - `pwd` — print working directory
  - `echo <args>` — print arguments
  - `exit` — quit the shell
  - `export VAR=value` — set environment variable
- External commands: use `os.execvp` or `subprocess` to run programs

**Test Cases:**
```python
shell = Shell()
assert shell.execute("echo hello world") == "hello world"
assert shell.execute("pwd") == os.getcwd()

shell.execute("cd /tmp")
assert shell.execute("pwd") == "/tmp"

parser = CommandParser()
assert parser.parse('echo "hello world"') == [["echo", "hello world"]]
assert parser.parse("ls -la /tmp") == [["ls", "-la", "/tmp"]]
```

---

## Level 2: Pipes + Redirection

**Add I/O redirection and piping:**

```
class Pipeline:
    __init__(commands: list[list[str]])
    execute() -> str

class Redirector:
    parse_redirections(tokens: list[str]) -> tuple[list[str], dict]
    # Returns (clean_args, {"stdin": file, "stdout": file, "stderr": file, "append": bool})
```

**Requirements:**
- Pipe: `ls | grep foo | wc -l` — stdout of one becomes stdin of next
- Output redirect: `echo hello > file.txt` — write stdout to file
- Append redirect: `echo hello >> file.txt`
- Input redirect: `sort < file.txt` — read stdin from file
- Stderr redirect: `cmd 2> errors.txt`
- Combined: `cmd < input.txt | sort > output.txt`
- Implement pipes using `os.pipe()` — create file descriptors, fork processes, connect them
- Handle broken pipes gracefully

**Test Cases:**
```python
shell = Shell()
# Pipe
result = shell.execute("echo hello world | wc -w")
assert result.strip() == "2"

# Redirect (creates file)
shell.execute("echo hello > /tmp/test_shell_out.txt")
with open("/tmp/test_shell_out.txt") as f:
    assert f.read().strip() == "hello"

# Input redirect
shell.execute("echo 'banana\\napple\\ncherry' > /tmp/test_sort.txt")
result = shell.execute("sort < /tmp/test_sort.txt")
assert result.strip().split("\n") == ["apple", "banana", "cherry"]
```

---

## Level 3: Job Control

**Add background processes and job management:**

```
class JobManager:
    __init__()
    add_job(pid: int, command: str) -> int     # returns job number
    list_jobs() -> list[dict]
    foreground(job_num: int) -> None
    background(job_num: int) -> None
    wait(job_num: int) -> int                  # wait and return exit code
```

**Requirements:**
- Background execution: `sleep 10 &` — run in background, return to prompt
- `jobs` — list running/stopped background jobs with status
- `fg %1` — bring job 1 to foreground
- `bg %1` — resume stopped job in background
- Signal handling:
  - `Ctrl+C` (SIGINT) — interrupt foreground process, not the shell
  - `Ctrl+Z` (SIGTSTP) — stop foreground process, return to prompt
- Wait for background jobs to finish, report completion
- Track job status: running, stopped, done

**Test Cases:**
```python
jm = JobManager()
# Simulate adding a background job
job_id = jm.add_job(pid=12345, command="sleep 10")
assert job_id == 1

jobs = jm.list_jobs()
assert len(jobs) == 1
assert jobs[0]["status"] == "running"
```

---

## Level 4: Environment + Globbing

**Add variable expansion and filename globbing:**

```
class Expander:
    expand_variables(tokens: list[str], env: dict) -> list[str]
    expand_globs(tokens: list[str]) -> list[str]
    expand_home(token: str) -> str
```

**Requirements:**
- Variable expansion: `$HOME`, `$PATH`, `${VAR}`
- Command substitution: `echo $(date)` — execute inner command, use output
- Globbing: `ls *.py` expands to matching files in current directory
  - `*` matches any characters
  - `?` matches single character
  - `[abc]` matches character class
- Tilde expansion: `~/docs` → `/home/user/docs`
- `$?` — exit code of last command
- `$$` — PID of the shell
- Expansion order: variables → command substitution → globbing

**Test Cases:**
```python
exp = Expander()
env = {"HOME": "/home/alice", "USER": "alice"}

result = exp.expand_variables(["echo", "$HOME"], env)
assert result == ["echo", "/home/alice"]

result2 = exp.expand_variables(["echo", "${USER}_data"], env)
assert result2 == ["echo", "alice_data"]

result3 = exp.expand_home("~/docs")
assert result3 == "/home/alice/docs"

# Globbing (assuming *.py files exist in current dir)
expanded = exp.expand_globs(["ls", "*.py"])
assert all(f.endswith(".py") for f in expanded[1:])
```
