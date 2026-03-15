# Project 14: RAG (Retrieval-Augmented Generation)

## Level 1: Text Chunking

**Implement document chunking strategies:**

```
class TextChunker:
    __init__(chunk_size: int = 500, overlap: int = 50)
    chunk_by_chars(text: str) -> list[str]
    chunk_by_sentences(text: str) -> list[str]
    chunk_by_tokens(text: str, tokenizer: Callable) -> list[str]
```

**Requirements:**
- `chunk_by_chars`: split text into chunks of `chunk_size` characters with `overlap`
- `chunk_by_sentences`: split on sentence boundaries, merge until chunk_size
- `chunk_by_tokens`: split by token count (uses a tokenizer function)
- Overlap ensures context isn't lost at boundaries
- No chunk should be empty
- Preserve word boundaries (don't split mid-word for char chunking)

**Test Cases:**
```python
chunker = TextChunker(chunk_size=100, overlap=20)
text = "This is sentence one. This is sentence two. " * 10
chunks = chunker.chunk_by_chars(text)
assert all(len(c) <= 100 for c in chunks)
assert len(chunks) > 1

# Overlap: end of chunk N should overlap with start of chunk N+1
assert chunks[0][-20:] == chunks[1][:20]

# Sentence chunking
chunks_sent = chunker.chunk_by_sentences(text)
assert all(c.endswith(". ") or c.endswith(".") for c in chunks_sent)
```

---

## Level 2: Embeddings + Vector Store

**Implement a simple vector store with cosine similarity:**

```
class VectorStore:
    __init__()
    add(text: str, embedding: list[float], metadata: dict | None = None) -> int
    search(query_embedding: list[float], top_k: int = 5) -> list[dict]
    size() -> int

def cosine_similarity(a: list[float], b: list[float]) -> float
```

**Requirements:**
- `add()` stores text + embedding + metadata, returns an ID
- `search()` returns top-k most similar documents by cosine similarity
- Results include: text, similarity score, metadata
- Implement cosine similarity from scratch: `dot(a,b) / (norm(a) * norm(b))`
- Handle edge cases: zero vectors, empty store
- No numpy required — pure Python is fine

**Test Cases:**
```python
store = VectorStore()
store.add("python is great", [1.0, 0.0, 0.0])
store.add("java is okay", [0.0, 1.0, 0.0])
store.add("python programming", [0.9, 0.1, 0.0])

results = store.search([1.0, 0.0, 0.0], top_k=2)
assert len(results) == 2
assert results[0]["text"] == "python is great"    # exact match
assert results[1]["text"] == "python programming"  # closest

assert cosine_similarity([1, 0], [1, 0]) == 1.0
assert cosine_similarity([1, 0], [0, 1]) == 0.0
```

---

## Level 3: Retrieval + Ranking

**Add retrieval pipeline with re-ranking:**

```
class Retriever:
    __init__(vector_store: VectorStore, embed_fn: Callable[[str], list[float]])
    retrieve(query: str, top_k: int = 5) -> list[dict]

class ReRanker:
    __init__(score_fn: Callable[[str, str], float])
    rerank(query: str, documents: list[dict], top_k: int = 3) -> list[dict]
```

**Requirements:**
- `Retriever`: embed the query, search vector store, return results
- `embed_fn`: any function that turns text into a vector (pluggable)
- `ReRanker`: take initial results, re-score with a different function, re-sort
- Score function could be: keyword overlap, TF-IDF, or a more sophisticated metric
- Implement TF-IDF scoring from scratch for the re-ranker
- Pipeline: embed query -> vector search (recall) -> re-rank (precision)

**Test Cases:**
```python
# Simple embedding: bag of words vector
def simple_embed(text):
    vocab = {"python": 0, "java": 1, "code": 2, "great": 3}
    vec = [0.0] * len(vocab)
    for word in text.lower().split():
        if word in vocab:
            vec[vocab[word]] = 1.0
    return vec

retriever = Retriever(store, simple_embed)
results = retriever.retrieve("python code", top_k=3)
assert len(results) <= 3
```

---

## Level 4: Full RAG Pipeline

**Wire everything together into a complete RAG system:**

```
class RAGPipeline:
    __init__(chunker: TextChunker, store: VectorStore,
             retriever: Retriever, prompt_template: str)
    ingest(documents: list[str]) -> None         # chunk + embed + store
    query(question: str) -> str                  # retrieve + build prompt
    build_prompt(question: str, context: list[str]) -> str
```

**Requirements:**
- `ingest()`: chunk documents, embed each chunk, store in vector store
- `query()`: retrieve relevant chunks, build a prompt with context, return it
- Prompt template uses retrieved context: `"Context: {context}\n\nQuestion: {question}\n\nAnswer:"`
- Handle case where no relevant documents found
- Deduplication: don't include near-duplicate chunks in context
- Token budget: limit total context size to fit in a prompt window

**Test Cases:**
```python
rag = RAGPipeline(chunker, store, retriever,
    prompt_template="Context:\n{context}\n\nQ: {question}\nA:")

# Ingest some documents
rag.ingest(["Python is a programming language created by Guido van Rossum.",
            "Java was developed by James Gosling at Sun Microsystems."])

# Query
prompt = rag.query("Who created Python?")
assert "Guido van Rossum" in prompt
assert "Q: Who created Python?" in prompt
```

---

## Advanced RAG Topics (L5-L8)

> **These topics are covered through two other paths:**
> - **Theory**: [DeepLearning.ai RAG course](https://learn.deeplearning.ai/courses/retrieval-augmented-generation/)
> - **Practice**: trialmatch project (`/Users/joelwang/Projects/trial/`) — Phases 3-5 implement hybrid search, criterion-level matching with evidence linking, exhaustive retrieval across 400K+ trials, and scoring evaluation
>
> Topics covered there: hybrid search (BM25 + vector + RRF), citation/grounding, exhaustive retrieval (map-reduce), RAG evaluation metrics
