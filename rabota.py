import csv
import random
import os
import sqlite3
import pygame
import sys
from math import radians, sin, cos

pygame.init()
pygame.font.init()
SIZE = WIDTH, HEIGHT = 1350, 730
screen = pygame.display.set_mode(SIZE)
all_sprites = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
bubbles = pygame.sprite.Group()
bullets = pygame.sprite.Group()
guns = pygame.sprite.Group()
explosions = pygame.sprite.Group()
pygame.display.set_caption('Bubble shooter')
ARIAL_50 = pygame.font.SysFont('comicsansms', 50)
clock = pygame.time.Clock()
FPS = 200
screen_rect = (0, 0, WIDTH, HEIGHT)
GRAVITY = 0.05
HITS = {
    1: {
        1: 2,
        2: 1,
        3: 3
    },
    2: {
        1: 3,
        2: 2,
        3: 1
    },
    3: {
        1: 1,
        2: 3,
        3: 2
    }
}
VELOCITIES = {
    '1': 1,
    '2': 2,
    '3': 3
}
DIFFICULTIES = {
    '1': 1,
    '2': 2,
    '3': 3
}


def load_image(name, colorkey=None):
    fullname = os.getcwd() + '/data/' + name
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден ")
        sys.exit()
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


class Menu:
    def __init__(self):
        self._option_surfaces = []
        self._callbacks = []
        self._current_options_index = 0

    def append_option(self, option, callback):
        self._option_surfaces.append(ARIAL_50.render(
            option, True, (255, 255, 255)))
        self._callbacks.append(callback)

    def switch(self, direction):
        self._current_options_index = \
            (self._current_options_index + direction) % len(
                self._option_surfaces)

    def draw(self, surf, x, y, option_y_padding):
        for i, option in enumerate(self._option_surfaces):
            option_rect = option.get_rect()
            option_rect.topleft = (x, y + i * option_y_padding)
            if i == self._current_options_index:
                pygame.draw.rect(surf, (0, 125, 0), option_rect)
            surf.blit(option, option_rect)


class Board(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((WIDTH, HEIGHT))
        self.image.fill((13, 13, 13))
        self.image.set_colorkey((13, 13, 13))
        self.rect = self.image.get_rect()
        self.font = pygame.font.SysFont("monospace", 30)

    def add(self, letter, pos):
        s = self.font.render(letter, 1, (0, 200, 0))
        self.image.blit(s, pos)


class Cursor(pygame.sprite.Sprite):
    def __init__(self, board):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface((10, 20))
        self.image.fill((0, 250, 0))
        self.text_height = 30
        self.text_width = 20
        self.rect = self.image.get_rect(topleft=(
            self.text_width, self.text_height))
        self.board = board
        self.text = ''
        self.cooldown = 0

    def write(self, text):
        self.text = list(text)

    def update(self):
        if not self.cooldown and self.text:
            letter = self.text.pop(0)
            if letter == '\n':
                self.rect.move_ip((0, self.text_height))
                self.rect.x = self.text_width
            else:
                self.board.add(letter, self.rect.topleft)
                self.rect.move_ip((self.text_width, 0))
            self.cooldown = 5

        if self.cooldown:
            self.cooldown -= 1


class Border(pygame.sprite.Sprite):
    def __init__(self, x1, y1, x2, y2):
        super().__init__(all_sprites)
        if x1 == x2:
            self.add(vertical_borders)
            self.image = pygame.Surface([1, y2 - y1])
            self.rect = pygame.Rect(x1, y1, 1, y2 - y1)
        else:
            self.add(horizontal_borders)
            self.image = pygame.Surface([x2 - x1, 1])
            self.rect = pygame.Rect(x1, y1, x2 - x1, 1)


class Particle(pygame.sprite.Sprite):
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()
        self.velocity = [dx, dy]
        self.rect.x, self.rect.y = pos
        self.gravity = GRAVITY

    def update(self):
        self.velocity[1] += self.gravity
        if self.velocity[1] == 0:
            self.velocity[1] += self.gravity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        if not self.rect.colliderect(screen_rect):
            self.kill()


class Bubble(pygame.sprite.Sprite):
    def __init__(self, pos, dif):
        super().__init__(all_sprites, bubbles)
        image = random.choice(['bluebubble.png', 'redbubble.png',
                               'greenbubble.png'])
        self.image = pygame.transform.scale(load_image(image),
                                            (70 // dif, 70 // dif))
        self.color = 1 if image == 'bluebubble.png' else 2 \
            if image == 'redbubble.png' else 3
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            self.kill()


class Button:
    def __init__(self):
        self.x, self.y, self.text = 0, 0, ''
        self.font, self.font_size = pygame.font.get_default_font(), 0
        self.width, self.height = 0, 0
        self.action = None
        self.draw_rect = False
        self.was_clicked = False
        self.rect = pygame.rect.Rect(self.x, self.y,
                                     self.x + self.width, self.y + self.height)

    def set_text(self, text):
        self.text = text

    def set_font(self, font):
        self.font = font

    def set_size(self, size):
        self.font_size = size

    def set_rect(self, x, y, width, height):
        self.x, self.y, self.width, self.height = x, y, width, height
        self.rect = pygame.rect.Rect(self.x, self.y,
                                     self.x + self.width, self.y + self.height)

    def set_draw_rect(self, drawing):
        self.draw_rect = drawing

    def render(self):
        text = pygame.font.SysFont(self.font, self.font_size).render(
            self.text, False, 'white')
        if self.draw_rect:
            pygame.draw.rect(screen, (120, 160, 200), (self.x, self.y,
                                                       self.width, self.height))
        screen.blit(text, (self.x, self.y))

    def clicked(self, pos):
        if self.x <= pos[0] <= self.x + self.width:
            if self.y <= pos[1] <= self.y + self.height:
                self.was_clicked = True


class Explosion(pygame.sprite.Sprite):
    def __init__(self, center, gun, bullet):
        super().__init__(explosions, all_sprites)
        self.image = explosion_animation[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_rate = 50
        self.gun = gun
        self.bullet = bullet

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.frame_rate:
            self.last_update = now
            self.frame += 1
            if self.frame == len(explosion_animation):
                self.kill()
                pygame.time.delay(80)
                event_type = pygame.USEREVENT + 1
                pygame.event.post(pygame.event.Event(event_type,
                                                     {self.gun: self.bullet}))
            else:
                center = self.rect.center
                self.image = explosion_animation[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


explosion_animation = []
for i in range(9):
    img = pygame.transform.scale(load_image(f'Explosion{i}.png'), (80, 80))
    explosion_animation.append(img)


def create_particles(position):
    particle_count = 5
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


class Gun(pygame.sprite.Sprite):
    def __init__(self, pos, rotate, rotate_right, reverse, name, velocity):
        super().__init__(all_sprites, guns)
        image = load_image(random.choice(['blue.png', 'red.png', 'green.png']))
        self.color = 1 if image == load_image('blue.png') else 2 \
            if image == load_image('red.png') else 3
        if reverse:
            image = pygame.transform.flip(image, 1, 0)

        self.image = pygame.transform.scale(image, (70, 70))
        self.origin = self.image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.rotating = rotate
        self.angle = 30
        self.right = rotate_right
        self.reverse = reverse
        self.name = name
        self.velocity = velocity

    def update(self):
        if self.rotating:
            self.angle = (self.angle - self.velocity) % 360 if self.right \
                else (self.angle + self.velocity) % 360
            self.rotate()

    def rotate(self):
        self.image = pygame.transform.rotate(self.origin, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def fire(self):
        angle = self.angle
        if self.reverse:
            angle = -angle
            x, y = self.rect.x - 10, self.rect.y - 10
        else:
            x, y = self.rect.x + 10, self.rect.y + 10
        Bullet(x, y, 20, -angle, self.color, self.reverse, self.name)

    def hit(self, bullet):
        if bullet.name != self.name:
            Explosion(self.rect.center, self, bullet)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, width, angle, color, reverse, name):
        super().__init__(all_sprites, bullets)
        self.image = pygame.Surface((width, width), pygame.SRCALPHA, 32)
        self.color = color
        pygame.draw.circle(self.image, pygame.Color('white'), (3, 3), 3)
        self.rect = pygame.Rect(x, y, width, width)
        self.width, self.angle = width, angle
        self.vx = 10 * cos(radians(angle))
        if reverse:
            self.vx = -self.vx
        self.vy = 10 * sin(radians(angle))
        self.hp = 10
        self.name = name

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.hp -= 2
            if self.hp < 1:
                self.kill()
            self.vy = -self.vy
            self.image = pygame.Surface((6, 6), pygame.SRCALPHA, 32)
            pygame.draw.circle(self.image, pygame.Color('white'), (3, 3), 3)
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.hp -= 2
            if self.hp < 1:
                self.kill()
            self.vx = -self.vx
            self.image = pygame.Surface((6, 6), pygame.SRCALPHA, 32)
            pygame.draw.circle(self.image, pygame.Color('white'), (3, 3), 3)


def collisions(hits, score):
    for bubble, bullet in hits.items():
        bullet = bullet[0]
        score[bullet.name]['Hits'] = score[bullet.name].get('Hits', 0) + 1
        dmg = HITS[bullet.color][bubble.color]
        hit = dmg if bullet.hp >= dmg else bullet.hp
        bullet.hp -= hit
        if bullet.hp > 0:
            pygame.sprite.groupcollide(bubbles, bullets,
                                       pygame.sprite.collide_circle, False)
        else:
            pygame.sprite.groupcollide(bubbles, bullets,
                                       pygame.sprite.collide_circle, True)


def gun_collision(hits):
    for hit in hits:
        hit.hit(hits[hit][0])


def easy():
    pass


def start_screen():
    text = pygame.font.SysFont('comicsansms', 100).render(
        'Bubble Shooter', False, (255, 255, 255))
    menu = Menu()
    menu.append_option("START", settings)
    menu.append_option('STATISTICS', stat)
    menu.append_option('AUTHORS', authors)
    menu.append_option('RULES', rules)
    menu.append_option('QUIT', quit)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    menu.switch(-1)
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    menu.switch(+1)
                elif event.key == pygame.K_SPACE or \
                        event.key == pygame.K_RETURN:
                    return menu._callbacks[menu._current_options_index]()
        screen.fill((0, 0, 0))
        screen.blit(text, (300, 30))
        menu.draw(screen, 300, 250, 75)
        pygame.display.flip()
        clock.tick(FPS)


def authors():
    pygame.display.set_caption('Authors')
    x1 = x3 = 300
    x2 = 500
    font = pygame.font.SysFont('comicsansms', 32)
    text_o = font.render("VORCHUK OLEG", 1, 'red', 'green')
    text_k = font.render("KOMOV KIRILL", 1, 'red', 'green')
    text_i = font.render("ZELENOV IGOR", 1, 'red', 'green')
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return start_screen()
        screen.fill((0, 0, 0))
        screen.blit(text_o, (x1 - 100, 300))
        screen.blit(text_k, (x2 - 200, 350))
        screen.blit(text_i, (x3 - 100, 400))
        clock.tick(FPS)
        pygame.display.flip()
        x1 = (x1 - 2) % WIDTH
        x2 = (x2 + 2) % WIDTH
        x3 = (x3 - 2) % WIDTH
    pygame.quit()


def rules():
    pygame.display.set_caption('Rules')
    board = Board()
    cursor = Cursor(board)
    all_sprites.add(cursor, board)
    text = """
Welcome!

In this game you have a gun, lots of annoying bubbles
and an opponent who wants to shoot you! Do it first!

1) Use the WASD buttons or ARROWS
to switch in the game menu and settings.

2) In the settings write your name,
choose gun's speed rotation
and the difficulty level.

3) Guns shoot in turns, click the SPACE button to shoot.

Good luck! (Tap SPACE to continue)"""
    running = True
    cursor.write(text)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                all_sprites.empty()
                return start_screen()
        screen.fill((0, 0, 0))
        all_sprites.update()
        all_sprites.draw(screen)
        clock.tick(FPS)
        pygame.display.flip()
    pygame.quit()


def stat():
    con = sqlite3.connect('overall_stats.sqlite')
    cur = con.cursor()
    cur.execute('create table if not exists player_stats ('
                'Player string primary key,'
                'Hits integer,'
                'Wins integer,'
                'Games_count integer)')
    values = list(cur.execute('select * from player_stats').fetchall())[::-1][:10]
    font = pygame.font.SysFont('comicsansms', 30)
    table = []
    name_text = font.render('Player', False, 'white')
    hits_text = font.render('Hits', False, 'white')
    wins_text = font.render('Wins', False, 'white')
    count_text = font.render('Games count', False, 'white')
    for i in range(len(values)):
        vs = list(values[i])
        name = font.render(vs[0], False, 'white')
        hits = font.render(str(vs[1]), False, 'white')
        wins = font.render(str(vs[2]), False, 'white')
        count = font.render(str(vs[3]), False, 'white')
        table.append([name, hits, wins, count])
    con.close()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                return start_screen()
        screen.fill('black')
        for i, v in enumerate(table):
            screen.blit(v[0], (200, 100 + 50 * i))
            screen.blit(v[1], (610, 100 + 50 * i))
            screen.blit(v[2], (825, 100 + 50 * i))
            screen.blit(v[3], (1100, 100 + 50 * i))
        screen.blit(name_text, (200, 30))
        screen.blit(hits_text, (600, 30))
        screen.blit(wins_text, (800, 30))
        screen.blit(count_text, (1000, 30))
        clock.tick(FPS)
        pygame.display.flip()


def settings():
    running = True
    text_d = pygame.font.SysFont('Times New Roman', 50).render(
        'Difficulty', False, (255, 255, 255))
    text_v = pygame.font.SysFont('Times New Roman', 50).render(
        'Velocity', False, (255, 255, 255))
    text_p1 = pygame.font.SysFont('Times New Roman', 40).render(
        'Player 1:', False, (255, 255, 255))
    text_p2 = pygame.font.SysFont('Times New Roman', 40).render(
        'Player 2:', False, (255, 255, 255))
    name1 = pygame.draw.rect(screen, 'white', (190, 30, 400, 50))
    name2 = pygame.draw.rect(screen, 'white', (800, 30, 400, 50))
    name_1 = name_2 = ''
    menu = Menu()
    menuv = Menu()
    menu.append_option("beginner", easy)
    menu.append_option('normal', easy)
    menu.append_option('expert', easy)
    menuv.append_option("low", easy)
    menuv.append_option('average', easy)
    menuv.append_option('high', easy)
    changing_name1 = changing_name2 = False
    current_menu = 0
    btn = Button()
    btn.set_text('GAME START')
    btn.set_size(100)
    btn.set_font('comicsansms')
    btn.set_draw_rect(False)
    btn.set_rect(300, 550, 200, 100)
    finished = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                create_particles(pygame.mouse.get_pos())
                changing_name1 = changing_name2 = False
                x, y = event.pos
                x1, y1 = name1.x, name1.y
                if x1 < x < x1 + name1.width and y1 < y < y1 + name1.height:
                    changing_name1 = True
                    changing_name2 = False
                x1, y1 = name2.x, name2.y
                if x1 < x < x1 + name2.width and y1 < y < y1 + name2.height:
                    changing_name1 = False
                    changing_name2 = True
                if btn.rect.collidepoint(event.pos):
                    with open('game_settings.csv', 'a', newline='') as file:
                        writer = csv.writer(file, delimiter=';', quotechar='"',
                                            quoting=csv.QUOTE_MINIMAL)
                        dif = menu._current_options_index + 1
                        vel = menuv._current_options_index + 1
                        name_1 = name_1 if name_1 else 'Player 1'
                        name_2 = name_2 if name_2 else 'Player 2'
                        finished = True
                        writer.writerow([dif, vel, name_1, name_2])
            if event.type == pygame.KEYDOWN:
                if changing_name1:
                    name_1 += event.unicode
                elif changing_name2:
                    name_2 += event.unicode
                else:
                    if event.key == pygame.K_a or event.key == pygame.K_LEFT or \
                            event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                        current_menu = current_menu * -1 + 1 ** current_menu
                    if event.key == pygame.K_w or event.key == pygame.K_UP:
                        if not current_menu:
                            menu.switch(-1)
                        else:
                            menuv.switch(-1)
                    elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                        if not current_menu:
                            menu.switch(+1)
                        else:
                            menuv.switch(+1)
        if finished and not any(
                x for x in all_sprites if x.__class__ == Particle):
            return game()
        screen.fill('black')
        btn.render()
        pygame.draw.rect(screen, 'white', (200, 30, 400, 50), 1)
        pygame.draw.rect(screen, 'white', (800, 30, 400, 50), 1)
        all_sprites.draw(screen)
        all_sprites.update()
        menu.draw(screen, 100, 250, 75)
        menuv.draw(screen, 800, 250, 75)
        screen.blit(text_p1, (50, 30))
        screen.blit(text_p2, (650, 30))
        screen.blit(pygame.font.SysFont('monospace', 50).render(
            name_1, False, (255, 0, 0)), (203, 30))
        screen.blit(pygame.font.SysFont('monospace', 50).render(
            name_2, False, (0, 255, 0)), (800, 30))
        screen.blit(text_d, (200, 130))
        screen.blit(text_v, (800, 130))
        clock.tick(FPS)
        pygame.display.flip()


def game(last_score={}):
    with open('game_settings.csv') as file:
        reader = csv.reader(file, delimiter=';', quotechar='"')
        dif, vel, name1, name2 = list(reader)[-1]
    dif, vel = DIFFICULTIES[dif], VELOCITIES[vel]
    running = True
    score = {
        name1:
            {
                'Wins': 0,
                'Defeats': 0,
                'Count': 0
            },
        name2:
            {
                'Wins': 0,
                'Defeats': 0
            }
    }
    for player in last_score.keys():
        for item in last_score[player].keys():
            score[player][item] = last_score[player][item]
    r, g, b = 0, 0, 0
    for i in range(12 * dif):
        for j in range(12 * dif):
            Bubble((300 + i * 60 // dif, 0 + j * 60 // dif), dif)
    Border(5, 5, WIDTH - 5, 5)
    Border(5, HEIGHT - 5, WIDTH - 5, HEIGHT - 5)
    Border(5, 5, 5, HEIGHT - 5)
    Border(WIDTH - 5, 5, WIDTH - 5, HEIGHT - 5)
    gun1 = Gun((30, 300), True, True, False, name1, vel)
    gun2 = Gun((1200, 300), False, False, True, name2, vel)
    shots1 = shots2 = 0
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                gun1.rotating, gun2.rotating = gun2.rotating, gun1.rotating
                if gun1.rotating:
                    gun2.fire()
                    shots2 += 1
                else:
                    gun1.fire()
                    shots1 += 1
            if event.type == pygame.USEREVENT + 1:
                for key in event.__dict__.keys():
                    gun, bullet = key, event.__dict__[key]
                gun.kill()
                running = False
                score[bullet.name]['Wins'] = score[bullet.name]['Wins'] + 1
                score[gun.name]['Defeats'] = score[gun.name]['Defeats'] + 1
                shots = shots1 if bullet.name == gun1.name else shots2
                hits = (score[name1]['Hits'] - last_score.get(
                        name1, {}).get('Hits', 0),
                        score[name2]['Hits'] - last_score.get(
                        name2, {}).get('Hits', 0))
                winner = bullet.name
                score[name1]['Count'] += 1
                return gameover(score, shots, hits, winner)
        screen.fill((r, g, b))
        hits = pygame.sprite.groupcollide(bubbles, bullets, False, False)
        gun_hit = pygame.sprite.groupcollide(guns, bullets, False, False)
        collisions(hits, score)
        gun_collision(gun_hit)
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)


def gameover(score, shots, hits, winner):
    text = pygame.font.SysFont('comicsansms', 100).render(
        'Bubble Shooter', False, (255, 255, 255))
    menu = Menu()
    menu.append_option("NEW GAME", lambda: game(score))
    menu.append_option('MENU', lambda: new_game(True, score))
    menu.append_option('STATISTICS', lambda: local_stat(
        score, shots, hits, winner))
    menu.append_option('QUIT', lambda: new_game(False, score))
    all_sprites.empty()
    bullets.empty()
    bubbles.empty()
    horizontal_borders.empty()
    vertical_borders.empty()
    guns.empty()
    explosions.empty()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_UP:
                    menu.switch(-1)
                elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                    menu.switch(+1)
                elif event.key == pygame.K_SPACE or \
                        event.key == pygame.K_RETURN:
                    return menu._callbacks[menu._current_options_index]()
        screen.fill((0, 0, 0))
        screen.blit(text, (300, 30))
        menu.draw(screen, 300, 250, 75)
        pygame.display.flip()
        clock.tick(FPS)


def new_game(yes, score):
    con = sqlite3.connect('overall_stats.sqlite')
    cur = con.cursor()
    cur.execute('create table if not exists player_stats ('
                'Player string primary key,'
                'Hits integer,'
                'Wins integer,'
                'Games_count integer)')
    for pl in score.keys():
        if score[pl].get('Count', 0):
            count = score[pl]['Count']
    players = [x[0] for x in cur.execute('select Player from player_stats').fetchall()]
    for player in score.keys():
        if player in players:
            info = cur.execute(f'select * from player_stats where Player = '
                               f'"{player}"').fetchone()
            print(info)
            cur.execute(f'update player_stats set Hits = '
                        f'{info[1] + score[player]["Hits"]} where Player = "{player}"')
            cur.execute(f'update player_stats set Wins = '
                        f'{info[2] + score[player]["Wins"]} where Player = "{player}"')
            cur.execute(f'update player_stats set Games_count = '
                        f'{info[3] + count} where Player = "{player}"')
        else:
            cur.execute('insert into player_stats values(?, ?, ?, ?)',
                        (player, score[player]['Hits'],
                         score[player]['Wins'], count))
    con.commit()
    con.close()
    if yes:
        return start_screen()


def local_stat(score, shots, all_hits, winner):
    running = True
    font = pygame.font.SysFont('comicsansms', 30)
    name1, name2 = score.keys()
    text1 = font.render(name1, False, (255, 255, 255))
    text2 = font.render(name2, False, 'white')
    wins1 = font.render(str(score[name1]['Wins']), False, 'white')
    wins2 = font.render(str(score[name2]['Wins']), False, 'white')
    current_hits1 = font.render(str(all_hits[0]), False, 'white')
    current_hits2 = font.render(str(all_hits[1]), False, 'white')
    hits1 = font.render(str(score[name1]['Hits']), False, 'white')
    hits2 = font.render(str(score[name2]['Hits']), False, 'white')
    text = font.render('Players', False, 'white')
    wins = font.render('Wins', False, 'white')
    hits = font.render('Hits', False, 'white')
    hits_text = font.render('Current Hits', False, 'white')
    stats = pygame.font.SysFont('comicsansms', 50).render('Stats', False, 'white')
    current_winner_text = font.render('Winner', False, 'white')
    current_shots_text = font.render("Winner's shots", False, 'white')
    current_shots = font.render(str(shots), False, 'white')
    current_winner = font.render(winner, False, 'white')
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                return gameover(score, shots, all_hits, winner)
        screen.fill('black')
        pygame.draw.line(screen, 'white', (350, 30), (350, 500))
        pygame.draw.line(screen, 'white', (50, 100), (WIDTH - 100, 100))
        pygame.draw.line(screen, 'white', (50, 370), (WIDTH - 100, 370))
        screen.blit(text1, (500, 150))
        screen.blit(text2, (900, 150))
        screen.blit(wins1, (500, 200))
        screen.blit(wins2, (900, 200))
        screen.blit(current_hits1, (500, 250))
        screen.blit(current_hits2, (900, 250))
        screen.blit(hits1, (500, 300))
        screen.blit(hits2, (900, 300))
        screen.blit(text, (100, 150))
        screen.blit(wins, (100, 200))
        screen.blit(hits, (100, 300))
        screen.blit(stats, (700, 30))
        screen.blit(current_winner, (700, 400))
        screen.blit(current_shots, (750, 450))
        screen.blit(hits_text, (100, 250))
        screen.blit(current_winner_text, (100, 400))
        screen.blit(current_shots_text, (100, 450))
        clock.tick(FPS)
        pygame.display.flip()


def all_content():
    if start_screen():
        game()
    pygame.quit()


all_content()
