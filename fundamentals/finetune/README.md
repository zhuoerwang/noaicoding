# Project 26: Fine-tuning + LoRA

**Builds on:** Autograd (Project 12), Transformer (Project 13)

**No GPU required** — works on the small models built in earlier projects. The goal is understanding the mechanics, not training a large model.

## Level 1: Dataset Preparation

**Build a fine-tuning data pipeline:**

```
class FinetuneDataset:
    __init__(data: list[dict], tokenizer, max_length: int = 128)
    __len__() -> int
    __getitem__(index: int) -> dict      # {"input_ids": [...], "labels": [...]}

class DataCollator:
    __init__(pad_token_id: int = 0)
    collate(batch: list[dict]) -> dict   # pad + stack into batches

class InstructionFormatter:
    format(instruction: str, input: str, output: str) -> str
    parse(formatted: str) -> dict
```

**Requirements:**
- Load instruction-tuning data (Alpaca format): `{"instruction": ..., "input": ..., "output": ...}`
- Format into prompt template:
  ```
  ### Instruction:
  {instruction}
  ### Input:
  {input}
  ### Response:
  {output}
  ```
- Tokenize using your BPE tokenizer (Project 9) or a simple tokenizer
- Create labels: mask the instruction/input tokens with -100 (only train on response)
- Padding: pad shorter sequences to max_length in batch
- Truncation: cut sequences longer than max_length
- Shuffle and batch the dataset

**Test Cases:**
```python
data = [
    {"instruction": "Translate to French", "input": "Hello", "output": "Bonjour"},
    {"instruction": "Summarize", "input": "Long text here...", "output": "Short summary"},
]

dataset = FinetuneDataset(data, tokenizer, max_length=64)
assert len(dataset) == 2

item = dataset[0]
assert "input_ids" in item
assert "labels" in item
assert len(item["input_ids"]) <= 64

# Labels should have -100 for instruction tokens
assert item["labels"][0] == -100  # instruction part is masked

collator = DataCollator()
batch = collator.collate([dataset[0], dataset[1]])
assert batch["input_ids"].shape[0] == 2  # batch of 2
```

---

## Level 2: Full Fine-tuning

**Implement the fine-tuning training loop:**

```
class Trainer:
    __init__(model, optimizer, dataset: FinetuneDataset,
             batch_size: int = 4, epochs: int = 3)
    train() -> list[float]       # returns loss per step
    evaluate(eval_data: FinetuneDataset) -> float
    save_checkpoint(path: str) -> None
    load_checkpoint(path: str) -> None
```

**Requirements:**
- Training loop: forward pass → compute loss → backward → update weights
- Loss function: cross-entropy on predicted vs target tokens
  - Only compute loss on non-masked labels (where label != -100)
- All model parameters are updated (full fine-tuning)
- Learning rate scheduler: linear warmup then cosine decay
- Gradient clipping: clip gradient norm to prevent exploding gradients
- Checkpointing: save model weights + optimizer state
- Evaluation: compute loss on held-out data without updating weights
- Track and print loss per step to show convergence

**Test Cases:**
```python
# Use the small transformer from Project 13
model = GPT(vocab_size=100, embed_dim=32, num_heads=4, num_layers=2, max_seq_len=64)
optimizer = SGD(model.parameters(), lr=0.001)

trainer = Trainer(model, optimizer, dataset, batch_size=2, epochs=5)
losses = trainer.train()

# Loss should decrease
assert losses[-1] < losses[0]

# Save and reload
trainer.save_checkpoint("/tmp/checkpoint.pt")
trainer.load_checkpoint("/tmp/checkpoint.pt")

# Eval
eval_loss = trainer.evaluate(eval_dataset)
assert eval_loss > 0
```

---

## Level 3: LoRA (Low-Rank Adaptation)

**Implement LoRA — train only small adapter matrices instead of full weights:**

```
class LoRALinear:
    __init__(original_weight: np.ndarray, rank: int = 4, alpha: float = 1.0)
    forward(x: np.ndarray) -> np.ndarray
    lora_parameters() -> list          # only the A and B matrices
    merged_weight() -> np.ndarray      # original + LoRA delta

class LoRAModel:
    __init__(base_model, target_modules: list[str], rank: int = 4)
    inject_lora() -> None              # replace target layers with LoRA versions
    lora_parameters() -> list          # only LoRA params (for optimizer)
    base_parameters() -> list          # frozen base params
    trainable_percentage() -> float    # what % of params are trainable
```

**Requirements:**
- LoRA decomposes weight updates: `W' = W + (alpha/rank) * B @ A`
  - `W` = original weight (frozen, not updated)
  - `A` = (rank x in_features) — initialized randomly (Kaiming)
  - `B` = (out_features x rank) — initialized to zeros
  - Only `A` and `B` are trained — much fewer parameters
- `inject_lora()`: find target layers (e.g., attention Q, K, V projections), replace with LoRA versions
- Freeze all base model parameters
- Only pass LoRA parameters to the optimizer
- `trainable_percentage()`: should be ~1-5% of total parameters
- Forward pass: `output = x @ W.T + (alpha/rank) * x @ A.T @ B.T`

**The key insight:**
```
Full fine-tuning:  train ALL 1,000,000 parameters
LoRA (rank=4):     train only 8,000 parameters (0.8%)
Same quality for most tasks!
```

**Test Cases:**
```python
model = GPT(vocab_size=100, embed_dim=32, num_heads=4, num_layers=2, max_seq_len=64)
total_params = sum(p.size for p in model.parameters())

lora_model = LoRAModel(model, target_modules=["q_proj", "v_proj"], rank=4)
lora_model.inject_lora()

trainable = len(lora_model.lora_parameters())
pct = lora_model.trainable_percentage()
assert pct < 10.0  # less than 10% of params are trainable

# Train with LoRA — only LoRA params should change
optimizer = SGD(lora_model.lora_parameters(), lr=0.01)
# ... training loop ...

# Base weights should not have changed
# LoRA weights should have changed
```

---

## Level 4: LoRA Merge + Comparison

**Merge LoRA weights back and compare approaches:**

```
class LoRAMerger:
    merge(lora_model: LoRAModel) -> None      # merge LoRA into base weights permanently
    unmerge(lora_model: LoRAModel) -> None    # remove LoRA delta from base weights

class Benchmark:
    __init__(model, eval_dataset: FinetuneDataset)
    evaluate() -> dict    # loss, perplexity, accuracy
    compare(models: dict[str, Any]) -> dict   # compare multiple models
```

**Requirements:**
- `merge()`: permanently add LoRA delta to base weights: `W = W + (alpha/rank) * B @ A`
  - After merging, model runs at original speed (no LoRA overhead)
  - The merged model is a standard model — can be saved/shared normally
- `unmerge()`: subtract the delta back out (for switching between LoRA adapters)
- Multiple LoRA adapters: swap different adapters for different tasks
- Benchmark comparison:
  - Base model (no fine-tuning) vs full fine-tuning vs LoRA
  - Compare: loss, parameter count, training time, memory usage
  - LoRA should achieve similar quality to full fine-tuning with far fewer parameters

**Test Cases:**
```python
# Train both approaches on same data
model_full = train_full_finetune(base_model, dataset)
model_lora = train_lora(base_model, dataset, rank=4)

# Merge LoRA
merger = LoRAMerger()
merger.merge(model_lora)

# Compare
bench = Benchmark(eval_dataset=eval_data)
results = bench.compare({
    "base": base_model,
    "full_finetune": model_full,
    "lora_rank4": model_lora,
})

# LoRA should be close to full fine-tuning in quality
assert results["lora_rank4"]["loss"] < results["base"]["loss"]
# But with way fewer trained parameters
assert results["lora_rank4"]["trainable_params"] < results["full_finetune"]["trainable_params"] * 0.1
```
