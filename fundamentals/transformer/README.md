# Project 13: Transformer

## Level 1: Token Embeddings + Positional Encoding

**Implement the input layer of a transformer (using numpy only):**

```
class Embedding:
    __init__(vocab_size: int, embed_dim: int)
    __call__(token_ids: list[int]) -> np.ndarray   # (seq_len, embed_dim)

class PositionalEncoding:
    __init__(max_len: int, embed_dim: int)
    __call__(seq_len: int) -> np.ndarray            # (seq_len, embed_dim)
```

**Requirements:**
- `Embedding`: lookup table mapping token IDs to dense vectors
- Initialize weights randomly (small values)
- `PositionalEncoding`: sinusoidal encoding per "Attention Is All You Need"
  - `PE(pos, 2i) = sin(pos / 10000^(2i/d))`
  - `PE(pos, 2i+1) = cos(pos / 10000^(2i/d))`
- Output = embedding + positional encoding
- All operations in numpy, no PyTorch

**Test Cases:**
```python
emb = Embedding(vocab_size=100, embed_dim=32)
x = emb([5, 12, 3])
assert x.shape == (3, 32)

pe = PositionalEncoding(max_len=512, embed_dim=32)
pos = pe(3)
assert pos.shape == (3, 32)
# Different positions should have different encodings
assert not np.allclose(pos[0], pos[1])
```

---

## Level 2: Self-Attention

**Implement scaled dot-product attention:**

```
class SelfAttention:
    __init__(embed_dim: int, head_dim: int)
    __call__(x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray

class MultiHeadAttention:
    __init__(embed_dim: int, num_heads: int)
    __call__(x: np.ndarray, mask: np.ndarray | None = None) -> np.ndarray
```

**Requirements:**
- Compute Q, K, V by multiplying input with weight matrices
- Attention scores: `softmax(Q @ K^T / sqrt(d_k))`
- Apply causal mask: set future positions to `-inf` before softmax
- Output: `scores @ V`
- Multi-head: split embed_dim into num_heads, run attention in parallel, concatenate
- Implement `softmax` manually (no scipy)

**The attention formula:**
```
Attention(Q, K, V) = softmax(Q @ K^T / sqrt(d_k)) @ V
```

**Test Cases:**
```python
attn = SelfAttention(embed_dim=32, head_dim=32)
x = np.random.randn(5, 32)  # 5 tokens, 32 dim
out = attn(x)
assert out.shape == (5, 32)

# With causal mask, position 0 should only attend to itself
mha = MultiHeadAttention(embed_dim=32, num_heads=4)
out = mha(x, mask="causal")
assert out.shape == (5, 32)
```

---

## Level 3: Transformer Block

**Stack components into a full transformer block:**

```
class LayerNorm:
    __init__(dim: int)
    __call__(x: np.ndarray) -> np.ndarray

class FeedForward:
    __init__(embed_dim: int, ff_dim: int)
    __call__(x: np.ndarray) -> np.ndarray

class TransformerBlock:
    __init__(embed_dim: int, num_heads: int, ff_dim: int)
    __call__(x: np.ndarray) -> np.ndarray
```

**Requirements:**
- `LayerNorm`: normalize across the last dimension, learnable scale + shift
- `FeedForward`: two linear layers with ReLU/GELU in between
- `TransformerBlock`: attention -> residual -> layernorm -> feedforward -> residual -> layernorm
- Pre-norm architecture (norm before attention, not after)
- Implement GELU activation manually

**Test Cases:**
```python
block = TransformerBlock(embed_dim=32, num_heads=4, ff_dim=64)
x = np.random.randn(5, 32)
out = block(x)
assert out.shape == (5, 32)

ln = LayerNorm(32)
normed = ln(x)
assert normed.shape == x.shape
# Mean should be ~0, std should be ~1 per token
assert np.allclose(normed.mean(axis=-1), 0, atol=1e-5)
```

---

## Level 4: GPT — Stack + Generate

**Build a minimal GPT and generate text:**

```
class GPT:
    __init__(vocab_size: int, embed_dim: int, num_heads: int,
             num_layers: int, max_seq_len: int)
    __call__(token_ids: list[int]) -> np.ndarray      # logits (seq_len, vocab_size)
    generate(prompt: list[int], max_tokens: int) -> list[int]
```

**Requirements:**
- Stack N transformer blocks
- Final layer: layernorm + linear projection to vocab_size
- `__call__` returns logits (unnormalized scores) for each position
- `generate()`: autoregressive generation
  - Compute logits for current sequence
  - Sample or argmax from last position's logits
  - Append to sequence, repeat
- Temperature sampling: divide logits by temperature before softmax
- Top-k sampling: only consider top k tokens

**Test Cases:**
```python
gpt = GPT(vocab_size=100, embed_dim=32, num_heads=4, num_layers=2, max_seq_len=64)
logits = gpt([1, 2, 3])
assert logits.shape == (3, 100)

generated = gpt.generate(prompt=[1, 2, 3], max_tokens=10)
assert len(generated) == 13  # 3 prompt + 10 generated
assert all(0 <= t < 100 for t in generated)
```
