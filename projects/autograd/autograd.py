from __future__ import annotations
import math

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

    def __pow__(self, other) -> Tensor:
        if isinstance(other, (int, float)):
            other = Tensor(other)

        out = Tensor(self.data ** other.data, _children=(self, other), label="pow")
        
        def _backward():
            self.grad += other.data * self.data ** (other.data - 1) * out.grad
        
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
    pass


class Layer:
    pass


class MLP:
    pass


class SGD:
    pass

