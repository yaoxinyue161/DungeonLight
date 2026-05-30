# lighting.py
import math
from settings import *


class ShadowCaster:
    """阴影投射光照系统"""

    def __init__(self, width, height):
        self.width = width
        self.height = height

    def compute_visibility(self, grid, player_x, player_y, view_radius=10):
        """计算可见区域"""
        visible = [[False for _ in range(self.width)] for _ in range(self.height)]

        # 玩家所在格总是可见
        visible[player_y][player_x] = True

        # 对八个八分圆分别计算
        for octant in range(8):
            self._cast_light(grid, visible, player_x, player_y, view_radius, 1, 1.0, 0.0, octant)

        return visible

    def _cast_light(self, grid, visible, cx, cy, radius, row, start_slope, end_slope, octant):
        """在单个八分圆中投射光线"""
        if start_slope >= end_slope:
            return

        radius_sq = radius * radius

        for r in range(row, radius + 1):
            dx = -r - 1
            dy = -r
            blocked = False

            while dx <= 0:
                dx += 1

                # 计算当前点的投影
                x, y = self._rotate(octant, cx, cy, dx, dy)

                if x < 0 or x >= self.width or y < 0 or y >= self.height:
                    continue

                # 计算左右斜率
                l_slope = (dx - 0.5) / (dy + 0.5)
                r_slope = (dx + 0.5) / (dy - 0.5)

                if start_slope < r_slope:
                    continue
                if end_slope > l_slope:
                    break

                # 检查距离
                dist_sq = dx * dx + dy * dy
                if dist_sq <= radius_sq:
                    visible[y][x] = True

                # 检查是否被阻挡
                if blocked:
                    if grid[y][x] == 1:  # 墙
                        blocked = False
                        start_slope = r_slope
                else:
                    if grid[y][x] == 1:  # 墙
                        blocked = True
                        self._cast_light(grid, visible, cx, cy, radius, r + 1, start_slope, l_slope, octant)
                        start_slope = r_slope

            if blocked:
                break

    def _rotate(self, octant, cx, cy, dx, dy):
        """将八分圆中的坐标转换回世界坐标"""
        if octant == 0:  # 右
            return cx + dx, cy - dy
        elif octant == 1:  # 右上
            return cx + dy, cy - dx
        elif octant == 2:  # 上
            return cx - dx, cy - dy
        elif octant == 3:  # 左上
            return cx - dy, cy - dx
        elif octant == 4:  # 左
            return cx - dx, cy + dy
        elif octant == 5:  # 左下
            return cx - dy, cy + dx
        elif octant == 6:  # 下
            return cx + dx, cy + dy
        else:  # 右下
            return cx + dy, cy + dx


class TorchLight:
    """火把光照效果"""

    def __init__(self, flicker_speed=0.1):
        self.flicker_speed = flicker_speed
        self.flicker_offset = 0
        self.time = 0

    def update(self, dt):
        """更新火把闪烁"""
        self.time += dt
        self.flicker_offset = math.sin(self.time * self.flicker_speed) * 0.2 + 0.8

    def get_light_intensity(self, distance, max_radius):
        """根据距离计算光照强度"""
        if distance > max_radius:
            return 0
        ratio = 1 - (distance / max_radius)
        return ratio * self.flicker_offset