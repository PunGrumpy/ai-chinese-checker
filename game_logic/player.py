from .game import *
from .piece import *
from .literals import *
from .helpers import *
import pygame
import math
from pygame.locals import *
import sys
from abc import ABC, ABCMeta, abstractmethod
import math
from lib.utils import resource_path


class PlayerMeta(ABCMeta):
    playerTypes = []

    def __init__(cls, name, bases, attrs):
        if ABC not in bases:
            PlayerMeta.playerTypes.append(cls)
        super().__init__(name, bases, attrs)


class Player(ABC, metaclass=PlayerMeta):
    def __init__(self, playerCount: int):
        self.playerNum = 0
        self.has_won = False
        self.playerCount = playerCount

    def getPlayerNum(self):
        return self.playerNum

    def setPlayerNum(self, num: int):
        self.playerNum = num

    @abstractmethod
    def pickMove(self, g: Game): ...


class HumanPlayer(Player):
    def __init__(self, playerCount: int):
        super().__init__(playerCount)
        self.playerColor = (0, 0, 0)

    def getPlayerColor(self):
        return self.playerColor

    def setPlayerColor(self, color: tuple):
        self.playerColor = color

    def pickMove(self, g: Game, window: pygame.Surface, highlight=None):
        pieceSet: set[Piece] = g.pieces[self.playerNum]
        validmoves = []
        clicking = False
        mouse_hover_home = False
        selected_piece_coor = ()
        prev_selected_piece_coor = ()
        # pygame.event.set_allowed([QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP])
        while True:
            ev = pygame.event.wait()
            if ev.type == QUIT:
                pygame.quit()
                sys.exit()
            # wait for a click,
            # if mouse hovers on a piece, highlight it
            mouse_pos = pygame.mouse.get_pos()
            clicking = ev.type == MOUSEBUTTONDOWN
            #
            if highlight:
                pygame.draw.circle(
                    window,
                    (117, 10, 199),
                    abs_coors(g.centerCoor, highlight[0], g.unitLength),
                    g.circleRadius,
                    g.lineWidth + 2,
                )
                pygame.draw.circle(
                    window,
                    (117, 10, 199),
                    abs_coors(g.centerCoor, highlight[1], g.unitLength),
                    g.circleRadius,
                    g.lineWidth + 2,
                )

            button_image = pygame.image.load(
                resource_path(
                    "images/normal_home.png"
                    if not mouse_hover_home
                    else "images/hover_home.png"
                )
            ).convert_alpha()
            button_image = pygame.transform.scale(button_image, (100, 100))
            tutorial_button_rect = button_image.get_rect()
            tutorial_button_rect.topleft = (1800, 10)  # กำหนดตำแหน่งที่ต้องการ
            window.blit(button_image, tutorial_button_rect)

            if tutorial_button_rect.collidepoint(mouse_pos):
                mouse_hover_home = True  # เมาส์ hover อยู่บนปุ่ม
                if clicking:
                    return (False, False)
            else:
                mouse_hover_home = False  # เมาส์ไม่ได้ hover อยู่บนปุ่ม

            for piece in pieceSet:
                coor = (
                    # obj_to_subj_coor(piece.getCoor(), self.playerNum, 2)
                    # if humanPlayerNum != 0
                    # else
                    piece.getCoor()
                )
                absCoor = abs_coors(g.centerCoor, coor, g.unitLength)
                if (
                    math.dist(mouse_pos, absCoor) <= g.circleRadius
                    and piece.mouse_hovering == False
                ):
                    # change the piece's color
                    pygame.draw.circle(
                        window,
                        brighten_color(
                            self.playerColor,
                            0.75,
                        ),
                        absCoor,
                        g.circleRadius - 2,
                    )
                    piece.mouse_hovering = True
                elif (
                    math.dist(mouse_pos, absCoor) > g.circleRadius
                    and piece.mouse_hovering == True
                    and tuple(window.get_at(ints(absCoor))) != WHITE
                ):
                    # draw a circle of the original color
                    pygame.draw.circle(
                        window,
                        self.playerColor,
                        absCoor,
                        g.circleRadius - 2,
                    )
                    piece.mouse_hovering = False
                # when a piece is selected, and you click any of the valid destinations,
                # you will move that piece to the destination
                if selected_piece_coor == piece.getCoor() and validmoves != []:
                    for d in validmoves:
                        destCoor = abs_coors(g.centerCoor, d, g.unitLength)
                        if math.dist(mouse_pos, destCoor) <= g.circleRadius:
                            if clicking:
                                return [selected_piece_coor, d]
                            # draw a gray circle
                            else:
                                pygame.draw.circle(
                                    window, LIGHT_GRAY, destCoor, g.circleRadius - 2
                                )
                        elif math.dist(mouse_pos, destCoor) > g.circleRadius:
                            # draw a white circle
                            pygame.draw.circle(
                                window, GRAY, destCoor, g.circleRadius - 2
                            )
                # clicking the piece
                if math.dist(mouse_pos, absCoor) <= g.circleRadius and clicking == True:
                    selected_piece_coor = piece.getCoor()
                    if (
                        prev_selected_piece_coor != ()
                        and selected_piece_coor != prev_selected_piece_coor
                    ):
                        g.drawBoard(window, self.playerCount, self.playerNum)
                    prev_selected_piece_coor = selected_piece_coor
                    # draw a semi-transparent gray circle outside the piece
                    pygame.draw.circle(
                        window,
                        (161, 166, 196, 50),
                        absCoor,
                        g.circleRadius,
                        g.lineWidth + 1,
                    )
                    # draw semi-transparent circles around all coordinates in getValidMoves()
                    validmoves = g.getValidMoves(
                        selected_piece_coor, self.playerNum, self.playerCount
                    )
                for c in validmoves:
                    pygame.draw.circle(
                        window,
                        (161, 166, 196),
                        abs_coors(g.centerCoor, c, g.unitLength),
                        g.circleRadius,
                        g.lineWidth + 2,
                    )

            pygame.display.update()
            # return [start_coor, end_coor]
