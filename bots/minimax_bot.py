import time
from game_logic.player import Player
from game_logic.game import Game
from game_logic.helpers import (
    get_player_zone,
    subj_to_obj_coor,
    obj_to_subj_coor,
    distance,
)
from game_logic.literals import ZONE_COOR
import math
import random


class MinimaxBotPlayer(Player):
    def __init__(self, playerCount: int, max_depth: int = 6, max_time: float = 4.0):
        super().__init__(playerCount)
        self.max_depth = max_depth
        self.max_time = max_time
        self.start_time = 0
        self.transposition_table = {}

    def pickMove(self, g: Game):
        self.start_time = time.time()
        best_move = None
        alpha = -math.inf
        beta = math.inf
        best_score = -math.inf

        moves = self.get_sorted_moves(g)

        for depth in range(1, self.max_depth + 1):
            if time.time() - self.start_time > self.max_time:
                break

            for start, end in moves:
                if time.time() - self.start_time > self.max_time:
                    break
                new_game = g.clone()
                new_game.movePiece(start, end)
                score = self.alphabeta(
                    new_game, depth - 1, alpha, beta, False, self.playerNum
                )

                if score > best_score:
                    best_score = score
                    best_move = (start, end)

                alpha = max(alpha, score)

        return best_move if best_move else random.choice(moves)

    def get_sorted_moves(self, g: Game):
        moves = []
        all_moves = g.allMovesDict(self.playerNum, True)
        for start in all_moves:
            for end in all_moves[start]:
                obj_start = subj_to_obj_coor(start, self.playerNum, self.playerCount)
                obj_end = subj_to_obj_coor(end, self.playerNum, self.playerCount)
                score = self.quick_evaluate_move(g, obj_start, obj_end)
                moves.append((obj_start, obj_end, score))
        return [move[:2] for move in sorted(moves, key=lambda x: x[2], reverse=True)]

    def quick_evaluate_move(self, g: Game, start, end):
        end_zone = (get_player_zone(self.playerNum, self.playerCount) + 4) % 6
        end_zone = end_zone if end_zone != 0 else 6
        score = distance(start, end)
        if end in ZONE_COOR[end_zone]:
            score += 10
        return score

    def alphabeta(
        self,
        g: Game,
        depth: int,
        alpha: float,
        beta: float,
        maximizing_player: bool,
        player_num: int,
    ):
        if time.time() - self.start_time > self.max_time:
            return self.evaluate(g, player_num)

        game_hash = hash(str(g.getBoardState(player_num)))
        if game_hash in self.transposition_table:
            return self.transposition_table[game_hash]

        if depth == 0 or g.checkWin(player_num, self.playerCount):
            score = self.evaluate(g, player_num)
            self.transposition_table[game_hash] = score
            return score

        moves = self.get_sorted_moves(g)

        if maximizing_player:
            max_eval = -math.inf
            for start, end in moves:
                new_game = g.clone()
                new_game.movePiece(start, end)
                eval = self.alphabeta(
                    new_game, depth - 1, alpha, beta, False, player_num
                )
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)
                if beta <= alpha:
                    break
            self.transposition_table[game_hash] = max_eval
            return max_eval
        else:
            min_eval = math.inf
            next_player = (player_num % self.playerCount) + 1
            for start, end in moves:
                new_game = g.clone()
                new_game.movePiece(start, end)
                eval = self.alphabeta(
                    new_game, depth - 1, alpha, beta, True, next_player
                )
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)
                if beta <= alpha:
                    break
            self.transposition_table[game_hash] = min_eval
            return min_eval

    def evaluate(self, g: Game, player_num: int):
        score = 0
        end_zone = (get_player_zone(self.playerNum, self.playerCount) + 4) % 6
        end_zone = end_zone if end_zone != 0 else 6

        pieces_in_end_zone = 0
        total_distance = 0
        blocking_score = 0

        for piece in g.pieces[player_num]:
            obj_coor = piece.getCoor()
            subj_coor = obj_to_subj_coor(obj_coor, player_num, self.playerCount)

            # Distance to end zone
            min_distance = min(
                distance(obj_coor, end_coor) for end_coor in ZONE_COOR[end_zone]
            )
            total_distance += min_distance

            # Pieces in end zone
            if obj_coor in ZONE_COOR[end_zone]:
                pieces_in_end_zone += 1
                score += 50 - min_distance  # ให้คะแนนเพิ่มเติมเมื่ออยู่ใกล้กลางของ end zone

            # Forward progress
            score += subj_coor[1] * 2

            # Blocking opponent's pieces
            for opponent in range(1, self.playerCount + 1):
                if opponent != player_num:
                    for opp_piece in g.pieces[opponent]:
                        if distance(obj_coor, opp_piece.getCoor()) == 1:
                            blocking_score += 1

        # Overall strategies
        score += (
            10 - pieces_in_end_zone
        ) * 30  # Encourage getting all pieces to end zone
        score -= total_distance * 2  # Minimize total distance to end zone
        score += blocking_score * 5  # Reward for blocking opponents

        # Bonus for winning
        if g.checkWin(player_num, self.playerCount):
            score += 10000

        return score
