from .literals import *
from .helpers import *
from .piece import *
import pygame, copy


class Game:
    def __init__(self, playerCount, playerColor):
        self.width = 1920
        self.height = 1080
        self.playerCount = playerCount
        self.playerColor = playerColor
        self.pieces: dict[int, set[Piece]] = {
            1: set(),
            2: set(),
            3: set(),
            4: set(),
            5: set(),
            6: set(),
        }
        self.board = self.createBoard(playerCount)
        # for drawing board
        self.unitLength = int(self.width * 0.035)  # unitLength length in pixels
        self.lineWidth = int(self.unitLength * 0.05)  # line width
        self.circleRadius = int(self.height * 0.025)  # board square (circle) radius
        self.centerCoor = (self.width / 2, self.height / 2)

    def getBoard(self):
        return self.board

    def createBoard(self, playerCount: int):
        Board = {}

        # 2 Player
        if playerCount == 2:
            for i in range(1, 7):
                for z in ZONE_COOR[i]:
                    if i == 1:  # Player 1   zone 1
                        Board[z] = Piece(1, z[0], z[1])
                        self.pieces[1].add(Board[z])
                    elif i == 4:  # Player 2   zone 4
                        Board[z] = Piece(2, z[0], z[1])
                        self.pieces[2].add(Board[z])
                    else:
                        Board[z] = None

        elif playerCount == 3:
            for i in range(1, 7):
                for z in ZONE_COOR[i]:
                    if i == 1:  # Player 1   zone 1
                        Board[z] = Piece(1, z[0], z[1])
                        self.pieces[1].add(Board[z])
                    elif i == 3:  # Player 2   zone 3
                        Board[z] = Piece(2, z[0], z[1])
                        self.pieces[2].add(Board[z])
                    elif i == 5:  # Player 3   zone 5
                        Board[z] = Piece(3, z[0], z[1])
                        self.pieces[3].add(Board[z])
                    else:
                        Board[z] = None

        elif playerCount == 4:
            for i in range(1, 7):
                for z in ZONE_COOR[i]:
                    if i == 2:  # Player 1   zone 2
                        Board[z] = Piece(1, z[0], z[1])
                        self.pieces[1].add(Board[z])
                    elif i == 3:  # Player 2   zone 3
                        Board[z] = Piece(2, z[0], z[1])
                        self.pieces[2].add(Board[z])
                    elif i == 5:  # Player 3   zone 5
                        Board[z] = Piece(3, z[0], z[1])
                        self.pieces[3].add(Board[z])
                    elif i == 6:  # Player 3   zone 6
                        Board[z] = Piece(4, z[0], z[1])
                        self.pieces[4].add(Board[z])
                    else:
                        Board[z] = None

        elif playerCount == 6:

            for i in range(1, 7):
                for z in ZONE_COOR[i]:
                    if i == 1:  # Player 1   zone 1
                        Board[z] = Piece(1, z[0], z[1])
                        self.pieces[1].add(Board[z])
                    elif i == 2:  # Player 2   zone 2
                        Board[z] = Piece(2, z[0], z[1])
                        self.pieces[2].add(Board[z])
                    elif i == 3:  # Player 3   zone 3
                        Board[z] = Piece(3, z[0], z[1])
                        self.pieces[3].add(Board[z])
                    elif i == 4:  # Player 4   zone 4
                        Board[z] = Piece(4, z[0], z[1])
                        self.pieces[4].add(Board[z])
                    elif i == 5:  # Player 5   zone 5
                        Board[z] = Piece(5, z[0], z[1])
                        self.pieces[5].add(Board[z])
                    elif i == 6:  # Player 6   zone 6
                        Board[z] = Piece(6, z[0], z[1])
                        self.pieces[6].add(Board[z])
                    else:
                        Board[z] = None

        for n in NEUTRAL_COOR:
            Board[n] = None

        return Board

    def getValidMoves(self, startPos: tuple, playerNum: int, playerCount: int):
        moves = []
        for direction in DIRECTIONS:
            destination = add(startPos, direction)
            if destination not in self.board:
                continue  # out of bounds
            elif self.board[destination] == None:
                moves.append(destination)  # walk
            else:  # self.board[destination] != None
                destination = add(destination, direction)
                if destination not in self.board or self.board[destination] != None:
                    continue  # out of bounds or can't jump
                moves.append(destination)
                checkJump(moves, self.board, destination, direction, playerNum)
        for i in copy.deepcopy(moves):
            # You can move past other player's territory, but you can't stay there.
            if (
                (i not in ZONE_COOR[1])
                and (i not in ZONE_COOR[2])
                and (i not in ZONE_COOR[3])
                and (i not in ZONE_COOR[4])
                and (i not in ZONE_COOR[5])
                and (i not in ZONE_COOR[6])
                and (i not in NEUTRAL_COOR)
            ):
                while i in moves:
                    moves.remove(i)
        return list(set(moves))

    def getValidMovesWithZone(self, startPos: tuple, playerNum: int, playerCount: int):
        # 2 Player
        if playerCount == 2:
            start_zone = 1 if playerNum == 1 else 4
            end_zone = 4 if playerNum == 1 else 1
        elif playerCount == 3:
            start_zone = 1 if playerNum == 1 else 3 if playerNum == 2 else 5
            end_zone = 4 if playerNum == 1 else 6 if playerNum == 2 else 2
        elif playerCount == 4:
            start_zone = (
                2
                if playerNum == 1
                else 3 if playerNum == 2 else 5 if playerNum == 3 else 6
            )
            end_zone = (
                4
                if playerNum == 1
                else 5 if playerNum == 2 else 2 if playerNum == 3 else 3
            )
        elif playerCount == 6:
            start_zone = playerNum
            end_zone = (playerNum + 3) % 6
            end_zone = end_zone if end_zone != 0 else 6

        moves = []
        for direction in DIRECTIONS:
            destination = add(startPos, direction)
            if destination not in self.board:
                continue  # out of bounds
            elif self.board[destination] == None:
                moves.append(destination)  # walk
            else:  # self.board[destination] != None
                destination = add(destination, direction)
                if destination not in self.board or self.board[destination] != None:
                    continue  # out of bounds or can't jump
                moves.append(destination)
                checkJump(moves, self.board, destination, direction, playerNum)
        for i in copy.deepcopy(moves):
            # You can move past other player's territory, but you can't stay there.
            if (
                (i not in ZONE_COOR[start_zone])
                and (i not in ZONE_COOR[end_zone])
                and (i not in NEUTRAL_COOR)
            ):
                while i in moves:
                    moves.remove(i)
        return list(set(moves))

    def checkWin(self, playerNum: int, playerCount: int):
        check = False
        if playerCount == 2:
            end_zone = 4 if playerNum == 1 else 1
        elif playerCount == 3:
            end_zone = 4 if playerNum == 1 else 6 if playerNum == 2 else 2
        elif playerCount == 4:
            end_zone = (
                4
                if playerNum == 1
                else 5 if playerNum == 2 else 2 if playerNum == 3 else 3
            )
        elif playerCount == 6:
            end_zone = (playerNum + 3) % 6
            end_zone = end_zone if end_zone != 0 else 6

        for i in ZONE_COOR[end_zone]:
            if self.board[i] == None:
                return False
            if (
                isinstance(self.board[i], Piece)
                and self.board[i].getPlayerNum() == playerNum
            ):
                check = True
        return check

    def getBoardState(self, playerNum: int):
        """Key: subjective coordinates\nValue: piece's player number, or 0 if it's vacant"""
        state = dict()
        for i in self.board:
            state[obj_to_subj_coor(i, playerNum, self.playerCount)] = (
                0 if self.board[i] == None else int(self.board[i].getPlayerNum())
            )
        return state

    def getBoolBoardState(self, playerNum: int):
        """Key: subjective coordinates\nValue: `true`, or `false` if it's vacant"""
        state = dict()
        for i in self.board:
            state[obj_to_subj_coor(i, playerNum, self.playerCount)] = (
                self.board[i] != None
            )
        return state

    def allMovesDict(self, playerNum: int, withZone: bool = False):
        """Returns a dict of all valid moves, in subjective coordinates.
        The key is the coordinates of a piece (`tuple`), and the value is a `list` of destination coordinates.
        """
        moves = dict()

        for p in self.pieces[playerNum]:
            if withZone:
                p_moves_list = self.getValidMovesWithZone(
                    p.getCoor(), playerNum, self.playerCount
                )
            else:
                p_moves_list = self.getValidMoves(
                    p.getCoor(), playerNum, self.playerCount
                )
            if p_moves_list == []:
                continue
            p_subj_coor = obj_to_subj_coor(p.getCoor(), playerNum, self.playerCount)
            moves[p_subj_coor] = [
                obj_to_subj_coor(i, playerNum, self.playerCount) for i in p_moves_list
            ]

        return moves

    # def movePiece(self, start: tuple, end: tuple):
    #     assert self.board[start] != None and self.board[end] == None, "AssertionError at movePiece()"
    #     self.board[start].setCoor(end)
    #     self.board[end] = self.board[start]
    #     self.board[start] = None

    def movePiece(self, start: tuple, end: tuple):
        if self.board[start] is None:
            raise ValueError(f"No piece at start position: {start}")
        if self.board[end] is not None:
            raise ValueError(f"End position not empty: {end}")

        assert (
            self.board[start] != None and self.board[end] == None
        ), "AssertionError at movePiece()"

        self.board[start].setCoor(end)
        self.board[end] = self.board[start]
        self.board[start] = None

    # def drawBoard(self, window: pygame.Surface, playerNum: int=1):
    def drawBoard(self, window: pygame.Surface, playerCount: int, playerTurn: int):
        """inputs Surface object"""
        playerNum = 1

        self.drawPolygons(window, playerTurn, playerCount, playerNum)
        self.drawLines(window)
        self.drawCircles(window, playerNum, playerCount)

    def drawCircles(self, window: pygame.Surface, playerNum: int, playerCount: int):
        for obj_coor in self.board:
            coor = obj_to_subj_coor(obj_coor, playerNum, 2)
            c = add(
                self.centerCoor, mult(h2c(coor), self.unitLength)
            )  # absolute coordinates on screen
            pygame.draw.circle(window, WHITE, c, self.circleRadius)
            pygame.draw.circle(window, BLACK, c, self.circleRadius, self.lineWidth)
            if isinstance(self.board[obj_coor], Piece):

                pygame.draw.circle(
                    window,
                    self.playerColor[self.board[obj_coor].getPlayerNum() - 1],
                    c,
                    self.circleRadius - 2,
                )

    def drawLines(self, window: pygame.Surface):
        """Draws the black lines of the board. Doesn't need playerNum"""
        visited = set()
        neighbors = set()
        for coor in self.board:
            for dir in DIRECTIONS:
                n_coor = add(coor, dir)
                if n_coor not in visited and n_coor in self.board:
                    neighbors.add(n_coor)
            for n_coor in neighbors:
                c = add(self.centerCoor, mult(h2c(coor), self.unitLength))
                n = add(self.centerCoor, mult(h2c(n_coor), self.unitLength))
                pygame.draw.line(window, BLACK, c, n, self.lineWidth)
            neighbors.clear()
        # self.screen_is_altered = False

    def drawPolygons(
        self,
        window: pygame.Surface,
        playerTurn: int,
        playerCount: int,
        playerNum: int = 1,
    ):
        # center hexagon
        pygame.draw.polygon(
            window,
            WHITE,
            (
                abs_coors(self.centerCoor, (-4, 4), self.unitLength),
                abs_coors(self.centerCoor, (0, 4), self.unitLength),
                abs_coors(self.centerCoor, (4, 0), self.unitLength),
                abs_coors(self.centerCoor, (4, -4), self.unitLength),
                abs_coors(self.centerCoor, (0, -4), self.unitLength),
                abs_coors(self.centerCoor, (-4, 0), self.unitLength),
            ),
        )
        # triangles
        colors = [DARK_GRAY, DARK_GRAY, DARK_GRAY, DARK_GRAY, DARK_GRAY, DARK_GRAY]
        for i in range(playerCount):
            colors[get_player_zone(i + 1, playerCount)] = self.playerColor[i]
        border = 10
        highlight_border = 12

        playerZone = get_player_zone(playerTurn + 1, playerCount)
        if playerZone == 0:
            pygame.draw.polygon(
                window,
                YELLOW,
                (
                    add(
                        self.centerCoor,
                        mult(h2c((0, -4)), self.unitLength + highlight_border),
                    ),
                    add(
                        self.centerCoor,
                        mult(h2c((4, -4)), self.unitLength + highlight_border),
                    ),
                    add(
                        self.centerCoor,
                        mult(h2c((4, -8)), self.unitLength + highlight_border),
                    ),
                ),
            )
        elif playerZone == 1:
            pygame.draw.polygon(
                window,
                YELLOW,
                (
                    add(
                        self.centerCoor,
                        mult(h2c((-4, 0)), self.unitLength + highlight_border),
                    ),
                    add(
                        self.centerCoor,
                        mult(h2c((-4, -4)), self.unitLength + highlight_border),
                    ),
                    add(
                        self.centerCoor,
                        mult(h2c((0, -4)), self.unitLength + highlight_border),
                    ),
                ),
            )

        elif playerZone == 2:
            pygame.draw.polygon(
                window,
                YELLOW,
                (
                    add(
                        self.centerCoor,
                        mult(h2c((-8, 4)), self.unitLength + highlight_border),
                    ),
                    add(
                        self.centerCoor,
                        mult(h2c((-4, 4)), self.unitLength + highlight_border),
                    ),
                    add(
                        self.centerCoor,
                        mult(h2c((-4, 0)), self.unitLength + highlight_border),
                    ),
                ),
            )

        elif playerZone == 3:
            pygame.draw.polygon(
                window,
                YELLOW,
                (
                    add(
                        self.centerCoor,
                        mult(h2c((-4, 8)), self.unitLength + highlight_border),
                    ),
                    add(
                        self.centerCoor,
                        mult(h2c((-4, 4)), self.unitLength + highlight_border),
                    ),
                    add(
                        self.centerCoor,
                        mult(h2c((0, 4)), self.unitLength + highlight_border),
                    ),
                ),
            )

        elif playerZone == 4:
            pygame.draw.polygon(
                window,
                YELLOW,
                (
                    add(
                        self.centerCoor,
                        mult(h2c((0, 4)), self.unitLength + highlight_border),
                    ),
                    add(
                        self.centerCoor,
                        mult(h2c((4, 4)), self.unitLength + highlight_border),
                    ),
                    add(
                        self.centerCoor,
                        mult(h2c((4, 0)), self.unitLength + highlight_border),
                    ),
                ),
            )

        else:
            pygame.draw.polygon(
                window,
                YELLOW,
                (
                    add(
                        self.centerCoor,
                        mult(h2c((4, 0)), self.unitLength + highlight_border),
                    ),
                    add(
                        self.centerCoor,
                        mult(h2c((8, -4)), self.unitLength + highlight_border),
                    ),
                    add(
                        self.centerCoor,
                        mult(h2c((4, -4)), self.unitLength + highlight_border),
                    ),
                ),
            )

        pygame.draw.polygon(
            window,
            BLACK,
            (
                add(self.centerCoor, mult(h2c((-4, 8)), self.unitLength + border)),
                add(self.centerCoor, mult(h2c((0, 4)), self.unitLength + border)),
                add(self.centerCoor, mult(h2c((4, 4)), self.unitLength + border)),
                add(self.centerCoor, mult(h2c((4, 0)), self.unitLength + border)),
                add(self.centerCoor, mult(h2c((8, -4)), self.unitLength + border)),
                add(self.centerCoor, mult(h2c((4, -4)), self.unitLength + border)),
                add(self.centerCoor, mult(h2c((4, -8)), self.unitLength + border)),
                add(self.centerCoor, mult(h2c((0, -4)), self.unitLength + border)),
                add(self.centerCoor, mult(h2c((-4, -4)), self.unitLength + border)),
                add(self.centerCoor, mult(h2c((-4, 0)), self.unitLength + border)),
                add(self.centerCoor, mult(h2c((-8, 4)), self.unitLength + border)),
                add(self.centerCoor, mult(h2c((-4, 4)), self.unitLength + border)),
            ),
        )

        pygame.draw.polygon(
            window,
            colors[0],
            (
                add(self.centerCoor, mult(h2c((0, -4)), self.unitLength)),
                add(self.centerCoor, mult(h2c((4, -4)), self.unitLength)),
                add(self.centerCoor, mult(h2c((4, -8)), self.unitLength)),
            ),
        )
        pygame.draw.polygon(
            window,
            colors[1],
            (
                add(self.centerCoor, mult(h2c((-4, 0)), self.unitLength)),
                add(self.centerCoor, mult(h2c((-4, -4)), self.unitLength)),
                add(self.centerCoor, mult(h2c((0, -4)), self.unitLength)),
            ),
        )
        pygame.draw.polygon(
            window,
            colors[2],
            (
                add(self.centerCoor, mult(h2c((-8, 4)), self.unitLength)),
                add(self.centerCoor, mult(h2c((-4, 4)), self.unitLength)),
                add(self.centerCoor, mult(h2c((-4, 0)), self.unitLength)),
            ),
        )
        pygame.draw.polygon(
            window,
            colors[3],
            (
                add(self.centerCoor, mult(h2c((-4, 8)), self.unitLength)),
                add(self.centerCoor, mult(h2c((-4, 4)), self.unitLength)),
                add(self.centerCoor, mult(h2c((0, 4)), self.unitLength)),
            ),
        )
        pygame.draw.polygon(
            window,
            colors[4],
            (
                add(self.centerCoor, mult(h2c((0, 4)), self.unitLength)),
                add(self.centerCoor, mult(h2c((4, 4)), self.unitLength)),
                add(self.centerCoor, mult(h2c((4, 0)), self.unitLength)),
            ),
        )
        pygame.draw.polygon(
            window,
            colors[5],
            (
                add(self.centerCoor, mult(h2c((4, 0)), self.unitLength)),
                add(self.centerCoor, mult(h2c((8, -4)), self.unitLength)),
                add(self.centerCoor, mult(h2c((4, -4)), self.unitLength)),
            ),
        )

        pygame.draw.polygon(
            window,
            WHITE,
            (
                add(self.centerCoor, mult(h2c((-4, 4)), self.unitLength)),
                add(self.centerCoor, mult(h2c((0, 4)), self.unitLength)),
                add(self.centerCoor, mult(h2c((4, 0)), self.unitLength)),
                add(self.centerCoor, mult(h2c((4, -4)), self.unitLength)),
                add(self.centerCoor, mult(h2c((0, -4)), self.unitLength)),
                add(self.centerCoor, mult(h2c((-4, 0)), self.unitLength)),
            ),
        )

    def clone(self):
        """
        Creates a deep copy of the game state. This is useful for AI decision-making,
        where we need to simulate moves without altering the actual game state.
        """
        # Use copy.deepcopy to create a full clone of the game object
        return copy.deepcopy(self)
