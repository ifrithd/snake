import pygame, os
from settings import *
from random import random, randrange
from pygame.locals import *

vec = pygame.math.Vector2

def rand_place():
    return randrange(20, WIDTH-40), randrange(20,HEIGHT-40)


class SnakeHead(pygame.sprite.Sprite):
    imgs = []
    containers = None
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.imgs[0]
        self.rect = self.image.get_rect()
        self.pos = self.rect.center = WIDTH/2, HEIGHT/2
        self.width, self.height = self.rect.width, self.rect.height
        self.speed = self.width
        # 初始蛇头朝向右
        self.dir = vec(1, 0)
        self.next = self.tail = SnakeBody((WIDTH/2-20, HEIGHT), 0)
        self.eating = 0
        self.length = 1
        # 剩余无敌时间
        self.cheating = 0

    def update(self):
        # 处理蛇尾
        tmp = SnakeBody(self.rect.center, int(self.dir.y))
        self.next.pre = tmp
        self.next = tmp
        self.length += 1
        if not self.eating:
            self.cut(1)
        else:
            self.eating -= 1

        if self.cheating:
            if self.cheating == 1:
                pygame.event.post(my_event)
            self.cheating -= 1

        # 处理键盘输入
        keys = pygame.key.get_pressed()
        self._change_dir(keys)

        # 更新坐标
        self.pos = self.pos + self.speed * self.dir
        # 边界处理
        if self.rect.left > WIDTH:
            self.pos.x = 0 - self.width / 2
        if self.rect.right < 0:
            self.pos.x = WIDTH + self.width / 2
        if self.rect.top > HEIGHT:
            self.pos.y = 0 - self.height / 2
        if self.rect.bottom < 0:
            self.pos.y = HEIGHT + self.height / 2

        # 更新矩阵位置
        self.rect.center = self.pos

    def _change_dir(self, keys):
        next_pos = self.dir
        # 新方向不能与原方向相反
        try_change = lambda dir:next_pos if -dir == self.dir else dir
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            next_pos = try_change(vec(-1, 0))
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            next_pos = try_change(vec(1, 0))
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            next_pos = try_change(vec(0, -1))
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            next_pos = try_change(vec(0, 1))
        # 动画
        if next_pos.x == 1:
            self.image = self.imgs[0]
        elif next_pos.x == -1:
            self.image = self.imgs[1]
        elif next_pos.y == 1:
            if next_pos.x == 1:
                self.image = self.imgs[2]
            else:
                self.image = self.imgs[3]

        self.dir = next_pos

    def eat(self, num = 1):
        self.eating += num

    def cheat(self):
        # 设置无敌时间
        self.cheating = int(FPS.v) * 7

    def cut(self, length):
        # 删除length个蛇身矩阵
        for _ in range(length):
            tmp = self.tail
            self.tail = self.tail.pre
            tmp.kill()
            self.length -= 1


class SnakeBody(pygame.sprite.Sprite):
    imgs = []
    containers = None

    def __init__(self, pos, pattern):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.image = self.imgs[pattern]
        self.rect = self.image.get_rect(center = pos)
        self.pre = None


class Food(pygame.sprite.Sprite):
    score = 5
    image = None
    containers = None

    def __init__(self, live_time):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect()
        self.rect.topleft = rand_place()
        self.life = FPS.v * live_time

    def update(self):
        self.life -= 1
        if self.life <= 0:  self.destroy()

    def destroy(self):
        Food(randrange(3, 11))
        rand = random()*100
        if rand <= STARODDS:
            Star()
        if rand <= SPEEDUPODDS:
            SpeedUp()
        if rand <= SPEEDDOWNODDS:
            SpeedDown()
        if rand <= CUTHALFODDS:
            CutHalf()
        self.kill()


class Star(Food):
    score = 100

    def __init__(self):
        Food.__init__(self, 5)

    def destroy(self):
        self.kill()


class SpeedUp(Food):
    score = 30

    def __init__(self):
        Food.__init__(self, randrange(3, 11))

    def destroy(self):
        self.kill()


class SpeedDown(Food):
    score = 5

    def __init__(self):
        Food.__init__(self, randrange(3, 11))

    def destroy(self):
        self.kill()


class CutHalf(Food):
    score = 5

    def __init__(self):
        Food.__init__(self, randrange(3, 11))

    def destroy(self):
        self.kill()


class Warn(pygame.sprite.Sprite):
    containers = None
    image = None

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect(topleft = rand_place())
        self.life = FPS.v * 2

    def update(self):
        self.life -= 1
        if self.life <= 0:
            Brick(self.rect.topleft, randrange(5, 11))
            self.kill()


class Brick(pygame.sprite.Sprite):
    containers = None
    image = None

    def __init__(self, pos, live_time):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.rect = self.image.get_rect(topleft=pos)
        self.life = FPS.v * live_time

    def update(self):
        self.life -= 1
        if self.life <= 0:
            self.destroy()

    def destroy(self):
        Warn()
        if random()*100 <= BRICKODDS:
            Warn()
        self.kill()