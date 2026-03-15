import math
import time
from dataclasses import dataclass
from collections import defaultdict, deque
from collections.abc import Callable
                                                                                                
@dataclass                                                                                        
class BucketState:
    tokens: float
    last_refill: float


class RateLimiter:
    def __init__(self, max_requests: int, window_seconds: int, strategy: str = "fixed",
                 bucket_capacity: int | None = None, refill_rate: float | None = None):
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._strategy = strategy
        self._bucket_capacity = bucket_capacity
        self._refill_rate = refill_rate
        self._fixed_window: float | None = None # for fixed window
        self._counter = defaultdict(int) # for fixed window
        self._logs = defaultdict(deque) # for sliding window
        self._buckets = {} # for token bucket
        self._callback = None
   
    def allow(self, client_id: str) -> bool:
        if self._strategy == "fixed":
            allowed = self._allow_fixed(client_id)
        elif self._strategy == "sliding_log":
            allowed = self._allow_sliding(client_id)
        else:
            allowed = self._allow_bucket(client_id)
        
        if not allowed and self._callback:
            self._callback(client_id)
        
        return allowed

    def _allow_fixed(self, client_id: str) -> bool:
        now = time.time()
        self._fixed_peek(now)
        if self._counter[client_id] >= self._max_requests:
            return False
        
        self._counter[client_id] += 1
        return True
    
    def _allow_sliding(self, client_id: str) -> bool:
        now = time.time()
        self._sliding_peek(client_id, now)

        if len(self._logs[client_id]) >= self._max_requests:
            return False
        
        self._logs[client_id].append(now)
        return True
    
    def _allow_bucket(self, client_id: str) -> bool:
        now = time.time()
        self._bucket_peek(client_id, now)
        if self._buckets[client_id].tokens < 1:
            return False
        
        self._buckets[client_id].tokens -= 1
        return True

    def _fixed_peek(self, now: float) -> None:
        window = math.floor(now / self._window_seconds)
        if window != self._fixed_window:
            self._fixed_window = window
            self._counter = defaultdict(int)

    def _sliding_peek(self, client_id: str, now: float) -> None:
        cutoff = now - self._window_seconds
        log_queue = self._logs[client_id]
        
        # Prune expired entries
        while len(log_queue) > 0 and log_queue[0] < cutoff:
            log_queue.popleft()
    
    def _bucket_peek(self, client_id: str, now: float) -> None:
        assert self._bucket_capacity is not None
        assert self._refill_rate is not None
        
        if client_id not in self._buckets:
            self._buckets[client_id] = BucketState(self._bucket_capacity, now)
        state = self._buckets[client_id]
        tokens, last_refill = state.tokens, state.last_refill
        tokens += (now - last_refill) * self._refill_rate
        self._buckets[client_id] = BucketState(min(self._bucket_capacity, tokens), now)

    def remaining(self, client_id: str) -> int:
        """How many requests left in current window/bucket"""
        now = time.time()
        if self._strategy == "fixed":
            self._fixed_peek(now)
            return self._max_requests - self._counter[client_id]
        elif self._strategy == "sliding_log":
            self._sliding_peek(client_id, now)
            return int(self._max_requests - len(self._logs[client_id]))
        else:
            self._bucket_peek(client_id, now)
            return int(self._buckets[client_id].tokens)

    def retry_after(self, client_id: str) -> float | None:
        """seconds until next request allowed None if not limited"""
        if self.remaining(client_id) > 0:
            return None
        now = time.time()
        if self._strategy == "fixed":
            assert self._fixed_window is not None
            wait = (self._fixed_window + 1) * self._window_seconds - now
        elif self._strategy == "sliding_log":
            wait = self._logs[client_id][0] + self._window_seconds - now
        else:
            assert self._refill_rate is not None
            state = self._buckets[client_id]
            # Only 1 exact token needed
            wait = state.last_refill + 1 / self._refill_rate - now
        return wait

    def on_reject(self, callback: Callable[[str], None]) -> None:
        """called with client_id when rejected"""
        self._callback = callback