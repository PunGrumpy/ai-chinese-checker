import random

from game_logic.player import Player
from game_logic.game import *


class GreedyEasyBot(Player):
    def __init__(self, playerCount: int):
        super().__init__(playerCount)

    def pickMove(self, g: Game):
        """returns [start_coor, end_coor]"""
        moves = g.allMovesDict(self.playerNum, True)
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
            if len(tempMoves) > 0:
                coor = random.choice(list(tempMoves))
                move = random.choice(tempMoves[coor])
            else:
                # backways
                tempMoves.clear()
                for coor in moves:
                    if moves[coor] != []:
                        tempMoves[coor] = []
                    else:
                        continue
                    for dest in moves[coor]:
                        if dest[1] < coor[1]:
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
