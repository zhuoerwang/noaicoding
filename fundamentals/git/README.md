# Project 20: Git

## Level 1: Object Store (Content-Addressable Storage)

**Implement Git's object model:**

```
class GitObject:
    obj_type: str         # "blob", "tree", "commit"
    data: bytes
    hash() -> str         # SHA-1 hash of the object

class ObjectStore:
    __init__(repo_path: str)
    write_object(obj: GitObject) -> str          # store object, return hash
    read_object(sha: str) -> GitObject           # retrieve by hash
    exists(sha: str) -> bool
```

**Requirements:**
- Objects are stored by their SHA-1 hash (content-addressable)
- Object format: `"{type} {size}\0{data}"` — then SHA-1 the whole thing
- Store objects as files: `.git/objects/ab/cdef1234...` (first 2 chars = dir, rest = filename)
- Compress with zlib before writing to disk
- Three object types:
  - **Blob**: raw file content
  - **Tree**: list of (mode, name, hash) entries — like a directory listing
  - **Commit**: tree hash + parent hash + author + message
- Same content always produces same hash (deterministic)

**Test Cases:**
```python
store = ObjectStore("/tmp/test-repo")
blob = GitObject("blob", b"hello world")
sha = store.write_object(blob)
assert len(sha) == 40  # SHA-1 hex

retrieved = store.read_object(sha)
assert retrieved.data == b"hello world"
assert retrieved.obj_type == "blob"

# Same content = same hash
sha2 = store.write_object(GitObject("blob", b"hello world"))
assert sha == sha2
```

---

## Level 2: Staging Area + Commits

**Implement the index (staging area) and commit creation:**

```
class Index:
    __init__(repo_path: str)
    add(filepath: str) -> None          # stage a file
    remove(filepath: str) -> None
    get_entries() -> list[dict]         # staged files with hashes
    write_tree() -> str                 # create tree object from index, return hash

class CommitBuilder:
    __init__(store: ObjectStore, index: Index)
    commit(message: str, author: str) -> str   # create commit, return hash
```

**Requirements:**
- `add()`: read file, create blob, add entry to index (path + hash + mode)
- Index is a flat list of all tracked files (not nested trees)
- `write_tree()`: convert flat index into nested tree objects (handle subdirectories)
- `commit()`: create tree from index, create commit object pointing to tree + parent
- Commits form a linked list: each commit points to its parent
- Store current branch tip (HEAD) in a ref file: `.git/refs/heads/main`
- Update HEAD after each commit

**Test Cases:**
```python
index = Index("/tmp/test-repo")
index.add("hello.txt")       # file must exist in working dir
index.add("src/main.py")

tree_hash = index.write_tree()
assert store.exists(tree_hash)

builder = CommitBuilder(store, index)
commit_hash = builder.commit("initial commit", "Alice <alice@example.com>")
commit_obj = store.read_object(commit_hash)
assert "initial commit" in commit_obj.data.decode()
```

---

## Level 3: Branches + Log

**Implement branching and commit history:**

```
class RefManager:
    __init__(repo_path: str)
    get_head() -> str                             # current commit hash
    get_branch() -> str                           # current branch name
    create_branch(name: str) -> None
    switch_branch(name: str) -> None
    list_branches() -> list[str]

class Log:
    __init__(store: ObjectStore)
    log(start_hash: str) -> list[dict]            # walk commit history
    diff(hash_a: str, hash_b: str) -> list[str]   # files changed between commits
```

**Requirements:**
- Branches are just files containing a commit hash: `.git/refs/heads/{name}`
- HEAD is either a commit hash (detached) or a ref: `ref: refs/heads/main`
- `create_branch()`: create new ref pointing to current HEAD
- `switch_branch()`: update HEAD + restore working directory to match branch's tree
- `log()`: walk the parent chain from a commit, return list of commit info
- `diff()`: compare two trees, report added/modified/deleted files
- Handle the common case: create branch, make commits, switch back

**Test Cases:**
```python
refs = RefManager("/tmp/test-repo")
refs.create_branch("feature")
refs.switch_branch("feature")
assert refs.get_branch() == "feature"

# Make a commit on feature branch
builder.commit("feature work", "Alice <alice@example.com>")

# Log should show commit history
log = Log(store)
history = log.log(refs.get_head())
assert len(history) >= 1
assert history[0]["message"] == "feature work"

# Diff between branches
branches = refs.list_branches()
assert "main" in branches
assert "feature" in branches
```

---

## Level 4: Merge

**Implement three-way merge:**

```
class Merger:
    __init__(store: ObjectStore, index: Index, refs: RefManager)
    find_common_ancestor(hash_a: str, hash_b: str) -> str
    merge(branch_name: str) -> MergeResult

class MergeResult:
    success: bool
    conflicts: list[str]     # list of conflicting file paths
    commit_hash: str | None  # merge commit hash if successful
```

**Requirements:**
- Find common ancestor: walk both parent chains, find first shared commit
- Three-way merge: compare (ancestor, ours, theirs) for each file
  - Both unchanged → keep as is
  - Only one side changed → take the change
  - Both changed same way → take either (identical change)
  - Both changed differently → **conflict**
- Conflict markers in file:
  ```
  <<<<<<< ours
  our version
  =======
  their version
  >>>>>>> theirs
  ```
- If no conflicts: create a merge commit with two parents
- If conflicts: leave conflict markers in working dir, don't commit

**Test Cases:**
```python
merger = Merger(store, index, refs)

# Setup: main and feature diverged
# main changed file A, feature changed file B — clean merge
result = merger.merge("feature")
assert result.success is True
assert result.conflicts == []

# Setup: both branches changed same file differently — conflict
result2 = merger.merge("conflicting-branch")
assert result2.success is False
assert len(result2.conflicts) > 0
```
