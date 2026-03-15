# Project 28: Load Balancer

## Level 1: Basic Algorithms

**Implement core load balancing algorithms:**

```
class Server:
    __init__(host: str, port: int, weight: int = 1)
    healthy: bool
    active_connections: int

class RoundRobin:
    __init__(servers: list[Server])
    next() -> Server

class WeightedRoundRobin:
    __init__(servers: list[Server])
    next() -> Server

class LeastConnections:
    __init__(servers: list[Server])
    next() -> Server
    connect(server: Server) -> None
    disconnect(server: Server) -> None
```

**Requirements:**
- `RoundRobin`: cycle through servers sequentially 0 → 1 → 2 → 0 → 1 → ...
- `WeightedRoundRobin`: servers with higher weight get proportionally more requests
  - Weight=3 gets 3x the traffic of weight=1
  - Use smooth weighted round robin (no bursts to one server)
- `LeastConnections`: pick the server with fewest active connections
  - Track connection count with connect/disconnect calls
  - Break ties with round robin
- All algorithms skip unhealthy servers
- Empty/all-unhealthy server list returns None

**Test Cases:**
```python
servers = [Server("a", 8080), Server("b", 8081), Server("c", 8082)]

rr = RoundRobin(servers)
assert rr.next().host == "a"
assert rr.next().host == "b"
assert rr.next().host == "c"
assert rr.next().host == "a"  # wraps around

# Skip unhealthy
servers[1].healthy = False
assert rr.next().host == "a"
assert rr.next().host == "c"  # skips b

# Weighted
weighted_servers = [Server("a", 8080, weight=3), Server("b", 8081, weight=1)]
wrr = WeightedRoundRobin(weighted_servers)
picks = [wrr.next().host for _ in range(8)]
assert picks.count("a") == 6  # 3x weight
assert picks.count("b") == 2

# Least connections
lc = LeastConnections(servers)
lc.connect(servers[0])
lc.connect(servers[0])
assert lc.next().host == "c"  # a has 2 conns, c has 0
```

---

## Level 2: Consistent Hashing

**Implement consistent hashing for distributed systems:**

```
class ConsistentHash:
    __init__(nodes: list[str] | None = None, virtual_nodes: int = 150)
    add_node(node: str) -> None
    remove_node(node: str) -> None
    get_node(key: str) -> str
    get_distribution() -> dict[str, int]    # node -> count of keys assigned
```

**Requirements:**
- Hash ring: map nodes and keys to positions on a circular hash space (0 to 2^32)
- Each real node gets `virtual_nodes` positions on the ring (for even distribution)
- `get_node(key)`: hash the key, walk clockwise on ring, return first node
- `add_node()`: only remaps keys between new node and its predecessor (minimal disruption)
- `remove_node()`: only remaps keys that were assigned to removed node
- Key property: adding/removing a node only moves ~1/N of keys (not all of them)
- Use SHA-256 or MD5 for hashing (or implement your own hash)
- `get_distribution()`: show how many of N test keys map to each node

**Why consistent hashing matters:**
```
Naive hash (key % N):  add 1 server → ~100% of keys remapped
Consistent hashing:    add 1 server → ~1/N of keys remapped
```

**Test Cases:**
```python
ch = ConsistentHash(["server1", "server2", "server3"])

# Same key always maps to same node
assert ch.get_node("user:123") == ch.get_node("user:123")

# Distribution should be roughly even
dist = {}
for i in range(10000):
    node = ch.get_node(f"key:{i}")
    dist[node] = dist.get(node, 0) + 1
# Each server should get ~3333 keys (within reasonable variance)
for count in dist.values():
    assert 2500 < count < 4500

# Add a node — most keys should NOT move
before = {f"key:{i}": ch.get_node(f"key:{i}") for i in range(1000)}
ch.add_node("server4")
after = {f"key:{i}": ch.get_node(f"key:{i}") for i in range(1000)}
moved = sum(1 for k in before if before[k] != after[k])
assert moved < 350  # roughly 1/4 should move (1/N), not all

# Remove a node — only its keys move
ch.remove_node("server2")
assert ch.get_node("user:123") is not None  # still works
```

---

## Level 3: Health Checks + Failover

**Add health monitoring and automatic failover:**

```
class HealthChecker:
    __init__(interval: float = 5.0, timeout: float = 2.0,
             healthy_threshold: int = 2, unhealthy_threshold: int = 3)
    check(server: Server) -> bool
    start() -> None           # background health check loop
    stop() -> None
    on_healthy(callback: Callable) -> None
    on_unhealthy(callback: Callable) -> None

class LoadBalancer:
    __init__(servers: list[Server], algorithm: str = "round_robin")
    route(request: dict) -> Server
    add_server(server: Server) -> None
    remove_server(server: Server) -> None
```

**Requirements:**
- Health check: send TCP connection or HTTP GET to each server periodically
- State machine per server:
  - `healthy → unhealthy`: after `unhealthy_threshold` consecutive failures
  - `unhealthy → healthy`: after `healthy_threshold` consecutive successes
  - Prevents flapping (one failed check doesn't immediately mark unhealthy)
- Callbacks: notify when server goes healthy/unhealthy
- `LoadBalancer` automatically removes unhealthy servers from rotation
- Failover: if selected server fails mid-request, retry on next healthy server
- Drain: gracefully remove a server (finish existing connections, no new ones)

**Test Cases:**
```python
lb = LoadBalancer(servers, algorithm="round_robin")

# All healthy — normal routing
server = lb.route({"path": "/api"})
assert server.healthy is True

# Mark one unhealthy
servers[0].healthy = False
# Should never route to unhealthy server
for _ in range(100):
    s = lb.route({"path": "/api"})
    assert s.host != servers[0].host

# Health check thresholds
hc = HealthChecker(unhealthy_threshold=3)
# Needs 3 consecutive failures before marking unhealthy
```

---

## Level 4: Sticky Sessions + Rate Limiting

**Add session affinity and per-server rate limiting:**

```
class SessionAffinity:
    __init__(method: str = "cookie", ttl: int = 3600)
    get_server(request: dict) -> Server | None   # return pinned server if exists
    pin(request: dict, server: Server) -> None

class LoadBalancer:
    __init__(..., sticky: bool = False, rate_limit: int | None = None)
    route(request: dict) -> Server | None    # None if all servers rate-limited
    stats() -> dict
```

**Requirements:**
- Sticky sessions: route same client to same server
  - Cookie-based: set a cookie with server ID, read on subsequent requests
  - IP-based: hash client IP to consistent server (uses consistent hashing!)
  - If pinned server is unhealthy, re-pin to new server
- Rate limiting per server: max N requests per second per backend
  - If server is at limit, route to next available
  - If all servers at limit, return None (503 response)
- Stats: requests per server, current connections, error rates, p50/p99 latency
- Connection pooling: reuse TCP connections to backend servers
- Request logging: log method, path, selected server, response time

**Test Cases:**
```python
lb = LoadBalancer(servers, sticky=True, rate_limit=100)

# Same client goes to same server
req = {"client_ip": "1.2.3.4", "path": "/api"}
server1 = lb.route(req)
server2 = lb.route(req)
assert server1.host == server2.host  # sticky

# Different clients may go to different servers
req2 = {"client_ip": "5.6.7.8", "path": "/api"}
server3 = lb.route(req2)
# server3 may or may not equal server1

# Rate limiting
lb2 = LoadBalancer(servers, rate_limit=2)
lb2.route({"path": "/1"})
lb2.route({"path": "/2"})
result = lb2.route({"path": "/3"})  # may route to different server

stats = lb.stats()
assert "requests_per_server" in stats
```
