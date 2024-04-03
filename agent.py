
import constants
import random

class Agent:
	def __init__(self, board):
		self.board = board
	
	def __neighbours(self, pos_row, pos_col):
		rows, cols = self.board.size, self.board.size
		d = [ (1,0), (0,1), (-1,0), (0,-1) ]
		if pos_row % 2 == 0:
			d.extend([ (1,-1), (-1,-1) ])
		else:
			d.extend( [ (-1,1), (1,1) ] )
		neighbours = []
		for dr, dc in d:
			new_row, new_col = pos_row + dr, pos_col + dc
			if 0 <= new_row < rows and 0 <= new_col < cols:
				if self.board.board[new_row][new_col] == constants.TILE_EMPTY:
					neighbours.append( (new_row, new_col) )
		return neighbours
	
	def __BFSvisit(self, prev_pos, pos, distance_map, previous_map, to_visit, visited):
		if (prev_pos, pos) in visited or (pos, prev_pos) in visited: return
		visited.add( (prev_pos, pos) )
	
		prev_row, prev_col = prev_pos
		row, col = pos
		distance = distance_map[prev_row][prev_col] + 1
		
		if distance_map[row][col] < distance:
			return
		elif distance_map[row][col] == distance:
			previous_map[row][col].append( (prev_row, prev_col) )
		elif distance_map[row][col] > distance:
			distance_map[row][col] = distance
			previous_map[row][col] = [ (prev_row, prev_col) ]
		
		to_visit.append( ((row, col), self.__neighbours( row, col )))
	
	def BFSCatDistance(self):
		rows, cols = self.board.size, self.board.size
		cat_row, cat_col = self.board.cat_pos
		distance_map = [[ constants.DISTANCE_UNREACHABLE for _ in range(cols) ] for _ in range(rows) ]
		previous_map = [[ [] for _ in range(cols) ] for _ in range(rows) ]
		distance_map[cat_row][cat_col] = 0 # this is where is the cat, so it takes 0 edge-traverses to get him there
		visited = set()
		
		to_visit = [ ( (cat_row, cat_col), self.__neighbours( cat_row, cat_col ) ) ]
		to_visit_next = []
		
		while to_visit:
			for pos, neighbours in to_visit:
				for neighbour in neighbours:
					self.__BFSvisit( pos, neighbour, distance_map, previous_map, to_visit_next, visited )
			to_visit = to_visit_next
			to_visit_next = []
		return distance_map, previous_map
	
	def FindClosestExit(self, dmap, pmap):
		rows, cols = self.board.size, self.board.size
		closest_distance = constants.DISTANCE_UNREACHABLE
		closest_nodes = []
		
		for row in range(rows):
			for col in [ 0, cols - 1 ]:
				if closest_distance < dmap[row][col]:
					continue
				elif closest_distance > dmap[row][col]:
					closest_distance = dmap[row][col]
					closest_nodes = [ (row, col) ]
				else:
					closest_nodes.append( (row, col) )
		for row in [ 0, rows - 1 ]:
			for col in range(cols):
				if closest_distance < dmap[row][col]:
					continue
				elif closest_distance > dmap[row][col]:
					closest_distance = dmap[row][col]
					closest_nodes = [ (row, col) ]
				else:
					closest_nodes.append( (row, col) )
		
		landlocked = (closest_distance == constants.DISTANCE_UNREACHABLE)
		return closest_nodes, landlocked
	
	def random_move(self):
		cat_row, cat_col = self.board.cat_pos
		neighbours = self.__neighbours( cat_row, cat_col )
		if neighbours:
			return random.choice( neighbours )
	
	def debug_print_dmap(self, dmap):
		for r in range(self.board.size):
			print( " ".join( [ str(i) for i in dmap[r] ] ) )
	
	def get_cat_move(self):
		dmap, pmap = self.BFSCatDistance()
		target_nodes, landlocked = self.FindClosestExit( dmap, pmap )
		#self.debug_print_dmap(dmap)
		if landlocked: return self.random_move()
		
		target = random.choice(target_nodes)
		while True:
			prev = random.choice( pmap[target[0]][target[1]] )
			if prev == self.board.cat_pos:
				return target
			target = prev
		