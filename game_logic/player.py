from .game import *
from .piece import *
from .literals import *
from .helpers import *
import random
import pygame
import math
from pygame.locals import *
import sys
from abc import ABC, ABCMeta, abstractmethod
import time
import math


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


class RandomBotPlayer(Player):
    def __init__(self, playerCount: int):
        super().__init__(playerCount)

    def pickMove(self, g: Game):
        """returns [start_coor, end_coor]"""
        moves = g.allMovesDict(self.playerNum)
        l = []
        for coor in moves:
            if moves[coor] != []:
                l.append(coor)
        coor = random.choice(l)
        move = random.choice(moves[coor])
        return [
            subj_to_obj_coor(coor, self.playerNum, self.playerCount),
            subj_to_obj_coor(move, self.playerNum, self.playerCount),
        ]


class GreedyRandomBotPlayer(Player):
    def __init__(self, playerCount: int):
        super().__init__(playerCount)

    def pickMove(self, g: Game):
        """returns [start_coor, end_coor]"""
        moves = g.allMovesDict(self.playerNum)
        tempMoves = dict()
        # forward
        for coor in moves:
            if moves[coor] != []:
                tempMoves[coor] = []
            else:
                continue
            for dest in moves[coor]:
                if dest[1] > coor[1]:
                    tempMoves[coor].append(dest)
        for coor in list(tempMoves):
            if tempMoves[coor] == []:
                del tempMoves[coor]
        if len(tempMoves) > 0:
            coor = random.choice(list(tempMoves))
            move = random.choice(tempMoves[coor])
        else:
            # sideways
            tempMoves.clear()
            for coor in moves:
                if moves[coor] != []:
                    tempMoves[coor] = []
                else:
                    continue
                for dest in moves[coor]:
                    if dest[1] == coor[1]:
                        tempMoves[coor].append(dest)
            for coor in list(tempMoves):
                if tempMoves[coor] == []:
                    del tempMoves[coor]
            coor = random.choice(list(tempMoves))
            move = random.choice(tempMoves[coor])
        return [
            subj_to_obj_coor(coor, self.playerNum, self.playerCount),
            subj_to_obj_coor(move, self.playerNum, self.playerCount),
        ]


class Greedy1BotPlayer(Player):
    """Always finds the move that moves a piece to the topmost square"""

    def __init__(self, playerCount: int):
        super().__init__(playerCount)

    def pickMove(self, g: Game):
        """returns [start_coor, end_coor] in objective coordinates"""
        moves = g.allMovesDict(self.playerNum)
        # state = g.boardState(self.playerNum)
        forwardMoves = dict()
        sidewaysMoves = dict()
        start_coor = ()
        end_coor = ()
        # split moves into forward and sideways
        for coor in moves:
            if moves[coor] != []:
                forwardMoves[coor] = []
                sidewaysMoves[coor] = []
            else:
                continue
            for dest in moves[coor]:
                if dest[1] > coor[1]:
                    forwardMoves[coor].append(dest)
                if dest[1] == coor[1]:
                    sidewaysMoves[coor].append(dest)
        for coor in list(forwardMoves):
            if forwardMoves[coor] == []:
                del forwardMoves[coor]
        for coor in list(sidewaysMoves):
            if sidewaysMoves[coor] == []:
                del sidewaysMoves[coor]

        # choose the furthest destination (biggest y value in dest),
        # then backmost piece (smallest y value in coor)
        biggestDestY = -8
        smallestStartY = 8
        if len(forwardMoves) == 0:
            start_coor = random.choice(list(sidewaysMoves))
            end_coor = random.choice(sidewaysMoves[start_coor])
        else:
            for coor in forwardMoves:
                for i in range(len(forwardMoves[coor])):
                    dest = forwardMoves[coor][i]
                    if dest[1] > biggestDestY:
                        start_coor = coor
                        end_coor = dest
                        biggestDestY = dest[1]
                        smallestStartY = coor[1]
                    elif dest[1] == biggestDestY:
                        startY = coor[1]
                        if startY < smallestStartY:
                            start_coor = coor
                            end_coor = dest
                            biggestDestY = dest[1]
                            smallestStartY = coor[1]
                        elif startY == smallestStartY:
                            start_coor, end_coor = random.choice(
                                [[start_coor, end_coor], [coor, dest]]
                            )
                            biggestDestY = end_coor[1]
                            smallestStartY = start_coor[1]
        return [
            subj_to_obj_coor(start_coor, self.playerNum, self.playerCount),
            subj_to_obj_coor(end_coor, self.playerNum, self.playerCount),
        ]


class Greedy2BotPlayer(Player):
    """Always finds a move that jumps through the maximum distance (dest[1] - coor[1])"""

    def __init__(self, playerCount: int):
        super().__init__(playerCount)

    def pickMove(self, g: Game):
        """returns [start_coor, end_coor] in objective coordinates\n
        return [subj_to_obj_coor(start_coor, self.playerNum), subj_to_obj_coor(end_coor, self.playerNum)]
        """
        moves = g.allMovesDict(self.playerNum)
        # state = g.boardState(self.playerNum)
        forwardMoves = dict()
        sidewaysMoves = dict()
        start_coor = ()
        end_coor = ()
        max_dist = 0
        # split moves into forward and sideways
        for coor in moves:
            if moves[coor] != []:
                forwardMoves[coor] = []
                sidewaysMoves[coor] = []
            else:
                continue
            for dest in moves[coor]:
                if dest[1] > coor[1]:
                    forwardMoves[coor].append(dest)
                if dest[1] == coor[1]:
                    sidewaysMoves[coor].append(dest)
        for coor in list(forwardMoves):
            if forwardMoves[coor] == []:
                del forwardMoves[coor]
        for coor in list(sidewaysMoves):
            if sidewaysMoves[coor] == []:
                del sidewaysMoves[coor]
        # if forward is empty, move sideways
        if len(forwardMoves) == 0:
            start_coor = random.choice(list(sidewaysMoves))
            end_coor = random.choice(sidewaysMoves[start_coor])
            return [
                subj_to_obj_coor(start_coor, self.playerNum, self.playerCount),
                subj_to_obj_coor(end_coor, self.playerNum, self.playerCount),
            ]
        # forward: max distance
        for coor in forwardMoves:
            for dest in forwardMoves[coor]:
                if start_coor == () and end_coor == ():
                    start_coor = coor
                    end_coor = dest
                    max_dist = end_coor[1] - start_coor[1]
                else:
                    dist = dest[1] - coor[1]
                    if dist > max_dist:
                        max_dist = dist
                        start_coor = coor
                        end_coor = dest
                    elif dist == max_dist:
                        # prefers to move the piece that is more backwards
                        if dest[1] < end_coor[1]:
                            max_dist = dist
                            start_coor = coor
                            end_coor = dest
        return [
            subj_to_obj_coor(start_coor, self.playerNum, self.playerCount),
            subj_to_obj_coor(end_coor, self.playerNum, self.playerCount),
        ]


class MinimaxAlphaBetaBotPlayer(Player):
    def __init__(self, playerCount: int, depth=3, time_limit=5):
        super().__init__(playerCount)
        self.depth = depth
        self.time_limit = time_limit
        self.start_time = 0

    def pickMove(self, g: Game):
        self.start_time = time.time()
        best_move = None
        best_score = float("-inf")
        alpha = float("-inf")
        beta = float("inf")

        moves = g.allMovesDict(self.playerNum)
        for start in moves:
            for end in moves[start]:
                # ใช้การ clone แทนการย้อนกลับ จะทำให้เร็วขึ้น เพราะไม่ต้องทำการย้อนกลับ
                game_clone = g.clone()
                obj_start = subj_to_obj_coor(start, self.playerNum, self.playerCount)
                obj_end = subj_to_obj_coor(end, self.playerNum, self.playerCount)

                game_clone.movePiece(obj_start, obj_end)
                score = self.minimax(game_clone, self.depth - 1, alpha, beta, False)

                if score > best_score:
                    best_score = score
                    best_move = (obj_start, obj_end)

                alpha = max(alpha, best_score)

                if time.time() - self.start_time > self.time_limit:
                    break
            if time.time() - self.start_time > self.time_limit:
                break

        return best_move if best_move else self.fallback_move(g)

    def minimax(self, g: Game, depth, alpha, beta, maximizing_player):
        if (
            depth == 0
            or g.checkWin(self.playerNum)
            or time.time() - self.start_time > self.time_limit
        ):
            return self.evaluate(g)

        if maximizing_player:
            return self.alpha_pruning(g, depth, alpha, beta)
        else:
            return self.beta_pruning(g, depth, alpha, beta)

    def alpha_pruning(self, g: Game, depth, alpha, beta):
        max_eval = float("-inf")
        moves = g.allMovesDict(self.playerNum)
        for start in moves:
            for end in moves[start]:
                obj_start = subj_to_obj_coor(start, self.playerNum, self.playerCount)
                obj_end = subj_to_obj_coor(end, self.playerNum, self.playerCount)

                g.movePiece(obj_start, obj_end)
                eval = self.minimax(g, depth - 1, alpha, beta, False)
                g.movePiece(obj_end, obj_start)

                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    return max_eval
        return max_eval

    def beta_pruning(self, g: Game, depth, alpha, beta):
        min_eval = float("inf")
        opponent = self.playerNum % len(g.pieces) + 1
        moves = g.allMovesDict(opponent)
        for start in moves:
            for end in moves[start]:
                obj_start = subj_to_obj_coor(start, opponent, self.playerCount)
                obj_end = subj_to_obj_coor(end, opponent, self.playerCount)

                g.movePiece(obj_start, obj_end)
                eval = self.minimax(g, depth - 1, alpha, beta, True)
                g.movePiece(obj_end, obj_start)

                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    return min_eval
        return min_eval

    # Heuristic function (สำหรับการประเมินคะแนน)
    def evaluate(self, g: Game):
        score = 0
        goal_coords = ZONE_COOR[self.playerNum]

        # ประเมินตำแหน่งของหมากทั้งหมด
        for piece in g.pieces[self.playerNum]:
            # ระยะทางถึงเป้าหมาย
            min_distance = min(
                self.manhattan_distance(piece.getCoor(), goal) for goal in goal_coords
            )
            score -= min_distance * 20  # เพิ่มน้ำหนักของระยะทาง

            # หมากในพื้นที่เป้าหมาย
            if piece.getCoor() in goal_coords:
                score += 200

            # การควบคุมพื้นที่กลาง
            if piece.getCoor() in NEUTRAL_COOR:
                score += 30

        # โบนัสสำหรับการจบเกม
        if all(piece.getCoor() in goal_coords for piece in g.pieces[self.playerNum]):
            score += 1000

        # ประเมินการกีดขวางคู่ต่อสู้
        opponent = self.playerNum % len(g.pieces) + 1
        for op_piece in g.pieces[opponent]:
            if any(
                self.manhattan_distance(op_piece.getCoor(), our_piece.getCoor()) == 1
                for our_piece in g.pieces[self.playerNum]
            ):
                score += 15

        return score

    def manhattan_distance(self, coord1, coord2):
        return abs(coord1[0] - coord2[0]) + abs(coord1[1] - coord2[1])

    def fallback_move(self, g: Game):
        moves = g.allMovesDict(self.playerNum)
        start = random.choice(list(moves.keys()))
        end = random.choice(moves[start])
        return subj_to_obj_coor(
            start, self.playerNum, self.playerCount
        ), subj_to_obj_coor(end, self.playerNum, self.playerCount)


class HumanPlayer(Player):
    def __init__(self, playerCount: int):
        super().__init__(playerCount)

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
                "images/normal_home.png"
                if not mouse_hover_home
                else "images/hover_home.png"
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
                            PLAYER_COLORS[
                                get_player_zone(piece.getPlayerNum(), self.playerCount)
                            ],
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
                        PLAYER_COLORS[
                            get_player_zone(piece.getPlayerNum(), self.playerCount)
                        ],
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
                        g.drawBoard(window, self.playerCount)
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
