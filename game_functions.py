# Zbiór funkcji pomocniczych do obsługiwania różnych aspektów gry, takich jak aktualizacje stanu gry

import pygame
import sys
import constants

def check_events(board, turn):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.MOUSEBUTTONDOWN and turn == constants.TURN_PLAYER:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            target = board.mouse_click(mouse_x, mouse_y)
            return target
    return None


def update_screen(settings, screen, board):
    # Aktualizuj obrazy na ekranie i przejdź do nowego ekranu.
    screen.fill(settings.bg_color)
    board.draw_board()
    pygame.display.flip()