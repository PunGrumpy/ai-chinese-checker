import random

from game_logic.player import Player
from game_logic.game import *


class Greedy2BotPlayer(Player):
    """Always finds a move that jumps through the maximum distance (dest[1] - coor[1])"""

    def __init__(self, playerCount: int):
        super().__init__(playerCount)

    def pickMove(self, g: Game):
        """returns [start_coor, end_coor] in objective coordinates\n
        return [subj_to_obj_coor(start_coor, self.playerNum), subj_to_obj_coor(end_coor, self.playerNum)]
        """
        moves = g.allMovesDict(self.playerNum, True)
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
