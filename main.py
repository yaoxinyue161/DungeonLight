# main.py
import pygame
import sys
import random
from settings import *
from map_generator import DungeonGenerator
from lighting import ShadowCaster, TorchLight
from player import Player
from enemy import Enemy
from ui import UI


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Dungeon Light")
        self.clock = pygame.time.Clock()

        self.ui = UI(self.screen)
        self.state = STATE_MENU
        self.difficulty = 'normal'
        self.selected_option = 0
        self.fps = 0

        # 游戏对象（稍后初始化）
        self.grid = None
        self.rooms = None
        self.player = None
        self.enemies = []
        self.crystals = []
        self.shadow_caster = ShadowCaster(MAP_WIDTH, MAP_HEIGHT)
        self.torch = TorchLight()
        self.visible = None

        # 游戏计时
        self.game_time = 0

        # 特效
        self.damage_effects = []
        self.crystal_effects = []

    def run(self):
        """主游戏循环"""
        running = True
        while running:
            dt = self.clock.tick(FPS) / 1000.0
            self.fps = self.clock.get_fps()

            # 更新火把闪烁
            self.torch.update(dt)

            # 事件处理
            running = self.handle_events()

            # 更新游戏逻辑
            if self.state == STATE_PLAYING:
                self.update(dt)

            # 渲染
            self.render()

            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def handle_events(self):
        """处理输入事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSE
                    elif self.state == STATE_PAUSE:
                        self.state = STATE_PLAYING
                    elif self.state in [STATE_MENU, STATE_GAME_OVER, STATE_VICTORY]:
                        return False

                elif event.key == pygame.K_r:
                    if self.state in [STATE_GAME_OVER, STATE_VICTORY]:
                        self.new_game()

                elif event.key == pygame.K_p:
                    if self.state == STATE_PLAYING:
                        self.state = STATE_PAUSE
                    elif self.state == STATE_PAUSE:
                        self.state = STATE_PLAYING

                # 菜单控制
                if self.state == STATE_MENU:
                    if event.key == pygame.K_UP:
                        self.selected_option = max(0, self.selected_option - 1)
                    elif event.key == pygame.K_DOWN:
                        self.selected_option = min(3, self.selected_option + 1)
                    elif event.key == pygame.K_SPACE:
                        if self.selected_option == 0:
                            self.difficulty = 'easy'
                            self.new_game()
                        elif self.selected_option == 1:
                            self.difficulty = 'normal'
                            self.new_game()
                        elif self.selected_option == 2:
                            self.difficulty = 'hard'
                            self.new_game()
                        elif self.selected_option == 3:
                            return False

        # 游戏中的移动和攻击
        if self.state == STATE_PLAYING and self.player and self.player.is_alive():
            keys = pygame.key.get_pressed()
            dx = dy = 0
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                dx = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                dx = 1
            if keys[pygame.K_UP] or keys[pygame.K_w]:
                dy = -1
            if keys[pygame.K_DOWN] or keys[pygame.K_s]:
                dy = 1

            if dx != 0 or dy != 0:
                self.player.move(dx, dy, self.grid)

            # 攻击
            mouse_buttons = pygame.mouse.get_pressed()
            if mouse_buttons[0]:
                hit_enemies = self.player.attack(self.enemies)
                for enemy in hit_enemies:
                    self.damage_effects.append({
                        'pos': (enemy.x * CELL_SIZE, enemy.y * CELL_SIZE),
                        'damage': self.player.attack_damage,
                        'timer': 0.5
                    })

        return True

    def new_game(self):
        """开始新游戏"""
        # 生成地图
        generator = DungeonGenerator(MAP_WIDTH, MAP_HEIGHT)
        self.grid, self.rooms = generator.generate(iterations=8, min_room=4, max_room=8)

        # 寻找起始房间（第一个房间）
        if self.rooms:
            start_room = self.rooms[0]
            start_x = start_room[0] + start_room[2] // 2
            start_y = start_room[1] + start_room[3] // 2

            # 创建玩家
            self.player = Player(start_x, start_y, self.difficulty)

            # 创建敌人
            self.enemies = []
            enemy_count = DIFFICULTY[self.difficulty]['enemy_count']
            available_rooms = self.rooms[1:] if len(self.rooms) > 1 else self.rooms
            for i in range(min(enemy_count, len(available_rooms))):
                room = available_rooms[i % len(available_rooms)]
                ex = room[0] + random.randint(1, room[2] - 2)
                ey = room[1] + random.randint(1, room[3] - 2)
                self.enemies.append(Enemy(ex, ey, self.difficulty))

            # 创建水晶
            self.crystals = []
            crystal_count = enemy_count * 2
            for _ in range(min(crystal_count, len(self.rooms) * 2)):
                room = random.choice(self.rooms)
                cx = room[0] + random.randint(1, room[2] - 2)
                cy = room[1] + random.randint(1, room[3] - 2)
                self.crystals.append((cx, cy))

        # 重置状态
        self.state = STATE_PLAYING
        self.game_time = 0
        self.damage_effects = []
        self.crystal_effects = []

    def update(self, dt):
        """更新游戏逻辑"""
        if not self.player or not self.player.is_alive():
            self.state = STATE_GAME_OVER
            return

        # 更新玩家
        self.player.update(dt)

        # 计算可见区域
        view_radius = 8
        self.visible = self.shadow_caster.compute_visibility(
            self.grid, self.player.x, self.player.y, view_radius
        )

        # 更新敌人
        for enemy in self.enemies[:]:
            enemy.update(dt, self.player.x, self.player.y, self.grid, self.visible)
            enemy.attack_player(self.player)
            if not enemy.is_alive():
                self.enemies.remove(enemy)

        # 收集水晶
        for crystal in self.crystals[:]:
            cx, cy = crystal
            if abs(self.player.x - cx) + abs(self.player.y - cy) <= 1:
                self.crystals.remove(crystal)
                self.player.add_crystal()
                self.crystal_effects.append({
                    'pos': (cx * CELL_SIZE, cy * CELL_SIZE),
                    'timer': 0.5
                })

        # 更新特效
        for effect in self.damage_effects[:]:
            effect['timer'] -= dt
            if effect['timer'] <= 0:
                self.damage_effects.remove(effect)

        for effect in self.crystal_effects[:]:
            effect['timer'] -= dt
            if effect['timer'] <= 0:
                self.crystal_effects.remove(effect)

        # 胜利条件（收集所有水晶或击败所有敌人）
        if len(self.crystals) == 0 or len(self.enemies) == 0:
            self.state = STATE_VICTORY

        # 游戏时间
        self.game_time += dt

    def render(self):
        """渲染游戏画面"""
        # 清屏
        self.screen.fill(BLACK)

        if self.state == STATE_MENU:
            self.ui.draw_status(self.state, self.difficulty)
            return

        if self.grid is None:
            return

        # 绘制地图
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                # 检查是否可见
                if self.visible and self.visible[y][x]:
                    if cell == 0:
                        color = DARK_GRAY
                    else:
                        color = BROWN
                    pygame.draw.rect(self.screen, color,
                                     (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))

                    # 添加墙壁纹理
                    if cell == 1:
                        pygame.draw.rect(self.screen, DARK_BROWN,
                                         (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

        # 绘制水晶
        for cx, cy in self.crystals:
            if self.visible and self.visible[cy][cx]:
                center_x = cx * CELL_SIZE + CELL_SIZE // 2
                center_y = cy * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(self.screen, YELLOW, (center_x, center_y), CELL_SIZE // 3)
                pygame.draw.circle(self.screen, ORANGE, (center_x, center_y), CELL_SIZE // 4)

        # 绘制敌人
        for enemy in self.enemies:
            if self.visible and self.visible[enemy.y][enemy.x]:
                # 根据状态改变颜色
                color = RED if enemy.state == 'chase' else PURPLE
                center_x = enemy.x * CELL_SIZE + CELL_SIZE // 2
                center_y = enemy.y * CELL_SIZE + CELL_SIZE // 2
                pygame.draw.circle(self.screen, color, (center_x, center_y), CELL_SIZE // 2 - 2)
                pygame.draw.circle(self.screen, BLACK, (center_x - 4, center_y - 4), 4)
                pygame.draw.circle(self.screen, BLACK, (center_x + 4, center_y - 4), 4)
                # 血条
                health_percent = enemy.health / enemy.max_health
                bar_width = CELL_SIZE - 4
                bar_height = 4
                pygame.draw.rect(self.screen, DARK_RED,
                                 (enemy.x * CELL_SIZE + 2, enemy.y * CELL_SIZE - 6, bar_width, bar_height))
                pygame.draw.rect(self.screen, RED,
                                 (enemy.x * CELL_SIZE + 2, enemy.y * CELL_SIZE - 6, bar_width * health_percent,
                                  bar_height))

        # 绘制玩家
        if self.player:
            center_x = self.player.x * CELL_SIZE + CELL_SIZE // 2
            center_y = self.player.y * CELL_SIZE + CELL_SIZE // 2

            # 火把光照效果
            light_intensity = self.torch.get_light_intensity(0, 5)
            light_color = (255, 200, 100, int(50 * light_intensity))

            # 绘制玩家
            pygame.draw.circle(self.screen, BLUE, (center_x, center_y), CELL_SIZE // 2)
            pygame.draw.circle(self.screen, WHITE, (center_x - 4, center_y - 4), 4)
            pygame.draw.circle(self.screen, WHITE, (center_x + 4, center_y - 4), 4)

            # 绘制火把效果
            for i in range(1, 4):
                alpha = int(30 * self.torch.get_light_intensity(i, 5))
                if alpha > 0:
                    s = pygame.Surface((CELL_SIZE * 2, CELL_SIZE * 2), pygame.SRCALPHA)
                    pygame.draw.circle(s, (255, 200, 100, alpha), (CELL_SIZE, CELL_SIZE), CELL_SIZE * i)
                    self.screen.blit(s, (center_x - CELL_SIZE, center_y - CELL_SIZE))

            # 绘制血条
            health_percent = self.player.health / self.player.max_health
            bar_width = CELL_SIZE * 2
            bar_height = 8
            bar_x = center_x - bar_width // 2
            bar_y = center_y - CELL_SIZE // 2 - 10
            pygame.draw.rect(self.screen, DARK_RED, (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(self.screen, RED, (bar_x, bar_y, bar_width * health_percent, bar_height))
            pygame.draw.rect(self.screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 1)

        # 雾暗效果（未探索区域）
        if self.visible:
            for y in range(MAP_HEIGHT):
                for x in range(MAP_WIDTH):
                    if not self.visible[y][x]:
                        alpha = 180
                        s = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                        s.fill((0, 0, 0, alpha))
                        self.screen.blit(s, (x * CELL_SIZE, y * CELL_SIZE))

        # 绘制UI
        if self.player:
            self.ui.draw_health_bar(10, 10, self.player.health, self.player.max_health)
            self.ui.draw_crystals(self.player.crystals)
            if self.visible:
                self.ui.draw_minimap(self.grid, self.player.x, self.player.y, self.rooms, self.visible)

        # 绘制伤害特效
        for effect in self.damage_effects:
            self.ui.draw_damage_indicator(effect['pos'][0] + CELL_SIZE // 2,
                                          effect['pos'][1] + CELL_SIZE // 2,
                                          effect['damage'])

        # 绘制水晶收集特效
        for effect in self.crystal_effects:
            self.ui.draw_crystal_collect(effect['pos'][0] + CELL_SIZE // 2,
                                         effect['pos'][1] + CELL_SIZE // 2)

        # 绘制状态UI
        self.ui.draw_status(self.state, self.difficulty, self.fps)


if __name__ == "__main__":
    game = Game()
    game.run()