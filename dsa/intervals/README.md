# Project: Interval-Based Usage Billing

**Core skills tested**: Interval intersection, sweep line, coordinate compression, priority resolution

## Level 1: Single Price Override

**Implement a function `calculate_charge`:**

```
def calculate_charge(
    usages: list[list[int, int]],      # half-open intervals [start, end)
    default_price: int,
    overrides: list[list[int, int, int]],  # [[start, end, price], ...]
) -> int:
```

**Assumptions:**
- All intervals are half-open: `[start, end)`
- Usage records do not overlap with each other
- All values are non-negative integers
- Usage records and override may or may not overlap

**Requirements:**
- For each usage interval, compute its overlap with the override period
- Overlapping duration → charged at override price per unit
- Non-overlapping duration → charged at default price per unit
- Return total charge across all usage records

**Interval overlap cases:**
```
No overlap:       [====]              [====]
                         [override]

Full overlap:     [====]
                  [========override========]

Partial left:     [=====]
                     [=====override]

Partial right:        [=====]
                  [override=====]

Override inside:  [================]
                      [override]
                  → splits into 3 segments: before, during, after
```

**Example:**
```
Days:      01 02 03 04 05 06 07 08 09 10 11 12

Usages:    [---------)           [---------)
           1         5           8         12

Override:        [--------------------)
                 3                   10

Default price: 5, Override price: 2

Usage [1, 5):
  [1, 3) → 2 units × 5 = 10  (before override)
  [3, 5) → 2 units × 2 = 4   (during override)

Usage [8, 12):
  [8, 10) → 2 units × 2 = 4  (during override)
  [10, 12) → 2 units × 5 = 10 (after override)

Total: 28
```

**Test Cases:**
```python
# No overlap — usage before override
assert calculate_charge([[1, 5]], 10, [[6, 10, 2]]) == 40

# No overlap — usage after override
assert calculate_charge([[10, 15]], 10, [[1, 5, 2]]) == 50

# Full overlap — usage within override
assert calculate_charge([[3, 7]], 10, [[1, 10, 2]]) == 8

# Partial overlap — override starts mid-usage
assert calculate_charge([[1, 8]], 10, [[5, 15, 3]]) == 49  # 4×10 + 3×3

# Override inside usage — splits into 3 segments
assert calculate_charge([[1, 10]], 5, [[3, 7, 2]]) == 33  # 2×5 + 4×2 + 3×5

# Multiple usage records
assert calculate_charge([[1, 5], [8, 12]], 5, [[3, 10, 2]]) == 28

# Empty usages
assert calculate_charge([], 10, [[1, 5, 2]]) == 0

# Adjacent — usage end == override start (half-open, no overlap)
assert calculate_charge([[1, 5]], 10, [[5, 10, 2]]) == 40
```

---

## Level 2: Multiple Non-Overlapping Overrides

**Implement a function `calculate_charge_multi`:**

```
def calculate_charge(
    usages: list[list[int, int]],
    default_price: int,
    overrides: list[list[int, int, int]],  # [[start, end, price], ...]
) -> int:
```

**Assumptions:**
- Overrides are guaranteed non-overlapping with each other
- Overrides are NOT necessarily sorted
- Empty overrides list means everything is charged at default price
- All Level 1 concepts apply (half-open intervals, etc.)

**Requirements:**
- For each usage interval, split against all applicable overrides
- Gaps between overrides are charged at default price
- Return total charge across all usage records
- All Level 1 test cases should be expressible using this function (single override in a list)

**Key insight:**
This follow-up doesn't increase algorithmic complexity much — it tests whether you can design clean, extensible code. Sort overrides, then sweep through each usage.

**Example:**
```
Usage:     [--------------------------------------)
           1                                     20

Overrides: [---------)              [---------)
           5         10             15        25

Default price: 10

[1, 5)   → 4 × 10 = 40   (gap before first override)
[5, 10)  → 5 × 2  = 10   (first override)
[10, 15) → 5 × 10 = 50   (gap between overrides)
[15, 20) → 5 × 3  = 15   (second override)
Total: 115
```

**Test Cases:**
```python
# Single override — same as Level 1
assert calculate_charge([[1, 5]], 10, [[6, 10, 2]]) == 40

# Multiple overrides, usage spans them
assert calculate_charge([[1, 20]], 10, [[5, 10, 2], [15, 25, 3]]) == 115

# Overrides given unsorted — same result
assert calculate_charge([[1, 20]], 10, [[15, 25, 3], [5, 10, 2]]) == 115

# Usage entirely in gap between overrides
assert calculate_charge([[11, 14]], 10, [[5, 10, 2], [15, 25, 3]]) == 30

# No overrides — all default
assert calculate_charge([[1, 10]], 5, []) == 45

# Multiple usages, multiple overrides
assert calculate_charge(
    [[1, 5], [8, 12], [18, 22]], 10,
    [[3, 9, 2], [15, 20, 3]]
) == 82
# [1,3)=20 + [3,5)=4 + [8,9)=2 + [9,12)=30 + [18,20)=6 + [20,22)=20
```

---

## Level 3: Overlapping Overrides with Priority

**Implement a function `calculate_charge_priority`:**

```
def calculate_charge_priority(
    usages: list[list[int, int]],
    default_price: int,
    overrides: list[list[int, int, int, int]],  # [[start, end, price, priority], ...]
) -> int:
```

**Assumptions:**
- Overrides CAN overlap with each other
- Higher priority number wins (priority 10 beats priority 5)
- Equal priority: lower price wins (customer-friendly)
- Non-overlapping overrides should produce the same result as Level 2

**Requirements:**
- Flatten overlapping overrides into non-overlapping segments with resolved prices
- For each time point, determine the winning override (highest priority, then lowest price)
- Apply resolved overrides like Level 2
- All Level 2 test cases should work (add priority=0 or any constant to each override)

**Key insight:**
This is where the real algorithmic complexity lives. The approach is coordinate compression / sweep line:
1. Collect all override endpoints as coordinates
2. Sort coordinates
3. Between each consecutive pair, determine active overrides and pick the winner
4. Produces non-overlapping resolved segments
5. Apply against usage intervals like Level 2

**Example:**
```
Override A: [--------------------)  price=2, priority=5
            1                   10

Override B:      [--------------------)  price=3, priority=10
                 5                   15

Flattened:
  [1, 5)  → only A        → price=2
  [5, 10) → A(p=5), B(p=10) → B wins → price=3
  [10, 15) → only B       → price=3

Usage [1, 15), default=10:
  [1, 5)  = 4 × 2 = 8
  [5, 10) = 5 × 3 = 15
  [10, 15) = 5 × 3 = 15
  Total: 38
```

**Test Cases:**
```python
# Non-overlapping — same as Level 2
assert calculate_charge_priority(
    [[1, 20]], 10, [[5, 10, 2, 1], [15, 25, 3, 1]]
) == 115

# Overlapping, higher priority wins
assert calculate_charge_priority(
    [[1, 15]], 10, [[1, 10, 2, 5], [5, 15, 3, 10]]
) == 38  # 4×2 + 5×3 + 5×3

# Equal priority, lower price wins
assert calculate_charge_priority(
    [[1, 10]], 10, [[1, 10, 5, 1], [1, 10, 3, 1]]
) == 27  # 9 × 3

# Override nested inside another
assert calculate_charge_priority(
    [[1, 20]], 10, [[1, 20, 5, 1], [5, 15, 2, 10]]
) == 65  # 4×5 + 10×2 + 5×5

# No overrides — all default
assert calculate_charge_priority([[1, 10]], 10, []) == 90

# Three overrides, complex nesting
assert calculate_charge_priority(
    [[1, 20]], 10,
    [[1, 15, 5, 1], [5, 20, 3, 5], [8, 12, 1, 10]]
) == 57
# [1,5)=4×5 + [5,8)=3×3 + [8,12)=4×1 + [12,15)=3×3 + [15,20)=5×3
```
