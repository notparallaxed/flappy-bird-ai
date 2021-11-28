import pygame, random, json, sys
from pygame.draw import rect
from pygame.locals import *
from pygame.surface import Surface

# Game constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 800
SPEED = 10
GRAVITY = 1
GAME_SPEED = 10

GROUND_WIDTH = 2 * SCREEN_WIDTH
GROUND_HEIGHT = 100

PIPE_WIDTH = 80
PIPE_HEIGHT = 500

PIPE_GAP = 200

# Game Elements
class Bird(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.images = [pygame.image.load('bluebird-upflap.png').convert_alpha(),
                       pygame.image.load('bluebird-midflap.png').convert_alpha(),
                       pygame.image.load('bluebird-downflap.png').convert_alpha()]

        self.speed = SPEED

        self.current_image = 0

        self.image = pygame.image.load('bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDTH / 2
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        self.current_image = (self.current_image + 1) % 3
        self.image = self.images[ self.current_image ]

        self.speed += GRAVITY
        

        # Update height
        self.rect[1] += self.speed
    
    def bump(self):
        self.speed = -SPEED

class Pipe(pygame.sprite.Sprite):

    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('pipe-red.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDTH,PIPE_HEIGHT))

        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED

class Ground(pygame.sprite.Sprite):

    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDTH, GROUND_HEIGHT))

        self.mask = pygame.mask.from_surface(self.image)

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT
    
    def update(self):
        self.rect[0] -= GAME_SPEED

class Score():

    def __init__(self, attempt):
        self.top = 10
        self.left = 160
        self.width = 120
        self.height = 50
        self.color = (255, 255, 255)
        self.points_font = pygame.font.Font(pygame.font.get_default_font(), 36)
        self.attempts_font = pygame.font.Font(pygame.font.get_default_font(), 18)

        self.points = 0
        self.attempt = attempt

    def draw(self, surface):
        # points
        score_surface = pygame.Surface((self.width, self.height))
        score_surface.fill(self.color)
        points_text_surface = self.points_font.render(str(self.points), 1, (0, 0, 0))
        xpos_points = (self.width - points_text_surface.get_size()[0])/2
        score_surface.blit(points_text_surface, (xpos_points,2))

        #attempts
        attempts_text_surface = self.attempts_font.render(
                                    "tentativa: "+ str(self.attempt), 1, (0, 0, 0))
        xpos_attemps = (self.width - attempts_text_surface.get_size()[0])/2
        score_surface.blit(attempts_text_surface, (xpos_attemps,30))
                
        surface.blit(score_surface, (self.left, self.top))

class StdOutput():

    def __init__(self, conn = None):
        self.bird = { 
            'size': (0,0),
            'pos' : (0,0)
            }
        self.pipes = {
            'top' : {
                'size': (0,0),
                'pos' : (0,0)
            },
            'bottom' : {
                'size': (0,0),
                'pos' : (0,0)
            }
        }
        self.score = {
            'points': 0,
            'attempts': 0
        }
        self.conn = conn

    def saveBird(self, bird_rect):
        self.bird['size'] = bird_rect.size
        self.bird['pos'] = bird_rect.topleft
    
    def savePipes(self, pipes_sprites):
        top_pipe_rect = pipes_sprites[0].rect
        bottom_pipe_rect = pipes_sprites[1].rect
        self.pipes['top']['size'] = top_pipe_rect.size
        self.pipes['top']['pos'] = top_pipe_rect.topleft
        self.pipes['bottom']['size'] = bottom_pipe_rect.size
        self.pipes['bottom']['pos'] = bottom_pipe_rect.topleft

    def saveScore(self, score_input):
        self.score['points'] = score_input.points
        self.score['attempts'] = score_input.attempt

    def json_serialized_out(self):
        obj = {
            'bird' : self.bird,
            'pipes': self.pipes,
            'score': self.score
        }

        if self.conn is not None:
            self.conn.send(obj)
            
        print(json.dumps(obj))

# Game functions
def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return (pipe, pipe_inverted)

# Main game loop
def main(screen, stdoutput, attempt):
    BACKGROUND = pygame.image.load('background-day.png')
    BACKGROUND = pygame.transform.scale(BACKGROUND, (SCREEN_WIDTH, SCREEN_HEIGHT))

    score = Score(attempt)

    bird_group = pygame.sprite.Group()
    bird = Bird()
    bird_group.add(bird)

    ground_group = pygame.sprite.Group()
    for i in range(2):
        ground = Ground(GROUND_WIDTH * i)
        ground_group.add(ground)

    pipe_group = pygame.sprite.Group()
    for i in range(2):
        pipes = get_random_pipes(SCREEN_WIDTH * i + 800)
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

    clock = pygame.time.Clock()
    running = True

    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            if event.type == KEYDOWN:
                if event.key == K_SPACE:
                    bird.bump()
                
                    

        screen.blit(BACKGROUND, (0, 0))

        if is_off_screen(ground_group.sprites()[0]):
            ground_group.remove(ground_group.sprites()[0])

            new_ground = Ground(GROUND_WIDTH - 20)
            ground_group.add(new_ground)

        if is_off_screen(pipe_group.sprites()[0]):
            pipe_group.remove(pipe_group.sprites()[0])
            pipe_group.remove(pipe_group.sprites()[0])

            pipes = get_random_pipes(SCREEN_WIDTH * 2)

            pipe_group.add(pipes[0])
            pipe_group.add(pipes[1])

        bird_group.update()
        ground_group.update()
        pipe_group.update()

        bird_group.draw(screen)
        stdoutput.saveBird(bird_group.sprites()[0].rect)

        pipe_group.draw(screen)
        stdoutput.savePipes(pipe_group.sprites())

        ground_group.draw(screen)

        score.draw(screen)
        stdoutput.saveScore(score)
        
        stdoutput.json_serialized_out()
        pygame.display.update()

        # Verifica se houve colisão 
        if (pygame.sprite.groupcollide(bird_group, ground_group, False, False, pygame.sprite.collide_mask) or
        pygame.sprite.groupcollide(bird_group, pipe_group, False, False, pygame.sprite.collide_mask)):
            # Game over
            score.points = 0
            main(screen, stdoutput, attempt + 1)

        # Mark points in score
        if ((pipe_group.sprites()[0]).rect[0] == 100):
            score.points += 1
    
    pygame.quit()
    sys.exit()
# Start the game

if __name__ == '__main__': 
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    stdout = StdOutput()

    main(screen, stdout, 1)
