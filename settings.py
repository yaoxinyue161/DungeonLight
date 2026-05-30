# settings.py
import pygame

# 窗口设置
SCREEN_WIDTH = 1024
SCREEN_HEIGHT = 768
FPS = 60

# 网格设置
CELL_SIZE = 32
MAP_WIDTH = 30
MAP_HEIGHT = 20

# 颜色定义
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN = (0, 200, 0)
BLUE = (0, 100, 255)
YELLOW = (255, 200, 0)
ORANGE = (255, 100, 0)
DARK_GRAY = (40, 40, 40)
GRAY = (100, 100, 100)
LIGHT_GRAY = (180, 180, 180)
BROWN = (101, 67, 33)
DARK_BROWN = (60, 40, 20)
PURPLE = (128, 0, 128)
LIGHT_YELLOW = (255, 255, 150)
DARK_RED = (100, 0, 0)

# 游戏状态
STATE_MENU = 0
STATE_PLAYING = 1
STATE_GAME_OVER = 2
STATE_PAUSE = 3
STATE_VICTORY = 4

# 难度设置
DIFFICULTY = {
    'easy': {'enemy_speed': 1.5, 'enemy_count': 3, 'crystal_spawn': 0.4, 'player_health': 100},
    'normal': {'enemy_speed': 2.5, 'enemy_count': 5, 'crystal_spawn': 0.3, 'player_health': 80},
    'hard': {'enemy_speed': 3.5, 'enemy_count': 8, 'crystal_spawn': 0.2, 'player_health': 60}
}