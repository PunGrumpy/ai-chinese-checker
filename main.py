from game_logic.loops import *
from game_logic.game import *
from game_logic.player import *
from game_logic.literals import *
import pygame
from lib.utils import resource_path

pygame.init()
window = pygame.display.set_mode((1920, 1080), pygame.SCALED | pygame.SRCALPHA)
pygame.display.set_caption("Chinese Checkers")

icon = pygame.image.load(resource_path("images/icon.png"))
pygame.display.set_icon(icon)

lc = LoopController()

while True:
    """
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()"""
    lc.mainLoop(window)
