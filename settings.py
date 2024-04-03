# Plik ustawień, w którym definiujemy wszystkie stałe i konfiguracje gry

class Settings:
    def __init__(self):
        self.screen_width = 600
        self.screen_height = 600
        self.bg_color = (188, 158, 130)
        self.board_size = 11
        self.tile_size = self.screen_width // self.board_size
        self.board_color = (255, 255, 255)
        self.trap_color = (155, 103, 60)
        self.cat_color = (0, 0, 255)