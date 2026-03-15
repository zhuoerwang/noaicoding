# noaicoding.com — Build Software From Scratch

> 42 projects. From hash maps to coding agents to system design. All from scratch.

## Curriculum (ordered by difficulty + dependencies)

### Phase 1: Data Structure Foundations
*The building blocks everything else is built on.*

| # | Project | Key concepts | Difficulty |
|---|---------|---|---|
| 1 | KV Store | Hash map, TTL, persistence | Easy |
| 2 | LRU Cache | Doubly-linked list, eviction, O(1) get/put | Easy |
| 3 | Rate Limiter | Sliding window, token bucket, time-based algorithms | Easy-Medium |

### Phase 2: Parsing
*Three parsing techniques used in almost every project after this.*

| # | Project | Key concepts | Difficulty |
|---|---------|---|---|
| 4 | CSV Parser | State machine, streaming, windowed aggregation | Medium |
| 5 | JSON Parser | Lexer, recursive descent, serialization | Medium |
| 6 | Regex Engine | NFA, DFA, Thompson's construction, finite automata | Medium-Hard |

### Phase 3: Networking
*How the internet works, layer by layer.*

| # | Project | Key concepts | Difficulty | Dependencies |
|---|---------|---|---|---|
| 7 | DNS Resolver | UDP, packet parsing, recursive resolution, caching | Medium | |
| 8 | HTTP Server | TCP sockets, request parsing, routing | Medium | Parsing skills from Phase 2 |
| 9 | Web Crawler | BFS, async/await, retry with backoff | Medium | HTTP concepts |
| 10 | WebSocket | Upgrade handshake, frame protocol, connection lifecycle | Medium-Hard | HTTP Server |

### Phase 4: Core Systems
*Common patterns in backend engineering and system design interviews.*

| # | Project | Key concepts | Difficulty |
|---|---------|---|---|
| 11 | Load Balancer | Round robin, **consistent hashing**, health checks, sticky sessions | Medium |
| 12 | Task Scheduler | Priority queue, async workers, retry + DLQ | Medium |
| 13 | Pub/Sub | Message queues, patterns, delivery guarantees, backpressure | Medium |
| 14 | Spreadsheet Engine | DAG, topological sort, expression eval, cycle detection | Medium-Hard |
| 15 | Sandbox | Subprocess isolation, resource limits, virtual filesystem | Medium-Hard |

### Phase 5: Dev Tools
*Understand the tools you use every day.*

| # | Project | Key concepts | Difficulty |
|---|---------|---|---|
| 16 | Shell | REPL, pipes, redirection, job control, globbing | Medium-Hard |
| 17 | Git | Content-addressable storage (SHA-1), commits, branches, 3-way merge | Hard |
| 18 | Compression | Huffman coding, LZ77, DEFLATE, gzip format | Hard |

### Phase 6: Advanced Systems
*The hardest systems projects — builds on parsing + systems skills.*

| # | Project | Key concepts | Difficulty | Dependencies |
|---|---------|---|---|---|
| 19 | SQL Database | B-tree, SQL parser, query execution, joins, optimizer | Hard | Parsing (Phase 2), KV Store |
| 20 | Compiler | Lexer → parser → AST → interpreter → bytecode VM → optimizations | Very Hard | Parsing (Phase 2) |

### Phase 7: Game AI (bridge to ML)
*Classical AI — prerequisite for RL.*

| # | Project | Key concepts | Difficulty |
|---|---------|---|---|
| 21 | Checker Board Game | Minimax, alpha-beta pruning, evaluation functions | Medium-Hard |

### Phase 8: ML Foundations
*Build the entire ML stack from raw math to text generation.*

| # | Project | Key concepts | Difficulty | Dependencies |
|---|---------|---|---|---|
| 22 | BPE Tokenizer | Byte-pair encoding, merge rules, encode/decode | Medium | |
| 23 | Autograd Engine | Value class, backprop, chain rule, neuron/MLP, training | Hard | |
| 24 | Transformer | Embeddings, self-attention, multi-head, generation | Hard | BPE, Autograd concepts |

### Phase 9: ML Training
*How models are trained and improved.*

| # | Project | Key concepts | Difficulty | Dependencies |
|---|---------|---|---|---|
| 25 | Fine-tune + LoRA | Data prep, full fine-tune, low-rank adapters, merge | Hard | Autograd, Transformer |
| 26 | RL | Q-learning, REINFORCE, policy gradient, train Checker agent | Hard | Autograd, Checker |

### Phase 10: AI Applications (capstone)
*Wire everything together into real AI products.*

| # | Project | Key concepts | Difficulty | Dependencies |
|---|---------|---|---|---|
| 27 | RAG | Chunking, vector store, cosine similarity, retrieval + ranking | Medium-Hard | BPE |
| 28 | AI Chatbot | Conversation, streaming tokens, tool use, context window | Medium-Hard | BPE, Transformer |
| 29 | Coding Agent | Tool system, ReAct loop, coding tools, planning + error recovery | Hard | Chatbot, Sandbox |

### Phase 11: Crypto
*How money works underneath.*

| # | Project | Key concepts | Difficulty |
|---|---------|---|---|
| 30 | Bitcoin | SHA-256, ECDSA, transactions, Merkle tree, proof of work, blockchain | Hard |

### Phase 12: CodeSignal ICF-Style System Design
*Multi-level OOP system design — the format used in real hiring assessments (Uber, Dropbox, Roblox, Capital One).*

| # | Project | Key concepts | Difficulty |
|---|---------|---|---|
| 31 | Parking Lot | Vehicle types, spot fitting, fee calculation, reservations, peak pricing | Medium |
| 32 | Hotel Booking | Room types, date overlap, seasonal pricing, loyalty, overbooking, waitlist | Medium |
| 33 | Flight Reservation | Seat classes, fares, baggage, upgrades, multi-leg PNR, atomic booking | Medium |
| 34 | Employee Time Tracker | Check-in/out, overtime rules (daily/weekly), departments, payroll reports | Medium |
| 35 | Library Management | Multiple copies, waitlist, fines, recommendations, bulk operations | Medium |
| 36 | Connect Four | Variable grid, win detection (4 directions), score tracking, undo/redo | Easy-Medium |
| 37 | Blackjack | Card/deck/hand, ace logic, dealer AI, betting, multi-round stats | Medium |
| 38 | Bank | Accounts, tellers, transactions, branches, cash management, settlement | Medium |
| 39 | Movie Recommendation | Ratings, collaborative filtering, similarity scores, genre-based recs | Medium |
| 40 | Elevator | Directional priority, FIFO service, multi-elevator dispatch, state management | Medium |
| 41 | Chess | Piece movement, path blocking, turn enforcement, check/checkmate/stalemate | Medium-Hard |
| 42 | Flight Search | Route search, filters/sorting, multi-leg connections, recurring schedules | Medium |

---

## Dependency Graph

```
Phase 1: Foundations     Phase 2: Parsing      Phase 3: Networking
KV Store ─┐              CSV Parser            DNS Resolver (UDP)
LRU Cache ├─ no deps     JSON Parser               │
Rate Limiter             Regex Engine          HTTP Server (TCP) ──→ WebSocket
                              │                    │
          ┌───────────────────┤               Web Crawler
          ↓                   ↓
     SQL Database          Compiler

Phase 7-9: Game AI + ML
Checker ──────────────────→ RL (L4: train agent)
BPE Tokenizer ──→ Transformer ──→ Fine-tune + LoRA
Autograd ────────↗            ↘
                               ↘──→ AI Chatbot ──→ Coding Agent
                    RAG ──────↗          ↑
                                    Sandbox ──┘
```

---

## Skill Coverage Matrix

| Skill Area | Covered By |
|------------|-----------|
| Hash maps, KV stores | #1 KV Store, #2 LRU Cache |
| Sliding window, time algorithms | #3 Rate Limiter, #9 Web Crawler |
| State machine parsing | #4 CSV Parser |
| Recursive descent parsing | #5 JSON Parser |
| NFA, DFA, finite automata | #6 Regex Engine |
| UDP, DNS protocol | #7 DNS Resolver |
| TCP/HTTP protocol | #8 HTTP Server |
| Async, concurrency | #9 Web Crawler, #12 Task Scheduler |
| WebSocket protocol | #10 WebSocket |
| Consistent hashing, load distribution | #11 Load Balancer |
| Priority queues, worker pools | #12 Task Scheduler |
| Message queues, pub/sub | #13 Pub/Sub |
| DAG, topological sort, cycle detection | #14 Spreadsheet |
| Process isolation, sandboxing | #15 Sandbox |
| Process management, piping | #16 Shell |
| Content-addressable storage, merging | #17 Git |
| Huffman coding, LZ77, DEFLATE | #18 Compression |
| B-tree, SQL, query planning | #19 SQL Database |
| Bytecode, stack-based VM, optimization | #20 Compiler |
| Recursion, minimax, game trees | #21 Checker |
| Tokenization, BPE | #22 BPE Tokenizer |
| Backpropagation, autograd | #23 Autograd |
| Attention, transformers | #24 Transformer |
| Fine-tuning, LoRA adapters | #25 Fine-tune + LoRA |
| Q-learning, policy gradient | #26 RL |
| Vector search, retrieval | #27 RAG |
| Conversation, streaming generation | #28 AI Chatbot |
| Agent loop, tool dispatch, planning | #29 Coding Agent |
| Cryptography, blockchain, PoW | #30 Bitcoin |
| OOP design, extensibility, multi-level progression | #31–35 ICF System Design |

---

## All Projects

| # | Project | Directory | Test File | Status |
|---|---------|-----------|-----------|--------|
| 1 | KV Store | `database/` | `test_database.py` | ✅ Done |
| 2 | LRU Cache | `lru/` | `test_lru.py` | ✅ Done |
| 3 | Rate Limiter | `rate/` | `test_ratelimiter.py` | ✅ Done |
| 4 | CSV Parser | `csv_parser/` | `test_csv_parser.py` | Pending |
| 5 | JSON Parser | `json_parser/` | `test_json_parser.py` | New |
| 6 | Regex Engine | `regex/` | `test_regex.py` | New |
| 7 | DNS Resolver | `dns/` | `test_dns.py` | New |
| 8 | HTTP Server | `http_server/` | `test_http_server.py` | New |
| 9 | Web Crawler | `crawler/` | `test_crawler.py` | ✅ Done |
| 10 | WebSocket | `websocket/` | `test_websocket.py` | New |
| 11 | Load Balancer | `load_balancer/` | `test_load_balancer.py` | New |
| 12 | Task Scheduler | `scheduler/` | `test_scheduler.py` | Pending |
| 13 | Pub/Sub | `pubsub/` | `test_pubsub.py` | New |
| 14 | Spreadsheet | `spreadsheet/` | `test_spreadsheet.py` | Pending |
| 15 | Sandbox | `sandbox/` | `test_sandbox.py` | New |
| 16 | Shell | `shell/` | `test_shell.py` | New |
| 17 | Git | `git/` | `test_git.py` | New |
| 18 | Compression | `compression/` | `test_compression.py` | New |
| 19 | SQL Database | `database_sql/` | `test_database_sql.py` | New |
| 20 | Compiler | `compiler/` | `test_compiler.py` | New |
| 21 | Checker | `checker/` | `test_checker.py` | Pending |
| 22 | BPE Tokenizer | `bpe/` | `test_bpe.py` | Pending |
| 23 | Autograd | `autograd/` | `test_autograd.py` | New |
| 24 | Transformer | `transformer/` | `test_transformer.py` | New |
| 25 | Fine-tune + LoRA | `finetune/` | `test_finetune.py` | New |
| 26 | RL | `rl/` | `test_rl.py` | New |
| 27 | RAG | `rag/` | `test_rag.py` | New |
| 28 | AI Chatbot | `chatbot/` | `test_chatbot.py` | New |
| 29 | Coding Agent | `agent/` | `test_agent.py` | New |
| 30 | Bitcoin | `bitcoin/` | `test_bitcoin.py` | New |
| 31 | Parking Lot | `parking_lot/` | `test_parking_lot.py` | New |
| 32 | Hotel Booking | `hotel_booking/` | `test_hotel_booking.py` | New |
| 33 | Flight Reservation | `flight_reservation/` | `test_flight_reservation.py` | New |
| 34 | Employee Time Tracker | `time_tracker/` | `test_time_tracker.py` | New |
| 35 | Library Management | `library/` | `test_library.py` | New |
| 36 | Connect Four | `connect_four/` | `test_connect_four.py` | New |
| 37 | Blackjack | `blackjack/` | `test_blackjack.py` | New |
| 38 | Bank | `bank/` | `test_bank.py` | New |
| 39 | Movie Recommendation | `movie_recommendation/` | `test_movie_recommendation.py` | New |
| 40 | Elevator | `elevator/` | `test_elevator.py` | New |
| 41 | Chess | `chess/` | `test_chess.py` | New |
| 42 | Flight Search | `flight_search/` | `test_flight_search.py` | New |

---

## Completion Checklist

- [x] #1 KV Store
- [x] #2 LRU Cache
- [x] #3 Rate Limiter
- [ ] #4 CSV Parser
- [ ] #5 JSON Parser
- [ ] #6 Regex Engine
- [ ] #7 DNS Resolver
- [ ] #8 HTTP Server
- [x] #9 Web Crawler
- [ ] #10 WebSocket
- [ ] #11 Load Balancer
- [ ] #12 Task Scheduler
- [ ] #13 Pub/Sub
- [ ] #14 Spreadsheet
- [ ] #15 Sandbox
- [ ] #16 Shell
- [ ] #17 Git
- [ ] #18 Compression
- [ ] #19 SQL Database
- [ ] #20 Compiler
- [ ] #21 Checker
- [ ] #22 BPE Tokenizer
- [ ] #23 Autograd
- [ ] #24 Transformer
- [ ] #25 Fine-tune + LoRA
- [ ] #26 RL
- [ ] #27 RAG
- [ ] #28 AI Chatbot
- [ ] #29 Coding Agent
- [ ] #30 Bitcoin
- [ ] #31 Parking Lot
- [ ] #32 Hotel Booking
- [ ] #33 Flight Reservation
- [ ] #34 Employee Time Tracker
- [ ] #35 Library Management
- [ ] #36 Connect Four
- [ ] #37 Blackjack
- [ ] #38 Bank
- [ ] #39 Movie Recommendation
- [ ] #40 Elevator
- [ ] #41 Chess
- [ ] #42 Flight Search

---

## Evaluation Criteria

1. **Correctness** — All pytest tests pass for the level
2. **Extensibility** — Level N+1 doesn't require rewriting Level N
3. **Code quality** — Clear names, small functions, type hints
4. **Edge cases** — Empty inputs, duplicates, boundaries
5. **Complexity** — Meets O(?) requirements

---

## Rules of Engagement

1. Implement each level before seeing the next
2. No AI coding assistance (hints only)
3. Verbalize your Big-O when you submit
4. If stuck >20 min, ask for a hint
5. After each level, evaluate and get feedback
