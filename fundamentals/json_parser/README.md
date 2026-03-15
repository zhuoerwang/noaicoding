# Project 22: JSON Parser

## Level 1: Lexer (Tokenizer)

**Implement a JSON lexer that converts raw text into tokens:**

```
class TokenType(Enum):
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    COLON = ":"
    COMMA = ","
    STRING = "STRING"
    NUMBER = "NUMBER"
    TRUE = "TRUE"
    FALSE = "FALSE"
    NULL = "NULL"

class Token:
    type: TokenType
    value: Any
    position: int

class Lexer:
    __init__(text: str)
    tokenize() -> list[Token]
```

**Requirements:**
- Scan input character by character, emit tokens
- Strings: handle `"..."` with escape sequences: `\"`, `\\`, `\/`, `\b`, `\f`, `\n`, `\r`, `\t`, `\uXXXX`
- Numbers: integers, floats, negative, exponent notation (`-3.14e+10`)
- Keywords: `true`, `false`, `null`
- Skip whitespace between tokens
- Track position for error reporting
- Raise clear error on invalid input: `"Unexpected character 'x' at position 5"`

**Test Cases:**
```python
lexer = Lexer('{"name": "Alice", "age": 30, "active": true}')
tokens = lexer.tokenize()
assert tokens[0].type == TokenType.LBRACE
assert tokens[1].type == TokenType.STRING
assert tokens[1].value == "name"
assert tokens[5].type == TokenType.NUMBER
assert tokens[5].value == 30

# Escape sequences
lexer2 = Lexer('"hello\\nworld"')
tokens2 = lexer2.tokenize()
assert tokens2[0].value == "hello\nworld"

# Scientific notation
lexer3 = Lexer("3.14e-2")
tokens3 = lexer3.tokenize()
assert abs(tokens3[0].value - 0.0314) < 1e-10
```

---

## Level 2: Recursive Descent Parser

**Parse tokens into a Python data structure:**

```
class Parser:
    __init__(tokens: list[Token])
    parse() -> Any    # returns dict, list, str, int, float, bool, or None

def json_parse(text: str) -> Any:
    tokens = Lexer(text).tokenize()
    return Parser(tokens).parse()
```

**Requirements:**
- Recursive descent: each JSON type is a function that consumes tokens
  - `parse_value()` → dispatches to the right parser based on current token
  - `parse_object()` → `{` key `:` value (`,` key `:` value)* `}`
  - `parse_array()` → `[` value (`,` value)* `]`
  - `parse_string()`, `parse_number()`, `parse_bool()`, `parse_null()`
- Handle nested structures: objects in arrays, arrays in objects, arbitrary depth
- Error messages: `"Expected ':' after key at position 12, got ','"`
- Handle empty objects `{}` and empty arrays `[]`
- Handle trailing commas: either reject with clear error or accept (configurable)

**Test Cases:**
```python
assert json_parse('42') == 42
assert json_parse('"hello"') == "hello"
assert json_parse('true') is True
assert json_parse('null') is None
assert json_parse('[]') == []
assert json_parse('{}') == {}

result = json_parse('{"name": "Alice", "scores": [90, 85, 92]}')
assert result == {"name": "Alice", "scores": [90, 85, 92]}

# Deeply nested
deep = json_parse('{"a": {"b": {"c": [1, 2, {"d": true}]}}}')
assert deep["a"]["b"]["c"][2]["d"] is True
```

---

## Level 3: JSON Serializer

**Implement serialization (Python objects → JSON string):**

```
class JSONSerializer:
    __init__(indent: int | None = None, sort_keys: bool = False)
    serialize(obj: Any) -> str

def json_stringify(obj: Any, indent: int | None = None) -> str:
    return JSONSerializer(indent=indent).serialize(obj)
```

**Requirements:**
- Serialize: dict, list, str, int, float, bool, None → valid JSON string
- String escaping: reverse of lexer — escape special characters
- Pretty printing: when `indent` is set, add newlines and indentation
- `sort_keys`: output object keys in alphabetical order
- Handle special floats: `inf`, `-inf`, `nan` → raise error (not valid JSON)
- Circular reference detection: raise error instead of infinite recursion
- Round-trip property: `json_parse(json_stringify(obj)) == obj`

**Test Cases:**
```python
assert json_stringify(42) == "42"
assert json_stringify("hello") == '"hello"'
assert json_stringify(True) == "true"
assert json_stringify(None) == "null"
assert json_stringify({"a": 1}) == '{"a": 1}'

# Pretty print
pretty = json_stringify({"name": "Alice", "age": 30}, indent=2)
assert "\\n" in pretty
assert "  " in pretty

# Round-trip
obj = {"key": [1, "two", None, True, {"nested": 3.14}]}
assert json_parse(json_stringify(obj)) == obj

# Circular reference
d = {}
d["self"] = d
# json_stringify(d) should raise an error
```

---

## Level 4: JSON Schema Validator

**Validate JSON data against a JSON Schema:**

```
class SchemaValidator:
    __init__(schema: dict)
    validate(data: Any) -> ValidationResult

class ValidationResult:
    valid: bool
    errors: list[str]    # list of error messages with paths
```

**Requirements:**
- Type validation: `{"type": "string"}`, `{"type": "number"}`, `{"type": "object"}`, etc.
- Object properties: `{"properties": {"name": {"type": "string"}}}"`
- Required fields: `{"required": ["name", "age"]}`
- Array items: `{"type": "array", "items": {"type": "number"}}`
- Constraints: `minimum`, `maximum`, `minLength`, `maxLength`, `pattern`
- Nested schemas: validate deeply nested structures
- Error paths: `"$.address.zip: expected string, got number"`
- Enum: `{"enum": ["red", "green", "blue"]}`

**Test Cases:**
```python
schema = {
    "type": "object",
    "properties": {
        "name": {"type": "string", "minLength": 1},
        "age": {"type": "number", "minimum": 0},
        "tags": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["name", "age"]
}

validator = SchemaValidator(schema)

result = validator.validate({"name": "Alice", "age": 30, "tags": ["dev"]})
assert result.valid is True

result2 = validator.validate({"name": ""})
assert result2.valid is False
assert any("minLength" in e for e in result2.errors)
assert any("required" in e and "age" in e for e in result2.errors)
```
