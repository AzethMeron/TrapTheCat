import constants

class Agent:
    def __init__(self, board):
        self.board = board

    def _neighbours(self, pos_row, pos_col):
        neighbours = self.board.pos_neighbours(pos_row, pos_col)
        neighbours = [(row, col) for (row, col) in neighbours if
                      self.board.board[row][col] == constants.TILE_EMPTY]
        return neighbours

    def __bfs_visit(self, prev_pos, pos, distance_map, previous_map, to_visit,
                    visited):
        if (prev_pos, pos) in visited or (pos, prev_pos) in visited: return
        visited.add((prev_pos, pos))

        prev_row, prev_col = prev_pos
        row, col = pos
        distance = distance_map[prev_row][prev_col] + 1

        if distance_map[row][col] < distance:
            return
        elif distance_map[row][col] == distance:
            previous_map[row][col].append((prev_row, prev_col))
        elif distance_map[row][col] > distance:
            distance_map[row][col] = distance
            previous_map[row][col] = [(prev_row, prev_col)]

        to_visit.append(((row, col), self._neighbours(row, col)))

    def BFSCatDistance(self):
        rows, cols = self.board.size, self.board.size
        cat_row, cat_col = self.board.cat_pos
        distance_map = [[constants.DISTANCE_UNREACHABLE for _ in range(cols)] for _ in range(rows)]
        previous_map = [[[] for _ in range(cols)] for _ in range(rows)]
        distance_map[cat_row][cat_col] = 0  # this is where is the cat, so it takes 0 edge-traverses to get him there
        visited = set()

        to_visit = [((cat_row, cat_col), self._neighbours(cat_row, cat_col))]
        to_visit_next = []

        while to_visit:
            for pos, neighbours in to_visit:
                for neighbour in neighbours:
                    self.__bfs_visit(pos, neighbour, distance_map,
                                     previous_map, to_visit_next, visited)
            to_visit = to_visit_next
            to_visit_next = []
        return distance_map, previous_map

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
        return closest_nodes, landlocked, closest_distance