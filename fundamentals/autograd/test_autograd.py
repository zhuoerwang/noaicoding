"""
Tests for Autograd Engine
Run: pytest test_autograd.py -v
Run by level: pytest test_autograd.py -v -k "TestLevel1"
"""

import math
import pytest
from autograd import Tensor


# ============================================================
# Level 1: Tensor Class + Basic Operations
# ============================================================

class TestLevel1:
    def test_create_tensor(self):
        a = Tensor(2.0)
        assert a.data == 2.0
        assert a.grad == 0.0

    def test_create_tensor_with_label(self):
        a = Tensor(2.0, label="a")
        assert a.label == "a"

    def test_add_tensors(self):
        a = Tensor(2.0)
        b = Tensor(3.0)
        c = a + b
        assert isinstance(c, Tensor)
        assert c.data == 5.0

    def test_mul_tensors(self):
        a = Tensor(2.0)
        b = Tensor(3.0)
        d = a * b
        assert isinstance(d, Tensor)
        assert d.data == 6.0

    def test_add_tensor_and_float(self):
        a = Tensor(2.0)
        e = a + 1.0
        assert e.data == 3.0

    def test_mul_tensor_and_float(self):
        a = Tensor(2.0)
        e = a * 3.0
        assert e.data == 6.0

    def test_radd_float_plus_tensor(self):
        a = Tensor(2.0)
        e = 1.0 + a
        assert e.data == 3.0

    def test_rmul_float_times_tensor(self):
        a = Tensor(2.0)
        e = 3.0 * a
        assert e.data == 6.0

    def test_neg_tensor(self):
        a = Tensor(2.0)
        f = -a
        assert f.data == -2.0

    def test_sub_tensors(self):
        a = Tensor(2.0)
        b = Tensor(3.0)
        g = a - b
        assert g.data == -1.0

    def test_children_tracked(self):
        a = Tensor(2.0)
        b = Tensor(3.0)
        c = a + b
        assert a in c._children
        assert b in c._children

    def test_leaf_has_no_children(self):
        a = Tensor(5.0)
        assert len(a._children) == 0

    def test_chain_operations(self):
        a = Tensor(2.0)
        b = Tensor(3.0)
        c = a + b       # 5
        d = c * a       # 10
        assert d.data == 10.0


# ============================================================
# Level 2: Backpropagation
# ============================================================

class TestLevel2:
    # --- basic backward ---

    def test_add_backward(self):
        a = Tensor(2.0)
        b = Tensor(3.0)
        c = a + b
        c.backward()
        assert a.grad == 1.0
        assert b.grad == 1.0

    def test_mul_backward(self):
        a = Tensor(2.0)
        b = Tensor(3.0)
        c = a * b
        c.backward()
        assert a.grad == 3.0  # d/da = b
        assert b.grad == 2.0  # d/db = a

    def test_node_used_twice(self):
        """a is used in both mul and add — gradients must accumulate."""
        a = Tensor(2.0)
        b = Tensor(3.0)
        c = a * b       # 6.0
        d = c + a       # 8.0
        d.backward()
        assert a.grad == 4.0  # d/da = b + 1 = 3 + 1 = 4
        assert b.grad == 2.0  # d/db = a = 2

    def test_root_grad_is_one(self):
        a = Tensor(5.0)
        b = Tensor(3.0)
        c = a + b
        c.backward()
        assert c.grad == 1.0

    def test_neg_backward(self):
        a = Tensor(4.0)
        b = -a
        b.backward()
        assert a.grad == -1.0

    def test_sub_backward(self):
        a = Tensor(5.0)
        b = Tensor(3.0)
        c = a - b
        c.backward()
        assert a.grad == 1.0
        assert b.grad == -1.0

    # --- pow ---

    def test_pow_forward(self):
        a = Tensor(3.0)
        b = a ** 2
        assert b.data == 9.0

    def test_pow_backward(self):
        a = Tensor(3.0)
        b = a ** 2
        b.backward()
        assert a.grad == 6.0  # 2 * 3 = 6

    def test_pow_cube(self):
        a = Tensor(2.0)
        b = a ** 3
        b.backward()
        assert b.data == 8.0
        assert a.grad == 12.0  # 3 * 2^2 = 12

    def test_pow_in_expression(self):
        a = Tensor(2.0)
        b = Tensor(3.0)
        c = (a + b) ** 2  # (5)^2 = 25
        c.backward()
        assert c.data == 25.0
        assert a.grad == 10.0  # 2 * (a+b) * 1 = 10
        assert b.grad == 10.0

    # --- relu ---

    def test_relu_positive(self):
        a = Tensor(3.0)
        b = a.relu()
        assert b.data == 3.0

    def test_relu_negative(self):
        a = Tensor(-2.0)
        b = a.relu()
        assert b.data == 0.0

    def test_relu_positive_backward(self):
        a = Tensor(3.0)
        b = a.relu()
        b.backward()
        assert a.grad == 1.0

    def test_relu_negative_backward(self):
        a = Tensor(-2.0)
        b = a.relu()
        b.backward()
        assert a.grad == 0.0

    def test_relu_zero(self):
        a = Tensor(0.0)
        b = a.relu()
        assert b.data == 0.0

    # --- tanh ---

    def test_tanh_forward(self):
        a = Tensor(0.0)
        b = a.tanh()
        assert b.data == pytest.approx(0.0)

    def test_tanh_backward(self):
        a = Tensor(0.0)
        b = a.tanh()
        b.backward()
        assert a.grad == pytest.approx(1.0)  # 1 - tanh(0)^2 = 1

    def test_tanh_nonzero(self):
        a = Tensor(1.0)
        b = a.tanh()
        expected = math.tanh(1.0)
        assert b.data == pytest.approx(expected)
        b.backward()
        assert a.grad == pytest.approx(1 - expected ** 2)

    # --- complex expressions ---

    def test_mul_add_chain(self):
        """f = (a * b) + (b * c)"""
        a = Tensor(1.0)
        b = Tensor(2.0)
        c = Tensor(3.0)
        d = a * b       # 2
        e = b * c       # 6
        f = d + e       # 8
        f.backward()
        assert a.grad == 2.0   # d/da = b = 2
        assert b.grad == 4.0   # d/db = a + c = 1 + 3 = 4
        assert c.grad == 2.0   # d/dc = b = 2

    def test_nested_expression(self):
        """L = (a * b + c) ** 2"""
        a = Tensor(1.0)
        b = Tensor(2.0)
        c = Tensor(3.0)
        d = a * b + c   # 5
        L = d ** 2       # 25
        L.backward()
        assert L.data == 25.0
        assert a.grad == pytest.approx(20.0)  # 2*d * b = 2*5*2 = 20
        assert b.grad == pytest.approx(10.0)  # 2*d * a = 2*5*1 = 10
        assert c.grad == pytest.approx(10.0)  # 2*d * 1 = 10


# ============================================================
# Level 3: Neuron + MLP
# ============================================================
from autograd import Neuron, Layer, MLP

class TestLevel3:
    def test_neuron_output(self):
        n = Neuron(3)
        x = [Tensor(1.0), Tensor(2.0), Tensor(3.0)]
        out = n(x)
        assert isinstance(out, Tensor)

    def test_neuron_has_parameters(self):
        n = Neuron(3)
        # 3 weights + 1 bias
        assert len(n.parameters()) == 4

    def test_layer_output_count(self):
        layer = Layer(3, 4)
        x = [Tensor(1.0), Tensor(2.0), Tensor(3.0)]
        out = layer(x)
        assert len(out) == 4
        assert all(isinstance(o, Tensor) for o in out)

    def test_mlp_output(self):
        model = MLP(3, [4, 4, 1])
        x = [Tensor(1.0), Tensor(2.0), Tensor(3.0)]
        out = model(x)
        assert len(out) == 1
        assert isinstance(out[0], Tensor)

    def test_mlp_parameter_count(self):
        model = MLP(3, [4, 4, 1])
        params = model.parameters()
        expected = (3*4 + 4) + (4*4 + 4) + (4*1 + 1)  # 37
        assert len(params) == expected

    def test_mlp_backward_runs(self):
        """Backward should run without error through the whole network."""
        model = MLP(2, [3, 1])
        x = [Tensor(1.0), Tensor(2.0)]
        out = model(x)[0]
        out.backward()
        for p in model.parameters():
            assert isinstance(p.grad, float)


# ============================================================
# Level 4: Training Loop
# ============================================================
from autograd import SGD

class TestLevel4:
    def test_sgd_step(self):
        p = Tensor(5.0)
        p.grad = 2.0
        optimizer = SGD([p], lr=0.1)
        optimizer.step()
        assert p.data == pytest.approx(4.8)  # 5.0 - 0.1 * 2.0

    def test_sgd_zero_grad(self):
        p = Tensor(5.0)
        p.grad = 2.0
        optimizer = SGD([p], lr=0.1)
        optimizer.zero_grad()
        assert p.grad == 0.0

    def test_loss_decreases(self):
        import random
        random.seed(42)
        xs = [[2.0, 3.0], [-1.0, -2.0], [1.0, -1.0], [-2.0, 1.0]]
        ys = [1.0, -1.0, 1.0, -1.0]

        model = MLP(2, [4, 4, 1])
        optimizer = SGD(model.parameters(), lr=0.05)

        initial_loss = None
        final_loss = None
        for step in range(100):
            preds = [model([Tensor(x[0]), Tensor(x[1])])[0] for x in xs]
            loss = sum((p - Tensor(y)) ** 2 for p, y in zip(preds, ys))

            if step == 0:
                initial_loss = loss.data
            if step == 99:
                final_loss = loss.data

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        assert final_loss < initial_loss
