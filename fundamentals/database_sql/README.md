# Project 27: SQL Database

**Builds on:** KV Store (Project 1), JSON Parser (Project 22) for parsing techniques

## Level 1: Storage Engine (B-Tree + Pages)

**Implement a page-based storage engine with B-tree indexing:**

```
class Page:
    __init__(page_id: int, size: int = 4096)
    data: bytearray
    read_slot(index: int) -> bytes
    write_slot(index: int, data: bytes) -> None

class BTree:
    __init__(order: int = 100)
    insert(key: Any, value: int) -> None      # value = row_id / page offset
    search(key: Any) -> int | None
    range_search(low: Any, high: Any) -> list[int]
    delete(key: Any) -> bool

class Table:
    __init__(name: str, columns: list[dict])
    insert_row(values: dict) -> int           # returns row_id
    get_row(row_id: int) -> dict | None
    scan() -> Iterator[dict]                  # full table scan
```

**Requirements:**
- Pages: fixed-size blocks (4KB) that hold multiple rows
- Row storage: serialize rows into bytes, pack into pages
- B-tree: balanced tree for O(log n) lookups
  - Each node holds up to `order` keys
  - Split nodes when full, merge when underfull
  - Leaf nodes point to row locations (page_id, slot)
- `range_search`: return all keys in [low, high] range efficiently
- `scan()`: iterate all rows without index (for queries without WHERE)
- Handle variable-length strings (store length prefix)

**Test Cases:**
```python
table = Table("users", [
    {"name": "id", "type": "int", "primary_key": True},
    {"name": "name", "type": "str"},
    {"name": "age", "type": "int"},
])

table.insert_row({"id": 1, "name": "Alice", "age": 30})
table.insert_row({"id": 2, "name": "Bob", "age": 25})

row = table.get_row(1)
assert row["name"] == "Alice"

# B-tree index lookup
btree = BTree(order=4)
for i in range(100):
    btree.insert(i, i * 10)
assert btree.search(42) == 420
assert len(btree.range_search(10, 20)) == 11
```

---

## Level 2: SQL Parser

**Implement a SQL lexer and parser:**

```
class SQLLexer:
    tokenize(sql: str) -> list[Token]

class SQLParser:
    parse(sql: str) -> Statement

class SelectStatement:
    columns: list[str]          # ["name", "age"] or ["*"]
    table: str
    where: Expression | None
    order_by: list[tuple[str, str]] | None   # [(col, "ASC"/"DESC")]
    limit: int | None

class InsertStatement:
    table: str
    columns: list[str]
    values: list[list[Any]]

class CreateTableStatement:
    table: str
    columns: list[dict]
```

**Requirements:**
- Lex SQL into tokens: keywords (SELECT, FROM, WHERE, INSERT, CREATE, etc.), identifiers, literals, operators
- Keywords are case-insensitive: `SELECT` = `select`
- Parse supported statements:
  - `SELECT col1, col2 FROM table WHERE condition ORDER BY col LIMIT n`
  - `INSERT INTO table (col1, col2) VALUES (val1, val2)`
  - `CREATE TABLE name (col1 TYPE, col2 TYPE)`
  - `DELETE FROM table WHERE condition`
- WHERE expressions: `=`, `!=`, `<`, `>`, `<=`, `>=`, `AND`, `OR`, `NOT`
- Handle string literals with single quotes: `WHERE name = 'Alice'`
- Clear error messages: `"Unexpected token 'FROME' at position 20, did you mean 'FROM'?"`

**Test Cases:**
```python
parser = SQLParser()

stmt = parser.parse("SELECT name, age FROM users WHERE age > 25")
assert isinstance(stmt, SelectStatement)
assert stmt.columns == ["name", "age"]
assert stmt.table == "users"

stmt2 = parser.parse("INSERT INTO users (name, age) VALUES ('Alice', 30)")
assert isinstance(stmt2, InsertStatement)
assert stmt2.values == [["Alice", 30]]

stmt3 = parser.parse("SELECT * FROM users WHERE name = 'Bob' AND age >= 20 ORDER BY age DESC LIMIT 10")
assert stmt3.order_by == [("age", "DESC")]
assert stmt3.limit == 10
```

---

## Level 3: Query Execution

**Execute parsed SQL against the storage engine:**

```
class QueryExecutor:
    __init__(catalog: dict[str, Table])
    execute(statement: Statement) -> QueryResult

class QueryResult:
    columns: list[str]
    rows: list[dict]
    rows_affected: int
```

**Requirements:**
- SELECT: retrieve rows, apply WHERE filter, apply ORDER BY, apply LIMIT
- INSERT: add row to table, update indexes
- DELETE: remove matching rows, update indexes
- Two scan strategies:
  - **Full table scan**: check every row against WHERE (no index)
  - **Index scan**: use B-tree to find matching rows (when WHERE uses indexed column)
- Automatically choose index scan when available
- Aggregate functions: `COUNT(*)`, `SUM(col)`, `AVG(col)`, `MIN(col)`, `MAX(col)`
- GROUP BY: group rows and apply aggregates per group
- NULL handling: NULL comparisons, IS NULL, IS NOT NULL

**Test Cases:**
```python
executor = QueryExecutor({"users": users_table})

result = executor.execute(parser.parse("SELECT * FROM users WHERE age > 25"))
assert all(row["age"] > 25 for row in result.rows)

result2 = executor.execute(parser.parse("SELECT COUNT(*), AVG(age) FROM users"))
assert result2.rows[0]["COUNT(*)"] == len(users_table)

executor.execute(parser.parse("INSERT INTO users (id, name, age) VALUES (3, 'Charlie', 35)"))
result3 = executor.execute(parser.parse("SELECT * FROM users WHERE name = 'Charlie'"))
assert len(result3.rows) == 1

# GROUP BY
result4 = executor.execute(parser.parse("SELECT age, COUNT(*) FROM users GROUP BY age"))
assert len(result4.rows) > 0
```

---

## Level 4: Joins + Query Optimizer

**Add JOIN support and a basic query optimizer:**

```
class JoinExecutor:
    nested_loop_join(left: list, right: list, condition) -> list
    hash_join(left: list, right: list, left_key: str, right_key: str) -> list

class QueryPlanner:
    plan(statement: SelectStatement, catalog: dict) -> QueryPlan
    estimate_cost(plan: QueryPlan) -> float

class QueryPlan:
    steps: list[str]    # human-readable execution plan
    strategy: str       # "table_scan", "index_scan", "hash_join", etc.
```

**Requirements:**
- JOIN types: `INNER JOIN`, `LEFT JOIN` on a condition
- Two join algorithms:
  - **Nested loop join**: O(n*m) — simple, works for any condition
  - **Hash join**: O(n+m) — build hash table on smaller table, probe with larger
- Query planner chooses strategy:
  - Use index scan if WHERE column has an index
  - Use hash join if join key is equality
  - Estimate row counts to pick smaller table for hash build
- `EXPLAIN` command: show the query plan without executing
- Subqueries: `SELECT * FROM users WHERE age > (SELECT AVG(age) FROM users)`

**Test Cases:**
```python
# Create orders table
executor.execute(parser.parse(
    "CREATE TABLE orders (id INT, user_id INT, amount INT)"))
executor.execute(parser.parse(
    "INSERT INTO orders (id, user_id, amount) VALUES (1, 1, 100)"))
executor.execute(parser.parse(
    "INSERT INTO orders (id, user_id, amount) VALUES (2, 2, 200)"))

# JOIN
result = executor.execute(parser.parse(
    "SELECT users.name, orders.amount FROM users INNER JOIN orders ON users.id = orders.user_id"))
assert len(result.rows) >= 2

# Query plan
plan = planner.plan(parser.parse("SELECT * FROM users WHERE id = 1"), catalog)
assert "index_scan" in plan.strategy  # id has an index

plan2 = planner.plan(parser.parse("SELECT * FROM users WHERE name = 'Alice'"), catalog)
assert "table_scan" in plan2.strategy  # name has no index
```
