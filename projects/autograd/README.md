# Project 12: Autograd Engine

## Level 1: Tensor Class + Basic Operations

**Implement a scalar autograd engine:**

```
class Tensor:
    __init__(data: float, _children: tuple = (), label: str = "")
    data: float
    grad: float              # gradient, initialized to 0.0
    _children: tuple         # parent tensors that produced this
    _backward: Callable      # closure that computes local gradients (default: no-op)
    __add__(other) -> Tensor
    __mul__(other) -> Tensor
    __neg__() -> Tensor
    __sub__(other) -> Tensor
    __radd__(other) -> Tensor
    __rmul__(other) -> Tensor
```

**Requirements:**
- Single `Tensor` class — all operations return `Tensor` instances (no subclasses)
- Each operation creates a new `Tensor` and attaches a `_backward` closure that knows the local gradient rule
- The closure captures references to input tensors and multiplies by `out.grad` (chain rule)
- Support `Tensor + Tensor`, `Tensor * Tensor`, `float + Tensor`, etc. via `__radd__`/`__rmul__`
- Wrap raw floats into `Tensor` inside `__add__`/`__mul__` when needed
- No gradient computation yet — just build the expression graph

**Test Cases:**
```python
a = Tensor(2.0)
b = Tensor(3.0)
c = a + b
assert c.data == 5.0

d = a * b
assert d.data == 6.0

e = a + 1.0
assert e.data == 3.0

f = -a
assert f.data == -2.0

g = a - b
assert g.data == -1.0

# float on left side
h = 1.0 + a
assert h.data == 3.0
```

---

## Level 2: Backpropagation

**Add backward pass and more operations to `Tensor`:**

```
class Tensor:
    backward() -> None       # topological sort + reverse + call _backward
    __pow__(n: float) -> Tensor
    relu() -> Tensor
    tanh() -> Tensor
```

**Requirements:**
- `backward()` does: set root grad to 1.0 → topological sort → call `_backward()` in reverse order
- Each operation (`__pow__`, `relu`, `tanh`) attaches its own `_backward` closure to the result
- Handle nodes used in multiple expressions (gradients accumulate with `+=`)

**Gradient rules (each implemented as a closure inside the operation):**
```
__add__:   self.grad += out.grad;          other.grad += out.grad
__mul__:   self.grad += other.data * out.grad;  other.grad += self.data * out.grad
__pow__:   self.grad += n * self.data^(n-1) * out.grad
relu():    self.grad += (1.0 if self.data > 0 else 0.0) * out.grad
tanh():    self.grad += (1 - out.data^2) * out.grad
```

**Test Cases:**
```python
a = Tensor(2.0)
b = Tensor(3.0)
c = a * b       # 6.0
d = c + a       # 8.0 (a is used twice!)
d.backward()

assert a.grad == 4.0   # d/da = b + 1 = 3 + 1 = 4 (chain rule, a used twice)
assert b.grad == 2.0   # d/db = a = 2

# Power
a = Tensor(3.0)
b = a ** 2       # 9.0
b.backward()
assert a.grad == 6.0   # 2 * 3 = 6

# ReLU
a = Tensor(-2.0)
b = a.relu()
assert b.data == 0.0
b.backward()
assert a.grad == 0.0

# tanh
a = Tensor(0.0)
b = a.tanh()
b.backward()
assert a.grad == 1.0   # 1 - tanh(0)^2 = 1

# Verify against PyTorch (if available)
```

---

## Level 3: Neuron + MLP

**Build a neural network from Tensor objects:**

```
class Neuron:
    __init__(n_inputs: int, activation: str = "relu")
    __call__(x: list[Tensor]) -> Tensor
    parameters() -> list[Tensor]

class Layer:
    __init__(n_inputs: int, n_outputs: int, activation: str = "relu")
    __call__(x: list[Tensor]) -> list[Tensor]
    parameters() -> list[Tensor]

class MLP:
    __init__(n_inputs: int, layer_sizes: list[int])
    __call__(x: list[Tensor]) -> list[Tensor]
    parameters() -> list[Tensor]
```

**Requirements:**
- `Neuron`: stores weights + bias as `Tensor` objects, computes `activation(sum(w*x) + b)`
- `Layer`: list of neurons, applies each to the same input
- `MLP`: chain of layers, output of one feeds into next
- Last layer has no activation (linear output)
- `parameters()` returns flat list of all `Tensor` weights and biases
- Initialize weights randomly (small values, e.g., uniform(-1, 1))

**Test Cases:**
```python
model = MLP(3, [4, 4, 1])  # 3 inputs, two hidden layers of 4, 1 output
x = [Tensor(1.0), Tensor(2.0), Tensor(3.0)]
out = model(x)
assert len(out) == 1
assert isinstance(out[0], Tensor)

params = model.parameters()
assert len(params) == (3*4 + 4) + (4*4 + 4) + (4*1 + 1)  # weights + biases
```

---

## Level 4: Training Loop

**Train the MLP on a simple dataset:**

```
class SGD:
    __init__(parameters: list[Tensor], lr: float = 0.01)
    step() -> None       # update parameters: p.data -= lr * p.grad
    zero_grad() -> None  # reset all gradients to 0
```

**Requirements:**
- Implement mean squared error loss: `sum((pred - target)^2) / n`
- Training loop: forward pass -> compute loss -> backward -> update -> zero grad
- Train on a simple binary classification (e.g., XOR-like data)
- Loss should decrease over iterations
- Print loss every N steps to show convergence

**Test Cases:**
```python
# Simple dataset: learn to predict y = 1 if sum(x) > 0 else -1
xs = [[2.0, 3.0], [-1.0, -2.0], [1.0, -1.0], [-2.0, 1.0]]
ys = [1.0, -1.0, 1.0, -1.0]

model = MLP(2, [4, 4, 1])
optimizer = SGD(model.parameters(), lr=0.05)

# Train for 100 steps
initial_loss = None
final_loss = None
for step in range(100):
    # forward
    preds = [model([Tensor(x[0]), Tensor(x[1])])[0] for x in xs]
    loss = sum((p - Tensor(y)) ** 2 for p, y in zip(preds, ys))

    if step == 0:
        initial_loss = loss.data
    if step == 99:
        final_loss = loss.data

    # backward
    optimizer.zero_grad()
    loss.backward()
    optimizer.step()

assert final_loss < initial_loss  # loss decreased
```
