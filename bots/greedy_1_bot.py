import random

from game_logic.player import Player
from game_logic.game import *


class GreedyNormalBot(Player):
    """Always finds the move that moves a piece to the topmost square"""

    def __init__(self, playerCount: int):
        super().__init__(playerCount)

    def pickMove(self, g: Game):
        """returns [start_coor, end_coor] in objective coordinates"""
        moves = g.allMovesDict(self.playerNum,True)
        # state = g.boardState(self.playerNum)
        forwardMoves = dict()
        sidewaysMoves = dict()
        backwardMoves = dict()
        start_coor = ()
        end_coor = ()
        # split moves into forward and sideways
        for coor in moves:
            if moves[coor] != []:
                forwardMoves[coor] = []
                sidewaysMoves[coor] = []
                backwardMoves[coor] = []
            else:
                continue
            for dest in moves[coor]:
                if dest[1] > coor[1]:
                    forwardMoves[coor].append(dest)
                if dest[1] == coor[1]:
                    sidewaysMoves[coor].append(dest)
                else:
                    backwardMoves[coor].append(dest)
        for coor in list(forwardMoves):
            if forwardMoves[coor] == []:
                del forwardMoves[coor]
        for coor in list(sidewaysMoves):
            if sidewaysMoves[coor] == []:
                del sidewaysMoves[coor]
        for coor in list(backwardMoves):
            if backwardMoves[coor] == []:
                del backwardMoves[coor]

        # choose the furthest destination (biggest y value in dest),
        # then backmost piece (smallest y value in coor)
        biggestDestY = -8
        smallestStartY = 8
        if len(forwardMoves) == 0:
            if len(sidewaysMoves) == 0:
                start_coor = random.choice(list(backwardMoves))
                end_coor = random.choice(backwardMoves[start_coor])
            else:
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