import pygame
SIZE = WIDTH, HEIGHT = 640, 480
ORIGIN_FPS = 6

TITLE = 'Hungry Snake'
FONT_NAME = 'harrington'
FONT_NAME_2 = 'arialrounded'

# 机率
BRICKODDS = 15
SPEEDUPODDS = 25
SPEEDDOWNODDS = 15
CUTHALFODDS = 10
STARODDS = 5

GREY = 250, 250, 250
GREEN = 0, 255, 0
BLACK = 0, 0, 0
YELLOW = 255, 255, 0
RED = 255, 0, 0
GOLD = 255, 215, 0
LIME = 0,255,0
WHITE = 255, 255, 255
SPRING_GREEN = 60,179,113
BG_COLOR = GREY

# 结束无敌事件
CHEAT_END = pygame.USEREVENT + 1
my_event = pygame.event.Event(CHEAT_END)

# 全局变量FPS
class FPS:
    v = ORIGIN_FPS