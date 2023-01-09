import random
import os
import pygame
import sys

pygame.init()
pygame.font.init()
SIZE = WIDTH, HEIGHT = 1400, 610
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
        self.image = pygame.transform.scale(load_image(random.choice(
            ['bluebubble.png', 'redbubble.png', 'greenbubble.png'])), (70, 70))
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos

    def update(self, *args):
        if args and args[0].type == pygame.MOUSEBUTTONDOWN and \
                self.rect.collidepoint(args[0].pos):
            self.kill()


def start_screen():
    font = pygame.font.SysFont('impact', 60)
    text = font.render('Bubble shooter', False, 'white')
    text_coords = (500, 100)
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


# class Gun(pygame.sprite.Sprite):
#     def blitRotate(self, image, pos, origin_pos, angle, surface):
#         self.surface = surface
#
#         image_rect = image.get_rect(topleft=(pos[0] - origin_pos[0], pos[1] - origin_pos[1]))
#         offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
#
#         rotated_offset = offset_center_to_pivot.rotate(-angle)
#
#         rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
#
#         rotated_image = pygame.transform.rotate(image, angle)
#         rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)
#
#         self.surface.blit(rotated_image, rotated_image_rect)
#
#     def blitRotate2(self, image, topleft, angle):
#         rotated_image = pygame.transform.rotate(image, angle)
#         new_rect = rotated_image.get_rect(center=image.get_rect(topleft=topleft).center)
#
#         self.surface.blit(rotated_image, new_rect.topleft)
#         pygame.draw.rect(self.surface, (255, 0, 0), new_rect, 2)
#
#     try:
#         image = pygame.transform.scale(load_image(random.choice(
#             ['blue.png', 'red.png', 'green.png'])), (70, 70))
#     except Exception:
#         text = pygame.font.SysFont('Times New Roman', 50).render('image', False, (255, 255, 0))
#         image = pygame.Surface((text.get_width() + 1, text.get_height() + 1))
#         pygame.draw.rect(image, (0, 0, 255), (1, 1, *text.get_size()))
#         image.blit(text, (1, 1))
#     w, h = image.get_size()
#
#     angle = 0
#     done = False
#     while not done:
#         clock.tick(50)
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 done = True
#
#         pos = (screen.get_width() / 2, screen.get_height() / 2)
#
#         screen.fill(0)
#         blitRotate(screen, image, pos, (w / 2, h / 2), angle)
#
#         angle += 2
#
#         pygame.display.flip()


class Gun(pygame.sprite.Sprite):
    def __init__(self, pos, rotate):
        super().__init__(all_sprites)
        self.image = pygame.transform.scale(load_image(random.choice(
            ['blue.png', 'red.png', 'green.png'])), (70, 70))
        self.origin = self.image
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = pos
        self.rotating = rotate
        self.angle = 0

    def update(self):
        if self.rotating:
            self.angle = (self.angle - 1) % 360
            self.rotate()

    def rotate(self):
        self.image = pygame.transform.rotate(self.origin, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)


def game():
    running = True
    r, g, b = 0, 0, 0
    for i in range(10):
        for j in range(10):
            Bubble((400 + i * 60, 0 + j * 60))
    gun1 = Gun((30, 300), True)
    gun2 = Gun((1200, 300), False)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                gun1.rotating, gun2.rotating = gun2.rotating, gun1.rotating
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
