import random
import os
from math import cos, sin, radians

import pygame
import sys
# from ctypes import windll
# import win32con

# import win32gui

pygame.init()
pygame.font.init()
SIZE = WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode(SIZE)
all_sprites = pygame.sprite.Group()
vertical_borders = pygame.sprite.Group()
horizontal_borders = pygame.sprite.Group()
pygame.display.set_caption('Bubble shooter')
clock = pygame.time.Clock()
FPS = 50
screen_rect = (0, 0, WIDTH, HEIGHT)
GRAVITY = 0,2


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


def create_particles(position):
    particle_count = 20
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers)

class Bubble(pygame.sprite.Sprite):
    def __init__(self, pos):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image('bubble.png'), (30, 30))
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


def start_screen():
    text = pygame.font.SysFont('impact', 60).render('Bubble Shooter', False, (255, 255, 255))
    btn = Button()
    btn.set_text('Начать')
    btn.set_font('impact')
    btn.set_rect(350, 600, 200, 80)
    btn.set_size(60)
    exit_btn = Button()
    exit_btn.set_text('Выйти')
    exit_btn.set_font('impact')
    exit_btn.set_rect(350, 700, 200, 80)
    exit_btn.set_size(60)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                btn.clicked(event.pos)
                if btn.was_clicked:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
                exit_btn.clicked(event.pos)
                if exit_btn.was_clicked:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))
        screen.blit(text, (260, 380))
        btn.render()
        exit_btn.render()
        pygame.display.flip()
        clock.tick(FPS)
    return btn.was_clicked


def all_content():
    if start_screen():
        game()
    pygame.quit()


class Gun(pygame.sprite.Sprite):
    def __init__(self, pos, rotate, rotate_right, reverse):
        super().__init__(all_sprites)
        image = load_image(random.choice(['blue.png', 'red.png', 'green.png']))
        if reverse:
            image = pygame.transform.flip(image, 1, 0)
        self.image = pygame.transform.scale(image, (70, 70))
        self.origin = self.image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos        self.rotating = rotate        self.angle = 0        self.right = rotate_right    def update(self):
        if self.rotating:
            self.angle = (self.angle - 1) % 360 if self.right \
                else (self.angle + 1) % 360            self.rotate()

    def rotate(self):
        self.image = pygame.transform.rotate(self.origin, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

    def fire(self):
        x, y = self.rect.x, self.rect.y
        angle = self.angle
        Bullet(x, y, 20, angle)


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, width, angle):
        super().__init__(all_sprites)
        self.image = pygame.Surface((width, width), pygame.SRCALPHA, 32)
        pygame.draw.line(self.image, pygame.Color('white'), (0, 0), (width * cos(radians(angle)), width * sin(radians(angle))), 2)
        self.rect = pygame.Rect(x, y, width, width)
        self.width, self.angle = width, angle
        self.vx = 10 * cos(radians(angle))
        self.vy = 10 * sin(radians(angle))

    def update(self):
        self.rect = self.rect.move(self.vx, self.vy)
        if pygame.sprite.spritecollideany(self, horizontal_borders):
            self.vy = -self.vy
            self.image = pygame.Surface((2 * self.width, 2 * self.width), pygame.SRCALPHA, 32)
            if self.vy < 0:
                pygame.draw.line(self.image, pygame.Color('white'), (0, self.width),                                 (self.width * cos(radians(self.angle)),                                  self.width * (1 - sin(radians(self.angle)))), 2)
            else:
                pygame.draw.line(self.image, pygame.Color('white'), (0, 0),                                 (self.width * cos(radians(self.angle)),                                  self.width * sin(radians(self.angle))), 2)
        if pygame.sprite.spritecollideany(self, vertical_borders):
            self.vx = -self.vx
            if self.vx < 0:
                self.image = pygame.Surface((2 * self.width, 2 * self.width), pygame.SRCALPHA, 32)
                pygame.draw.line(self.image, pygame.Color('white'), (self.width, 0),                                 (self.width * (1 - cos(radians(self.angle))),                                  self.width * sin(radians(self.angle))), 2)
            else:
                self.image = pygame.Surface((2 * self.width, 2 * self.width), pygame.SRCALPHA, 32)
                pygame.draw.line(self.image, pygame.Color('white'), (self.width, 0),                                 (self.width * (1 - cos(radians(self.angle))),                                  self.width * sin(radians(self.angle))), 2)


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

def game():
    running = True
    r, g, b = 0, 0, 0
    for i in range(10):
        for j in range(10):
            Bubble((400 + i * 60, 0 + j * 60))
    Border(5, 5, WIDTH - 5, 5)
    Border(5, HEIGHT - 5, WIDTH - 5, HEIGHT - 5)
    Border(5, 5, 5, HEIGHT - 5)
    Border(WIDTH - 5, 5, WIDTH - 5, HEIGHT - 5)
    gun1 = Gun((30, 300), True, True, False)
    gun2 = Gun((1200, 300), False, False, True)
    Bullet(100, 300, 20, 30)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    gun1.rotating, gun2.rotating = gun2.rotating, gun1.rotating
                    r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                    create_particles(pygame.mouse.get_pos())
                if gun1.rotating:
                    gun2.fire()
                else:
                    gun1.fire()
                for bubble in all_sprites:
                    if bubble.__class__ == Bubble:
                        bubble.update(event)
        screen.fill((r, g, b))
        all_sprites.draw(screen)
        all_sprites.update()
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


all_content()
start_screen()
game()
