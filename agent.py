import multiprocessing as mp
import pygame, os
from flappy_game import flappy
origin_folder = os.getcwd()
os.chdir("./flappy_game")

# Game constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 800
Y_FLOOR_POS = (SCREEN_HEIGHT - 100)

X_SPEED = 10
BUMP_SPEED = 10
Y_GRAVITY = 1

def initialize_game(conn):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    stdout = flappy.StdInOut(conn)
    flappy.main(screen, stdout, 1)

parent_conn, child_conn = mp.Pipe()
p = mp.Process(target=initialize_game, args=(child_conn,))
p.start()
while p.is_alive():
    parent_conn.send({'bump': True})
    print(parent_conn.recv())









