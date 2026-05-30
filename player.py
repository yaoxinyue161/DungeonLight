# player.py
import pygame
from settings import *


class Player:
    def __init__(self, x, y, difficulty='normal'):
        self.x = x
        self.y = y
        self.difficulty = difficulty
        self.max_health = DIFFICULTY[difficulty]['player_health']
        self.health = self.max_health
        self.crystals = 0
        self.attack_cooldown = 0
        self.invincible_frames = 0
        self.attack_range = 2
        self.attack_damage = 25

    def update(self, dt):
        """更新玩家状态"""
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt
        if self.invincible_frames > 0:
            self.invincible_frames -= dt

    def move(self, dx, dy, grid):
        """移动玩家"""
        new_x = self.x + dx
        new_y = self.y + dy

        # 检查边界和墙壁碰撞
        if 0 <= new_x < len(grid[0]) and 0 <= new_y < len(grid):
            if grid[new_y][new_x] == 0:  # 只能走到路面上
                self.x = new_x
                self.y = new_y
                return True
        return False

    def attack(self, enemies):
        """攻击敌人"""
        if self.attack_cooldown > 0:
            return []

        hit_enemies = []
        for enemy in enemies:
            # 计算距离
            dist = abs(self.x - enemy.x) + abs(self.y - enemy.y)
            if dist <= self.attack_range:
                enemy.take_damage(self.attack_damage)
                hit_enemies.append(enemy)

        self.attack_cooldown = 0.5  # 0.5秒冷却
        return hit_enemies

    def take_damage(self, damage):
        """受到伤害"""
        if self.invincible_frames <= 0:
            self.health -= damage
            self.invincible_frames = 1.0  # 1秒无敌
            return True
        return False

    def heal(self, amount):
        """治疗"""
        self.health = min(self.max_health, self.health + amount)

    def add_crystal(self):
        """添加水晶"""
        self.crystals += 1

    def is_alive(self):
        return self.health > 0

    def get_rect(self):
        """获取碰撞矩形（用于绘制）"""
        return pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)