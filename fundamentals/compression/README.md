# Project 23: Compression

## Level 1: Huffman Coding

**Implement Huffman encoding and decoding:**

```
class HuffmanTree:
    build(frequencies: dict[str, int]) -> "HuffmanTree"
    get_codes() -> dict[str, str]    # char -> binary string ("0110...")

class HuffmanCodec:
    __init__()
    encode(text: str) -> tuple[bytes, dict]   # compressed data + code table
    decode(data: bytes, code_table: dict, length: int) -> str
```

**Requirements:**
- Build a Huffman tree from character frequencies:
  - Create leaf node for each character
  - Repeatedly merge the two lowest-frequency nodes
  - Use a priority queue (min-heap)
- Generate variable-length codes: frequent characters get shorter codes
- Encode: replace each character with its binary code, pack into bytes
- Decode: walk the tree bit by bit, emit character when reaching a leaf
- Handle the last byte padding (may have unused bits)
- Code table must be stored alongside compressed data for decoding

**Test Cases:**
```python
codec = HuffmanCodec()
text = "aaaaabbbccdddddddd"

encoded, table = codec.encode(text)
assert len(encoded) < len(text)  # compression happened

decoded = codec.decode(encoded, table, len(text))
assert decoded == text

# Character with highest frequency should have shortest code
assert len(table["d"]) <= len(table["c"])

# Edge cases
encoded_single, _ = codec.encode("aaaa")
decoded_single = codec.decode(encoded_single, _, 4)
assert decoded_single == "aaaa"
```

---

## Level 2: LZ77 (Sliding Window Compression)

**Implement LZ77 — the algorithm behind gzip:**

```
class LZ77Token:
    offset: int      # how far back to look
    length: int      # how many chars to copy
    next_char: str   # the literal character after the match

class LZ77:
    __init__(window_size: int = 4096, lookahead_size: int = 18)
    compress(text: str) -> list[LZ77Token]
    decompress(tokens: list[LZ77Token]) -> str
```

**Requirements:**
- Sliding window: search buffer (past data) + lookahead buffer (upcoming data)
- For each position, find the longest match in the search buffer
- Emit (offset, length, next_char) tokens:
  - `(0, 0, 'a')` — no match, literal character 'a'
  - `(5, 3, 'x')` — copy 3 chars from 5 positions back, then literal 'x'
- Decompress by replaying the tokens: copy from decoded output
- Handle overlapping copies: `(1, 5, ...)` copies from 1 back for 5 chars (repeats)
- Window size controls max lookback distance
- Longer matches = better compression

**Test Cases:**
```python
lz = LZ77(window_size=100)
text = "abracadabra abracadabra"

tokens = lz.compress(text)
assert len(tokens) < len(text)  # fewer tokens than characters

decompressed = lz.decompress(tokens)
assert decompressed == text

# Repetitive text should compress well
repetitive = "abcabc" * 100
tokens_rep = lz.compress(repetitive)
assert len(tokens_rep) < 50  # high compression ratio

# No repetition — mostly literals
random_text = "abcdefghijklmnop"
tokens_rand = lz.compress(random_text)
assert lz.decompress(tokens_rand) == random_text
```

---

## Level 3: DEFLATE (Huffman + LZ77)

**Combine LZ77 and Huffman into the DEFLATE algorithm:**

```
class Deflate:
    __init__(window_size: int = 32768)
    compress(data: bytes) -> bytes
    decompress(data: bytes) -> bytes
    compression_ratio(data: bytes) -> float
```

**Requirements:**
- Stage 1: LZ77 compression — find repeated patterns
- Stage 2: Huffman coding of LZ77 tokens — compress the tokens themselves
- Two Huffman trees: one for literal/length values, one for distances
- Fixed Huffman codes (simplified) or dynamic Huffman codes
- Bit-level packing: write individual bits, not bytes
- Implement a BitWriter and BitReader for bit-level I/O
- Round-trip: `decompress(compress(data)) == data`

**Test Cases:**
```python
deflate = Deflate()

data = b"Hello Hello Hello Hello World World World"
compressed = deflate.compress(data)
assert len(compressed) < len(data)

decompressed = deflate.decompress(compressed)
assert decompressed == data

ratio = deflate.compression_ratio(data)
assert ratio < 1.0  # compressed is smaller

# Binary data
binary = bytes(range(256)) * 10
assert deflate.decompress(deflate.compress(binary)) == binary
```

---

## Level 4: File Format (gzip compatible)

**Wrap DEFLATE in the gzip file format:**

```
class GzipFile:
    compress_file(input_path: str, output_path: str) -> None
    decompress_file(input_path: str, output_path: str) -> None
    compress_bytes(data: bytes) -> bytes
    decompress_bytes(data: bytes) -> bytes
```

**Requirements:**
- Gzip header: magic bytes (1f 8b), compression method, flags, timestamp
- Gzip footer: CRC32 checksum + original size
- Implement CRC32 from scratch (table-based)
- Compressed files should be decompressable by system `gzip -d`
- Should be able to decompress files created by system `gzip`
- Handle the gzip member format correctly
- Verify CRC32 on decompression, raise error if mismatch

**Test Cases:**
```python
gz = GzipFile()

# Compress and decompress bytes
data = b"The quick brown fox jumps over the lazy dog" * 100
compressed = gz.compress_bytes(data)
assert compressed[:2] == b"\\x1f\\x8b"  # gzip magic bytes

decompressed = gz.decompress_bytes(compressed)
assert decompressed == data

# File-level round trip
gz.compress_file("/tmp/test_input.txt", "/tmp/test_output.gz")
gz.decompress_file("/tmp/test_output.gz", "/tmp/test_result.txt")
with open("/tmp/test_input.txt", "rb") as f1, open("/tmp/test_result.txt", "rb") as f2:
    assert f1.read() == f2.read()

# Interoperability: our compressed file should work with system gzip
# os.system("gzip -d /tmp/test_output.gz") should succeed
```
