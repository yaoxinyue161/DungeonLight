# enemy.py
import pygame
import math
from settings import *


class Enemy:
    def __init__(self, x, y, difficulty='normal'):
        self.x = x
        self.y = y
        self.speed = DIFFICULTY[difficulty]['enemy_speed']
        self.health = 30
        self.max_health = 30
        self.damage = 15
        self.state = 'patrol'  # patrol, chase
        self.patrol_target = None
        self.path = []
        self.attack_cooldown = 0

    def update(self, dt, player_x, player_y, grid, visible):
        """更新敌人状态"""
        # 更新攻击冷却
        if self.attack_cooldown > 0:
            self.attack_cooldown -= dt

        # 检查是否发现玩家
        if self._can_see_player(player_x, player_y, visible):
            self.state = 'chase'
            self._chase(player_x, player_y, grid)
        else:
            self.state = 'patrol'
            self._patrol(dt, grid)

        # 移动
        self._move(dt, grid)

    def _can_see_player(self, player_x, player_y, visible):
        """检查是否能看到玩家"""
        if 0 <= player_y < len(visible) and 0 <= player_x < len(visible[0]):
            return visible[player_y][player_x]
        return False

    def _chase(self, target_x, target_y, grid):
        """追逐玩家（A*寻路）"""
        # 简化的A*寻路
        path = self._a_star_search(self.x, self.y, target_x, target_y, grid)
        if path:
            self.path = path
        else:
            # 如果找不到路径，直接直线移动
            dx = 1 if target_x > self.x else -1 if target_x < self.x else 0
            dy = 1 if target_y > self.y else -1 if target_y < self.y else 0

            if dx != 0 and 0 <= self.x + dx < len(grid[0]) and grid[self.y][self.x + dx] == 0:
                self.x += dx
            elif dy != 0 and 0 <= self.y + dy < len(grid) and grid[self.y + dy][self.x] == 0:
                self.y += dy

    def _a_star_search(self, start_x, start_y, goal_x, goal_y, grid):
        """A*寻路算法"""
        # 简化的A*实现
        open_set = [(start_x, start_y)]
        came_from = {}
        g_score = {(start_x, start_y): 0}
        f_score = {(start_x, start_y): self._heuristic(start_x, start_y, goal_x, goal_y)}

        while open_set:
            # 找到f_score最小的节点
            current = min(open_set, key=lambda pos: f_score.get(pos, float('inf')))

            if current[0] == goal_x and current[1] == goal_y:
                # 重建路径
                path = []
                while current in came_from:
                    path.append(current)
                    current = came_from[current]
                return path[::-1]

            open_set.remove(current)

            # 检查邻居
            for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                nx, ny = current[0] + dx, current[1] + dy
                if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid):
                    if grid[ny][nx] == 1:  # 墙壁
                        continue

                    tentative_g = g_score[current] + 1
                    if tentative_g < g_score.get((nx, ny), float('inf')):
                        came_from[(nx, ny)] = current
                        g_score[(nx, ny)] = tentative_g
                        f_score[(nx, ny)] = tentative_g + self._heuristic(nx, ny, goal_x, goal_y)
                        if (nx, ny) not in open_set:
                            open_set.append((nx, ny))
        return None

    def _heuristic(self, x1, y1, x2, y2):
        """曼哈顿距离启发式"""
        return abs(x1 - x2) + abs(y1 - y2)

    def _patrol(self, dt, grid):
        """巡逻模式"""
        if self.path:
            self._move(dt, grid)
        else:
            # 随机移动
            import random
            if random.random() < 0.02:  # 2%概率改变方向
                dx = random.choice([-1, 0, 1])
                dy = random.choice([-1, 0, 1])
                if abs(dx) + abs(dy) == 1:  # 只允许四方向
                    new_x = self.x + dx
                    new_y = self.y + dy
                    if 0 <= new_x < len(grid[0]) and 0 <= new_y < len(grid):
                        if grid[new_y][new_x] == 0:
                            self.x = new_x
                            self.y = new_y

    def _move(self, dt, grid):
        """沿路径移动"""
        if self.path:
            target = self.path[0]
            dx = 1 if target[0] > self.x else -1 if target[0] < self.x else 0
            dy = 1 if target[1] > self.y else -1 if target[1] < self.y else 0

            new_x = self.x + dx
            new_y = self.y + dy

            if 0 <= new_x < len(grid[0]) and 0 <= new_y < len(grid):
                if grid[new_y][new_x] == 0:
                    self.x = new_x
                    self.y = new_y
                    if self.x == target[0] and self.y == target[1]:
                        self.path.pop(0)

    def take_damage(self, damage):
        """受到伤害"""
        self.health -= damage

    def attack_player(self, player):
        """攻击玩家"""
        if self.attack_cooldown <= 0:
            if abs(self.x - player.x) + abs(self.y - player.y) <= 1:
                player.take_damage(self.damage)
                self.attack_cooldown = 0.5
                return True
        return False

    def is_alive(self):
        return self.health > 0

    def get_rect(self):
        """获取碰撞矩形"""
        return pygame.Rect(self.x * CELL_SIZE, self.y * CELL_SIZE, CELL_SIZE, CELL_SIZE)