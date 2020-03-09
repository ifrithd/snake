import pygame, os
from settings import *
from sprites import *


class dummysound:
    def play(self): pass


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode(SIZE)
        pygame.display.set_caption(TITLE)
        self.font_name = FONT_NAME
        self.clock = pygame.time.Clock()
        self.running = True
        self.playing = False
        # status标志界面
        self.status = -1
        self.score = 0
        self.high_score = 0
        self.hard_factor = 1
        self.dir = os.path.split(os.path.abspath(__file__))[0]
        self.load_data()

    def new(self):
        """开始新一局游戏"""
        if not self.running:
            return
        self.score = 0
        pygame.mixer.music.load(os.path.join(self.dir, 'snd', 'BGM.ogg'))
        FPS.v = ORIGIN_FPS * self.hard_factor

        # 建立分组
        self.all_sprites = pygame.sprite.Group()
        self.foods = pygame.sprite.Group()
        self.obstacles = pygame.sprite.Group()

        SnakeHead.containers = self.all_sprites
        SnakeBody.containers = self.obstacles, self.all_sprites
        Food.containers = self.foods, self.all_sprites
        Warn.containers = self.all_sprites
        Brick.containers = self.obstacles, self.all_sprites

        # 初始化对象
        self.snake = SnakeHead()
        Food(10)
        for _ in range(3 * self.hard_factor):
            Warn()

        self.run()

    def run(self):
        """游戏循环"""
        pygame.mixer.music.play(-1)
        pygame.time.delay(1000)
        self.playing = True
        while self.playing and self.running:
            self.clock.tick(FPS.v)
            self.events()
            self.update()
            self.draw()

    def update(self):
        """游戏逻辑更新"""
        self.all_sprites.update()

        # 蛇头与食物碰撞
        for food in pygame.sprite.spritecollide(self.snake, self.foods, False):
            self.score += food.score
            # 速度逐渐加快
            FPS.v += 0.1 * self.hard_factor
            # 吃到无敌食物 切BGM
            if isinstance(food, Star):
                self.snake.cheat()
                pygame.mixer.music.load(os.path.join(self.dir, 'snd', 'cheating.ogg'))
                self.powerup_snd.play()
                pygame.mixer.music.play(-1)
            # 速度加快食物
            elif isinstance(food, SpeedUp):
                self.snake.eat(2)
                self.powerup_snd.play()
                FPS.v *= 1.25
            # 速度减慢食物
            elif isinstance(food, SpeedDown):
                self.snake.eat()
                self.strange_snd.play()
                FPS.v *= 0.75
                # 防止速度过慢
                FPS.v = max(FPS.v, ORIGIN_FPS - 1)
            # 长度减半食物
            elif isinstance(food, CutHalf):
                self.strange_snd.play()
                self.snake.cut(self.snake.length // 2)
            else:
                self.snake.eat()
                self.eat_snd.play()
            food.destroy()

        # 蛇头与障碍物碰撞,本局游戏结束
        hits =pygame.sprite.spritecollide(self.snake, self.obstacles, False)
        if hits and not self.snake.cheating:
            pygame.mixer.music.stop()
            self.explosion_snd.play()
            pygame.time.delay(100)
            for sprite in self.all_sprites:
                sprite.kill()
            self.playing = False

    def events(self):
        """游戏事件处理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if self.playing:
                    self.playing = False
                self.running = False
            # 无敌结束后BGM切换
            if event.type == CHEAT_END:
                pygame.mixer.music.load(os.path.join(self.dir, 'snd', 'BGM.ogg'))
                self.strange_snd.play()
                pygame.mixer.music.play()
            if event.type == pygame.KEYDOWN:
                # 暂停游戏
                if event.key == pygame.K_SPACE:
                    self.draw_text('Press SPACE to resume', 40, BLACK, WIDTH / 2, HEIGHT*0.7)
                    pygame.display.update()
                    self.wait_for_key([pygame.K_SPACE])
                elif event.key == pygame.K_ESCAPE:
                    if self.playing:
                        self.playing = False
                    self.running = False

    def draw(self):
        """游戏画面渲染绘制"""
        self.screen.fill(BG_COLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 20, BLACK, WIDTH / 2, 15)
        # 无敌时间提示
        if self.snake.cheating:
            msg = 'Cheat time:{:.2f}'.format(self.snake.cheating / FPS.v)
            self.draw_text(msg, 32, GOLD, WIDTH / 2, HEIGHT * 0.4)
        pygame.display.update()

    def show_start_screen(self):
        """游戏标题界面"""
        if not self.running:
            return
        pygame.mixer.music.load(os.path.join(self.dir, 'snd', 'startBGM.ogg'))
        pygame.mixer.music.play(-1)
        self.screen.fill(SPRING_GREEN)
        self.draw_text(TITLE, 80, GREY, WIDTH/2, HEIGHT*0.1)
        self.draw_text('H for help    S for setting', 32, GREY, WIDTH/2, HEIGHT*0.47)
        self.draw_text('SPACE to start', 32, GREY, WIDTH/2, HEIGHT*0.55)
        self.draw_text("High Score: " + str(self.high_score), 18, GREY, WIDTH / 2, HEIGHT*0.8)
        pygame.display.update()
        pk = self.wait_for_key([pygame.K_SPACE, pygame.K_h, pygame.K_s])
        pygame.mixer.music.fadeout(200)
        if pk == pygame.K_SPACE:
            self.status = 0
        elif pk == pygame.K_h:
            self.status = 1
        elif pk == pygame.K_s:
            self.status = 2

    def show_end_screen(self):
        """游戏结束界面"""
        if not self.running:
            return
        self.screen.fill(SPRING_GREEN)
        self.draw_text('GAME OVER', 60, GREY, WIDTH/2, HEIGHT*0.3)
        self.draw_text("Score:  " + str(self.score), 32, GREY, WIDTH / 2, HEIGHT * 0.5)
        self.draw_text("Press SPACE to play again, T return to title", 20, GREY, WIDTH / 2, HEIGHT * 0.7)
        # 处理高分
        if self.score > self.high_score:
            self.high_score = self.score
            self.draw_text("New High Score!", 28, GOLD, WIDTH / 2, 25)
            with open(os.path.join(self.dir, 'data', 'high_score.txt'), 'w') as fp:
                fp.write(str(self.high_score))
            pygame.mixer.music.load(os.path.join(self.dir, 'snd', 'win.ogg'))
            pygame.mixer.music.play(-1)
        else:
            self.draw_text("High Score: " + str(self.high_score), 20, GREY, WIDTH / 2, 15)
            pygame.mixer.music.load(os.path.join(self.dir, 'snd', 'gameover.ogg'))
            pygame.mixer.music.play(1)
        pygame.display.update()
        pk = self.wait_for_key([pygame.K_SPACE, pygame.K_t])
        self.status = 0 if pk == pygame.K_SPACE else 1
        pygame.mixer.music.fadeout(200)

    def show_set_screen(self):
        """设置界面"""
        if not self.running:
            return
        pygame.mixer.music.load(os.path.join(self.dir, 'snd', 'setBGM.ogg'))
        pygame.mixer.music.play(-1)
        setting = True
        while setting:
            self.clock.tick(FPS.v)
            # 绘制界面
            self.screen.fill(SPRING_GREEN)
            self.draw_text('Setting', 80, GREY, WIDTH / 2, HEIGHT * 0.06)
            msg = 'Use up/down or WS to select hardness'
            self.draw_text(msg, 32, GREY, WIDTH/2, HEIGHT * 0.3)
            if self.hard_factor == 1:
                msg = 'NORMAL'
            else:
                msg = 'HARD'
            self.draw_text(msg, 48, GOLD, WIDTH/2, HEIGHT * 0.5)
            msg = 'Press SPACE to return to title'
            self.draw_text(msg, 28, GREY, WIDTH / 2, HEIGHT * 0.8)
            pygame.display.update()
            # 事件处理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    setting = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    # 难度改变
                    if event.key in [pygame.K_w, pygame.K_UP]:
                        if self.hard_factor == 2:
                            self.hard_factor = 1
                            self.eat_snd.play()
                    elif event.key in [pygame.K_s, pygame.K_DOWN]:
                        if self.hard_factor == 1:
                            self.hard_factor = 2
                            self.eat_snd.play()
                    elif event.key == pygame.K_ESCAPE:
                        setting = False
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        setting = False
        # 修改文件
        with open(os.path.join(self.dir, 'data', 'Hard.txt'), 'w') as fp:
            fp.write(str(self.hard_factor))
        pygame.mixer.music.fadeout(200)

    def show_help_screen(self):
        """帮助界面"""
        if not self.running:
            return
        pygame.mixer.music.load(os.path.join(self.dir, 'snd', 'helpBGM.ogg'))
        pygame.mixer.music.play(-1)
        self.screen.fill(SPRING_GREEN)
        self.draw_text('HELP', 80, GREY, WIDTH/2, 0)
        # 玩法说明
        msg = 'Use WASD to control the hungry snake!'
        self.draw_text(msg, 32, GREY, WIDTH/2, HEIGHT*0.18)
        msg = 'You can use SPACE to pause the game'
        self.draw_text(msg, 32, GREY, WIDTH/2, HEIGHT*0.24)
        # 普通食物说明
        self.screen.blit(Food.image, (WIDTH*0.2, HEIGHT*0.34-5))
        msg = 'Normal Food. {} score'.format(Food.score)
        self.draw_text(msg, 20, GOLD, WIDTH * 0.5, HEIGHT * 0.34,FONT_NAME_2)
        # 减半食物说明
        self.screen.blit(CutHalf.image, (WIDTH * 0.2, HEIGHT * 0.42 - 5))
        msg = "make snake's length half. {} score".format(CutHalf.score)
        self.draw_text(msg, 20, GOLD, WIDTH * 0.52, HEIGHT * 0.42,FONT_NAME_2)
        # 加减速食物说明
        self.screen.blit(SpeedUp.image, (WIDTH*0.1, HEIGHT*0.51-5))
        self.screen.blit(SpeedDown.image, (WIDTH*0.15, HEIGHT*0.51-5))
        msg = "{}/{} score. change your snake's speed".format(SpeedUp.score, SpeedDown.score)
        self.draw_text(msg, 20, GOLD, WIDTH*0.52, HEIGHT*0.51,FONT_NAME_2)
        # 无敌食物说明
        self.screen.blit(Star.image, (WIDTH*0.1, HEIGHT*0.6-5))
        msg = "{} score food. Yor snake won't die in 7 second".format(Star.score)
        self.draw_text(msg, 20, GOLD, WIDTH * 0.52, HEIGHT * 0.6,FONT_NAME_2)
        # 警告说明
        self.screen.blit(Warn.image, (WIDTH*0.15, HEIGHT*0.7+5))
        msg = "There will be an obstacle here in 2s"
        self.draw_text(msg, 20, GOLD, WIDTH * 0.5, HEIGHT * 0.7,FONT_NAME_2)
        # 障碍说明
        self.screen.blit(Brick.image, (WIDTH*0.15, HEIGHT*0.8+5))
        msg = "Your snake die if it eat this"
        self.draw_text(msg, 20, GOLD, WIDTH * 0.5, HEIGHT * 0.8,FONT_NAME_2)

        msg = 'Press SPACE to return to title'
        self.draw_text(msg, 28, GREY, WIDTH/2, HEIGHT*0.9)

        pygame.display.update()
        self.wait_for_key([pygame.K_SPACE])

    def draw_text(self, text, size, color, x, y, font_name = None):
        """在屏幕上绘制文字"""
        if font_name == None:
            font_name = self.font_name
        font = pygame.font.SysFont(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)

    def wait_for_key(self, keys):
        """等待玩家键入按键"""
        waiting = True
        ret = None
        while waiting:
            self.clock.tick(FPS.v)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key in keys:
                        ret = event.key
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.running = False
        return ret

    def load_image(self, file_name, colorkey=None):
        """载入游戏图片"""
        file_path = os.path.join(self.dir, 'img', file_name)
        try:
            image = pygame.image.load(file_path)
        except pygame.error:
            print('Cannot load image:', file_name)
            raise SystemExit(str(pygame.get_error()))
        image = image.convert()
        if colorkey is not None:
            if colorkey is -1:
                colorkey = image.get_at((0, 0))
            image.set_colorkey(colorkey, RLEACCEL)
        return image

    def load_sound(self, file_name):
        """载入游戏音效"""
        if not pygame.mixer: return dummysound()
        file_path = os.path.join(self.dir, 'snd', file_name)
        try:
            sound = pygame.mixer.Sound(file_path)
            return sound
        except pygame.error:
            print('Warning, unable to load, {}'.format(file_name))
        return dummysound()

    def load_data(self):
        """载入游戏数据"""
        # 载入高分
        file_path = os.path.join(self.dir, 'data/high_score.txt')
        if os.path.exists(file_path):
            with open(file_path) as fp:
                try:
                    self.high_score = int(fp.read())
                except:
                    self.high_score = 0

        # 载入难度
        file_path = os.path.join(self.dir, 'data/Hard.txt')
        if os.path.exists(file_path):
            with open(file_path) as fp:
                try:
                    self.hard_factor = int(fp.read())
                    # 防止数值错误
                    if self.hard_factor <= 0:
                        raise ValueError
                    self.hard_factor = min(self.hard_factor, 3)
                except:
                    self.hard_factor = 1

        # 载入图片
        img = self.load_image('snakehead.png')
        SnakeHead.imgs = [img, pygame.transform.flip(img, 1, 0)]
        SnakeHead.imgs.append(pygame.transform.flip(img, 0, 1))
        SnakeHead.imgs.append(pygame.transform.flip(SnakeHead.imgs[1], 0, 1))

        img = self.load_image('snakebody.png')
        SnakeBody.imgs = [img, pygame.transform.rotate(img, 90)]

        Food.image = self.load_image('food.png', -1)
        Star.image = self.load_image('star.png', -1)
        Warn.image = self.load_image('warning.png', -1)
        Brick.image = self.load_image('brick.png')
        SpeedUp.image = self.load_image('speed_up.png', -1)
        SpeedDown.image = self.load_image('speed_down.png', -1)
        CutHalf.image = self.load_image('cut_half.png', -1)

        # 载入音效
        self.eat_snd = self.load_sound('Pickup.wav')
        self.powerup_snd = self.load_sound('Powerup.wav')
        self.explosion_snd = self.load_sound('Explosion.wav')
        self.strange_snd = self.load_sound('strange.wav')


def main():
    game = Game()
    while game.running:
        # status!=0 进入标题界面
        while game.status!=0 and game.running:
            game.show_start_screen()
            if game.status == 1:
                game.show_help_screen()
            elif game.status == 2:
                game.show_set_screen()
        game.new()
        game.show_end_screen()
    pygame.quit()


if __name__ == '__main__':
    main()