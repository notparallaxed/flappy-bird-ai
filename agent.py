import multiprocessing as mp
import pygame, os, random
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

# Multiprocessing game call
def initialize_game(conn):
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    stdout = flappy.StdInOut(conn)
    flappy.main(screen, stdout, 1)

# Pipe call
parent_conn, child_conn = mp.Pipe()
p = mp.Process(target=initialize_game, args=(child_conn,))

# Agent classes
class Sensor():
    def __init__(self, parent_conn):
        self.conn = parent_conn
        self.metrics = {}

    def update(self):
        self.metrics = self.conn.recv()

class State():
    def __init__(self, sensor, size, position):
        self.block_size = size
        self.block_position = position
        self.dist_colision = -1
        self.reward = 0
        self.sensor = sensor
    
    def has_bird(self):
        x0bird, y0bird = self.sensor.metrics['bird']['pos'] 
        x1bird, y1bird = tuple(map(sum, zip(self.sensor.metrics['bird']['pos'], 
                                            self.sensor.metrics['bird']['size'])))               
        x0block, y0block = self.block_position
        x1block, y1block = tuple(map(sum, zip(self.block_position, self.block_size)))

        if(x0bird < x1block and y0bird < y1block 
            and x1bird > x0block and y1bird > y0block):
            return True
        
        return False

    #def has_colider():

actions = ["DO_BUMP", "DONT_BUMP"]

sensor = Sensor(parent_conn)

BLOCK_SIZE = (40,25)
states = {(i,j) : (State(sensor,BLOCK_SIZE, (200 + (j-1)*BLOCK_SIZE[0], (i-1)*BLOCK_SIZE[1]))) 
                        for i in range(1,33) for j in range(1,6)} 
                    

for i in range(1,33):
    print(states[(i,1)].block_position,
     "|", states[(i,2)].block_position,
     "|", states[(i,3)].block_position, 
     "|", states[(i,4)].block_position, 
     "|", states[(i,5)].block_position, )
        
# Run all
p.start()
while p.is_alive():
    parent_conn.send({'bump': False})
    sensor.update()

    for i in range(1,33):
        print(states[(i,1)].block_position, states[(i,1)].has_bird(),
         "|", states[(i,2)].block_position, states[(i,2)].has_bird(),
         "|", states[(i,3)].block_position, states[(i,3)].has_bird(), 
         "|", states[(i,4)].block_position, states[(i,4)].has_bird(), 
         "|", states[(i,5)].block_position, states[(i,5)].has_bird())