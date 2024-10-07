import random
import time

from game_logic.player import Player
from game_logic.game import *


class MinimaxAlphaBetaBotPlayer(Player):
    def __init__(self, depth=3, time_limit=5):
        super().__init__()
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
                obj_start = subj_to_obj_coor(start, self.playerNum)
                obj_end = subj_to_obj_coor(end, self.playerNum)

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
                obj_start = subj_to_obj_coor(start, self.playerNum)
                obj_end = subj_to_obj_coor(end, self.playerNum)

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
                obj_start = subj_to_obj_coor(start, opponent)
                obj_end = subj_to_obj_coor(end, opponent)

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
        return subj_to_obj_coor(start, self.playerNum), subj_to_obj_coor(
            end, self.playerNum
        )
