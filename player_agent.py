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
        self.fc1 = nn.Linear(input_dim, input_dim)
        self.fc2 = nn.Linear(input_dim, input_dim)
        self.fc3 = nn.Linear(input_dim, input_dim)
        self.fc4 = nn.Linear(input_dim, output_dim)
        if freeze:
            for param in self.parameters():
                param.requires_grad = False

    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        x = torch.relu(self.fc3(x))
        x = self.fc4(x)
        return x
class PlayerAgent(Agent):
    def __init__(self, board, filename=None, learning_rate=0.001, discount_factor=0.95, epsilon=0.2):
        super().__init__(board)
        self.filename = filename
        self.epsilon = epsilon
        self.learning_rate = learning_rate
        self.discount_factor = discount_factor
        self.q_network = QNetwork(self.board.size * self.board.size, self.board.size * self.board.size)
        self.target_network = QNetwork(self.board.size * self.board.size, self.board.size * self.board.size, freeze=True)
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
        dmap, pmap = self.BFSCatDistance()
        if np.random.rand() < self.epsilon:
            return np.random.randint(self.board.size * self.board.size)
        else:
            with torch.no_grad():
                state_tensor = torch.tensor(state, dtype=torch.float32)
                q_values = self.q_network(state_tensor)
                for row in range(self.board.size):
                    for col in range(self.board.size):
                        idx = row + self.board.size*col
                        if dmap[row][col] == constants.DISTANCE_UNREACHABLE or not self.board.is_empty((row, col)):
                            q_values[idx] = constants.NEGATIVE_INF
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
        new_pos = self.move_based_on_action(action)
        reward = self.calculate_reward(new_pos)
        new_state = np.array(self.board.board).flatten("F")
        done = self.board.is_cat_trapped()
        if mode == constants.MODE_LEARNING: self.store_transition(state, action, reward, new_state, done)
        if mode == constants.MODE_LEARNING: self.learn()
        return new_pos

    def move_based_on_action(self, action):
        row = action % self.board.size
        col = action // self.board.size
        return (row, col)

    def calculate_reward(self, new_pos):
        old_dmap, old_pmap = self.BFSCatDistance()
        _, _, old_closest_distance = self.FindClosestExit(old_dmap, old_dmap)

        dummy_board = copy.deepcopy(self.board)
        dummy_board.place_trap( new_pos[0], new_pos[1] )
        dummy_agent = Agent(dummy_board)
        dmap, pmap = dummy_agent.BFSCatDistance()
        closest_nodes, landlocked, closest_distance = dummy_agent.FindClosestExit(dmap, pmap)

        if self.board.is_cat_trapped() or landlocked:
            return 500
        else:
            return closest_distance - old_closest_distance - 10

    def get_move(self, mode):
        if mode == constants.MODE_GREEDY:
            return self.get_move_greedy()
        elif mode == constants.MODE_MANUAL:
            return self.get_move_manual()
        elif mode in [constants.MODE_LEARNING, constants.MODE_FROZEN]:
            return self.get_move_q_learning(mode)
        raise RuntimeError(f"Unsupported mode {mode}")

    def get_move_manual(self):
        return gf.check_events(self.board, constants.TURN_PLAYER)

    def _get_weight(self, n, row, col, original_dmap, original_pmap):
        board = copy.deepcopy(self.board)
        board.place_trap(row, col)
        tmp_agent = Agent(board)
        dmap, pmap = tmp_agent.BFSCatDistance()
        exits = [ (row, col) for row in range(self.board.size) for col in [0, self.board.size-1] ] + [ (row, col) for col in range(self.board.size) for row in [0, self.board.size-1] ]
        exits = [ (row, col, dmap[row][col]) for (row, col) in exits  ]
        random.shuffle(exits)
        exits = sorted( exits, key=lambda x: x[2] )
        weight = sum( [ w for (r,c,w) in exits[:n] ] ) / n
        return (row, col, weight)

    def get_move_greedy(self, n = 5):
        dmap, pmap = self.BFSCatDistance()
        _, landlocked, _ = self.FindClosestExit(dmap, pmap)
        if not landlocked:
            parameters = [ (row, col) for row in range(self.board.size) for col in range(self.board.size) if self.board.is_empty( (row, col) ) and dmap[row][col] < self.board.size]
            results = [ self._get_weight(n, row, col, dmap, pmap) for (row, col) in parameters ]
            results = sorted(results, key=lambda x: -x[2])
            results = [ (row, col, weight) for (row, col, weight) in results if weight == results[0][2] ]
            results = sorted(results, key=lambda x: dmap[x[0]][x[1]])
            return results[0][0], results[0][1]
        else:
            return random.choice( self.board.pos_neighbours( self.board.cat_pos[0], self.board.cat_pos[1] ) )

    def get_move(self, mode):
        if mode == constants.MODE_GREEDY:
            return self.get_move_greedy()
        elif mode == constants.MODE_MANUAL:
            return self.get_move_manual()
        elif mode in [constants.MODE_LEARNING, constants.MODE_FROZEN]:
            return self.get_move_q_learning(mode)
        raise RuntimeError(f"Unsupported mode {mode}")
