# Project: Pretty Print Binary Tree

**Core skills tested**: Binary tree structure, level-order traversal, position calculation, string formatting

## Problem Description

Given a binary tree represented as a level-order array, produce a visual text representation where:
- Missing nodes are displayed as `*`
- Leaf-level nodes are separated by exactly one space
- Each parent node is horizontally centered between its two children
- Output is a list of strings, one per level, right-stripped (no trailing spaces)

**Implement a function `pretty_print`:**

```python
def pretty_print(tree: list) -> list[str]:
```

**Input:**
- `tree`: A binary tree in level-order array format
  - Values are single digits (0–9)
  - `None` represents a missing node
  - Trailing `None`s may be omitted (e.g., `[1, 2]` means `[1, 2, None]`)

**Requirements:**
- Extend the tree to its full depth, filling all missing positions with `*`
- At the bottom level, each node/`*` occupies 1 character, separated by 1 space
- Each parent is placed at the midpoint of its two children's positions
- Return a list of strings (one per level), right-stripped

**Layout formula:**

For a tree of height `h` (root is height 1):
- Total width: `2^h - 1`
- Bottom level (level `h-1`): nodes at character positions `0, 2, 4, 6, ...`
- Each parent: midpoint of its left and right child positions

```
Height 1 (width 1):    Height 2 (width 3):    Height 3 (width 7):

1                        1                          1
                        2 3                       2   3
                                                 4 5 6 7
```

**Examples:**

Tree: `[1]`
```
1
```

Tree: `[1, 2, 3]`
```
 1
2 3
```

Tree: `[1, 2, 3, 4, 5, 6, 7]`
```
   1
 2   3
4 5 6 7
```

Tree: `[1, 2, 3, None, 5, None, 7]`
```
   1
 2   3
* 5 * 7
```

Tree: `[5, 3, None]`
```
 5
3 *
```

Tree: `[1, 2, 3, 4, 5, 6, 7, 8, 9]` (height 4, nodes 8 and 9 force a 4th level)
```
       1
   2       3
 4   5   6   7
8 9 * * * * * *
```

**Test Cases:**
```python
assert pretty_print([1]) == ['1']
assert pretty_print([1, 2, 3]) == [' 1', '2 3']
assert pretty_print([5, 3, None]) == [' 5', '3 *']
assert pretty_print([1, None, 3]) == [' 1', '* 3']
assert pretty_print([1, 2, 3, 4, 5, 6, 7]) == ['   1', ' 2   3', '4 5 6 7']
assert pretty_print([1, 2, 3, None, 5, None, 7]) == ['   1', ' 2   3', '* 5 * 7']
assert pretty_print([1, 2, 3, 4, None, None, 7]) == ['   1', ' 2   3', '4 * * 7']
assert pretty_print([1, 2, 3, 4, 5]) == ['   1', ' 2   3', '4 5 * *']
assert pretty_print([1, 2, 3, None, None, 6, 7]) == ['   1', ' 2   3', '* * 6 7']
assert pretty_print([1, 2, None, 4, 5]) == ['   1', ' 2   *', '4 5 * *']
assert pretty_print([1, 2, 3, 4, 5, 6, 7, 8, 9]) == [
    '       1',
    '   2       3',
    ' 4   5   6   7',
    '8 9 * * * * * *'
]
```
