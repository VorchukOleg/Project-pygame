import random

import pygame

pygame.init()
pygame.font.init()
SIZE = WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode(SIZE)
pygame.display.set_caption('Bubble shooter')
clock = pygame.time.Clock()
FPS = 50


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
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
        screen.fill((r, g, b))
        pygame.display.flip()
        clock.tick(FPS)


start_screen()
game()
