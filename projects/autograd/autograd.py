from __future__ import annotations
import math
import random
import bisect

class Tensor:

    def __init__(self, data: float, _children: tuple=(), label: str=""):
        self.data = data
        self.grad = 0.0
        self._children = _children
        self.label = label
        self._backward = lambda: None

    def __add__(self, other) -> Tensor:
        if isinstance(other, (int, float)):
            other = Tensor(other)

        out = Tensor(self.data + other.data, _children=(self, other), label="+")
        def _backward():
            self.grad += 1.0 * out.grad
            other.grad += 1.0 * out.grad
        
        out._backward = _backward
        return out
    
    def __mul__(self, other) -> Tensor:
        if isinstance(other, (int, float)):
            other = Tensor(other)
        out = Tensor(self.data * other.data, _children=(self, other), label="*")
        
        def _backward():
            self.grad += other.data * out.grad
            other.grad += self.data * out.grad
        
        out._backward = _backward
        return out

    def __pow__(self, n) -> Tensor:
        assert isinstance(n, (int, float)), "exponent must be a number"
        out = Tensor(self.data ** n, _children=(self,), label="pow")

        def _backward():
            self.grad += n * self.data ** (n - 1) * out.grad
        
        out._backward = _backward
        return out

    def __neg__(self) -> Tensor:
        return -1 * self
    
    def __sub__(self, other) -> Tensor:
        return self + other.__neg__()
    
    def __radd__(self, other) -> Tensor:
        return self + other
    
    def __rmul__(self, other) -> Tensor:
        return self * other

    def tanh(self) -> Tensor:        
        e = math.exp(2 * self.data)
        out = Tensor((e - 1) / (e + 1), _children=(self, ), label="tanh")
        def _backward():
            self.grad += (1 - out.data ** 2) * out.grad
        
        out._backward = _backward
        return out
    
    def relu(self) -> Tensor:
        s = 1.0 if self.data > 0 else 0.0
        out = Tensor(s * self.data, _children=(self,), label="relu")
        
        def _backward():
            self.grad += s * out.grad
        
        out._backward = _backward
        return out
    
    def backward(self) -> None:
        # build topology of the compute graph
        topo = []
        visited = set()

        def build_graph(node):
            if node in visited:
                return
            visited.add(node)
            for child in node._children:
                build_graph(child)
            topo.append(node)         
        
        build_graph(self)
        self.grad = 1.0

        for node in reversed(topo):
            node._backward()


class Neuron:
    def __init__(self, n_inputs: int, activation: str = "relu"):
        self.activation = activation
        self.w = [Tensor(random.uniform(-1, 1)) for i in range(n_inputs)]
        self.b = Tensor(0.0)

    def __call__(self, x: list[Tensor]) -> Tensor:
        act = sum([wi * xi for wi, xi in zip(self.w, x)], self.b)
        return act.relu() if self.activation == "relu" else act
    
    def __repr__(self):
        return f"{'ReLU' if self.activation == "relu" else 'Linear'}Neuron({len(self.w)})"
    
    def parameters(self) -> list[Tensor]:
        return self.w + [self.b]

class Module:

    def zero_grad(self):
        for p in self.parameters():
            p.grad = 0

    def parameters(self):
        return []

class Layer(Module):
    def __init__(self, n_inputs: int, n_outputs: int, **kwargs):
        self.neurons = [Neuron(n_inputs, **kwargs) for _ in range(n_outputs)]

    def __call__(self, x: list[Tensor]) -> list[Tensor]:
        out = [n(x) for n in self.neurons]
        return out

    def __repr__(self):
        return f"Layer of [{', '.join(str(n) for n in self.neurons)}]"
    
    def parameters(self) -> list[Tensor]:
        return [p for n in self.neurons for p in n.parameters()]


class MLP(Module):
    def __init__(self, n_inputs: int, layer_sizes: list[int]):
        ls = [n_inputs] + layer_sizes
        self.layers = [Layer(ls[i], ls[i+1], activation='relu' if i<len(layer_sizes)-1 else None) for i in range(len(layer_sizes))]

    def __call__(self, x: list[Tensor]) -> list[Tensor]:
        for layer in self.layers:
            x = layer(x)
        return x

    def __repr__(self):
        return f"MLP of [{', '.join(str(layer) for layer in self.layers)}]"

    def parameters(self) -> list[Tensor]:
        return [p for layer in self.layers for p in layer.parameters()]


class SGD(Module):
    def __init__(self, parameters: list[Tensor], lr: float=0.01):
        self.lr = lr
        self.parameters = parameters
    
    def step(self) -> None:
        for i in range(len(self.parameters)):
            self.parameters[i].data += -self.lr * self.parameters[i].grad
    
    def zero_grad(self) -> None:
        for i in range(len(self.parameters)):
            self.parameters[i].grad = 0.0