import pygame_gui
from .game import *
from .player import *
from .helpers import *
import sys
import pygame
from pygame.locals import *
from pygame_gui.windows import UIColourPickerDialog
from PySide6 import QtWidgets
from bots import *
import time


class LoopController:

    def __init__(self) -> None:
        self.loopNum = 0
        self.winnerList = list()
        self.replayRecord = list()
        self.playerTypes = {}
        self.filePath = ""
        self.font_path = "font/ZCOOLKuaiLe-Regular.ttf"
        self.width = 1920
        self.height = 1080
        # key: class name strings
        # value: class without ()
        for i in PlayerMeta.playerTypes:
            self.playerTypes[i.__name__] = i
        self.playerList = []
        self.playerColor = []
        pygame.event.set_allowed([QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP])

    def mainLoop(self, window: pygame.Surface):

        if self.loopNum == 0:  # Home Screen
            pygame.event.set_allowed([QUIT, MOUSEBUTTONDOWN, MOUSEBUTTONUP])
            self.mainMenuLoop(window)
        elif self.loopNum == 1:  # Setting Screen
            self.playerList = []
            self.playerColor = []
            self.loadPlayerLoop(window)
        elif self.loopNum == 2:  # Game Screen
            self.winnerList, self.replayRecord = self.gameplayLoop(
                window, self.playerList
            )
            time.sleep(0)
        elif self.loopNum == 3:  # Game Over Screen
            self.gameOverLoop(window, self.winnerList, self.replayRecord)
        elif self.loopNum == 4:  # Tutorial Screen
            self.loadTutorial(window)

    def gameplayLoop(self, window: pygame.Surface, playerss: list[Player]):
        playingPlayerIndex = 0
        # returnStuff[0] is the winning player number,
        # or -1 if it's a draw
        # returnStuff[1] is replayRecord
        # if there are two players, len(returnStuff[0]) is 1
        # otherwise, it is 2, with the first winner at index 0
        returnStuff = [[], []]
        replayRecord = []
        fontHeader = pygame.font.Font(self.font_path, 42)
        fontBody = pygame.font.Font(self.font_path, 26)
        # replayRecord[0] marks the number of players
        players = copy.deepcopy(playerss)
        players_index = list(range(1, len(players) + 1))
        while None in players:
            players.remove(None)
        if len(players) > 6:
            players = players[:6]
        for i in range(len(players)):
            players[i].setPlayerNum(i + 1)
            if isinstance(players[i], HumanPlayer):
                players[i].setPlayerColor(self.playerColor[i])

        mouse_hover_home = False
        # generate the Game
        g = Game(len(players), self.playerColor)
        # some other settings
        replayRecord.append(str(len(players)))
        highlight = []
        # start the game loop
        while True:
            playingPlayer = players[playingPlayerIndex]
            players_index_queue = (
                players_index[(playingPlayerIndex - (len(players_index)) + 1) :]
                if (playingPlayerIndex - (len(players_index)) + 1) != 0
                else []
            ) + players_index[:playingPlayerIndex]
            # If 100 milliseconds (0.1 seconds) have passed
            # and there is no event, ev will be NOEVENT and
            # the bot player will make a move.
            # Otherwise, the bot player won't move until you
            # move your mouse.
            ev = pygame.event.wait(100)
            if ev.type == QUIT:
                pygame.quit()
                sys.exit()
            self.draw_gradient_background(window, (255, 0, 0), (0, 0, 0))
            g.drawBoard(window, len(players), playingPlayerIndex)
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
            mouse_pos = pygame.mouse.get_pos()
            mouse_left_click = ev.type == MOUSEBUTTONDOWN

            label_player_turn_rect = pygame.Rect(50, 50, 100, 50)  # player now
            draw_text_left(
                window,
                f"Player {playingPlayerIndex+1} 's Turn \n{type(playingPlayer).__name__}",
                fontHeader,
                WHITE,
                label_player_turn_rect,
            )

            label_player_queue_rect = pygame.Rect(50, 1000, 100, 50)  # player now
            players_queue_text = "".join(
                f"Player {i} , " for i in players_index_queue
            ).rstrip(", ")
            draw_text_left(
                window,
                f"Next Player : {players_queue_text}",
                fontBody,
                WHITE,
                label_player_queue_rect,
            )

            home_image = pygame.image.load(
                "images/normal_home.png"
                if not mouse_hover_home
                else "images/hover_home.png"
            ).convert_alpha()
            home_image = pygame.transform.scale(home_image, (100, 100))
            home_button_rect = home_image.get_rect()
            home_button_rect.topleft = (1800, 10)  # กำหนดตำแหน่งที่ต้องการ
            window.blit(home_image, home_button_rect)

            if home_button_rect.collidepoint(mouse_pos):
                mouse_hover_home = True  # เมาส์ hover อยู่บนปุ่ม
                if mouse_left_click:
                    self.loopNum = 0
                    return ([], [])
            else:
                mouse_hover_home = False  # เมาส์ไม่ได้ hover อยู่บนปุ่ม

            pygame.display.update()
            if isinstance(playingPlayer, HumanPlayer):
                start_coor, end_coor = playingPlayer.pickMove(g, window, highlight)
                if (not start_coor) and (not end_coor):
                    self.loopNum = 0
                    return ([], [])
            else:
                start_coor, end_coor = playingPlayer.pickMove(g)
            g.movePiece(start_coor, end_coor)
            time.sleep(0)
            highlight = [start_coor, end_coor]
            replayRecord.append(str(start_coor) + "to" + str(end_coor))
            winning = g.checkWin(playingPlayer.getPlayerNum(), len(players))
            # if winning and len(players) == 2:
            if winning:
                g.drawBoard(window, len(players), playingPlayerIndex)
                playingPlayer.has_won = True
                returnStuff[0].append(playingPlayer.getPlayerNum())
                returnStuff[1] = replayRecord
                self.loopNum = 3
                return returnStuff

            if playingPlayerIndex >= len(players) - 1:
                playingPlayerIndex = 0
            else:
                playingPlayerIndex += 1

    def gameOverLoop(
        self, window: pygame.Surface, winnerList: list, replayRecord: list
    ):
        self.draw_gradient_background(window, (255, 0, 0), (0, 0, 0))

        title_font = pygame.font.Font(self.font_path, int(self.width * 0.08))
        player_text = title_font.render(f"Player {winnerList[0]}", True, WHITE)
        player_text_rect = player_text.get_rect()
        player_text_rect.center = (
            self.width * 0.5,
            self.height * 0.22,
        )  # เลื่อนขึ้นเล็กน้อยเพื่อจัดให้ตรงกลาง

        # แสดงผลบรรทัดที่ 2: "Wins"
        wins_text = title_font.render("Wins", True, WHITE)
        wins_text_rect = wins_text.get_rect()
        wins_text_rect.center = (
            self.width * 0.5,
            self.height * 0.35,
        )  # เลื่อนลงเล็กน้อยสำหรับบรรทัดที่สอง

        # วาดข้อความทั้งสองบรรทัดบนหน้าต่าง
        window.blit(player_text, player_text_rect)
        window.blit(wins_text, wins_text_rect)
        PlayButton = TextButton(
            "Play Again",
            centerx=int(self.width * 0.5),
            centery=int(self.height * 0.6),
            width=self.width * 0.2,
            height=self.height * 0.05,
            font=self.font_path,
            font_size=48,
            text_color=WHITE,
            button_color=None,
            border_color=None,
        )
        SettingButton = TextButton(
            "Setting",
            centerx=int(self.width * 0.5),
            centery=int(self.height * 0.7),
            width=self.width * 0.2,
            height=self.height * 0.05,
            font=self.font_path,
            font_size=48,
            text_color=WHITE,
            button_color=None,
            border_color=None,
        )
        MenuButton = TextButton(
            "Main Menu",
            centerx=int(self.width * 0.5),
            centery=int(self.height * 0.8),
            width=self.width * 0.08,
            height=self.height * 0.05,
            font=self.font_path,
            font_size=48,
            text_color=WHITE,
            button_color=None,
            border_color=None,
        )
        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            mouse_pos = pygame.mouse.get_pos()
            mouse_left_click = pygame.mouse.get_pressed()[0]

            if PlayButton.isClicked(mouse_pos, mouse_left_click):
                self.loopNum = 2
                break
            if SettingButton.isClicked(mouse_pos, mouse_left_click):
                self.loopNum = 1
                break
            if MenuButton.isClicked(mouse_pos, mouse_left_click):
                self.loopNum = 0
                break
            if PlayButton.isHovering(mouse_pos):
                PlayButton.text_color = YELLOW
            else:
                PlayButton.text_color = WHITE

            if SettingButton.isHovering(mouse_pos):
                SettingButton.text_color = YELLOW
            else:
                SettingButton.text_color = WHITE

            if MenuButton.isHovering(mouse_pos):
                MenuButton.text_color = YELLOW
            else:
                MenuButton.text_color = WHITE

            PlayButton.draw(window, mouse_pos)
            SettingButton.draw(window, mouse_pos)
            MenuButton.draw(window, mouse_pos)

            pygame.display.update()

    def loadPlayerLoop(self, window: pygame.Surface):

        appWidth = window.get_width()
        appHeight = window.get_height()

        # กำหนดขนาดพื้นที่ของการแสดงผล
        box_x, box_y = appWidth * 0.0625, appHeight * 0.08
        box_width, box_height = appWidth * 0.875, appHeight * 0.8

        font = pygame.font.SysFont(None, 48)  # ฟอนต์สำหรับข้อความ
        fontTitle = pygame.font.Font(self.font_path, 80)
        fontBody = pygame.font.Font(self.font_path, 36)
        fontSelect = pygame.font.Font(self.font_path, 24)
        start_hover = False

        # ข้อมูลเริ่มต้นของผู้เล่น
        playerList = []
        for e in self.playerTypes:
            playerList.append(e)

        type_player_amount = len(self.playerTypes)

        selected_player_count = 2  # ค่าเริ่มต้นคือ 3 ผู้เล่น
        selected_player1_type = 0
        selected_player2_type = 0
        selected_player3_type = 0
        selected_player4_type = 0
        selected_player5_type = 0
        selected_player6_type = 0
        mouse_hover2 = False
        mouse_hover3 = False
        mouse_hover4 = False
        mouse_hover6 = False
        mouse_hover_tutorial = False

        ui_manager = pygame_gui.UIManager((1920, 1080))
        colour_image = pygame.image.load("images/logo_color.png").convert_alpha()
        colour_image = pygame.transform.scale(colour_image, (50, 50))

        # สร้างปุ่มที่ไม่ทำการ hover
        colour_picker_button1 = NonHoverButton(
            pygame.Rect(890, 450, 50, 50), "", ui_manager
        )
        colour_picker_button2 = NonHoverButton(
            pygame.Rect(1690, 450, 50, 50), "", ui_manager
        )
        colour_picker_button3 = NonHoverButton(
            pygame.Rect(890, 600, 50, 50), "", ui_manager
        )
        colour_picker_button4 = NonHoverButton(
            pygame.Rect(1690, 600, 50, 50), "", ui_manager
        )
        colour_picker_button5 = NonHoverButton(
            pygame.Rect(890, 750, 50, 50), "", ui_manager
        )
        colour_picker_button6 = NonHoverButton(
            pygame.Rect(1690, 750, 50, 50), "", ui_manager
        )

        colour_picker = None
        selected_player_colour_picker = 0
        current_colour1 = pygame.Color(PLAYER_COLORS[0])
        current_colour2 = pygame.Color(PLAYER_COLORS[1])
        current_colour3 = pygame.Color(DARK_GRAY)
        current_colour4 = pygame.Color(DARK_GRAY)
        current_colour5 = pygame.Color(DARK_GRAY)
        current_colour6 = pygame.Color(DARK_GRAY)
        clock = pygame.time.Clock()
        # วาดหน้าเริ่มต้น
        running = True
        while running:
            time_delta = clock.tick(60) / 1000.0
            self.draw_gradient_background(window, (255, 0, 0), (0, 0, 0))  # เคลียร์หน้าจอ

            # วาดกรอบ
            # สร้างพื้นผิวใหม่ที่รองรับความโปร่งใส
            transparent_surface = pygame.Surface(
                (box_width, box_height), pygame.SRCALPHA
            )

            # ตั้งค่าสีและความโปร่งใส (สี GRAY พร้อมความโปร่งใส 50%)
            transparent_surface.fill((0, 0, 0, 0))  # ทำพื้นหลังเป็นโปร่งใสทั้งหมดก่อน

            # วาดสี่เหลี่ยมที่มีขอบมนพร้อม alpha transparency ลงในพื้นผิว
            pygame.draw.rect(
                transparent_surface,
                (128, 128, 128, 128),
                (0, 0, box_width, box_height),
                border_radius=20,
            )

            # วาดพื้นผิวที่ทำขอบมนลงบนหน้าจอหลัก
            window.blit(transparent_surface, (box_x, box_y))

            # วาดรูปภาพปุ่ม Tutorial
            button_image = pygame.image.load(
                "images/Tutorial_On_Hover.png"
                if mouse_hover_tutorial
                else "images/Tutorial_Un_Hover.png"
            ).convert_alpha()
            tutorial_button_rect = button_image.get_rect()
            tutorial_button_rect.topleft = (1800, 10)  # กำหนดตำแหน่งที่ต้องการ
            window.blit(button_image, tutorial_button_rect.topleft)

            # วาดข้อความเลือกจำนวนผู้เล่น
            label_Setting_rect = pygame.Rect(129, box_y + 50, box_width, 50)
            draw_text(window, "Setting", fontTitle, WHITE, label_Setting_rect)

            # วาดปุ่มเลือกจำนวนผู้เล่น

            label_Setting_rect = pygame.Rect(
                box_x + 100, box_y + 190, 100, 50
            )  # player1
            draw_text(window, "Player", fontBody, WHITE, label_Setting_rect)

            rButton_2P_rect = pygame.Rect(box_x + 300, box_y + 170, 350, 100)
            rButton_3P_rect = pygame.Rect(box_x + 600, box_y + 170, 350, 100)
            rButton_4P_rect = pygame.Rect(box_x + 900, box_y + 170, 350, 100)
            rButton_6P_rect = pygame.Rect(box_x + 1170, box_y + 170, 350, 100)

            pygame.draw.rect(
                window,
                (
                    YELLOW
                    if selected_player_count == 6
                    else (GRAY if mouse_hover6 else DARK_GRAY)
                ),
                rButton_6P_rect,
                border_radius=20,
            )
            draw_text(
                window,
                "6",
                font,
                WHITE if selected_player_count == 6 else WHITE,
                rButton_6P_rect,
            )

            pygame.draw.rect(
                window,
                (
                    YELLOW
                    if selected_player_count == 4
                    else (GRAY if mouse_hover4 else DARK_GRAY)
                ),
                rButton_4P_rect,
                border_radius=20,
            )
            draw_text(
                window,
                "4",
                font,
                WHITE if selected_player_count == 4 else WHITE,
                rButton_4P_rect,
            )

            pygame.draw.rect(
                window,
                (
                    YELLOW
                    if selected_player_count == 3
                    else (GRAY if mouse_hover3 else DARK_GRAY)
                ),
                rButton_3P_rect,
                border_radius=20,
            )
            draw_text(
                window,
                "3",
                font,
                WHITE if selected_player_count == 3 else WHITE,
                rButton_3P_rect,
            )

            pygame.draw.rect(
                window,
                (
                    YELLOW
                    if selected_player_count == 2
                    else (GRAY if mouse_hover2 else DARK_GRAY)
                ),
                rButton_2P_rect,
                border_radius=20,
            )
            draw_text(
                window,
                "2",
                font,
                WHITE if selected_player_count == 2 else WHITE,
                rButton_2P_rect,
            )

            # Element Setting
            left_arrow_points = [(50, 0), (0, 25), (50, 50)]
            right_arrow_points = [(0, 0), (50, 25), (0, 50)]

            # Player 1 Setting
            player1x = 170
            player1y = 450
            label_Setting_rect1 = pygame.Rect(
                player1x + 30, player1y, 100, 50
            )  # player1
            draw_text(window, "Player 1", fontBody, WHITE, label_Setting_rect1)

            label_rect1 = pygame.Rect(
                player1x + 200, player1y - 10, 500, 70
            )  # selected 1
            pygame.draw.rect(
                window,
                WHITE if selected_player_count >= 1 else DARK_GRAY,
                label_rect1,
                border_radius=20,
            )  # วาดพื้นหลัง
            draw_text(
                window,
                f"{playerList[selected_player1_type]}",
                fontSelect,
                BLACK,
                label_rect1,
            )

            left_arrow_rect1 = pygame.Rect(player1x + 220, player1y, 50, 50)  # ลูกศรซ้าย
            left_arrow1_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            left_arrow1_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(left_arrow1_surface, YELLOW, left_arrow_points)
            window.blit(left_arrow1_surface, left_arrow_rect1.topleft)

            right_arrow_rect1 = pygame.Rect(player1x + 630, player1y, 50, 50)  # ลูกศรขวา
            rigth_arrow1_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            rigth_arrow1_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(rigth_arrow1_surface, YELLOW, right_arrow_points)
            window.blit(rigth_arrow1_surface, right_arrow_rect1.topleft)

            pygame.draw.circle(
                window,
                (current_colour1.r, current_colour1.g, current_colour1.b),
                (player1x + 745, player1y + 25),
                25,
                25,
            )
            colour_picker_button1.set_image(colour_image)

            # Player 2 Setting
            player2x = 970
            player2y = 450
            label_Setting_rect2 = pygame.Rect(
                player2x + 30, player2y, 100, 50
            )  # player2
            draw_text(window, "Player 2", fontBody, WHITE, label_Setting_rect2)

            label_rect2 = pygame.Rect(
                player2x + 200, player2y - 10, 500, 70
            )  # selected 2
            pygame.draw.rect(
                window,
                WHITE if selected_player_count >= 2 else DARK_GRAY,
                label_rect2,
                border_radius=20,
            )  # วาดพื้นหลัง
            draw_text(
                window,
                f"{playerList[selected_player2_type]}",
                fontSelect,
                BLACK,
                label_rect2,
            )

            left_arrow_rect2 = pygame.Rect(player2x + 220, player2y, 50, 50)  # ลูกศรซ้าย
            left_arrow2_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            left_arrow2_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(left_arrow2_surface, YELLOW, left_arrow_points)
            window.blit(left_arrow2_surface, left_arrow_rect2.topleft)

            right_arrow_rect2 = pygame.Rect(player2x + 630, player2y, 50, 50)  # ลูกศรขวา
            rigth_arrow2_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            rigth_arrow2_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(rigth_arrow2_surface, YELLOW, right_arrow_points)
            window.blit(rigth_arrow2_surface, right_arrow_rect2.topleft)

            pygame.draw.circle(
                window,
                (current_colour2.r, current_colour2.g, current_colour2.b),
                (player2x + 745, player2y + 25),
                25,
                25,
            )
            colour_picker_button2.set_image(colour_image)

            # Player 3 Setting
            player3x = 170
            player3y = 600
            label_Setting_rect3 = pygame.Rect(
                player3x + 30, player3y, 100, 50
            )  # player3
            draw_text(window, "Player 3", fontBody, WHITE, label_Setting_rect3)

            label_rect3 = pygame.Rect(
                player3x + 200, player3y - 10, 500, 70
            )  # selected 3
            pygame.draw.rect(
                window,
                WHITE if selected_player_count >= 3 else DARK_GRAY,
                label_rect3,
                border_radius=20,
            )  # วาดพื้นหลัง
            draw_text(
                window,
                (
                    f"{playerList[selected_player3_type]}"
                    if selected_player_count >= 3
                    else "Empty"
                ),
                fontSelect,
                BLACK,
                label_rect3,
            )

            left_arrow_rect3 = pygame.Rect(player3x + 220, player3y, 50, 50)  # ลูกศรซ้าย
            left_arrow3_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            left_arrow3_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(
                left_arrow3_surface,
                YELLOW if selected_player_count >= 3 else DARK_GRAY,
                left_arrow_points,
            )
            window.blit(left_arrow3_surface, left_arrow_rect3.topleft)

            right_arrow_rect3 = pygame.Rect(player3x + 630, player3y, 50, 50)  # ลูกศรขวา
            rigth_arrow3_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            rigth_arrow3_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(
                rigth_arrow3_surface,
                YELLOW if selected_player_count >= 3 else DARK_GRAY,
                right_arrow_points,
            )
            window.blit(rigth_arrow3_surface, right_arrow_rect3.topleft)

            pygame.draw.circle(
                window,
                (current_colour3.r, current_colour3.g, current_colour3.b),
                (player3x + 745, player3y + 25),
                25,
                25,
            )
            colour_picker_button3.set_image(colour_image)
            (
                colour_picker_button3.disable()
                if selected_player_count < 3
                else colour_picker_button3.enable()
            )

            # Player 4 Setting
            player4x = 970
            player4y = 600
            label_Setting_rect4 = pygame.Rect(
                player4x + 30, player4y, 100, 50
            )  # player4
            draw_text(window, "Player 4", fontBody, WHITE, label_Setting_rect4)

            label_rect4 = pygame.Rect(
                player4x + 200, player4y - 10, 500, 70
            )  # selected 4
            pygame.draw.rect(
                window,
                WHITE if selected_player_count >= 4 else DARK_GRAY,
                label_rect4,
                border_radius=20,
            )  # วาดพื้นหลัง
            draw_text(
                window,
                (
                    f"{playerList[selected_player4_type]}"
                    if selected_player_count >= 4
                    else "Empty"
                ),
                fontSelect,
                BLACK,
                label_rect4,
            )

            left_arrow_rect4 = pygame.Rect(player4x + 220, player4y, 50, 50)  # ลูกศรซ้าย
            left_arrow4_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            left_arrow4_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(
                left_arrow4_surface,
                YELLOW if selected_player_count >= 4 else DARK_GRAY,
                left_arrow_points,
            )
            window.blit(left_arrow4_surface, left_arrow_rect4.topleft)

            right_arrow_rect4 = pygame.Rect(player4x + 630, player4y, 50, 50)  # ลูกศรขวา
            rigth_arrow4_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            rigth_arrow4_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(
                rigth_arrow4_surface,
                YELLOW if selected_player_count >= 4 else DARK_GRAY,
                right_arrow_points,
            )
            window.blit(rigth_arrow4_surface, right_arrow_rect4.topleft)

            pygame.draw.circle(
                window,
                (current_colour4.r, current_colour4.g, current_colour4.b),
                (player4x + 745, player4y + 25),
                25,
                25,
            )
            colour_picker_button4.set_image(colour_image)
            (
                colour_picker_button4.disable()
                if selected_player_count < 4
                else colour_picker_button4.enable()
            )

            # Player 5 Setting
            player5x = 170
            player5y = 750
            label_Setting_rect5 = pygame.Rect(
                player5x + 30, player5y, 100, 50
            )  # player5
            draw_text(window, "Player 5", fontBody, WHITE, label_Setting_rect5)

            label_rect5 = pygame.Rect(
                player5x + 200, player5y - 10, 500, 70
            )  # selected 5
            pygame.draw.rect(
                window,
                WHITE if selected_player_count >= 5 else DARK_GRAY,
                label_rect5,
                border_radius=20,
            )  # วาดพื้นหลัง
            draw_text(
                window,
                (
                    f"{playerList[selected_player5_type]}"
                    if selected_player_count >= 5
                    else "Empty"
                ),
                fontSelect,
                BLACK,
                label_rect5,
            )

            left_arrow_rect5 = pygame.Rect(player5x + 220, player5y, 50, 50)  # ลูกศรซ้าย
            left_arrow5_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            left_arrow5_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(
                left_arrow5_surface,
                YELLOW if selected_player_count >= 5 else DARK_GRAY,
                left_arrow_points,
            )
            window.blit(left_arrow5_surface, left_arrow_rect5.topleft)

            right_arrow_rect5 = pygame.Rect(player5x + 630, player5y, 50, 50)  # ลูกศรขวา
            rigth_arrow5_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            rigth_arrow5_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(
                rigth_arrow5_surface,
                YELLOW if selected_player_count >= 5 else DARK_GRAY,
                right_arrow_points,
            )
            window.blit(rigth_arrow5_surface, right_arrow_rect5.topleft)

            pygame.draw.circle(
                window,
                (current_colour5.r, current_colour5.g, current_colour5.b),
                (player5x + 745, player5y + 25),
                25,
                25,
            )
            colour_picker_button5.set_image(colour_image)
            (
                colour_picker_button5.disable()
                if selected_player_count < 5
                else colour_picker_button5.enable()
            )

            # Player 6 Setting
            player6x = 970
            player6y = 750
            label_Setting_rect6 = pygame.Rect(
                player6x + 30, player6y, 100, 50
            )  # player6
            draw_text(window, "Player 6", fontBody, WHITE, label_Setting_rect6)

            label_rect6 = pygame.Rect(
                player6x + 200, player6y - 10, 500, 70
            )  # selected 6
            pygame.draw.rect(
                window,
                WHITE if selected_player_count >= 6 else DARK_GRAY,
                label_rect6,
                border_radius=20,
            )  # วาดพื้นหลัง
            draw_text(
                window,
                (
                    f"{playerList[selected_player6_type]}"
                    if selected_player_count >= 6
                    else "Empty"
                ),
                fontSelect,
                BLACK,
                label_rect6,
            )

            left_arrow_rect6 = pygame.Rect(player6x + 220, player6y, 50, 50)  # ลูกศรซ้าย
            left_arrow6_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            left_arrow6_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(
                left_arrow6_surface,
                YELLOW if selected_player_count >= 6 else DARK_GRAY,
                left_arrow_points,
            )
            window.blit(left_arrow6_surface, left_arrow_rect6.topleft)

            right_arrow_rect6 = pygame.Rect(player6x + 630, player6y, 50, 50)  # ลูกศรขวา
            rigth_arrow6_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            rigth_arrow6_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(
                rigth_arrow6_surface,
                YELLOW if selected_player_count >= 6 else DARK_GRAY,
                right_arrow_points,
            )
            window.blit(rigth_arrow6_surface, right_arrow_rect6.topleft)

            pygame.draw.circle(
                window,
                (current_colour6.r, current_colour6.g, current_colour6.b),
                (player6x + 745, player6y + 25),
                25,
                25,
            )
            colour_picker_button6.set_image(colour_image)
            (
                colour_picker_button6.disable()
                if selected_player_count < 6
                else colour_picker_button6.enable()
            )

            # วาดปุ่มเริ่มเกม

            start_button_rect = pygame.Rect(
                appWidth * 0.438, appHeight * 0.8125, 240, 40
            )
            start_button_surface = pygame.Surface((240, 40), pygame.SRCALPHA)
            start_button_surface.fill((0, 0, 0, 0))
            pygame.draw.rect(
                start_button_surface, (0, 0, 0, 0), (0, 0, 240, 40), border_radius=10
            )
            window.blit(start_button_surface, (appWidth * 0.438, appHeight * 0.8125))
            draw_text(
                window,
                "Start Game",
                fontBody,
                YELLOW if start_hover else WHITE,
                start_button_rect,
            )

            menu_button_rect = pygame.Rect(appWidth * 0.438, appHeight * 0.9, 240, 40)
            menu_button_surface = pygame.Surface((240, 40), pygame.SRCALPHA)
            menu_button_surface.fill((0, 0, 0, 0))
            pygame.draw.rect(
                menu_button_surface, (0, 0, 0, 0), (0, 0, 240, 40), border_radius=10
            )
            window.blit(menu_button_surface, (appWidth * 0.438, appHeight * 0.8125))
            draw_text(window, "menu", fontBody, WHITE, menu_button_rect)

            # ตรวจสอบเหตุการณ์
            for event in pygame.event.get():
                ui_manager.process_events(event)
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEMOTION:  # ตรวจสอบการเคลื่อนที่ของเมาส์ (Hover)
                    mouse_pos = pygame.mouse.get_pos()

                    if tutorial_button_rect.collidepoint(mouse_pos):
                        mouse_hover_tutorial = True
                    else:
                        mouse_hover_tutorial = False

                    if rButton_2P_rect.collidepoint(mouse_pos):
                        mouse_hover2 = True
                        mouse_hover3 = False
                        mouse_hover4 = False
                        mouse_hover6 = False

                    elif rButton_3P_rect.collidepoint(mouse_pos):
                        mouse_hover3 = True
                        mouse_hover2 = False
                        mouse_hover4 = False
                        mouse_hover6 = False

                    elif rButton_4P_rect.collidepoint(mouse_pos):
                        mouse_hover4 = True
                        mouse_hover2 = False
                        mouse_hover3 = False
                        mouse_hover6 = False

                    elif rButton_6P_rect.collidepoint(mouse_pos):
                        mouse_hover6 = True
                        mouse_hover2 = False
                        mouse_hover3 = False
                        mouse_hover4 = False

                    else:
                        mouse_hover2 = False
                        mouse_hover3 = False
                        mouse_hover4 = False
                        mouse_hover6 = False

                    if start_button_rect.collidepoint(mouse_pos):
                        start_hover = True
                    else:
                        start_hover = False

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # ตรวจสอบการคลิกปุ่ม tutorial
                    if tutorial_button_rect.collidepoint(mouse_pos):
                        self.loopNum = 4
                        running = False

                    # ตรวจสอบการคลิกปุ่มเลือกจำนวนผู้เล่น

                    if rButton_2P_rect.collidepoint(mouse_pos):
                        selected_player_count = 2
                        selected_player3_type = 0
                        selected_player4_type = 0
                        selected_player5_type = 0
                        selected_player6_type = 0
                        current_colour3 = pygame.Color(DARK_GRAY)
                        current_colour4 = pygame.Color(DARK_GRAY)
                        current_colour5 = pygame.Color(DARK_GRAY)
                        current_colour6 = pygame.Color(DARK_GRAY)
                    elif rButton_3P_rect.collidepoint(mouse_pos):
                        selected_player_count = 3
                        selected_player4_type = 0
                        selected_player5_type = 0
                        selected_player6_type = 0
                        current_colour3 = pygame.Color(PLAYER_COLORS[2])
                        current_colour4 = pygame.Color(DARK_GRAY)
                        current_colour5 = pygame.Color(DARK_GRAY)
                        current_colour6 = pygame.Color(DARK_GRAY)
                    elif rButton_4P_rect.collidepoint(mouse_pos):
                        selected_player_count = 4
                        selected_player5_type = 0
                        selected_player6_type = 0
                        current_colour3 = pygame.Color(PLAYER_COLORS[2])
                        current_colour4 = pygame.Color(PLAYER_COLORS[3])
                        current_colour5 = pygame.Color(DARK_GRAY)
                        current_colour6 = pygame.Color(DARK_GRAY)
                    elif rButton_6P_rect.collidepoint(mouse_pos):
                        selected_player_count = 6
                        current_colour3 = pygame.Color(PLAYER_COLORS[2])
                        current_colour4 = pygame.Color(PLAYER_COLORS[3])
                        current_colour5 = pygame.Color(PLAYER_COLORS[4])
                        current_colour6 = pygame.Color(PLAYER_COLORS[5])

                    if left_arrow_rect1.collidepoint(mouse_pos):  # player1
                        selected_player1_type = (
                            selected_player1_type - 1
                            if selected_player1_type > 0
                            else type_player_amount - 1
                        )

                    if right_arrow_rect1.collidepoint(mouse_pos):
                        selected_player1_type = (
                            selected_player1_type + 1
                            if selected_player1_type < type_player_amount - 1
                            else 0
                        )

                    if left_arrow_rect2.collidepoint(mouse_pos):  # player2
                        selected_player2_type = (
                            selected_player2_type - 1
                            if selected_player2_type > 0
                            else type_player_amount - 1
                        )

                    if right_arrow_rect2.collidepoint(mouse_pos):
                        selected_player2_type = (
                            selected_player2_type + 1
                            if selected_player2_type < type_player_amount - 1
                            else 0
                        )

                    if (
                        left_arrow_rect3.collidepoint(mouse_pos)
                        and selected_player_count >= 3
                    ):  # player3
                        selected_player3_type = (
                            selected_player3_type - 1
                            if selected_player3_type > 0
                            else type_player_amount - 1
                        )

                    if (
                        right_arrow_rect3.collidepoint(mouse_pos)
                        and selected_player_count >= 3
                    ):
                        selected_player3_type = (
                            selected_player3_type + 1
                            if selected_player3_type < type_player_amount - 1
                            else 0
                        )

                    if (
                        left_arrow_rect4.collidepoint(mouse_pos)
                        and selected_player_count >= 4
                    ):  # player4
                        selected_player4_type = (
                            selected_player4_type - 1
                            if selected_player4_type > 0
                            else type_player_amount - 1
                        )

                    if (
                        right_arrow_rect4.collidepoint(mouse_pos)
                        and selected_player_count >= 4
                    ):
                        selected_player4_type = (
                            selected_player4_type + 1
                            if selected_player4_type < type_player_amount - 1
                            else 0
                        )

                    if (
                        left_arrow_rect5.collidepoint(mouse_pos)
                        and selected_player_count >= 5
                    ):  # player5
                        selected_player5_type = (
                            selected_player5_type - 1
                            if selected_player5_type > 0
                            else type_player_amount - 1
                        )

                    if (
                        right_arrow_rect5.collidepoint(mouse_pos)
                        and selected_player_count >= 5
                    ):
                        selected_player5_type = (
                            selected_player5_type + 1
                            if selected_player5_type < type_player_amount - 1
                            else 0
                        )

                    if (
                        left_arrow_rect6.collidepoint(mouse_pos)
                        and selected_player_count >= 6
                    ):  # player6
                        selected_player6_type = (
                            selected_player6_type - 1
                            if selected_player6_type > 0
                            else type_player_amount - 1
                        )

                    if (
                        right_arrow_rect6.collidepoint(mouse_pos)
                        and selected_player_count >= 6
                    ):
                        selected_player6_type = (
                            selected_player6_type + 1
                            if selected_player6_type < type_player_amount - 1
                            else 0
                        )

                    # ตรวจสอบการคลิกปุ่มเริ่มเกม
                    if start_button_rect.collidepoint(mouse_pos):
                        self.startGame()  # เริ่มเกม
                        selected_player_type = [
                            selected_player1_type,
                            selected_player2_type,
                            selected_player3_type,
                            selected_player4_type,
                            selected_player5_type,
                            selected_player6_type,
                        ]
                        for i in range(selected_player_count):
                            self.playerList.append(
                                self.playerTypes[playerList[selected_player_type[i]]](
                                    selected_player_count
                                )
                            )
                        current_colour_list = [
                            current_colour1,
                            current_colour2,
                            current_colour3,
                            current_colour4,
                            current_colour5,
                            current_colour6,
                        ]
                        for i in range(selected_player_count):
                            current_colour = current_colour_list[i]
                            self.playerColor.append(
                                (current_colour.r, current_colour.g, current_colour.b)
                            )

                        running = False

                    if menu_button_rect.collidepoint(mouse_pos):
                        self.backToMenu()

                        running = False
                if (
                    event.type == pygame_gui.UI_BUTTON_PRESSED
                    and event.ui_element == colour_picker_button1
                ):  # set Color of player 1
                    colour_picker = UIColourPickerDialog(
                        pygame.Rect(50, 50, 300, 300),
                        ui_manager,
                        window_title="Change Colour Player 1",
                        initial_colour=current_colour1,
                    )
                    colour_picker_button1.disable()
                    selected_player_colour_picker = 1

                if (
                    event.type == pygame_gui.UI_BUTTON_PRESSED
                    and event.ui_element == colour_picker_button2
                ):  # set Color of player 2
                    colour_picker = UIColourPickerDialog(
                        pygame.Rect(50, 50, 300, 300),
                        ui_manager,
                        window_title="Change Colour Player 2",
                        initial_colour=current_colour2,
                    )
                    colour_picker_button2.disable()
                    selected_player_colour_picker = 2

                if (
                    event.type == pygame_gui.UI_BUTTON_PRESSED
                    and event.ui_element == colour_picker_button3
                ):  # set Color of player 3
                    colour_picker = UIColourPickerDialog(
                        pygame.Rect(50, 50, 300, 300),
                        ui_manager,
                        window_title="Change Colour Player 3",
                        initial_colour=current_colour3,
                    )
                    colour_picker_button3.disable()
                    selected_player_colour_picker = 3

                if (
                    event.type == pygame_gui.UI_BUTTON_PRESSED
                    and event.ui_element == colour_picker_button4
                ):  # set Color of player 4
                    colour_picker = UIColourPickerDialog(
                        pygame.Rect(50, 50, 300, 300),
                        ui_manager,
                        window_title="Change Colour Player 4",
                        initial_colour=current_colour4,
                    )
                    colour_picker_button4.disable()
                    selected_player_colour_picker = 4

                if (
                    event.type == pygame_gui.UI_BUTTON_PRESSED
                    and event.ui_element == colour_picker_button5
                ):  # set Color of player 5
                    colour_picker = UIColourPickerDialog(
                        pygame.Rect(50, 50, 300, 300),
                        ui_manager,
                        window_title="Change Colour Player 5",
                        initial_colour=current_colour5,
                    )
                    colour_picker_button5.disable()
                    selected_player_colour_picker = 5

                if (
                    event.type == pygame_gui.UI_BUTTON_PRESSED
                    and event.ui_element == colour_picker_button6
                ):  # set Color of player 6
                    colour_picker = UIColourPickerDialog(
                        pygame.Rect(50, 50, 300, 300),
                        ui_manager,
                        window_title="Change Colour Player 6",
                        initial_colour=current_colour6,
                    )
                    colour_picker_button5.disable()
                    selected_player_colour_picker = 6

                if event.type == pygame_gui.UI_COLOUR_PICKER_COLOUR_PICKED:
                    if selected_player_colour_picker == 1:
                        current_colour1 = event.colour
                    elif selected_player_colour_picker == 2:
                        current_colour2 = event.colour
                    elif selected_player_colour_picker == 3:
                        current_colour3 = event.colour
                    elif selected_player_colour_picker == 4:
                        current_colour4 = event.colour
                    elif selected_player_colour_picker == 5:
                        current_colour5 = event.colour
                    elif selected_player_colour_picker == 6:
                        current_colour6 = event.colour

                if event.type == pygame_gui.UI_WINDOW_CLOSE and colour_picker:
                    if selected_player_colour_picker == 1:
                        colour_picker_button1.enable()
                    elif selected_player_colour_picker == 2:
                        colour_picker_button2.enable()
                    elif selected_player_colour_picker == 3:
                        colour_picker_button3.enable()
                    elif selected_player_colour_picker == 4:
                        colour_picker_button4.enable()
                    elif selected_player_colour_picker == 5:
                        colour_picker_button5.enable()
                    elif selected_player_colour_picker == 6:
                        colour_picker_button6.enable()
                    colour_picker = None
                    selected_player_colour_picker = 0

            ui_manager.update(time_delta)
            ui_manager.draw_ui(window)
            pygame.display.update()

    # helpers for loadPlayerLoop and replayLoop
    def startGame(self):
        self.loopNum = 2  # go to gameplay

    def backToMenu(self):
        self.loopNum = 0  # go to main menu

    def closing(self):

        self.loopNum = 1
        QtWidgets.QApplication.closeAllWindows()

    def loadTutorial(self, window: pygame.Surface):

        selected_page = 1
        left_hovering = False
        right_hovering = False

        CloseButton = TextButton(
            "Close",
            centerx=int(self.width * 0.5),
            centery=int(self.height * 0.82),
            width=self.width * 0.08,
            height=self.height * 0.05,
            font=self.font_path,
            font_size=48,
            text_color=WHITE,
            button_color=None,
            border_color=None,
        )

        while True:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            mouse_pos = pygame.mouse.get_pos()
            mouse_left_click = pygame.mouse.get_pressed()[0]

            # กำหนดค่าโปร่งใส (alpha) ให้กับสีสี่เหลี่ยม (0-255, 128 ประมาณ 50% โปร่งใส)
            rect_color = (150, 0, 0, 100)  # สีเทา พร้อม alpha = 153 (60% โปร่งใส)
            pygame.draw.rect(
                window, rect_color, (160, 120, 1600, 800), border_radius=20
            )

            image = pygame.image.load(
                "images/Tutorial_page_" + str(selected_page) + ".png"
            )
            image = pygame.transform.scale(image, (1400, 800))
            window.blit(image, (260, 120))

            left_arrow_rect = pygame.Rect(180, 510, 50, 50)  # ลูกศรซ้าย
            left_arrow_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            left_arrow_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(
                left_arrow_surface,
                YELLOW if left_hovering else WHITE,
                [(50, 0), (0, 25), (50, 50)],
            )
            window.blit(left_arrow_surface, left_arrow_rect.topleft)

            right_arrow_rect = pygame.Rect(1690, 510, 50, 50)  # ลูกศรขวา
            rigth_arrow_surface = pygame.Surface((50, 50), pygame.SRCALPHA)
            rigth_arrow_surface.fill((0, 0, 0, 0))
            pygame.draw.polygon(
                rigth_arrow_surface,
                YELLOW if right_hovering else WHITE,
                [(0, 0), (50, 25), (0, 50)],
            )
            window.blit(rigth_arrow_surface, right_arrow_rect.topleft)

            if CloseButton.isClicked(mouse_pos, mouse_left_click):
                self.loopNum = 1
                break

            if CloseButton.isHovering(mouse_pos):
                CloseButton.text_color = YELLOW
            else:
                CloseButton.text_color = WHITE

            CloseButton.draw(window, mouse_pos)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break
                if event.type == pygame.MOUSEMOTION:  # ตรวจสอบการเคลื่อนที่ของเมาส์ (Hover)
                    mouse_pos = pygame.mouse.get_pos()

                    if left_arrow_rect.collidepoint(mouse_pos):
                        left_hovering = True
                    else:
                        left_hovering = False
                    if right_arrow_rect.collidepoint(mouse_pos):
                        right_hovering = True
                    else:
                        right_hovering = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()

                    # ตรวจสอบการคลิกปุ่ม tutorial
                    if left_arrow_rect.collidepoint(mouse_pos):
                        selected_page -= 1 if selected_page > 1 else -4

                    if right_arrow_rect.collidepoint(mouse_pos):
                        selected_page += 1 if selected_page < 5 else -4

            pygame.display.update()

    def draw_gradient_background(self, window: pygame.Surface, color_top, color_bottom):
        # ไล่สีจากบนลงล่าง
        for y in range(self.height):
            # คำนวณอัตราส่วนของสีจากด้านบนไปยังด้านล่าง
            ratio = y / self.height
            # ผสมสีตามอัตราส่วน
            r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
            g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
            b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
            pygame.draw.line(window, (r, g, b), (0, y), (self.width, y))

    def mainMenuLoop(self, window: pygame.Surface):

        self.draw_gradient_background(window, (255, 0, 0), (0, 0, 0))  # จากสีแดงไปสีดำ

        title_font = pygame.font.Font(self.font_path, int(self.width * 0.08))
        titleText = title_font.render("Chinese Checkers", True, YELLOW)
        titleTextRect = titleText.get_rect()
        titleTextRect.center = (self.width * 0.5, self.height * 0.25)
        window.blit(titleText, titleTextRect)
        StartButton = TextButton(
            "Start Game",
            centerx=int(self.width * 0.5),
            centery=int(self.height * 0.55),
            width=self.width * 0.2,
            height=self.height * 0.05,
            font=self.font_path,
            font_size=48,
            text_color=WHITE,
            button_color=None,
            border_color=None,
        )
        ExitButton = TextButton(
            "Exit",
            centerx=int(self.width * 0.5),
            centery=int(self.height * 0.7),
            width=self.width * 0.08,
            height=self.height * 0.05,
            font=self.font_path,
            font_size=48,
            text_color=WHITE,
            button_color=None,
            border_color=None,
        )
        while True:
            ev = pygame.event.wait()
            if ev.type == QUIT:
                pygame.quit()
                sys.exit()
            mouse_pos = pygame.mouse.get_pos()
            mouse_left_click = ev.type == MOUSEBUTTONDOWN
            if StartButton.isClicked(mouse_pos, mouse_left_click):
                self.loopNum = 1
                break
            if ExitButton.isClicked(mouse_pos, mouse_left_click):
                pygame.quit()
                sys.exit()

            if StartButton.isHovering(mouse_pos):  # เปลี่ยนที่นี่
                StartButton.text_color = YELLOW
            else:
                StartButton.text_color = WHITE

            if ExitButton.isHovering(mouse_pos):  # เปลี่ยนที่นี่
                ExitButton.text_color = YELLOW
            else:
                ExitButton.text_color = WHITE

            StartButton.draw(window, mouse_pos)
            ExitButton.draw(window, mouse_pos)
            pygame.display.update()
