import torch
from torch import nn
from collections import deque
from copy import deepcopy
import random
import time
from pathlib import Path
import os

torch.set_num_threads(1)


# Just the sensor values and an mlp for now
class QNetwork(nn.Module):
    #5 sensors and 3 actions for now
    def __init__(self, num_sensors=7, num_actions=3):
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
    def __init__(self, num_sensors=7, num_actions=3):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.num_sensors = num_sensors
        self.num_actions = num_actions

        # Online predicts, target evaluates choice
        self.online_network = QNetwork(num_sensors, num_actions).to(self.device)
        self.target_network = deepcopy(self.online_network)

        self.target_network.requires_grad_(False)
        self.target_network.eval()

        self.optimiser = torch.optim.Adam(self.online_network.parameters(), lr=1e-3)

        # Currently runs for 50,000 steps before epsilon becomes fixed at 5%
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
        exploring = random.random() < self.epsilon()

        if exploring:
            action = random.randrange(self.num_actions)
        else:
            sensors = torch.tensor(
                state["sensors"],
                dtype=torch.float32,
                device=self.device,
            ).unsqueeze(0)

            with torch.no_grad():
                q_values = self.online_network(sensors)

            action = q_values.argmax(dim=1).item()

        if self.environment_steps % 100 == 0:
            print(
                f"[CHOICE] action={action} "
                f"source={'random' if exploring else 'network'}",
                flush=True,
            )

        return action

    # add observed transitions to the memory array
    def observe(self, sensors, action, reward, next_sensors, terminated):
        if terminated:
            next_sensors = [0.0] * self.num_sensors

        self.memory.append((tuple(sensors), int(action), float(reward), tuple(next_sensors), bool(terminated)))
        self.environment_steps +=1

        if len(self.memory) < self.learning_starts:
            return None

        if self.environment_steps % 10 != 0:
            return None

        return self.learn()

    def learn(self):
        # put everything to cpu/gpu, predict q values and calculate loss
        batch = random.sample(self.memory, self.batch_size)
        states, actions, rewards, next_states, terminated = zip(*batch)

        states = torch.tensor(states, dtype=torch.float32, device=self.device)
        actions = torch.tensor(actions, dtype=torch.long, device=self.device)
        rewards = torch.tensor(rewards, dtype=torch.float32, device=self.device)
        next_states = torch.tensor(next_states, dtype=torch.float32, device=self.device)
        terminated = torch.tensor(terminated, dtype=torch.bool, device=self.device)

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


    # put model parameters in a file so you can pause and come back later. Make sure to check path names 
    def save(self, filename):
        filename = Path(filename)
        filename.parent.mkdir(parents=True, exist_ok=True)

        checkpoint = {
            "num_sensors": self.num_sensors,
            "num_actions": self.num_actions,
            "online": self.online_network.state_dict(),
            "target": self.target_network.state_dict(),
            "optimiser": self.optimiser.state_dict(),
            "memory": list(self.memory),
            "memory_capacity": self.memory.maxlen,
            "environment_steps": self.environment_steps,
            "learning_updates": self.learning_updates,
            "gamma": self.gamma,
            "batch_size": self.batch_size,
            "learning_starts": self.learning_starts,
        }

        temporary = filename.with_suffix(".tmp")
        torch.save(checkpoint, temporary)
        os.replace(temporary, filename)

        print(
            f"[SAVED] step={self.environment_steps} "
            f"updates={self.learning_updates}",
            flush=True,
        )


    # load file that presumably contains stored weights
    def load(self, filename):
        filename = Path(filename)

        if not filename.exists():
            print("[CHECKPOINT] Starting fresh", flush=True)
            return

        # load a checkpoint created by this program.
        checkpoint = torch.load(filename, map_location="cpu", weights_only=False)

        if (checkpoint["num_sensors"] != self.num_sensors or checkpoint["num_actions"] != self.num_actions):
            raise ValueError("Checkpoint sensor/action counts do not match")

        self.online_network.load_state_dict(checkpoint["online"])
        self.target_network.load_state_dict(checkpoint["target"])
        self.optimiser.load_state_dict(checkpoint["optimiser"])

        self.memory = deque(checkpoint["memory"],maxlen=checkpoint["memory_capacity"])

        self.environment_steps = checkpoint["environment_steps"]
        self.learning_updates = checkpoint["learning_updates"]
        self.gamma = checkpoint["gamma"]
        self.batch_size = checkpoint["batch_size"]
        self.learning_starts = checkpoint["learning_starts"]

        print(
            f"[RESUMED] step={self.environment_steps} "
            f"memory={len(self.memory)} "
            f"updates={self.learning_updates}",
            flush=True,
        )