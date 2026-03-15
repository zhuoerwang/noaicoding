# Project 15: Sandbox

## Level 1: Subprocess Runner with Restrictions

**Implement a basic code execution sandbox:**

```
class Sandbox:
    __init__(timeout: float = 5.0, max_memory_mb: int = 256)
    run(code: str, language: str = "python") -> ExecutionResult

class ExecutionResult:
    stdout: str
    stderr: str
    exit_code: int
    timed_out: bool
    runtime_ms: float
```

**Requirements:**
- Execute user code in a subprocess (not in the current process)
- Write code to a temp file, run with the language interpreter
- Enforce timeout: kill process after `timeout` seconds
- Capture stdout and stderr separately
- Measure execution time in milliseconds
- Handle crash/segfault: capture exit code
- Clean up temp files after execution

**Test Cases:**
```python
sb = Sandbox(timeout=5.0)
result = sb.run('print("hello")')
assert result.stdout.strip() == "hello"
assert result.exit_code == 0
assert result.timed_out is False

# Timeout
result = sb.run('import time; time.sleep(10)')
assert result.timed_out is True

# Error
result = sb.run('raise ValueError("oops")')
assert result.exit_code != 0
assert "ValueError" in result.stderr
```

---

## Level 2: Resource Limits

**Add resource restrictions:**

```
class Sandbox:
    __init__(timeout: float = 5.0, max_memory_mb: int = 256,
             max_output_bytes: int = 1_000_000,
             allowed_imports: list[str] | None = None)
```

**Requirements:**
- Memory limit: use `resource.setrlimit` (RLIMIT_AS) on the subprocess
- Output limit: truncate stdout/stderr if they exceed `max_output_bytes`
- Import restriction: scan code for import statements, reject disallowed modules
- Block dangerous modules by default: `os`, `subprocess`, `shutil`, `sys`, `socket`
- Process limit: prevent fork bombs with RLIMIT_NPROC
- Return clear error messages when limits are hit

**Test Cases:**
```python
sb = Sandbox(max_memory_mb=50)
# Memory bomb
result = sb.run('x = "a" * (100 * 1024 * 1024)')  # 100MB
assert result.exit_code != 0  # killed by memory limit

# Blocked import
sb2 = Sandbox(allowed_imports=["math", "json"])
result = sb2.run('import os; os.system("rm -rf /")')
assert result.exit_code != 0
assert "blocked" in result.stderr.lower() or result.exit_code != 0

# Output limit
sb3 = Sandbox(max_output_bytes=100)
result = sb3.run('print("x" * 10000)')
assert len(result.stdout) <= 100
```

---

## Level 3: Virtual Filesystem

**Add filesystem isolation:**

```
class Sandbox:
    __init__(..., filesystem: dict[str, str] | None = None)
    # filesystem: mapping of filename -> content to mount into sandbox
```

**Requirements:**
- Create a temp directory as the sandbox root
- Mount provided files into the sandbox directory
- User code can only access files within the sandbox root
- Prevent path traversal: reject `../` in filenames
- Clean up the entire sandbox directory after execution
- User code sees mounted files via normal `open()` calls

**Test Cases:**
```python
sb = Sandbox(filesystem={
    "data.csv": "name,age\nAlice,30\nBob,25",
    "config.json": '{"key": "value"}'
})
result = sb.run('''
with open("data.csv") as f:
    print(f.read())
''')
assert "Alice" in result.stdout

# Path traversal blocked
sb2 = Sandbox(filesystem={"../etc/passwd": "hacked"})
# Should raise or ignore the malicious path
```

---

## Level 4: Test Runner

**Build an auto-evaluation system (the core of noaicoding.com):**

```
class TestRunner:
    __init__(sandbox: Sandbox)
    run_tests(user_code: str, test_code: str) -> TestResult

class TestResult:
    passed: int
    failed: int
    errors: int
    details: list[dict]   # per-test: name, status, message
    total_runtime_ms: float
```

**Requirements:**
- Combine user code + test code into a single execution
- Parse test results from output (use pytest or a simple custom framework)
- Report per-test pass/fail with error messages
- Timeout applies to entire test suite
- Handle user code that breaks imports or has syntax errors
- Return structured results, not raw output

**Test Cases:**
```python
runner = TestRunner(Sandbox(timeout=10))
user_code = '''
def add(a, b):
    return a + b
'''
test_code = '''
assert add(1, 2) == 3
assert add(0, 0) == 0
assert add(-1, 1) == 0
'''
result = runner.run_tests(user_code, test_code)
assert result.passed == 3
assert result.failed == 0

# Buggy code
user_code_bad = '''
def add(a, b):
    return a - b  # bug!
'''
result = runner.run_tests(user_code_bad, test_code)
assert result.failed > 0
```
