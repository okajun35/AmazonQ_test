import pyxel
import random

class InvadersGame:
    def __init__(self):
        # ゲームの初期設定
        self.WIDTH = 160
        self.HEIGHT = 120
        
        # プレイヤーの設定
        self.player_x = self.WIDTH // 2
        self.player_y = self.HEIGHT - 20
        self.player_width = 8
        self.player_height = 8
        self.player_speed = 2
        
        # 弾の設定
        self.bullets = []
        self.bullet_width = 2
        self.bullet_height = 4
        self.bullet_speed = 4
        self.bullet_cooldown = 0
        
        # 敵の設定
        self.enemies = []
        self.enemy_width = 8
        self.enemy_height = 8
        self.enemy_speed = 1
        self.enemy_move_dir = 1  # 1: 右, -1: 左
        self.enemy_shoot_chance = 0.01
        self.enemy_bullets = []
        
        # ゲームの状態
        self.score = 0
        self.game_over = False
        
        # 敵の初期配置
        self.init_enemies()
        
        # Pyxelの初期化
        pyxel.init(self.WIDTH, self.HEIGHT, title="Invaders Game")
        pyxel.run(self.update, self.draw)
    
    def init_enemies(self):
        # 敵を5行6列で配置
        for y in range(5):
            for x in range(6):
                self.enemies.append({
                    'x': 20 + x * 20,
                    'y': 10 + y * 10,
                    'alive': True
                })
    
    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.__init__()
            return
        
        # プレイヤーの移動
        if pyxel.btn(pyxel.KEY_LEFT) and self.player_x > 0:
            self.player_x -= self.player_speed
        if pyxel.btn(pyxel.KEY_RIGHT) and self.player_x < self.WIDTH - self.player_width:
            self.player_x += self.player_speed
        
        # 弾の発射
        if pyxel.btnp(pyxel.KEY_SPACE) and self.bullet_cooldown <= 0:
            self.bullets.append({
                'x': self.player_x + self.player_width // 2 - self.bullet_width // 2,
                'y': self.player_y
            })
            self.bullet_cooldown = 10
        
        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1
        
        # 弾の移動
        for bullet in self.bullets[:]:
            bullet['y'] -= self.bullet_speed
            if bullet['y'] < 0:
                self.bullets.remove(bullet)
        
        # 敵の移動
        move_down = False
        for enemy in self.enemies:
            if not enemy['alive']:
                continue
            
            if (enemy['x'] >= self.WIDTH - self.enemy_width and self.enemy_move_dir > 0) or \
               (enemy['x'] <= 0 and self.enemy_move_dir < 0):
                move_down = True
                break
        
        if move_down:
            self.enemy_move_dir *= -1
            for enemy in self.enemies:
                if enemy['alive']:
                    enemy['y'] += 5
        else:
            for enemy in self.enemies:
                if enemy['alive']:
                    enemy['x'] += self.enemy_move_dir
        
        # 敵の弾発射
        for enemy in self.enemies:
            if enemy['alive'] and random.random() < self.enemy_shoot_chance:
                self.enemy_bullets.append({
                    'x': enemy['x'] + self.enemy_width // 2,
                    'y': enemy['y'] + self.enemy_height
                })
        
        # 敵の弾の移動
        for bullet in self.enemy_bullets[:]:
            bullet['y'] += 2
            if bullet['y'] > self.HEIGHT:
                self.enemy_bullets.remove(bullet)
        
        # 衝突判定（プレイヤーの弾と敵）
        for bullet in self.bullets[:]:
            for enemy in self.enemies:
                if enemy['alive'] and \
                   bullet['x'] < enemy['x'] + self.enemy_width and \
                   bullet['x'] + self.bullet_width > enemy['x'] and \
                   bullet['y'] < enemy['y'] + self.enemy_height and \
                   bullet['y'] + self.bullet_height > enemy['y']:
                    enemy['alive'] = False
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    self.score += 10
                    break
        
        # 衝突判定（敵の弾とプレイヤー）
        for bullet in self.enemy_bullets[:]:
            if bullet['x'] < self.player_x + self.player_width and \
               bullet['x'] + 2 > self.player_x and \
               bullet['y'] < self.player_y + self.player_height and \
               bullet['y'] + 4 > self.player_y:
                self.game_over = True
                break
        
        # 敵がプレイヤーに到達したらゲームオーバー
        for enemy in self.enemies:
            if enemy['alive'] and enemy['y'] + self.enemy_height >= self.player_y:
                self.game_over = True
                break
        
        # 敵が全滅したら再配置
        if all(not enemy['alive'] for enemy in self.enemies):
            self.enemies = []
            self.init_enemies()
            self.enemy_speed += 0.5
            self.enemy_shoot_chance += 0.005
    
    def draw(self):
        pyxel.cls(0)
        
        # プレイヤーの描画
        pyxel.rect(self.player_x, self.player_y, self.player_width, self.player_height, 11)
        
        # 弾の描画
        for bullet in self.bullets:
            pyxel.rect(bullet['x'], bullet['y'], self.bullet_width, self.bullet_height, 10)
        
        # 敵の弾の描画
        for bullet in self.enemy_bullets:
            pyxel.rect(bullet['x'], bullet['y'], 2, 4, 8)
        
        # 敵の描画
        for enemy in self.enemies:
            if enemy['alive']:
                pyxel.rect(enemy['x'], enemy['y'], self.enemy_width, self.enemy_height, 8)
        
        # スコアの表示
        pyxel.text(5, 5, f"SCORE: {self.score}", 7)
        
        # ゲームオーバー表示
        if self.game_over:
            pyxel.text(self.WIDTH // 2 - 30, self.HEIGHT // 2, "GAME OVER", 8)
            pyxel.text(self.WIDTH // 2 - 40, self.HEIGHT // 2 + 10, "PRESS R TO RESTART", 8)

if __name__ == "__main__":
    InvadersGame()
