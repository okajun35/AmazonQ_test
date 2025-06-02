import pyxel
import random
from abc import ABC, abstractmethod

class GameObject(ABC):
    """ゲームオブジェクトの基底クラス"""
    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.is_active = True
    
    @abstractmethod
    def update(self, game):
        """オブジェクトの状態を更新"""
        pass
    
    def draw(self):
        """オブジェクトを描画"""
        if self.is_active:
            pyxel.rect(self.x, self.y, self.width, self.height, self.color)
    
    def collides_with(self, other):
        """他のオブジェクトとの衝突判定"""
        if not self.is_active or not other.is_active:
            return False
        
        return (self.x < other.x + other.width and
                self.x + self.width > other.x and
                self.y < other.y + other.height and
                self.y + self.height > other.y)


class Player(GameObject):
    """プレイヤークラス"""
    def __init__(self, x, y, game_width):
        super().__init__(x, y, 8, 8, 11)
        self.speed = 3  # 移動速度を2から3に上昇
        self.game_width = game_width
        self.bullet_cooldown = 0
        self.lives = 5  # プレイヤーのライフ数
        self.invincible = False  # 無敵状態かどうか
        self.invincible_timer = 0  # 無敵時間のタイマー
        self.blink_timer = 0  # 点滅表示用タイマー
    
    def update(self, game):
        # 左右移動
        if pyxel.btn(pyxel.KEY_LEFT) and self.x > 0:
            self.x -= self.speed
        if pyxel.btn(pyxel.KEY_RIGHT) and self.x < self.game_width - self.width:
            self.x += self.speed
        
        # 弾の発射はゲームクラスで処理
        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1
            
        # 無敵時間の処理
        if self.invincible:
            self.invincible_timer -= 1
            self.blink_timer = (self.blink_timer + 1) % 6  # 点滅用タイマー
            if self.invincible_timer <= 0:
                self.invincible = False
    
    def hit(self):
        """敵の弾に当たった時の処理"""
        if not self.invincible:
            self.lives -= 1
            if self.lives > 0:
                # まだライフが残っている場合は無敵状態に
                self.invincible = True
                self.invincible_timer = 60  # 60フレーム（約1秒）の無敵時間
                return False  # ゲームオーバーではない
            return True  # ライフが0になったらゲームオーバー
        return False
    
    def draw(self):
        """プレイヤーを描画（無敵時は点滅）"""
        if not self.invincible or self.blink_timer < 3:
            super().draw()


class Bullet(GameObject):
    """弾の基底クラス"""
    def __init__(self, x, y, width, height, color, speed):
        super().__init__(x, y, width, height, color)
        self.speed = speed


class PlayerBullet(Bullet):
    """プレイヤーの弾クラス"""
    def __init__(self, x, y):
        super().__init__(x, y, 2, 4, 10, 5)  # 速度を4から5に上昇
    
    def update(self, game):
        self.y -= self.speed
        if self.y < 0:
            self.is_active = False


class EnemyBullet(Bullet):
    """敵の弾クラス"""
    def __init__(self, x, y):
        super().__init__(x, y, 2, 4, 8, 1)  # 速度を2から1に減速
    
    def update(self, game):
        self.y += self.speed
        if self.y > game.HEIGHT:
            self.is_active = False


class Enemy(GameObject):
    """敵クラス"""
    def __init__(self, x, y):
        super().__init__(x, y, 8, 8, 8)
        self.shoot_chance = 0.005  # 発射確率を0.01から0.005に減少
    
    def update(self, game):
        # 移動は EnemyManager で一括管理
        pass
    
    def try_shoot(self, game):
        """一定確率で弾を発射"""
        if self.is_active and random.random() < self.shoot_chance:
            bullet_x = self.x + self.width // 2 - 1
            game.add_enemy_bullet(bullet_x, self.y + self.height)


class EnemyManager:
    """敵の集団を管理するクラス"""
    def __init__(self, game_width, game_height):
        self.game_width = game_width
        self.game_height = game_height
        self.enemies = []
        self.move_dir = 1  # 1: 右, -1: 左
        self.speed = 0.5  # 移動速度を1から0.5に減速
        self.shoot_chance = 0.005  # 発射確率を0.01から0.005に減少
    
    def create_enemies(self):
        """敵を配置"""
        self.enemies = []
        # 敵の初期位置をより上に配置（y座標を変更）
        for y in range(3):  # 行数を5から3に減らす
            for x in range(6):
                enemy = Enemy(20 + x * 20, 5 + y * 10)  # y座標を10から5に変更
                enemy.shoot_chance = self.shoot_chance
                self.enemies.append(enemy)
    
    def update(self, game):
        """敵の移動と弾の発射"""
        # 移動方向の判定
        move_down = False
        for enemy in self.enemies:
            if not enemy.is_active:
                continue
            
            if ((enemy.x >= self.game_width - enemy.width and self.move_dir > 0) or 
                (enemy.x <= 0 and self.move_dir < 0)):
                move_down = True
                break
        
        # 移動処理
        if move_down:
            self.move_dir *= -1
            for enemy in self.enemies:
                if enemy.is_active:
                    enemy.y += 3  # 下降幅を5から3に減少
        else:
            for enemy in self.enemies:
                if enemy.is_active:
                    enemy.x += self.move_dir * self.speed
        
        # 弾の発射
        for enemy in self.enemies:
            enemy.try_shoot(game)
        
        # 全滅判定
        if all(not enemy.is_active for enemy in self.enemies):
            self.speed += 0.2  # 難易度上昇を緩やかに（0.5から0.2に）
            self.shoot_chance += 0.002  # 難易度上昇を緩やかに（0.005から0.002に）
            self.create_enemies()
        
        # プレイヤーに到達判定
        for enemy in self.enemies:
            if enemy.is_active and enemy.y + enemy.height >= game.player.y:
                game.game_over = True
                break
    
    def draw(self):
        """敵の描画"""
        for enemy in self.enemies:
            enemy.draw()


class InvadersGame:
    """ゲームのメインクラス"""
    def __init__(self):
        # ゲームの初期設定
        self.WIDTH = 160
        self.HEIGHT = 120
        
        # Pyxelの初期化（最初の1回だけ）
        pyxel.init(self.WIDTH, self.HEIGHT, title="Invaders Game OOP")
        
        # ゲームの初期状態をセット
        self.reset_game()
        
        # ゲームループの開始
        pyxel.run(self.update, self.draw)
    
    def reset_game(self):
        """ゲームの状態をリセット"""
        self.score = 0
        self.game_over = False
        
        # ゲームオブジェクト
        self.player = Player(self.WIDTH // 2, self.HEIGHT - 20, self.WIDTH)
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemy_manager = EnemyManager(self.WIDTH, self.HEIGHT)
        self.enemy_manager.create_enemies()
    
    def add_player_bullet(self, x, y):
        """プレイヤーの弾を追加"""
        self.player_bullets.append(PlayerBullet(x, y))
    
    def add_enemy_bullet(self, x, y):
        """敵の弾を追加"""
        self.enemy_bullets.append(EnemyBullet(x, y))
    
    def update(self):
        """ゲームの状態更新"""
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_game()
            return
        
        # プレイヤーの更新
        self.player.update(self)
        
        # 敵の更新
        self.enemy_manager.update(self)
        
        # 弾の更新
        for bullet in self.player_bullets:
            bullet.update(self)
        
        for bullet in self.enemy_bullets:
            bullet.update(self)
        
        # 衝突判定（プレイヤーの弾と敵）
        for bullet in self.player_bullets[:]:
            if not bullet.is_active:
                continue
                
            for enemy in self.enemy_manager.enemies:
                if enemy.is_active and bullet.collides_with(enemy):
                    enemy.is_active = False
                    bullet.is_active = False
                    self.score += 10
                    break
        
        # 衝突判定（敵の弾とプレイヤー）
        for bullet in self.enemy_bullets[:]:
            if bullet.is_active and bullet.collides_with(self.player):
                bullet.is_active = False
                if self.player.hit():
                    self.game_over = True
                break
        
        # 敵がプレイヤーに到達したらゲームオーバー
        for enemy in self.enemy_manager.enemies:
            if enemy.is_active and enemy.y + enemy.height >= self.player.y:
                self.game_over = True
                break
        
        # 不要なオブジェクトの削除
        self.player_bullets = [b for b in self.player_bullets if b.is_active]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.is_active]
        
        # 連射機能の追加（SPACEキーを押し続けると一定間隔で発射）
        if pyxel.btn(pyxel.KEY_SPACE) and self.player.bullet_cooldown <= 0:
            bullet_x = self.player.x + self.player.width // 2 - 1
            self.add_player_bullet(bullet_x, self.player.y)
            self.player.bullet_cooldown = 8  # クールダウンを10から8に短縮
    
    def draw(self):
        """ゲームの描画"""
        pyxel.cls(0)
        
        # プレイヤーの描画
        self.player.draw()
        
        # 敵の描画
        self.enemy_manager.draw()
        
        # 弾の描画
        for bullet in self.player_bullets:
            bullet.draw()
        
        for bullet in self.enemy_bullets:
            bullet.draw()
        
        # スコアとライフの表示
        pyxel.text(5, 5, f"SCORE: {self.score}", 7)
        pyxel.text(self.WIDTH - 60, 5, f"LIVES: {self.player.lives}", 7)
        
        # ゲームオーバー表示
        if self.game_over:
            pyxel.text(self.WIDTH // 2 - 30, self.HEIGHT // 2, "GAME OVER", 8)
            pyxel.text(self.WIDTH // 2 - 40, self.HEIGHT // 2 + 10, "PRESS R TO RESTART", 8)


if __name__ == "__main__":
    InvadersGame()
