import copy
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from agent import Agent
import constants
import game_functions as gf
import file
import os

class QNetwork(nn.Module):
    def __init__(self, input_dim, output_dim, freeze=False):
        super(QNetwork, self).__init__()
        self.fc1 = nn.Linear(input_dim, 64)
        self.fc2 = nn.Linear(64, 64)
        self.fc3 = nn.Linear(64, output_dim)
        if freeze:
            for param in self.parameters():
                param.requires_grad = False

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = self.fc3(x)
        return x

class CatAgent(Agent):
    def __init__(self, board, filename=None, learning_rate=0.001, discount_factor=0.95, epsilon=0.2):
        super().__init__(board)
        self.filename = filename
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.q_network = QNetwork(self.board.size * self.board.size, 6)
        self.target_network = QNetwork(self.board.size * self.board.size, 6, freeze=True)
        self.update_target_network()
        self.optimizer = optim.Adam(self.q_network.parameters(), lr=self.learning_rate)
        self.loss_fn = nn.MSELoss()
        self.memory = []
        self.batch_size = 32
        if os.path.isfile(filename):
            self.load()

    def update_target_network(self):
        self.target_network.load_state_dict(self.q_network.state_dict())

    def save(self):
        if self.filename:
            torch.save(self.q_network.state_dict(), self.filename)

    def load(self):
        if self.filename and os.path.isfile(self.filename):
            self.q_network.load_state_dict(torch.load(self.filename))

    def choose_action(self, state):
        if np.random.rand() < self.epsilon:
            return np.random.randint(6)
        else:
            with torch.no_grad():
                state_tensor = torch.tensor(state, dtype=torch.float32)
                q_values = self.q_network(state_tensor)
                for action, legal in enumerate(self.check_legality_of_moves(self.board.cat_pos)):
                    if not legal:
                        q_values[action] = constants.NEGATIVE_INF
                return torch.argmax(q_values).item()

    def store_transition(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))
        if len(self.memory) > 2000:
            self.memory.pop(0)

    def learn(self):
        if len(self.memory) < self.batch_size:
            return
        minibatch = random.sample(self.memory, self.batch_size)

        states = np.array([t[0] for t in minibatch])
        actions = np.array([t[1] for t in minibatch])
        rewards = np.array([t[2] for t in minibatch])
        next_states = np.array([t[3] for t in minibatch])
        dones = np.array([t[4] for t in minibatch])

        states_tensor = torch.tensor(states, dtype=torch.float32)
        actions_tensor = torch.tensor(actions, dtype=torch.int64).unsqueeze(1)
        rewards_tensor = torch.tensor(rewards, dtype=torch.float32)
        next_states_tensor = torch.tensor(next_states, dtype=torch.float32)
        dones_tensor = torch.tensor(dones, dtype=torch.float32)

        self.optimizer.zero_grad()

        q_values = self.q_network(states_tensor)
        next_q_values = self.target_network(next_states_tensor)

        q_value = q_values.gather(1, actions_tensor).squeeze(1)
        next_q_value = next_q_values.max(1)[0]
        expected_q_value = rewards_tensor + self.discount_factor * next_q_value * (1 - dones_tensor)

        loss = self.loss_fn(q_value, expected_q_value)
        loss.backward()
        self.optimizer.step()

        self.update_target_network()

    def get_move_q_learning(self, mode):
        current_pos = self.board.cat_pos
        state = np.array(self.board.board).flatten("F")
        action = self.choose_action(state)
        new_pos = self.move_based_on_action(current_pos, action)
        reward = self.calculate_reward(new_pos)
        new_state = np.array(self.board.board).flatten("F")
        done = self.board.is_exit(new_pos)
        if mode == constants.MODE_LEARNING: self.store_transition(state, action, reward, new_state, done)
        if mode == constants.MODE_LEARNING: self.learn()
        return new_pos

    def check_legality_of_moves(self, pos):
        row, col = pos
        output = []
        if row % 2 == 0:  # Parzysty wiersz
            delta = [(-1, -1), (-1, 0), (0, 1), (1, 0), (1, -1), (0, -1)] #[(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (0, -1)]
        else:  # Nieparzysty wiersz
            delta = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (0, -1)] # [(-1, -1), (-1, 0), (0, 1), (1, 0), (1, -1), (0, -1)]
        for (dr, dc) in delta:
            new_row = row + dr
            new_col = col + dc
            if self.board.is_empty( (new_row, new_col) ):
                output.append(True)
            else:
                output.append(False)
        return output

    def move_based_on_action(self, pos, action):
        row, col = pos
        if row % 2 == 0:  # Parzysty wiersz
            delta = [(-1, -1), (-1, 0), (0, 1), (1, 0), (1, -1), (0, -1)] #[(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (0, -1)]
        else:  # Nieparzysty wiersz
            delta = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (0, -1)] # [(-1, -1), (-1, 0), (0, 1), (1, 0), (1, -1), (0, -1)]
        new_row = row + delta[action][0]
        new_col = col + delta[action][1]
        return (new_row, new_col)

    def calculate_reward(self, new_pos):
        if self.board.is_exit(new_pos):
            return 500
        elif self.board.is_empty(new_pos):
            return -1
        else:
            return -10

    def get_move(self, mode):
        if mode == constants.MODE_GREEDY:
            return self.get_move_greedy()
        elif mode == constants.MODE_MANUAL:
            return self.get_move_manual()
        elif mode in [constants.MODE_LEARNING, constants.MODE_FROZEN]:
            return self.get_move_q_learning(mode)
        raise RuntimeError(f"Unsupported mode {mode}")

    def random_move(self):
        cat_row, cat_col = self.board.cat_pos
        neighbours = self._neighbours(cat_row, cat_col)
        if neighbours:
            return random.choice(neighbours)

    def get_move_greedy(self):
        dmap, pmap = self.BFSCatDistance()
        target_nodes, landlocked, _ = self.FindClosestExit(dmap, pmap)
        # self.__debug_print_dmap(dmap)
        if landlocked: return self.random_move()

        target = random.choice(target_nodes)
        while True:
            prev = random.choice(pmap[target[0]][target[1]])
            if prev == self.board.cat_pos:
                return target
            target = prev

    def get_move_manual(self):
        cat_row, cat_col = self.board.cat_pos
        neighbours = self._neighbours(cat_row, cat_col)
        target = gf.check_events(self.board, constants.TURN_PLAYER)
        if target in neighbours: return target
        return None
