
from board import Board
from settings import Settings
import constants

PRE_TURN_CALLBACK = "pre_turn"
POST_TURN_CALLBACK = "post_turn"

class Game:
    def __init__(self, cat_agent, player_agent, screen, callbacks, cat_mode, player_mode, random_traps = 10):
        self.cat_agent = cat_agent
        self.player_agent = player_agent
        self.settings = Settings()
        self.screen = screen
        self.board = Board(self.settings, screen, random_traps)
        self.cat_agent.board = self.board
        self.player_agent.board = self.board
        self.callbacks = callbacks
        self.cat_mode = cat_mode
        self.player_mode = player_mode
    def Play(self):
        turn = constants.TURN_PLAYER
        while True:
            if PRE_TURN_CALLBACK in self.callbacks: self.callbacks[PRE_TURN_CALLBACK](self)
            while True:
                if turn == constants.TURN_CAT:
                    if self.cat_move():
                        turn = constants.TURN_PLAYER
                        break
                elif turn == constants.TURN_PLAYER:
                    if self.player_move():
                        turn = constants.TURN_CAT
                        break
                else:
                    raise RuntimeError(f"Turn {turn}, something went horribly wrong")
            if POST_TURN_CALLBACK in self.callbacks: self.callbacks[POST_TURN_CALLBACK](self)
            dmap, pmap = self.cat_agent.BFSCatDistance()
            _, landlocked, _ = self.cat_agent.FindClosestExit(dmap, pmap)
            if landlocked:
                return -1
            if self.board.is_cat_trapped():
                return -1
            elif self.board.has_cat_escaped():
                return 1
    def cat_move(self):
        target = self.cat_agent.get_move(self.cat_mode)
        if target:
            new_x, new_y = target
            return self.board.place_cat(new_x, new_y)
        return False
    def player_move(self):
        target = self.player_agent.get_move(self.player_mode)
        if target:
            return self.board.place_trap(target[0], target[1])
        return False
