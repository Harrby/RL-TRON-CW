import torch
from torch import nn
from collections import deque
from copy import deepcopy
import random
import time


class DontCrashAgent:
    def __init__(self, threshold=0.45, cooldown=0.10):
        self.threshold = threshold
        self.cooldown = cooldown
        self.last_turn_time = float("-inf")

    def get_action(self, state):
        sensors = state["sensors"]

        right_distance = min(sensors[0], sensors[1])
        front_distance = sensors[2]
        left_distance = min(sensors[3], sensors[4])

        if front_distance >= self.threshold:
            return 0

        now = time.monotonic()
        if now - self.last_turn_time < self.cooldown:
            return 0

        if left_distance > right_distance:
            return 1
        else:
            return 2
        





# Just the sensor values and an mlp for now
class QNetwork(nn.Module):
    #5 sensors and 3 actions for now
    def __init__(self, num_sensors=5, num_actions=3):
        super().__init__()

        self.network = nn.Sequential(
            nn.Linear(num_sensors, 128),
            nn.ReLU(),
            nn.Linear(128,128),
            nn.ReLU(),
            nn.Linear(128, num_actions),
        )

    def forward(self, sensors):
        return self.network(sensors)


class DoubleQNetwork:
    def __init__(self, num_sensors=5, num_actions=3):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.num_sensors = num_sensors
        self.num_actions = num_actions
        self.online_network = QNetwork(num_sensors, num_actions).to(self.device)
        self.target_network = deepcopy(self.online_network)

        self.target_network.requires_grad_(False)
        self.target_network.eval()

        self.optimiser = torch.optim.Adam(self.online_network.parameters(), lr=1e-3)

        self.memory = deque(maxlen=50000)
        self.batch_size = 64
        self.learning_starts = 1000
        self.gamma = 0.99

        self.environment_steps = 0
        self.learning_updates = 0

    def epsilon(self):
        epsilon_decay = min(self.environment_steps/ 50000, 1.0)
        return 1.00 - 0.95*epsilon_decay

    # picks best action available (epsilon greedy)
    def get_action(self, state):
        if random.random < self.epsilon:
            return random.randrange(self.num_actions)
        else:
            sensors = torch.tensor(state["sensors"], dtype=torch.float32, device = self.device).unsqueeze(0)

        with torch.no_grad():
            q_values = self.online_network(sensors)
        return q_values.argmax(dim=1).item()

    # add observed transitions to the memory array
    def observe(self, sensors, action, reward, next_sensors, terminated):
        if terminated:
            next_sensors = [0.0] * self.num_sensors

        self.memory.append((tuple(sensors), int(action), float(reward), tuple(next_sensors), bool(terminated)))
        self.environment_steps +=1

        if len(self.memory) ( self.learning_starts):
            return None

        if self.environment_steps % 10 != 0:
            return None

        return self.learn()

    def learn(self):
        # construct a random batch of observed transitions to use to update weights
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, terminated = zip(*batch)

        states = torch.tensor(states, dtype=torch.float32, device=self.device)
        actions = torch.tensor(actions, dtype=torch.float32, device=self.device)
        rewards = torch.tensor(rewards, dtype=torch.float32, device=self.device)
        next_states = torch.tensor(next_states, dtype=torch.float32, device=self.device)
        terminated = torch.tensor(terminated, dtype=torch.float32, device=self.device)

        predicted_q = self.online_network(states).gather(1, actions.unsqueeze(1)).squeeze(1)

        with torch.no_grad():
            next_actions = self.online_network(next_states).argmax(dim=1, keepdim=True)
            next_q = self.target_network(next_states).gather(1, next_actions).squeeze(1)

        targets = (rewards + self.gamma * (~terminated).float() * next_q)

        loss = nn.functional.smooth_l1_loss(predicted_q, targets)

        self.optimiser.zero_grad()
        loss.backward()
        nn.utils.clip_grad_norm_(self.online_network.parameters(), max_norm=10.0)
        self.optimiser.step()

        self.learning_updates+=1

        if self.learning_updates % 1000 == 0:
            self.target_network.load_state_dict(self.online_network.state_dict())

        return loss.item()