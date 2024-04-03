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

        # Ładowanie obrazka kota
        self.cat_image = pygame.image.load('images/cat.png')
        self.cat_image = pygame.transform.scale(self.cat_image, (ai_settings.tile_size,ai_settings.tile_size))  # Skalowanie obrazka do rozmiaru kafelka

    def draw_board(self):
        # Horizontal distance between hexagon centers
        tile_size = (self.settings.tile_size / 2) * math.sqrt(3)
        hex_width = tile_size * math.sqrt(3)

        for row in range(self.size):
            for col in range(self.size):
                # Odd rows are offset by half the width of a hexagon
                offset = hex_width / 2 if row % 2 != 0 else 0

                # Calculate the center position of the hexagon
                x = col * hex_width + offset
                y = row * (tile_size * 1.5)

                # Calculate the vertices of the hexagon
                hexagon = [
                    (x, y - tile_size),
                    (x + hex_width / 2, y - tile_size / 2),
                    (x + hex_width / 2, y + tile_size / 2),
                    (x, y + tile_size),
                    (x - hex_width / 2, y + tile_size / 2),
                    (x - hex_width / 2, y - tile_size / 2)
                ]

                # Draw the hexagon
                if self.board[row][col] == constants.TILE_TRAP:
                    pygame.draw.polygon(self.screen, self.settings.trap_color, hexagon)
                elif self.board[row][col] == constants.TILE_CAT:
                    self.screen.blit(self.cat_image, (x - tile_size / 2, y - tile_size))
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

    def move_cat(self):
        target = self.cat_agent.get_cat_move()
        if target:
            new_x, new_y = target

            # Aktualizacja pozycji kota
            self.board[self.cat_pos[0]][self.cat_pos[1]] = constants.TILE_EMPTY  # Usunięcie kota z poprzedniego miejsca
            self.cat_pos = (new_x, new_y)  # Aktualizacja pozycji kota
            self.board[new_x][new_y] = constants.TILE_CAT  # Umieszczenie kota na nowej pozycji
        
