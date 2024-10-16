from game_logic.player import Player
from game_logic.game import *
from game_logic.helpers import add, mult


class CustomBotTemplate(Player):
    def __init__(self, playerCount: int):
        super().__init__(playerCount)

    def pickMove(self, g: Game):
        moves = g.allMovesDict(self.playerNum)
        # board_state = g.getBoardState(self.playerNum)
        # bool_board_state = g.getBoolBoardState(self.playerNum)
        """
        The following code section is a simple example: it
        randomly picks a valid move and return it.
        """
        from random import choice

        l = []
        for coor in moves:
            if moves[coor] != []:
                l.append(coor)
        start = choice(l)
        end = choice(moves[start])
        """
        This is the return section. `start` and `end` are
        the starting and ending subjective coordinates.
        """
        return [
            subj_to_obj_coor(start, self.playerNum, self.playerCount),
            subj_to_obj_coor(end, self.playerNum, self.playerCount),
        ]
