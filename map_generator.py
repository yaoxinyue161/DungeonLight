# map_generator.py
import random
import pygame
from settings import *


class BSPNode:
    """BSP树节点"""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.left = None
        self.right = None
        self.room = None
        self.hallway = None

    def split(self, min_size=6, split_ratio=0.35):
        """分割节点"""
        if self.left or self.right:
            return False

        # 决定分割方向（垂直或水平）
        split_vertical = random.choice([True, False])

        # 检查是否适合分割
        if split_vertical:
            if self.width < min_size * 2:
                split_vertical = False
        else:
            if self.height < min_size * 2:
                split_vertical = True

        # 随机选择分割位置（避开边缘，使用35%限制）
        if split_vertical:
            max_split = self.width - min_size
            if max_split <= min_size:
                return False
            split_pos = random.randint(
                int(self.width * split_ratio),
                int(self.width * (1 - split_ratio))
            )
            self.left = BSPNode(self.x, self.y, split_pos, self.height)
            self.right = BSPNode(self.x + split_pos, self.y, self.width - split_pos, self.height)
        else:
            max_split = self.height - min_size
            if max_split <= min_size:
                return False
            split_pos = random.randint(
                int(self.height * split_ratio),
                int(self.height * (1 - split_ratio))
            )
            self.left = BSPNode(self.x, self.y, self.width, split_pos)
            self.right = BSPNode(self.x, self.y + split_pos, self.width, self.height - split_pos)

        return True

    def create_rooms(self, min_room_size=3, max_room_size=8):
        """在叶子节点创建房间"""
        if self.left or self.right:
            if self.left:
                self.left.create_rooms(min_room_size, max_room_size)
            if self.right:
                self.right.create_rooms(min_room_size, max_room_size)
        else:
            # 在叶子节点创建房间
            room_width = random.randint(min_room_size, min(max_room_size, self.width - 2))
            room_height = random.randint(min_room_size, min(max_room_size, self.height - 2))
            room_x = self.x + random.randint(1, self.width - room_width - 1)
            room_y = self.y + random.randint(1, self.height - room_height - 1)
            self.room = (room_x, room_y, room_width, room_height)

    def connect_rooms(self):
        """连接房间（创建走廊）"""
        if self.left and self.right:
            # 获取左右子树中的房间
            left_room = self._get_room(self.left)
            right_room = self._get_room(self.right)

            if left_room and right_room:
                # 计算连接点
                lx = left_room[0] + left_room[2] // 2
                ly = left_room[1] + left_room[3] // 2
                rx = right_room[0] + right_room[2] // 2
                ry = right_room[1] + right_room[3] // 2

                # 随机决定先水平还是先垂直
                if random.choice([True, False]):
                    self.hallway = (lx, ly, rx, ly, rx, ry)  # 水平然后垂直
                else:
                    self.hallway = (lx, ly, lx, ry, rx, ry)  # 垂直然后水平

            self.left.connect_rooms()
            self.right.connect_rooms()

    def _get_room(self, node):
        """获取节点下的房间"""
        if node.room:
            return node.room
        elif node.left:
            return self._get_room(node.left)
        elif node.right:
            return self._get_room(node.right)
        return None


class DungeonGenerator:
    """地牢生成器"""

    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[1 for _ in range(width)] for _ in range(height)]  # 1=墙, 0=路
        self.rooms = []

    def generate(self, iterations=6, min_room=4, max_room=8):
        """生成地牢"""
        # 创建BSP树
        root = BSPNode(1, 1, self.width - 2, self.height - 2)

        # 分割
        leaves = [root]
        for _ in range(iterations):
            new_leaves = []
            for leaf in leaves:
                if leaf.split():
                    new_leaves.append(leaf.left)
                    new_leaves.append(leaf.right)
                else:
                    new_leaves.append(leaf)
            leaves = new_leaves

        # 创建房间
        root.create_rooms(min_room, max_room)

        # 连接房间
        root.connect_rooms()

        # 将房间和走廊绘制到网格
        self._draw_rooms(root)
        self._draw_hallways(root)

        # 找出所有房间
        self._collect_rooms(root)

        return self.grid, self.rooms

    def _draw_rooms(self, node):
        """绘制房间"""
        if node.room:
            x, y, w, h = node.room
            for i in range(y, y + h):
                for j in range(x, x + w):
                    if 0 <= i < self.height and 0 <= j < self.width:
                        self.grid[i][j] = 0
        if node.left:
            self._draw_rooms(node.left)
        if node.right:
            self._draw_rooms(node.right)

    def _draw_hallways(self, node):
        """绘制走廊"""
        if node.hallway:
            # 绘制水平段
            x1, y1, x2, y2, x3, y3 = node.hallway
            # 第一段
            for x in range(min(x1, x2), max(x1, x2) + 1):
                if 0 <= y1 < self.height and 0 <= x < self.width:
                    self.grid[y1][x] = 0
            # 第二段
            for y in range(min(y2, y3), max(y2, y3) + 1):
                if 0 <= y < self.height and 0 <= x2 < self.width:
                    self.grid[y][x2] = 0

        if node.left:
            self._draw_hallways(node.left)
        if node.right:
            self._draw_hallways(node.right)

    def _collect_rooms(self, node):
        """收集所有房间"""
        if node.room:
            self.rooms.append(node.room)
        if node.left:
            self._collect_rooms(node.left)
        if node.right:
            self._collect_rooms(node.right)