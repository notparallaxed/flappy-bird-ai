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

    def get_dist_bird_pipes(self):
            dist_bird_pipe_bot = math.dist(self.metrics['bird']['pos'], 
                                           self.metrics['pipes']['bottom']['pos'])
            dist_bird_pipe_top = math.dist(self.metrics['bird']['pos'], 
                                           self.metrics['pipes']['top']['pos'])
            
            return round((dist_bird_pipe_bot + dist_bird_pipe_top)/2)

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
        self.reward_history = []
        
        #self.dist_bird_floor = (Y_FLOOR_POS - self.bird_metrics['pos'][1])
        self.dist_bird_pipes = calculate_dist_bird_pipe(bird_metrics['pos'], pipes_metrics)
        
        self.q_values = {
            "DONT_BUMP" : 0,
            "DO_BUMP" : 0,
        }

        self.index = (bird_metrics['pos'][1], self.dist_bird_pipes)

    def get_max_q_action(self):
        if (self.actions_q_value['DO_BUMP'] > self.actions_q_value['DONT_BUMP']):
            return 'DO_BUMP'
        
        return 'DONT_BUMP'

class Score():
    def __init__(self, sensor):
        self.points = 0
        self.attempts = 1
        self.sensor = sensor
        self.reward_value = 0 # Padrão para todos os estados

    def achive_goal(self):
        # Goal is gain more points
        if self.points < self.sensor.metrics['score']['points']:
            self.points = self.sensor.metrics['score']['points']
            self.reward_value = 10000
            return True
        elif self.attempts < self.sensor.metrics['score']['attempts']:
            self.attempts = self.sensor.metrics['score']['attempts']
            self.points = self.sensor.metrics['score']['points']
            self.reward_value = -1000
            return False

        self.reward_value = -100
        return False
    


sensor = Sensor(parent_conn)
actuator = Actuator(parent_conn)                 
score = Score(sensor)

states = []
previous_state = None
actual_state = None
gamma = 8
def alpha(attempts):
    return math.pow(math.e, -(attempts/100))


# Run for 1st state
p.start()

actuator.dont_bump()
sensor.update()

actual_state = State(sensor.metrics['bird'], sensor.metrics['pipes'])
states.append(actual_state)
actual_state.reward_history.append( ('DONT_BUMP', score.reward_value) )

previous_state = actual_state
actuator.dont_bump()

while p.is_alive():
    sensor.update()
    
    # Check if the actual perceived state has beeen observed before, set the actual state
    if any(state.index == (sensor.metrics['bird']['pos'][1], 
                            sensor.get_dist_bird_pipes()) for state in states):
        actual_state = next(state for state in states if state.index == (sensor.metrics['bird']['pos'][1], 
                            sensor.get_dist_bird_pipes()))
        print('estado repetido')
    else:
        actual_state = State(sensor.metrics['bird'], sensor.metrics['pipes'])
        states.append(actual_state)

    # Verifies if the perceived state achieve the goal
    if score.achive_goal():
        actual_state.reward_history.append( ('DONT_BUMP', score.reward_value) )
        actual_state.q_values['DONT_BUMP'] = score.reward_value
    else:
        maxQ = max(actual_state.q_values, key=actual_state.q_values.get)
        print(actual_state.q_values)
        a, r = previous_state.reward_history[-1]
        previous_state.q_values[a] = previous_state.q_values[a] + alpha(score.attempts)*(r + gamma*actual_state.q_values[maxQ] - previous_state.q_values[a] )

    #Defines which action takes based on q-value
    next_action = max(actual_state.q_values, key=actual_state.q_values.get)
    print(next_action)
    if (next_action == 'DO_BUMP'):
        actual_state.reward_history.append(('DO_BUMP', score.reward_value))
        actuator.do_bump()
    else:
        actual_state.reward_history.append(('DONT_BUMP', score.reward_value))
        actuator.dont_bump()

    previous_state = actual_state

  
zip

