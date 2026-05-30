# ui.py
import pygame
from settings import *


class UI:
    def __init__(self, screen):
        self.screen = screen
        self.font_small = pygame.font.Font(None, 24)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_large = pygame.font.Font(None, 72)

    def draw_health_bar(self, x, y, current_health, max_health):
        """绘制血条"""
        bar_width = 200
        bar_height = 20
        health_percent = current_health / max_health
        health_width = bar_width * health_percent

        # 背景
        pygame.draw.rect(self.screen, DARK_RED, (x, y, bar_width, bar_height))
        # 当前血量
        pygame.draw.rect(self.screen, RED, (x, y, health_width, bar_height))
        # 边框
        pygame.draw.rect(self.screen, WHITE, (x, y, bar_width, bar_height), 2)

        # 血量文字
        health_text = self.font_small.render(f"{current_health}/{max_health}", True, WHITE)
        text_x = x + bar_width // 2 - health_text.get_width() // 2
        text_y = y + bar_height // 2 - health_text.get_height() // 2
        self.screen.blit(health_text, (text_x, text_y))

    def draw_crystals(self, count):
        """绘制水晶数量"""
        crystal_text = self.font_medium.render(f"Crystals: {count}", True, YELLOW)
        self.screen.blit(crystal_text, (10, 40))

    def draw_minimap(self, grid, player_x, player_y, rooms, visible):
        """绘制小地图"""
        mini_size = 5
        map_width = len(grid[0]) * mini_size
        map_height = len(grid) * mini_size
        map_x = SCREEN_WIDTH - map_width - 10
        map_y = 10

        # 背景
        pygame.draw.rect(self.screen, BLACK, (map_x - 2, map_y - 2, map_width + 4, map_height + 4))
        pygame.draw.rect(self.screen, WHITE, (map_x - 2, map_y - 2, map_width + 4, map_height + 4), 1)

        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if visible[y][x] or (x == player_x and y == player_y):
                    color = GRAY if cell == 1 else DARK_GRAY
                    if cell == 0:
                        color = (30, 30, 30)
                    pygame.draw.rect(self.screen, color,
                                     (map_x + x * mini_size, map_y + y * mini_size, mini_size, mini_size))

        # 绘制玩家
        pygame.draw.rect(self.screen, BLUE,
                         (map_x + player_x * mini_size, map_y + player_y * mini_size, mini_size, mini_size))

        # 标签
        label = self.font_small.render("Map", True, WHITE)
        self.screen.blit(label, (map_x, map_y - 20))

    def draw_status(self, state, difficulty, fps=None):
        """绘制状态信息"""
        if state == STATE_MENU:
            self._draw_menu()
        elif state == STATE_GAME_OVER:
            self._draw_game_over()
        elif state == STATE_VICTORY:
            self._draw_victory()
        elif state == STATE_PAUSE:
            self._draw_pause()

        # 难度显示
        diff_text = self.font_small.render(f"Difficulty: {difficulty.capitalize()}", True, WHITE)
        self.screen.blit(diff_text, (10, SCREEN_HEIGHT - 30))

        # FPS显示
        if fps:
            fps_text = self.font_small.render(f"FPS: {int(fps)}", True, LIGHT_GRAY)
            self.screen.blit(fps_text, (SCREEN_WIDTH - 80, SCREEN_HEIGHT - 30))

    def _draw_menu(self):
        """绘制主菜单"""
        # 标题
        title = self.font_large.render("DUNGEON LIGHT", True, YELLOW)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        # 菜单选项
        options = [
            ("Easy", 280),
            ("Normal", 350),
            ("Hard", 420),
            ("Quit", 520)
        ]

        for text, y in options:
            option = self.font_medium.render(text, True, WHITE)
            option_rect = option.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(option, option_rect)

        # 提示
        tip = self.font_small.render("Use arrow keys to select, SPACE to confirm", True, LIGHT_GRAY)
        tip_rect = tip.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        self.screen.blit(tip, tip_rect)

    def _draw_game_over(self):
        """绘制游戏结束画面"""
        # 半透明遮罩
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        # 文字
        game_over = self.font_large.render("GAME OVER", True, RED)
        game_over_rect = game_over.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_over, game_over_rect)

        restart = self.font_medium.render("Press R to restart or ESC to quit", True, WHITE)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart, restart_rect)

    def _draw_victory(self):
        """绘制胜利画面"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        victory = self.font_large.render("VICTORY!", True, GREEN)
        victory_rect = victory.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(victory, victory_rect)

        restart = self.font_medium.render("Press R to play again or ESC to quit", True, WHITE)
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart, restart_rect)

    def _draw_pause(self):
        """绘制暂停画面"""
        pause = self.font_large.render("PAUSED", True, WHITE)
        pause_rect = pause.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(pause, pause_rect)

        tip = self.font_small.render("Press P to resume", True, LIGHT_GRAY)
        tip_rect = tip.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(tip, tip_rect)

    def draw_damage_indicator(self, x, y, damage):
        """绘制伤害数字"""
        damage_text = self.font_medium.render(str(damage), True, RED)
        self.screen.blit(damage_text, (x, y))

    def draw_crystal_collect(self, x, y):
        """绘制水晶收集提示"""
        text = self.font_small.render("+1 Crystal", True, YELLOW)
        self.screen.blit(text, (x, y))