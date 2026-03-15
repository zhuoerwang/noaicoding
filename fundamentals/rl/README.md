# Project 25: Reinforcement Learning

**Builds on:** Checker (Project 5) for L4

## Level 1: Environment + Agent Interface

**Implement the RL framework — environment, agent, and the interaction loop:**

```
class Environment:
    reset() -> State
    step(action: int) -> tuple[State, float, bool]  # (next_state, reward, done)
    action_space() -> int        # number of possible actions
    render() -> str              # text visualization

class GridWorld(Environment):
    __init__(width: int, height: int, goal: tuple[int, int],
             obstacles: list[tuple[int, int]] | None = None)

class Agent:
    choose_action(state: State) -> int
    learn(state, action, reward, next_state, done) -> None

class RandomAgent(Agent):
    # Baseline: picks random actions
```

**Requirements:**
- `Environment` is the standard RL interface (like OpenAI Gym, but from scratch)
- `step()` returns next state, reward, and done flag
- `GridWorld`: agent navigates a grid to reach a goal
  - Actions: 0=up, 1=right, 2=down, 3=left
  - Reward: -1 per step (encourages shortest path), +10 for reaching goal
  - Obstacles block movement (agent stays in place)
  - Done when agent reaches goal or max steps exceeded
- `render()`: print the grid with agent position, goal, obstacles
- `RandomAgent`: baseline that picks random actions (for comparison)

**Test Cases:**
```python
env = GridWorld(width=5, height=5, goal=(4, 4))
state = env.reset()
assert state == (0, 0)  # start position

next_state, reward, done = env.step(1)  # move right
assert next_state == (1, 0)
assert reward == -1
assert done is False

# Random agent should eventually reach goal (but inefficiently)
agent = RandomAgent(env.action_space())
total_reward = 0
state = env.reset()
for _ in range(1000):
    action = agent.choose_action(state)
    state, reward, done = env.step(action)
    total_reward += reward
    if done:
        break
```

---

## Level 2: Q-Learning (Tabular)

**Implement Q-learning with a Q-table:**

```
class QLearningAgent(Agent):
    __init__(state_size: int, action_size: int,
             lr: float = 0.1, gamma: float = 0.99,
             epsilon: float = 1.0, epsilon_decay: float = 0.995)
    choose_action(state: State) -> int          # epsilon-greedy
    learn(state, action, reward, next_state, done) -> None
    get_q_table() -> dict
```

**Requirements:**
- Q-table: `Q[state][action] = expected future reward`
- Update rule: `Q(s,a) += lr * (reward + gamma * max(Q(s')) - Q(s,a))`
- Epsilon-greedy exploration: with probability epsilon, choose random action
- Epsilon decay: reduce exploration over time as agent learns
- After training, agent should find the optimal (shortest) path
- Train for N episodes, track total reward per episode to show learning

**Q-learning algorithm:**
```
For each episode:
    state = env.reset()
    while not done:
        action = epsilon_greedy(state)
        next_state, reward, done = env.step(action)
        Q[s][a] += lr * (reward + gamma * max(Q[s']) - Q[s][a])
        state = next_state
    decay epsilon
```

**Test Cases:**
```python
env = GridWorld(5, 5, goal=(4, 4))
agent = QLearningAgent(state_size=25, action_size=4)

# Train for 500 episodes
rewards = []
for ep in range(500):
    state = env.reset()
    total = 0
    done = False
    while not done:
        action = agent.choose_action(state)
        next_state, reward, done = env.step(action)
        agent.learn(state, action, reward, next_state, done)
        state = next_state
        total += reward
    rewards.append(total)

# Agent should improve: later episodes have higher rewards
avg_first_50 = sum(rewards[:50]) / 50
avg_last_50 = sum(rewards[-50:]) / 50
assert avg_last_50 > avg_first_50  # learning happened

# Optimal path in 5x5 grid is 8 steps → reward should be close to -8 + 10 = 2
assert avg_last_50 > -5
```

---

## Level 3: Policy Gradient (REINFORCE)

**Implement the REINFORCE algorithm with a neural network policy:**

```
class PolicyNetwork:
    __init__(input_size: int, hidden_size: int, output_size: int)
    forward(state: list[float]) -> list[float]    # action probabilities
    parameters() -> list                           # all weights

class REINFORCEAgent(Agent):
    __init__(state_size: int, action_size: int, lr: float = 0.01)
    choose_action(state: State) -> int
    store_transition(state, action, reward) -> None
    update() -> float     # update policy at end of episode, return loss
```

**Requirements:**
- Policy network: small MLP that outputs action probabilities
  - Input: state (one-hot or features)
  - Output: softmax over actions
  - Can use your Autograd engine from Project 12, or numpy
- Sample actions from the probability distribution (not argmax)
- Collect full episode trajectory: (state, action, reward) tuples
- At episode end, compute returns: `G_t = sum(gamma^k * r_{t+k})`
- Policy gradient: `loss = -sum(log(pi(a|s)) * G_t)`
- Update weights to increase probability of high-reward actions
- Baseline subtraction: subtract mean return to reduce variance

**Test Cases:**
```python
env = GridWorld(4, 4, goal=(3, 3))
agent = REINFORCEAgent(state_size=16, action_size=4, lr=0.01)

rewards = []
for ep in range(1000):
    state = env.reset()
    done = False
    total = 0
    while not done:
        action = agent.choose_action(state)
        next_state, reward, done = env.step(action)
        agent.store_transition(state, action, reward)
        state = next_state
        total += reward
    agent.update()  # update policy after each episode
    rewards.append(total)

# Should learn, but more slowly than Q-learning
avg_last_100 = sum(rewards[-100:]) / 100
assert avg_last_100 > sum(rewards[:100]) / 100
```

---

## Level 4: Train an Agent to Play Checkers

**Connect RL to your Checker game from Project 5:**

```
class CheckerEnvironment(Environment):
    __init__(opponent: str = "random")  # "random" or "minimax"
    reset() -> State
    step(action: int) -> tuple[State, float, bool]
    legal_actions() -> list[int]

class CheckerAgent(Agent):
    __init__(method: str = "q_learning")   # or "reinforce"
    train(env: CheckerEnvironment, episodes: int) -> None
    save(path: str) -> None
    load(path: str) -> None
```

**Requirements:**
- Wrap your Checker game (Project 5) as an RL environment
- State representation: flatten board into features
- Action space: enumerate all legal moves, agent picks an index
- Reward shaping:
  - +1 for winning, -1 for losing, 0 for draw
  - +0.1 for capturing a piece, +0.3 for getting a king
  - -0.01 per move (encourages faster wins)
- Train against a random opponent first, then against minimax
- Track win rate over training to show improvement
- Self-play: optionally train against copies of itself

**Test Cases:**
```python
env = CheckerEnvironment(opponent="random")
agent = CheckerAgent(method="q_learning")

# Train
win_rates = agent.train(env, episodes=1000)

# Agent should beat random opponent most of the time
assert win_rates[-1] > 0.7  # >70% win rate vs random

# Test against minimax (harder)
env_hard = CheckerEnvironment(opponent="minimax")
# Agent might not beat minimax, but should put up a fight
```
