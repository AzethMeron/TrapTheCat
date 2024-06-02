# Główny plik, który uruchamia grę

import pygame
from settings import Settings
from board import Board
import game_functions as gf
import constants
import cat_agent
import player_agent
import game
import tqdm
from matplotlib import pyplot as plt

DISPLAY = True

def bound_value(val, min_val, max_val):
    return min(max( val, min_val ), max_val )

def post_turn_callback(playthrough):
    if playthrough.screen:
        gf.update_screen(playthrough.settings, playthrough.screen, playthrough.board)
        pygame.display.flip()
        pygame.time.wait(20)

def run_game():
    settings = Settings()
    screen = None
    if DISPLAY:
        pygame.init()
        screen = pygame.display.set_mode((settings.screen_width, settings.screen_height))
        pygame.display.set_caption("Trap The Cat")
    dummy_board = Board(settings, screen) # Mamy circular dependency, obchodzimy problem za pomocą dummy argumentu.
    cat = cat_agent.CatAgent(board=dummy_board, filename="cat_q_table", epsilon=0)
    player = player_agent.PlayerAgent(board=dummy_board, filename="player_q_table", epsilon=0.25)

    cat_wins = 0
    player_wins = 0

    initial_traps = 20
    min_traps = 0
    max_traps = 40
    swap_sum = 10000
    lambd = 0.998 # epsilon = epsilon * lambd
    result_sum = 0 # licznik zbierający wyniki gier, będziemy próbowali trzymać go blisko 0. Gdy kot wygrywa, Play zwraca 1, gdy gracz -1
    random_traps = initial_traps
    cat_mode = constants.MODE_LEARNING
    player_mode = constants.MODE_GREEDY
    loop = tqdm.tqdm( [i for i in range(100000)] )
    X = []
    Y = []

    for i in loop:
        playthrough = game.Game(cat, player, screen, random_traps=random_traps, cat_mode=cat_mode, player_mode=player_mode, callbacks={
            game.POST_TURN_CALLBACK : post_turn_callback,
            game.PRE_TURN_CALLBACK : post_turn_callback
        })
        r = playthrough.Play()
        if r == 1: cat_wins += 1
        if r == -1: player_wins += 1
        result_sum = bound_value(result_sum + r, -swap_sum, swap_sum)
        cat.save()
        player.save()
        if cat_mode == constants.MODE_LEARNING and result_sum >= swap_sum:
            cat_mode = constants.MODE_FROZEN
            player_mode = constants.MODE_LEARNING
            result_sum = 0
        elif player_mode == constants.MODE_LEARNING and result_sum <= -swap_sum:
            cat_mode = constants.MODE_LEARNING
            player_mode = constants.MODE_FROZEN
            result_sum = 0
        if cat_mode == constants.MODE_LEARNING and result_sum <= -swap_sum:
            random_traps = max(min_traps, random_traps-1)
        if player_mode == constants.MODE_LEARNING and result_sum >= swap_sum:
            random_traps = min(max_traps, random_traps+1)
        X.append(i)
        Y.append(result_sum)
        loop.set_postfix(result_sum=result_sum, player_mode=player_mode, cat_mode=cat_mode, player_wins=player_wins, cat_wins=cat_wins, random_traps=random_traps)
        if player_mode == constants.MODE_LEARNING: player.epsilon = player.epsilon * lambd
        if cat_mode == constants.MODE_LEARNING: cat.epsilon = cat.epsilon * lambd

    plt.figure()
    plt.plot(X, Y)
    plt.xlabel("iteration")
    plt.ylabel("result_sum")
    plt.title("AAA")
    plt.show()

    if DISPLAY:
        pygame.quit()

if __name__ == "__main__":
    run_game()

