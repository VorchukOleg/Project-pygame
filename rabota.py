import random
import os
import pygame
import sys

pygame.init()
pygame.font.init()
SIZE = WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode(SIZE)
all_sprites = pygame.sprite.Group()
pygame.display.set_caption('Bubble shooter')
clock = pygame.time.Clock()
FPS = 50
screen_rect = (0, 0, WIDTH, HEIGHT)
GRAVITY = 0.2


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
        Particle(position, random.choice(numbers), random.choice(numbers))


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


def start_screen():
    font = pygame.font.SysFont('impact', 60)
    text = font.render('Bubble shooter', False, 'white')
    text_coords = (275, 200)
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                running = False
                screen.fill('black')
        screen.blit(text, text_coords)
        pygame.display.flip()
        clock.tick(FPS)


def game():
    running = True
    r, g, b = 0, 0, 0
    for i in range(10):
        for j in range(10):
            Bubble((275 + i * 35, 275 + j * 35))
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
                create_particles(pygame.mouse.get_pos())
                for bubble in all_sprites:
                    if bubble.__class__ == Bubble:
                        bubble.update(event)
        all_sprites.update()
        screen.fill((r, g, b))
        all_sprites.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()


start_screen()
game()
