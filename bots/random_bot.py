import random

from game_logic.player import Player
from game_logic.game import *


class RandomBotPlayer(Player):
    def __init__(self, playerCount: int):
        super().__init__(playerCount)

    def pickMove(self, g: Game):
        """returns [start_coor, end_coor]"""
        moves = g.allMovesDict(self.playerNum, True)
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
