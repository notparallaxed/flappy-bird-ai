import multiprocessing as mp
import pygame, os, math
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

class Actuator():
    def __init__(self, parent_conn):
        self.conn = parent_conn
    
    def do_bump(self):
        self.conn.send({'bump': True})

    def dont_bump(self):
        self.conn.send({'bump': False})

def calculate_dist_bird_pipe(bird_pos, pipes_pos):
    dist_bird_pipe_bot = math.dist(bird_pos, pipes_pos['bottom']['pos'])
    dist_bird_pipe_top = math.dist(bird_pos, pipes_pos['top']['pos'])

    return round((dist_bird_pipe_bot + dist_bird_pipe_top)/2)

class State():
    def __init__(self, bird_metrics, pipes_metrics):
        self.bird_metrics = bird_metrics
        self.pipes_metrics = pipes_metrics
        
        #self.dist_bird_floor = (Y_FLOOR_POS - self.bird_metrics['pos'][1])
        self.dist_bird_pipes = calculate_dist_bird_pipe(bird_metrics['pos'], pipes_metrics)
        
        self.actions_q_value = {
            "DO_BUMP" : 0,
            "DONT_BUMP" : 0
        }

        self.index = (bird_metrics['pos'][1], self.dist_bird_pipes)

    def get_max_q_action(self):
        if (self.actions_q_value['DO_BUMP'] > self.actions_q_value['DONT_BUMP']):
            return 'DO_BUMP'
        
        return 'DONT_BUMP'

sensor = Sensor(parent_conn)
actuator = Actuator(parent_conn)                 

latest_points = 0
latest_attempts = 1

goals = [(latest_points + 1)]

reward_history = []
actual_reward = 0 
states = []
actual_state = None

# Run all
p.start()
while p.is_alive():
    actuator.dont_bump()
    sensor.update()

    dist_bird_pipes = calculate_dist_bird_pipe(sensor.metrics['bird']['pos'], 
                                               sensor.metrics['pipes'])                                         
    
    if any(state.index == (sensor.metrics['bird']['pos'][1], 
                            dist_bird_pipes) for state in states):
        actual_state = next(state.index == (sensor.metrics['bird']['pos'][1], 
                            dist_bird_pipes) for state in states)
    else:
        actual_state = State(sensor.metrics['bird'], sensor.metrics['pipes'])
        states.append(actual_state)
    
