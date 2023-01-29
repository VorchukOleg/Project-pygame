import random
import os
import pygame
import sys
from math import radians, sin, cos

pygame.init()
pygame.font.init()
SIZE = WIDTH, HEIGHT = 1350, 730  # 610
screen = pygame.display.set_mode(SIZE)
all_sprites = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
bubbles = pygame.sprite.Group()
bullets = pygame.sprite.Group()
guns = pygame.sprite.Group()
explosions = pygame.sprite.Group()
pygame.display.set_caption('Bubble shooter')
ARIAL_50 = pygame.font.SysFont('arial', 50)
clock = pygame.time.Clock()
FPS = 200
screen_rect = (0, 0, WIDTH, HEIGHT)
GRAVITY = 0.2
HITS = {1: {1: 2,
            2: 1,
            3: 3},
        2: {1: 3,
            2: 2,
            3: 1},
        3: {1: 1,
            2: 3,
            3: 2}
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
        self._option_surfaces.append(ARIAL_50.render(option, True, (255, 255, 255)))
        self._callbacks.append(callback)

    def switch(self, direction):
        self._current_options_index = max(0,
                                          min(self._current_options_index + direction, len(self._option_surfaces) - 1))

    def select(self):
        pass

    def draw(self, surf, x, y, option_y_padding):
        for i, option in enumerate(self._option_surfaces):
            option_rect = option.get_rect()
            option_rect.topleft = (x, y + i * option_y_padding)
            if i == self._current_options_index:
                pygame.draw.rect(surf, (0, 125, 0), option_rect)
            surf.blit(option, option_rect)


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
    def __init__(self, pos):
        super().__init__(all_sprites, bubbles)
        image = random.choice(['bluebubble.png', 'redbubble.png', 'greenbubble.png'])
        self.image = pygame.transform.scale(load_image(image), (70, 70))
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
        self.rect = False
        self.was_clicked = False

    def set_text(self, text):
        self.text = text

    def set_font(self, font):
        self.font = font

    def set_size(self, size):
        self.font_size = size

    def set_rect(self, x, y, width, height):
        self.x, self.y, self.width, self.height = x, y, width, height

    def set_draw_rect(self, drawing):
        self.rect = drawing

    def render(self):
        text = pygame.font.SysFont(self.font, self.font_size).render(
            self.text, False, 'white')
        if self.rect:
            pygame.draw.rect(screen, (120, 160, 200), (self.x, self.y,
                                                       self.width, self.height))
        screen.blit(text, (self.x, self.y))

    def clicked(self, pos):
        if self.x <= pos[0] <= self.x + self.width:
            if self.y <= pos[1] <= self.y + self.height:
                self.was_clicked = True


explosion_animation = []
for i in range(9):
    img = pygame.transform.scale(load_image(f'Explosion{i}.png'), (30, 30))
    explosion_animation.append(img)


def create_particles(position):
    particle_count = 20
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers))


class Gun(pygame.sprite.Sprite):
    def __init__(self, pos, rotate, rotate_right, reverse, name):
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

    def update(self):
        if self.rotating:
            self.angle = (self.angle - 2) % 360 if self.right \
                else (self.angle + 2) % 360
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

    def boom(self):
        pass


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
                event_type = pygame.USEREVENT + 1
                pygame.event.post(pygame.event.Event(event_type, {self.gun: self.bullet}))
                # event.get() -> gun.kill() -> gama over -> score -> all_content()
            else:
                center = self.rect.center
                self.image = explosion_animation[self.frame]
                self.rect = self.image.get_rect()
                self.rect.center = center


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


def collisions(hits):
    for bubble, bullet in hits.items():
        bullet = bullet[0]
        dmg = HITS[bullet.color][bubble.color]
        hit = dmg if bullet.hp >= dmg else bullet.hp
        bullet.hp -= hit
        if bullet.hp > 0:
            # pygame.sprite.groupcollide(bubbles, bullets, True, False)
            pygame.sprite.groupcollide(bubbles, bullets, pygame.sprite.collide_circle, False)
        else:
            # pygame.sprite.groupcollide(bubbles, bullets, True, True)
            pygame.sprite.groupcollide(bubbles, bullets, pygame.sprite.collide_circle, True)


def start_screen():
    text = pygame.font.SysFont('impact', 100).render('Bubble Shooter', False, (255, 255, 255))
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
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return menu._callbacks[menu._current_options_index]()

        screen.fill((0, 0, 0))
        screen.blit(text, (300, 30))

        menu.draw(screen, 300, 250, 75)
        pygame.display.flip()
        clock.tick(FPS)


def gun_collision(hits):
    for hit in hits:
        hit.hit(hits[hit][0])


def settings():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill('black')
        clock.tick(FPS)
        pygame.display.flip()
    game()

def authors():
    pygame.display.set_caption('Authors')
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    BLUE = (0, 0, 255)

    x1 = x2 = x3 = 300
    font = pygame.font.SysFont('comicsansms', 32)
    text_O = font.render("VORCHUK OLEG", 1, RED, GREEN)
    text_K = font.render("KOMOV KIRILL", 1, RED, GREEN)
    text_I = font.render("ZELENOV IGOR", 1, RED, GREEN)

    running = True
    while running:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.fill((0, 0, 0))
        screen.blit(text_O, (x1, 300))
        screen.blit(text_K, (x2, 350))
        screen.blit(text_I, (x3, 400))
        clock.tick(FPS)
        pygame.display.flip()
        x1 = (x1 - 2) % WIDTH
        x2 = (x2 + 2) % WIDTH
        x3 = (x3 - 2) % WIDTH

    pygame.quit()


def rules():
    pass

def stat():
    pass

def game():
    running = True
    r, g, b = 0, 0, 0
    for i in range(12):
        for j in range(12):
            Bubble((300 + i * 60, 0 + j * 60))
    Border(5, 5, WIDTH - 5, 5)
    Border(5, HEIGHT - 5, WIDTH - 5, HEIGHT - 5)
    Border(5, 5, 5, HEIGHT - 5)
    Border(WIDTH - 5, 5, WIDTH - 5, HEIGHT - 5)
    gun1 = Gun((30, 300), True, True, False, 'Player 1')
    gun2 = Gun((1200, 300), False, False, True, 'Player 2')
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                gun1.rotating, gun2.rotating = gun2.rotating, gun1.rotating
                # r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                create_particles(pygame.mouse.get_pos())
                if gun1.rotating:
                    gun2.fire()
                else:
                    gun1.fire()
                for bubble in all_sprites:
                    if bubble.__class__ == Bubble:
                        bubble.update(event)
            if event.type == pygame.USEREVENT + 1:
                for key in event.__dict__.keys():
                    gun, bullet = key, event.__dict__[key]
                print(f'{gun.name} was hit by {bullet.name}')
                gun.kill()
                running = False
                return gameover()
                # send in some data for score
        screen.fill((r, g, b))
        hits = pygame.sprite.groupcollide(bubbles, bullets, False, False)
        gun_hit = pygame.sprite.groupcollide(guns, bullets, False, False)
        collisions(hits)
        gun_collision(gun_hit)
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


def gameover():
    text = pygame.font.SysFont('impact', 100).render('Bubble Shooter', False, (255, 255, 255))
    menu = Menu()
    menu.append_option("NEW GAME", game)
    menu.append_option('MENU', start_screen)
    menu.append_option('STATISTICS', stat)
    menu.append_option('QUIT', quit)

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
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    return menu._callbacks[menu._current_options_index]()
        screen.fill((0, 0, 0))
        screen.blit(text, (300, 30))

        menu.draw(screen, 300, 250, 75)
        pygame.display.flip()
        clock.tick(FPS)


def all_content():
    if start_screen():
        game()
    pygame.quit()


all_content()
