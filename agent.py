import subprocess
process = subprocess.Popen(['python', './flappy-game/flappy.py'], stdout=subprocess.PIPE)

# Game constants
MAX_SCREEN_WIDTH = 400
MAX_SCREEN_HEIGHT = 800
Y_FLOOR_POS = (MAX_SCREEN_HEIGHT - 100)

X_SPEED = 10
BUMP_SPEED = 10
GRAVITY = 1


