# Project 10: HTTP Server

## Level 1: Request Parser

**Implement a class `HTTPServer`:**

```
class HTTPRequest:
    method: str          # "GET", "POST", etc.
    path: str            # "/index.html"
    headers: dict[str, str]
    body: str

class HTTPParser:
    parse(raw: bytes) -> HTTPRequest
```

**Requirements:**
- Parse raw HTTP/1.1 request bytes into structured object
- Handle request line: `GET /path HTTP/1.1\r\n`
- Parse headers: `Key: Value\r\n` until empty line `\r\n`
- Body is everything after the blank line
- Headers are case-insensitive (store lowercase keys)
- Handle missing body (GET requests)
- Handle `Content-Length` header to know body size

**Test Cases:**
```python
parser = HTTPParser()
req = parser.parse(b"GET /index.html HTTP/1.1\r\nHost: localhost\r\n\r\n")
assert req.method == "GET"
assert req.path == "/index.html"
assert req.headers["host"] == "localhost"
assert req.body == ""

req2 = parser.parse(b"POST /api HTTP/1.1\r\nContent-Length: 13\r\n\r\n{\"key\":\"val\"}")
assert req2.method == "POST"
assert req2.body == '{"key":"val"}'
```

---

## Level 2: Response Builder + Routing

**Add classes:**

```
class HTTPResponse:
    __init__(status_code: int, body: str = "", headers: dict | None = None)
    to_bytes() -> bytes

class Router:
    add_route(method: str, path: str, handler: Callable) -> None
    resolve(method: str, path: str) -> Callable | None
```

**Requirements:**
- Build valid HTTP/1.1 response bytes: status line + headers + body
- Auto-set `Content-Length` header
- Status codes: 200, 201, 400, 404, 500 with correct reason phrases
- Router maps (method, path) pairs to handler functions
- Return 404 handler if no route matches
- Support path parameters: `/users/:id` matches `/users/42`

**Test Cases:**
```python
resp = HTTPResponse(200, body="hello")
raw = resp.to_bytes()
assert b"HTTP/1.1 200 OK" in raw
assert b"Content-Length: 5" in raw
assert raw.endswith(b"hello")

router = Router()
router.add_route("GET", "/hello", lambda req: HTTPResponse(200, "hi"))
handler = router.resolve("GET", "/hello")
assert handler is not None
assert router.resolve("GET", "/notfound") is None
```

---

## Level 3: TCP Socket Server

**Add server class:**

```
class HTTPServer:
    __init__(host: str = "localhost", port: int = 8080)
    router: Router
    start() -> None      # blocking, listens for connections
    stop() -> None
```

**Requirements:**
- Listen on TCP socket using Python's `socket` module (no `http.server`)
- Accept connections, read raw bytes, parse request, route, send response
- Handle multiple sequential requests (one at a time)
- Graceful shutdown on `stop()`
- Handle malformed requests with 400 response
- Handle handler exceptions with 500 response

**Test Cases:**
```python
server = HTTPServer("localhost", 9090)
server.router.add_route("GET", "/ping", lambda req: HTTPResponse(200, "pong"))
# Start server in background thread
# Use urllib or socket to send request
# Verify response
```

---

## Level 4: Concurrent Connections

**Extend `HTTPServer`:**

```
__init__(..., max_workers: int = 4)
```

**Requirements:**
- Handle multiple connections concurrently using threads or asyncio
- Thread pool with `max_workers` limit
- Keep-alive support: reuse connections for multiple requests
- Connection timeout: close idle connections after N seconds
- Basic access logging: method, path, status code, response time

**Test Cases:**
```python
# Send 10 concurrent requests, all should complete
# Verify keep-alive reuses connection
# Verify idle timeout closes connection
```
