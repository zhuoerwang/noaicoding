# Project 16: Pub/Sub

## Level 1: In-Memory Pub/Sub

**Implement a basic publish-subscribe system:**

```
class PubSub:
    __init__()
    subscribe(topic: str, callback: Callable[[str, Any], None]) -> int  # returns subscription ID
    unsubscribe(sub_id: int) -> bool
    publish(topic: str, message: Any) -> int   # returns number of subscribers notified
```

**Requirements:**
- Subscribers register a callback for a topic
- `publish()` calls all callbacks registered for that topic
- Each subscription gets a unique ID for unsubscribing
- `unsubscribe()` returns False if ID doesn't exist
- Multiple subscribers per topic, multiple topics per subscriber
- Callbacks receive (topic, message) arguments
- Publishing to a topic with no subscribers returns 0

**Test Cases:**
```python
ps = PubSub()
received = []
sub_id = ps.subscribe("news", lambda topic, msg: received.append(msg))

ps.publish("news", "hello")
assert received == ["hello"]

ps.publish("sports", "goal")  # different topic
assert received == ["hello"]  # unchanged

ps.unsubscribe(sub_id)
ps.publish("news", "world")
assert received == ["hello"]  # unsubscribed, no new messages
```

---

## Level 2: Pattern Matching + Message History

**Add wildcard subscriptions and message retention:**

```
class PubSub:
    __init__(history_size: int = 0)
    subscribe(topic: str, callback: Callable, replay: bool = False) -> int
    publish(topic: str, message: Any) -> int
    get_history(topic: str) -> list[Any]
```

**Requirements:**
- Wildcard topics: `"news.*"` matches `"news.sports"`, `"news.tech"`
- `"*"` matches all topics
- `history_size`: number of messages to retain per topic (0 = no history)
- `replay=True`: on subscribe, immediately replay retained messages to new subscriber
- `get_history()` returns messages in order (oldest first)
- History is per-topic, not per-pattern

**Test Cases:**
```python
ps = PubSub(history_size=5)
received = []
ps.subscribe("news.*", lambda t, m: received.append((t, m)))

ps.publish("news.sports", "goal")
ps.publish("news.tech", "launch")
assert received == [("news.sports", "goal"), ("news.tech", "launch")]

# Replay
late_msgs = []
ps.subscribe("news.sports", lambda t, m: late_msgs.append(m), replay=True)
assert late_msgs == ["goal"]  # replayed history

assert ps.get_history("news.sports") == ["goal"]
```

---

## Level 3: Async + Delivery Guarantees

**Add async publishing and at-least-once delivery:**

```
class AsyncPubSub:
    __init__(max_workers: int = 4)
    subscribe(topic: str, callback: Callable) -> int
    publish(topic: str, message: Any) -> None   # non-blocking
    acknowledge(sub_id: int, message_id: str) -> None
    pending(sub_id: int) -> list     # unacknowledged messages
    flush() -> None                  # wait for all deliveries
```

**Requirements:**
- `publish()` is non-blocking: messages are queued and delivered by worker threads
- Each message gets a unique ID
- At-least-once delivery: messages are redelivered if not acknowledged within timeout
- `pending()` returns unacknowledged messages for a subscriber
- `flush()` blocks until all queued messages are delivered
- Handle slow subscribers: queue messages, don't block publisher
- Handle subscriber errors: log error, continue delivering to others

**Test Cases:**
```python
ps = AsyncPubSub(max_workers=2)
received = []
sub_id = ps.subscribe("events", lambda t, m: received.append(m))

ps.publish("events", "msg1")
ps.publish("events", "msg2")
ps.flush()

assert "msg1" in received
assert "msg2" in received
```

---

## Level 4: Dead Letter Queue + Backpressure

**Add error handling and flow control:**

```
class AsyncPubSub:
    __init__(..., max_retries: int = 3, max_queue_size: int = 1000)
    on_dead_letter(callback: Callable) -> None
    stats() -> dict
```

**Requirements:**
- Messages that fail delivery `max_retries` times go to dead letter queue
- `on_dead_letter()`: register callback for failed messages
- Backpressure: when queue exceeds `max_queue_size`, `publish()` blocks or drops
- `stats()` returns: messages_published, messages_delivered, messages_failed, queue_depth
- Exponential backoff between retries
- Per-subscriber queue depth tracking

**Test Cases:**
```python
dead = []
ps = AsyncPubSub(max_retries=2)
ps.on_dead_letter(lambda topic, msg, error: dead.append(msg))

def bad_handler(topic, msg):
    raise Exception("always fails")

ps.subscribe("events", bad_handler)
ps.publish("events", "doomed")
ps.flush()

assert "doomed" in dead  # moved to dead letter after retries

stats = ps.stats()
assert stats["messages_failed"] >= 1
```
