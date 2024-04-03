# Główny plik, który uruchamia grę

import pygame
import sys
from settings import Settings
from board import Board
import game_functions as gf
import constants

def run_game():
    pygame.init()
    ai_settings = Settings()
    screen = pygame.display.set_mode((ai_settings.screen_width, ai_settings.screen_height))
    pygame.display.set_caption("Trap The Cat")

    board = Board(ai_settings, screen)
    turn = constants.TURN_PLAYER

    while True:
        turn = gf.check_events(board, turn)

        if turn == constants.TURN_CAT:
            board.move_cat()
            if board.is_cat_trapped():
                print("Gracz wygrywa!")
                break # albo ekran wygranej
            elif board.has_cat_escaped():
                print("Kot uciekł, gracz przegrywa!")
                break # albo ekran przegranej
            turn = constants.TURN_PLAYER

        gf.update_screen(ai_settings, screen, board)
        pygame.display.flip()

if __name__ == "__main__":
    run_game()
