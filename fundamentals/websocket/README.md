# Project 11: WebSocket

## Level 1: HTTP Upgrade Handshake

**Implement the WebSocket opening handshake:**

```
class WebSocketHandshake:
    parse_upgrade_request(raw: bytes) -> dict    # parse client's upgrade request
    build_accept_response(key: str) -> bytes     # build server's 101 response
    compute_accept_key(client_key: str) -> str   # SHA-1 + base64 per RFC 6455
```

**Requirements:**
- Parse client's HTTP upgrade request and validate required headers:
  - `Upgrade: websocket`
  - `Connection: Upgrade`
  - `Sec-WebSocket-Key: <base64 value>`
  - `Sec-WebSocket-Version: 13`
- Compute accept key: `base64(SHA1(client_key + "258EAFA5-E914-47DA-95CA-5AB0DC85B11B"))`
- Build `101 Switching Protocols` response with `Sec-WebSocket-Accept` header
- Reject non-upgrade requests with 400

**Test Cases:**
```python
hs = WebSocketHandshake()
key = "dGhlIHNhbXBsZSBub25jZQ=="
accept = hs.compute_accept_key(key)
assert accept == "s3pPLMBiTxaQ9kYGzzhZRbK+xOo="

resp = hs.build_accept_response(key)
assert b"101 Switching Protocols" in resp
assert b"s3pPLMBiTxaQ9kYGzzhZRbK+xOo=" in resp
```

---

## Level 2: Frame Parser

**Implement WebSocket frame encoding/decoding:**

```
class WebSocketFrame:
    fin: bool
    opcode: int       # 0x1=text, 0x2=binary, 0x8=close, 0x9=ping, 0xA=pong
    payload: bytes

class FrameParser:
    decode(data: bytes) -> WebSocketFrame
    encode(frame: WebSocketFrame) -> bytes
```

**Requirements:**
- Parse the wire format: FIN bit, opcode, mask bit, payload length
- Handle 3 payload length modes: 7-bit (<126), 16-bit (126), 64-bit (127)
- Client-to-server frames are masked (XOR with 4-byte mask key)
- Server-to-client frames are NOT masked
- Unmask client frames during decode
- Support text (0x1) and binary (0x2) opcodes

**Test Cases:**
```python
parser = FrameParser()
# Encode a simple text frame (server->client, no mask)
frame = WebSocketFrame(fin=True, opcode=0x1, payload=b"hello")
encoded = parser.encode(frame)
assert encoded[0] == 0x81  # FIN + text opcode

decoded = parser.decode(encoded)
assert decoded.payload == b"hello"
assert decoded.opcode == 0x1
assert decoded.fin is True
```

---

## Level 3: Connection Lifecycle

**Implement full connection management:**

```
class WebSocketConnection:
    __init__(socket)
    send(message: str) -> None
    receive() -> str | None
    close(code: int = 1000, reason: str = "") -> None
    ping() -> None
```

**Requirements:**
- `send()`: encode text frame and write to socket
- `receive()`: read from socket, decode frame, return payload
- Handle control frames: ping (auto-reply with pong), pong, close
- Close handshake: send close frame, wait for close frame back
- Handle fragmented messages: reassemble frames where FIN=0
- Timeout on receive: return None after N seconds

**Test Cases:**
```python
# Test with a mock socket or loopback
conn = WebSocketConnection(mock_socket)
conn.send("hello")
# Verify frame was written to socket

# Simulate receiving a ping, verify pong is auto-sent
# Simulate close handshake
```

---

## Level 4: Chat Server

**Build a simple WebSocket chat server:**

```
class ChatServer:
    __init__(host: str, port: int)
    start() -> None
    broadcast(message: str, exclude: WebSocketConnection | None = None) -> None
```

**Requirements:**
- Accept multiple WebSocket connections concurrently
- Broadcast messages to all connected clients
- Handle client disconnect gracefully (remove from client list)
- Support rooms/channels: clients join a room, messages broadcast within room
- Basic protocol: `{"type": "join", "room": "general"}`, `{"type": "message", "text": "hi"}`

**Test Cases:**
```python
# Start server, connect 2 clients
# Client 1 sends message, Client 2 receives it
# Client 2 disconnects, Client 1 sends message — no error
```
