# Project 17: Bitcoin

## Level 1: Hashing + Digital Signatures

**Implement the cryptographic primitives (inspired by Karpathy's bitcoin):**

```
class SHA256:
    __init__()
    update(data: bytes) -> None
    digest() -> bytes
    hexdigest() -> str

class PrivateKey:
    __init__(secret: int | None = None)    # random if None
    sign(message: bytes) -> tuple[int, int]  # (r, s) signature

class PublicKey:
    __init__(private_key: PrivateKey)
    verify(message: bytes, signature: tuple[int, int]) -> bool
    address() -> str    # hash of public key, base58 encoded
```

**Requirements:**
- Implement SHA-256 from scratch (no hashlib): message padding, schedule, compression rounds
- Implement ECDSA on the secp256k1 curve (the Bitcoin curve)
- Elliptic curve point addition and scalar multiplication
- Private key: random 256-bit integer
- Public key: private_key * Generator point on the curve
- Address: RIPEMD160(SHA256(public_key)) + base58check encoding
- Sign: hash the message, generate k (nonce), compute (r, s)
- Verify: recover point from signature, check against public key

**Test Cases:**
```python
# SHA-256
hasher = SHA256()
hasher.update(b"hello")
assert hasher.hexdigest() == "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824"

# Key pair
sk = PrivateKey()
pk = PublicKey(sk)
sig = sk.sign(b"send 1 BTC to Alice")
assert pk.verify(b"send 1 BTC to Alice", sig) is True
assert pk.verify(b"send 100 BTC to Alice", sig) is False  # tampered
```

---

## Level 2: Transactions

**Implement the Bitcoin transaction model:**

```
class TxInput:
    prev_tx_hash: str     # hash of previous transaction
    output_index: int     # which output of that transaction
    signature: bytes      # proof of ownership

class TxOutput:
    amount: int           # satoshis
    address: str          # recipient address

class Transaction:
    __init__(inputs: list[TxInput], outputs: list[TxOutput])
    txid() -> str                    # SHA256(SHA256(serialized tx))
    sign(private_key: PrivateKey) -> None
    verify(utxo_set: dict) -> bool   # verify signatures + amounts
    serialize() -> bytes
```

**Requirements:**
- UTXO model: inputs reference previous outputs, outputs create new UTXOs
- Transaction ID is double-SHA256 of serialized transaction
- Signing: sign the transaction hash with the sender's private key
- Verification: check signature matches the UTXO's address
- Amount validation: sum(inputs) >= sum(outputs), difference is fee
- Coinbase transaction: special tx with no inputs (mining reward)
- Serialize to bytes (simplified format, not full Bitcoin wire format)

**Test Cases:**
```python
alice_sk = PrivateKey()
bob_sk = PrivateKey()
alice_pk = PublicKey(alice_sk)
bob_pk = PublicKey(bob_sk)

# Coinbase tx gives Alice 50 BTC
coinbase = Transaction(inputs=[], outputs=[TxOutput(50_0000_0000, alice_pk.address())])

# Alice sends 10 BTC to Bob
tx = Transaction(
    inputs=[TxInput(coinbase.txid(), 0, b"")],
    outputs=[
        TxOutput(10_0000_0000, bob_pk.address()),   # to Bob
        TxOutput(39_9999_0000, alice_pk.address()),  # change back
        # fee = 1000 satoshis
    ]
)
tx.sign(alice_sk)

utxo_set = {(coinbase.txid(), 0): coinbase.outputs[0]}
assert tx.verify(utxo_set) is True
```

---

## Level 3: Block + Proof of Work

**Implement blocks and mining:**

```
class Block:
    __init__(prev_hash: str, transactions: list[Transaction])
    version: int
    timestamp: float
    nonce: int
    target: int           # difficulty target
    merkle_root: str

    compute_merkle_root() -> str
    hash() -> str
    mine(target: int) -> None   # find nonce such that hash < target

class MerkleTree:
    __init__(tx_hashes: list[str])
    root() -> str
    proof(index: int) -> list[tuple[str, str]]    # (hash, side) pairs
    verify(tx_hash: str, proof: list, root: str) -> bool
```

**Requirements:**
- Block header: version, prev_hash, merkle_root, timestamp, target, nonce
- Block hash: double-SHA256 of the header
- Proof of work: increment nonce until `hash < target`
- Merkle tree: binary tree of transaction hashes
  - Leaf = SHA256(tx_hash), parent = SHA256(left + right)
  - If odd number of leaves, duplicate the last one
- Merkle proof: path of sibling hashes from leaf to root
- Verify a transaction is in a block using only the merkle proof (no full block)

**Test Cases:**
```python
# Merkle tree
tx_hashes = ["aaa", "bbb", "ccc", "ddd"]
tree = MerkleTree(tx_hashes)
root = tree.root()
proof = tree.proof(0)  # proof for first tx
assert MerkleTree.verify("aaa", proof, root) is True
assert MerkleTree.verify("zzz", proof, root) is False

# Mining
block = Block(prev_hash="0" * 64, transactions=[coinbase])
easy_target = 2 ** 240  # very easy target for testing
block.mine(easy_target)
assert int(block.hash(), 16) < easy_target
```

---

## Level 4: Blockchain + Validation

**Chain blocks together into a full blockchain:**

```
class Blockchain:
    __init__(difficulty: int = 20)    # number of leading zero bits
    create_genesis_block() -> Block
    add_block(transactions: list[Transaction]) -> Block
    validate_chain() -> bool
    get_balance(address: str) -> int
    get_utxo_set() -> dict
```

**Requirements:**
- Genesis block: first block with no previous hash
- Each block references the previous block's hash
- Validate entire chain: check hashes, proof of work, transactions
- Maintain UTXO set: update on each new block (consume inputs, create outputs)
- `get_balance()`: sum all UTXOs for an address
- Reject blocks with invalid transactions (double-spend, bad signatures)
- Difficulty adjustment: every N blocks, adjust target based on time elapsed

**Test Cases:**
```python
chain = Blockchain(difficulty=8)  # easy difficulty for testing

alice_sk = PrivateKey()
alice_pk = PublicKey(alice_sk)
bob_pk = PublicKey(PrivateKey())

# Mine genesis block with coinbase to Alice
genesis = chain.create_genesis_block()
assert chain.validate_chain() is True

# Alice sends to Bob
tx = Transaction(
    inputs=[TxInput(genesis.transactions[0].txid(), 0, b"")],
    outputs=[TxOutput(25_0000_0000, bob_pk.address()),
             TxOutput(24_9999_0000, alice_pk.address())]
)
tx.sign(alice_sk)
chain.add_block([tx])

assert chain.validate_chain() is True
assert chain.get_balance(bob_pk.address()) == 25_0000_0000

# Double spend should fail
tx_double = Transaction(
    inputs=[TxInput(genesis.transactions[0].txid(), 0, b"")],  # already spent!
    outputs=[TxOutput(50_0000_0000, alice_pk.address())]
)
tx_double.sign(alice_sk)
# chain.add_block([tx_double]) should raise or reject
```
