# Project: DNS Resolver

## Level 1: DNS Packet Parser

**Implement DNS message encoding and decoding:**

```
class DNSHeader:
    id: int               # 16-bit query ID
    flags: int            # QR, opcode, AA, TC, RD, RA, rcode
    num_questions: int
    num_answers: int

class DNSQuestion:
    name: str             # "example.com"
    type: int             # 1=A, 28=AAAA, 5=CNAME, 15=MX, 2=NS
    cls: int              # 1=IN (internet)

class DNSRecord:
    name: str
    type: int
    cls: int
    ttl: int
    data: str             # "93.184.216.34" for A record

class DNSMessage:
    header: DNSHeader
    questions: list[DNSQuestion]
    answers: list[DNSRecord]

class DNSParser:
    encode_query(name: str, record_type: int = 1) -> bytes
    decode_response(data: bytes) -> DNSMessage
```

**Requirements:**
- Encode domain names in DNS wire format: `example.com` → `\x07example\x03com\x00`
- Parse DNS header: 12 bytes, big-endian fields
- Handle label compression: pointers (top 2 bits = 11) reference earlier names
- Encode a query message: header + question section
- Decode a response: header + questions + answer records
- Parse A records (IPv4), AAAA records (IPv6), CNAME records

**Test Cases:**
```python
parser = DNSParser()

# Encode a query
query = parser.encode_query("example.com", record_type=1)
assert query[:2] != b"\x00\x00"  # has a query ID
assert b"\x07example\x03com\x00" in query

# Decode (using a known response bytes)
response = parser.decode_response(sample_response_bytes)
assert response.header.num_answers > 0
assert response.answers[0].type == 1  # A record
assert response.answers[0].data == "93.184.216.34"
```

---

## Level 2: UDP Query + Recursive Resolution

**Send DNS queries over UDP and implement recursive resolution:**

```
class DNSResolver:
    __init__(root_servers: list[str] | None = None)
    resolve(name: str, record_type: int = 1) -> list[DNSRecord]
    query_server(server: str, name: str, record_type: int) -> DNSMessage
```

**Requirements:**
- Send UDP packets to DNS servers on port 53
- `query_server()`: send query, wait for response, parse it
- Timeout: retry after 2 seconds, give up after 3 attempts
- **Recursive resolution** (how DNS actually works):
  1. Ask root server for "example.com"
  2. Root returns NS for ".com" → ask that server
  3. ".com" NS returns NS for "example.com" → ask that server
  4. "example.com" NS returns the A record → done
- Follow CNAME chains: if answer is CNAME, resolve the CNAME target
- Use real root servers: `198.41.0.4` (a.root-servers.net), etc.

**Test Cases:**
```python
resolver = DNSResolver()

# Simple lookup
records = resolver.resolve("example.com")
assert len(records) > 0
assert records[0].type == 1  # A record

# CNAME chain
records = resolver.resolve("www.github.com")
# May return CNAME → then A record

# Direct server query
msg = resolver.query_server("8.8.8.8", "example.com", record_type=1)
assert msg.header.num_answers > 0
```

---

## Level 3: Caching + TTL

**Add a DNS cache that respects TTL:**

```
class DNSCache:
    __init__()
    put(name: str, record_type: int, records: list[DNSRecord]) -> None
    get(name: str, record_type: int) -> list[DNSRecord] | None
    is_expired(name: str, record_type: int) -> bool
    stats() -> dict       # hits, misses, evictions
```

**Requirements:**
- Cache DNS responses keyed by (name, record_type)
- Respect TTL: records expire after `ttl` seconds
- `get()` returns None for expired or missing entries
- Lazy expiration: clean up on access, not with background threads
- Cache negative results too: "NXDOMAIN" (domain doesn't exist) with short TTL
- Integrate with resolver: check cache before sending query
- Stats tracking: cache hits, misses, total queries saved

**Test Cases:**
```python
cache = DNSCache()
records = [DNSRecord("example.com", 1, 1, ttl=300, data="93.184.216.34")]
cache.put("example.com", 1, records)

# Cache hit
result = cache.get("example.com", 1)
assert result is not None
assert result[0].data == "93.184.216.34"

# Cache miss
assert cache.get("unknown.com", 1) is None

# Expiration
expired_records = [DNSRecord("short.com", 1, 1, ttl=1, data="1.2.3.4")]
cache.put("short.com", 1, expired_records)
import time; time.sleep(2)
assert cache.get("short.com", 1) is None  # expired

stats = cache.stats()
assert stats["hits"] >= 1
assert stats["misses"] >= 1
```

---

## Level 4: Local DNS Server

**Run a DNS server that answers queries from other programs:**

```
class DNSServer:
    __init__(host: str = "127.0.0.1", port: int = 5353,
             upstream: str = "8.8.8.8")
    start() -> None
    stop() -> None
    add_record(name: str, record_type: int, data: str, ttl: int) -> None
```

**Requirements:**
- Listen for UDP queries on a port
- For known records (added via `add_record`): respond directly
- For unknown records: forward query to upstream DNS server, cache + return response
- Handle multiple concurrent queries
- Custom records let you override DNS (like `/etc/hosts` but as a server)
- Test by pointing `dig` or `nslookup` at your server:
  ```
  dig @127.0.0.1 -p 5353 example.com
  ```
- Log queries: timestamp, client IP, domain, record type, response time

**Test Cases:**
```python
server = DNSServer("127.0.0.1", 5353, upstream="8.8.8.8")
server.add_record("myapp.local", 1, "127.0.0.1", ttl=3600)

# Start in background thread
# Query with resolver pointed at our server
resolver = DNSResolver()
records = resolver.query_server("127.0.0.1:5353", "myapp.local", 1)
assert records[0].data == "127.0.0.1"

# Unknown domain — forwards to upstream
records = resolver.query_server("127.0.0.1:5353", "example.com", 1)
assert len(records) > 0  # forwarded to 8.8.8.8 and cached
```
