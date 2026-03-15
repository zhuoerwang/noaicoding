# Project 19: Regex Engine

## Level 1: Basic Pattern Matching

**Implement a regex engine that compiles patterns and matches strings:**

```
class Regex:
    __init__(pattern: str)
    match(text: str) -> bool          # full string match
    search(text: str) -> Match | None  # find first match anywhere

class Match:
    start: int
    end: int
    group() -> str
```

**Requirements:**
- Literal characters: `abc` matches "abc"
- Dot wildcard: `.` matches any single character
- Character classes: `[abc]` matches a, b, or c; `[a-z]` matches ranges; `[^abc]` negation
- Anchors: `^` matches start, `$` matches end
- Escaping: `\.` matches literal dot, `\\` matches backslash
- `match()` must match the entire string
- `search()` finds the first occurrence anywhere in the string

**Test Cases:**
```python
r = Regex("hello")
assert r.match("hello") is True
assert r.match("hello world") is False

r2 = Regex("h.llo")
assert r2.match("hello") is True
assert r2.match("hallo") is True

r3 = Regex("[abc]at")
assert r3.match("bat") is True
assert r3.match("dat") is False

m = Regex("world").search("hello world")
assert m.group() == "world"
assert m.start == 6
```

---

## Level 2: Quantifiers (NFA Construction)

**Add repetition operators using Thompson's NFA construction:**

```
class NFA:
    states: list[State]
    start: State
    accept: State

class NFABuilder:
    from_pattern(pattern: str) -> NFA

class NFASimulator:
    matches(nfa: NFA, text: str) -> bool
```

**Requirements:**
- `*` — zero or more: `ab*c` matches "ac", "abc", "abbc"
- `+` — one or more: `ab+c` matches "abc", "abbc" but not "ac"
- `?` — zero or one: `ab?c` matches "ac", "abc"
- `{n}` — exactly n: `a{3}` matches "aaa"
- `{n,m}` — between n and m: `a{2,4}` matches "aa", "aaa", "aaaa"
- Build NFA using Thompson's construction:
  - Each operator creates small NFA fragments
  - Fragments are connected with epsilon transitions
- Simulate NFA: track set of current states, advance on each character
- NFA simulation is O(n * m) where n = text length, m = pattern states

**Test Cases:**
```python
r = Regex("ab*c")
assert r.match("ac") is True
assert r.match("abc") is True
assert r.match("abbbbc") is True
assert r.match("abbd") is False

r2 = Regex("a+b")
assert r2.match("ab") is True
assert r2.match("aaab") is True
assert r2.match("b") is False

r3 = Regex("colou?r")
assert r3.match("color") is True
assert r3.match("colour") is True
```

---

## Level 3: Groups + Alternation

**Add grouping and capture groups:**

```
class Regex:
    match(text: str) -> Match | None

class Match:
    group(n: int = 0) -> str    # 0 = full match, 1+ = capture groups
    groups() -> tuple[str, ...]
    span() -> tuple[int, int]
```

**Requirements:**
- Alternation: `cat|dog` matches "cat" or "dog"
- Grouping: `(ab)+` matches "ab", "abab"
- Capture groups: `(\d+)-(\d+)` captures the parts
- Nested groups: `((a)(b))` — group 1 = "ab", group 2 = "a", group 3 = "b"
- Shorthand classes: `\d` = digit, `\w` = word char, `\s` = whitespace
- Non-greedy quantifiers: `*?`, `+?` match as little as possible

**Test Cases:**
```python
r = Regex("(cat|dog) food")
m = r.match("cat food")
assert m is not None
assert m.group(1) == "cat"

r2 = Regex("(\\d+)-(\\d+)")
m2 = r2.match("123-456")
assert m2.groups() == ("123", "456")

r3 = Regex("(ab)+")
assert r3.match("ababab") is not None
assert r3.match("abc") is None
```

---

## Level 4: NFA to DFA Conversion

**Convert NFA to DFA for faster matching:**

```
class DFA:
    states: list[frozenset]     # each DFA state is a set of NFA states
    start: frozenset
    accept: set[frozenset]
    transitions: dict

class NFAtoDFA:
    convert(nfa: NFA) -> DFA

class DFASimulator:
    matches(dfa: DFA, text: str) -> bool
```

**Requirements:**
- Subset construction: each DFA state = set of NFA states
- Compute epsilon closures for state sets
- Build transition table: for each DFA state and input char, compute next state
- DFA matching is O(n) — one state at a time, no backtracking
- Compare performance: NFA vs DFA on pathological patterns like `a?{n}a{n}`
- Optional: DFA minimization (merge equivalent states)

**Test Cases:**
```python
# Pathological pattern that's slow with backtracking but fast with DFA
pattern = "a?" * 20 + "a" * 20
text = "a" * 20

r_nfa = Regex(pattern, engine="nfa")
r_dfa = Regex(pattern, engine="dfa")

# Both should match
assert r_nfa.match(text) is True
assert r_dfa.match(text) is True

# DFA should be significantly faster on this pattern
import time
start = time.time()
for _ in range(1000):
    r_dfa.match(text)
dfa_time = time.time() - start
# DFA should handle this efficiently
```
