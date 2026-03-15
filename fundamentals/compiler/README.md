# Project 29: Compiler

## Level 1: Lexer + Parser → AST

**Implement a compiler for a simple language (MiniLang):**

```
class Token:
    type: str       # "INT", "FLOAT", "STRING", "IDENT", "PLUS", "IF", "FN", etc.
    value: Any
    line: int
    col: int

class Lexer:
    __init__(source: str)
    tokenize() -> list[Token]

class Parser:
    __init__(tokens: list[Token])
    parse() -> AST

# AST Nodes
class NumberLiteral:    value: float
class StringLiteral:    value: str
class BinaryOp:         left: AST, op: str, right: AST
class Variable:         name: str
class Assignment:       name: str, value: AST
class IfStatement:      condition: AST, then_body: list[AST], else_body: list[AST]
class WhileLoop:        condition: AST, body: list[AST]
class FunctionDef:      name: str, params: list[str], body: list[AST]
class FunctionCall:     name: str, args: list[AST]
class ReturnStatement:  value: AST
class Program:          statements: list[AST]
```

**MiniLang syntax:**
```
// Variables and expressions
let x = 10
let y = x + 5 * 2

// Functions
fn add(a, b) {
    return a + b
}

// Control flow
if x > 5 {
    print(x)
} else {
    print(0)
}

while x > 0 {
    x = x - 1
}

// Function calls
let result = add(3, 4)
print(result)
```

**Requirements:**
- Lexer: tokenize MiniLang source into tokens
- Handle: integers, floats, strings, identifiers, operators, keywords
- Keywords: `let`, `fn`, `if`, `else`, `while`, `return`, `print`, `true`, `false`
- Operators: `+`, `-`, `*`, `/`, `%`, `==`, `!=`, `<`, `>`, `<=`, `>=`, `&&`, `||`, `!`
- Parser: recursive descent, produce an AST
- Operator precedence: `||` < `&&` < comparison < `+/-` < `*/ %` < unary
- Clear error messages: `"Line 5, col 12: Expected ')' after function arguments"`

**Test Cases:**
```python
lexer = Lexer("let x = 10 + 20")
tokens = lexer.tokenize()
assert tokens[0].type == "LET"
assert tokens[1].type == "IDENT"
assert tokens[1].value == "x"

parser = Parser(tokens)
ast = parser.parse()
assert isinstance(ast.statements[0], Assignment)
assert isinstance(ast.statements[0].value, BinaryOp)
assert ast.statements[0].value.op == "+"

# Function definition
ast2 = Parser(Lexer("fn add(a, b) { return a + b }").tokenize()).parse()
assert isinstance(ast2.statements[0], FunctionDef)
assert ast2.statements[0].params == ["a", "b"]
```

---

## Level 2: Tree-Walk Interpreter

**Execute the AST directly by walking it:**

```
class Environment:
    __init__(parent: Environment | None = None)
    get(name: str) -> Any
    set(name: str, value: Any) -> None
    define(name: str, value: Any) -> None

class Interpreter:
    __init__()
    execute(program: Program) -> Any
    eval(node: AST, env: Environment) -> Any
```

**Requirements:**
- Walk the AST node by node, evaluate each node
- `Environment`: variable scoping with parent chain (lexical scope)
  - Function bodies get a new environment with parent = definition scope
  - Inner scopes can read outer variables (closures)
- Type coercion: `"hello" + " world"` = string concat, `3 + 4` = arithmetic
- Runtime errors with clear messages: `"Line 5: Division by zero"`, `"Undefined variable 'x'"`
- Built-in functions: `print()`, `len()`, `type()`, `str()`, `int()`
- Truthiness: `0`, `""`, `false`, `null` are falsy, everything else truthy
- Return values: `return` unwinds the call stack (use exceptions internally)

**Test Cases:**
```python
interp = Interpreter()

# Arithmetic
result = interp.execute(parse("let x = 10 + 20\nprint(x)"))
# Should print 30

# Functions
code = """
fn fibonacci(n) {
    if n <= 1 { return n }
    return fibonacci(n - 1) + fibonacci(n - 2)
}
print(fibonacci(10))
"""
result = interp.execute(parse(code))
# Should print 55

# Closures
code2 = """
fn make_counter() {
    let count = 0
    fn increment() {
        count = count + 1
        return count
    }
    return increment
}
let counter = make_counter()
print(counter())
print(counter())
"""
# Should print 1, then 2

# Scoping
code3 = """
let x = "outer"
fn inner() { print(x) }
inner()
"""
# Should print "outer"
```

---

## Level 3: Bytecode Compiler + VM

**Compile AST to bytecode and execute on a stack-based virtual machine:**

```
class OpCode(Enum):
    CONST = "CONST"          # push constant
    ADD = "ADD"              # pop 2, push sum
    SUB = "SUB"
    MUL = "MUL"
    DIV = "DIV"
    EQ = "EQ"
    LT = "LT"
    GT = "GT"
    NOT = "NOT"
    LOAD = "LOAD"           # push variable value
    STORE = "STORE"         # pop and store to variable
    JUMP = "JUMP"           # unconditional jump
    JUMP_IF_FALSE = "JUMP_IF_FALSE"
    CALL = "CALL"           # call function
    RETURN = "RETURN"
    PRINT = "PRINT"
    HALT = "HALT"

class Compiler:
    compile(program: Program) -> list[Instruction]

class VM:
    __init__()
    run(bytecode: list[Instruction]) -> Any
    stack: list            # operand stack
    frames: list           # call stack
```

**Requirements:**
- Compiler: walk AST, emit bytecode instructions
  - Expressions: compile both sides, then emit operator instruction
  - If/while: emit JUMP_IF_FALSE with placeholder, patch address after compiling body
  - Functions: compile body separately, store as a constant
- VM: stack-based execution
  - Operand stack: push/pop values
  - Call stack: frames with local variables and return address
  - Execute instructions sequentially, jump for control flow
- The VM should be significantly faster than the tree-walk interpreter
- Disassembler: pretty-print bytecode for debugging

**Bytecode example:**
```
Source: let x = 3 + 4 * 2

Bytecode:
  CONST 3
  CONST 4
  CONST 2
  MUL         # stack: [3, 8]
  ADD         # stack: [11]
  STORE "x"   # x = 11
```

**Test Cases:**
```python
compiler = Compiler()
bytecode = compiler.compile(parse("let x = 3 + 4 * 2\nprint(x)"))

vm = VM()
vm.run(bytecode)
# Should print 11

# Function calls via bytecode
code = "fn double(n) { return n * 2 }\nprint(double(21))"
bytecode2 = compiler.compile(parse(code))
vm.run(bytecode2)
# Should print 42

# Performance: bytecode should be faster than interpreter
import time
fib_code = """
fn fib(n) {
    if n <= 1 { return n }
    return fib(n-1) + fib(n-2)
}
print(fib(20))
"""
# VM execution should be noticeably faster than tree-walk
```

---

## Level 4: Optimizations + Type Checking

**Add compiler optimizations and static type checking:**

```
class TypeChecker:
    __init__()
    check(program: Program) -> list[TypeError]

class Optimizer:
    optimize(bytecode: list[Instruction]) -> list[Instruction]
    constant_fold(ast: AST) -> AST
    dead_code_eliminate(ast: AST) -> AST
```

**Requirements:**
- **Constant folding**: `3 + 4` → `7` at compile time, not runtime
- **Dead code elimination**: remove code after `return`, unreachable branches
- **Strength reduction**: `x * 2` → `x + x`, `x * 1` → `x`
- **Type checking** (optional annotations): `fn add(a: int, b: int) -> int`
  - Infer types where possible
  - Report type errors before execution: `"Line 5: Cannot add string and int"`
  - Type check function arguments and return values
- Peephole optimization: simplify bytecode patterns (e.g., PUSH 0; ADD → remove both)
- Compare performance: unoptimized vs optimized bytecode on fibonacci(25)

**Test Cases:**
```python
# Constant folding
ast = parse("let x = 3 + 4 * 2")
optimized = Optimizer().constant_fold(ast)
# Assignment value should now be NumberLiteral(11), not a BinaryOp tree

# Dead code elimination
ast2 = parse("""
fn early() {
    return 1
    print("unreachable")
}
""")
optimized2 = Optimizer().dead_code_eliminate(ast2)
# print statement should be removed

# Type checking
errors = TypeChecker().check(parse("""
let x: int = 10
let y: str = "hello"
let z = x + y
"""))
assert len(errors) > 0
assert "Cannot add int and str" in errors[0].message

# Performance comparison
code = "fn fib(n) { if n <= 1 { return n } return fib(n-1) + fib(n-2) }\nprint(fib(25))"
bytecode_raw = compiler.compile(parse(code))
bytecode_opt = Optimizer().optimize(bytecode_raw)
assert len(bytecode_opt) <= len(bytecode_raw)
```
