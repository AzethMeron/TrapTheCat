import constants
import random
from agent import Agent


class CatAgent(Agent):
    def __init__(self, board):
        super().__init__(board)

    def FindClosestExit(self, dmap, pmap):
        rows, cols = self.board.size, self.board.size
        closest_distance = constants.DISTANCE_UNREACHABLE
        closest_nodes = []

        for row in range(rows):
            for col in [0, cols - 1]:
                if closest_distance < dmap[row][col]:
                    continue
                elif closest_distance > dmap[row][col]:
                    closest_distance = dmap[row][col]
                    closest_nodes = [(row, col)]
                else:
                    closest_nodes.append((row, col))
        for row in [0, rows - 1]:
            for col in range(cols):
                if closest_distance < dmap[row][col]:
                    continue
                elif closest_distance > dmap[row][col]:
                    closest_distance = dmap[row][col]
                    closest_nodes = [(row, col)]
                else:
                    closest_nodes.append((row, col))

        landlocked = (closest_distance == constants.DISTANCE_UNREACHABLE)
        return closest_nodes, landlocked

    def random_move(self):
        cat_row, cat_col = self.board.cat_pos
        neighbours = self._neighbours(cat_row, cat_col)
        if neighbours:
            return random.choice(neighbours)

    def __debug_print_dmap(self, dmap):
        for r in range(self.board.size):
            print(" ".join([str(i) for i in dmap[r]]))

    def get_cat_move(self):
        dmap, pmap = self.BFSCatDistance()
        target_nodes, landlocked = self.FindClosestExit(dmap, pmap)
        # self.__debug_print_dmap(dmap)
        if landlocked: return self.random_move()

        target = random.choice(target_nodes)
        while True:
            prev = random.choice(pmap[target[0]][target[1]])
            if prev == self.board.cat_pos:
                return target
            target = prev
