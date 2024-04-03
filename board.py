# Klasa reprezentująca planszę gry - umieszczanie planszy, kota, pułapek

import pygame
from pygame.sprite import Sprite
import random
import math  

import pygame

import constants
import agent

class Board:
    def __init__(self, ai_settings, screen):
        self.screen = screen
        self.settings = ai_settings
        self.size = self.settings.board_size
        self.board = [[constants.TILE_EMPTY for _ in range(self.size)] for _ in range(self.size)]
        self.cat_pos = (self.size // 2, self.size // 2)
        self.board[self.cat_pos[0]][self.cat_pos[1]] = constants.TILE_CAT  # 2 reprezentuje kota na planszy
        self.cat_agent = agent.Agent(self)

        S, L, K = self.get_slk()

        # Ładowanie obrazka kota
        self.cat_image = pygame.image.load('images/cat.png')
        self.cat_image = pygame.transform.scale(self.cat_image, (2*S,2*K))  # Skalowanie obrazka do rozmiaru kafelka

    def mouse_click(self, mouse_x, mouse_y):
        # parameters for hexagonal grid, no standards here
        S, L, K = self.get_slk()
        for row in range(self.size):
            for col in range(self.size):
                # Odd rows are offset by half the width of a hexagon
                offset = S if row % 2 != 0 else 0
                # Calculate the center position of the hexagon
                x = S + col * S * 2 + offset
                y = K + row * (K + L / 2)
                # Check if clicked within this hex
                v = math.sqrt((mouse_x - x)**2 + (mouse_y - y)**2)
                if v <= S: return (row, col)
    def get_slk(self):
        S = self.settings.screen_width / (self.settings.board_size * 2 + 1)
        L = S * 2 / math.sqrt(3)
        K = L
        return S, L, K

    def draw_board(self):
        # parameters for hexagonal grid, no standards here
        S, L, K = self.get_slk()

        for row in range(self.size):
            for col in range(self.size):
                # Odd rows are offset by half the width of a hexagon
                offset = S if row % 2 != 0 else 0

                # Calculate the center position of the hexagon
                x = S + col * S * 2 + offset
                y = K + row * (K + L / 2)

                # Display rows and cols - for debugging
                #font = pygame.font.SysFont(None, 24)
                #img = font.render(f"({row},{col})", True, (0,0,0))
                #self.screen.blit(img, (x, y))

                # Calculate the vertices of the hexagon
                hexagon = [
                    (x, y - K),
                    (x + S, y - L / 2),
                    (x + S, y + L / 2),
                    (x, y + K),
                    (x - S, y + L / 2),
                    (x - S, y - L / 2)
                ]

                # Draw the hexagon
                if self.board[row][col] == constants.TILE_TRAP:
                    pygame.draw.polygon(self.screen, self.settings.trap_color, hexagon)
                elif self.board[row][col] == constants.TILE_CAT:
                    self.screen.blit(self.cat_image,
                                     (x - self.cat_image.get_width() / 2,
                                      y - 0.75*self.cat_image.get_height()))
                else:
                    pygame.draw.polygon(self.screen, self.settings.board_color, hexagon, 1)

    def place_trap(self, row, col):
        if self.board[row][col] == constants.TILE_EMPTY:
            self.board[row][col] = constants.TILE_TRAP
            return True
        return False

    def is_cat_trapped(self):
        directions = [(0, -1), (1, 0), (0, 1), (-1, 0)]  # Góra, Prawo, Dół, Lewo
        for dx, dy in directions:
            new_x, new_y = self.cat_pos[0] + dx, self.cat_pos[1] + dy
            if 0 <= new_x < self.size and 0 <= new_y < self.size and \
                    self.board[new_x][new_y] == constants.TILE_EMPTY:
                return False  # Istnieje dostępny ruch, kot nie jest zablokowany
        return True  # Kot jest zablokowany

    def has_cat_escaped(self):
        x, y = self.cat_pos
        return x == 0 or x == self.size - 1 or y == 0 or y == self.size - 1
    def debug_display(self):
        for rows in range(self.size):
            print( " ".join( [ str(i) for i in self.board[rows] ] ) )
        print()

    def move_cat(self):
        target = self.cat_agent.get_cat_move()
        if target:
            new_x, new_y = target

            # Aktualizacja pozycji kota
            self.board[self.cat_pos[0]][self.cat_pos[1]] = constants.TILE_EMPTY  # Usunięcie kota z poprzedniego miejsca
            self.cat_pos = (new_x, new_y)  # Aktualizacja pozycji kota
            self.board[new_x][new_y] = constants.TILE_CAT  # Umieszczenie kota na nowej pozycji
