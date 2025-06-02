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
        self.speed = 3
        self.game_width = game_width
        self.bullet_cooldown = 0
        self.lives = 5
        self.invincible = False
        self.invincible_timer = 0
        self.blink_timer = 0
        
        # 必殺技関連
        self.special_charge = 0  # 必殺技のチャージ量
        self.special_max_charge = 100  # 必殺技の最大チャージ量
        self.special_charging = False  # チャージ中かどうか
        self.special_cooldown = 0  # 必殺技のクールダウン
        self.special_type = 0  # 0: 貫通弾, 1: バウンス弾
    
    def update(self, game):
        # 左右移動
        if pyxel.btn(pyxel.KEY_LEFT) and self.x > 0:
            self.x -= self.speed
        if pyxel.btn(pyxel.KEY_RIGHT) and self.x < self.game_width - self.width:
            self.x += self.speed
        
        # 弾の発射はゲームクラスで処理
        if self.bullet_cooldown > 0:
            self.bullet_cooldown -= 1
            
        # 必殺技のチャージと発射
        if pyxel.btn(pyxel.KEY_Z):  # Zキーでチャージ
            self.special_charging = True
            if self.special_charge < self.special_max_charge:
                self.special_charge += 1
        elif self.special_charging:  # Zキーを離したとき
            self.special_charging = False
            if self.special_charge >= self.special_max_charge and self.special_cooldown <= 0:
                # 必殺技発射
                game.fire_special_weapon(self.special_type)
                self.special_charge = 0
                self.special_cooldown = 180  # 3秒間のクールダウン
                # 必殺技タイプの切り替え
                self.special_type = (self.special_type + 1) % 2
        
        # 必殺技のクールダウン
        if self.special_cooldown > 0:
            self.special_cooldown -= 1
            
        # 無敵時間の処理
        if self.invincible:
            self.invincible_timer -= 1
            self.blink_timer = (self.blink_timer + 1) % 6
            if self.invincible_timer <= 0:
                self.invincible = False
    
    def hit(self):
        """敵の弾に当たった時の処理"""
        if not self.invincible:
            self.lives -= 1
            if self.lives > 0:
                self.invincible = True
                self.invincible_timer = 60
                return False
            return True
        return False
    
    def draw(self):
        """プレイヤーを描画（無敵時は点滅）"""
        if not self.invincible or self.blink_timer < 3:
            super().draw()
        
        # チャージゲージの描画（サイズを小さくして位置を調整）
        # プレイヤーの上部に表示して、下部の情報と重ならないようにする
        charge_width = int((self.special_charge / self.special_max_charge) * 16)
        pyxel.rect(self.x - 4, self.y - 4, 16, 2, 1)
        if charge_width > 0:
            pyxel.rect(self.x - 4, self.y - 4, charge_width, 2, 
                      10 if self.special_charge < self.special_max_charge else 11)


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


class SpecialBullet(Bullet):
    """必殺技の弾の基底クラス"""
    def __init__(self, x, y, width, height, color, speed):
        super().__init__(x, y, width, height, color, speed)
        self.penetrate = False  # 貫通するかどうか
        self.bounce = False  # 跳ね返るかどうか
        self.bounce_count = 0  # 跳ね返った回数
        self.max_bounce = 5  # 最大跳ね返り回数
        self.dx = 0  # X方向の移動量
        self.dy = 0  # Y方向の移動量


class PenetratingBullet(SpecialBullet):
    """貫通弾クラス"""
    def __init__(self, x, y):
        super().__init__(x, y, 4, 8, 9, 6)  # 大きめで速い弾
        self.penetrate = True
    
    def update(self, game):
        self.y -= self.speed
        if self.y < 0:
            self.is_active = False


class BouncingBullet(SpecialBullet):
    """バウンス弾クラス"""
    def __init__(self, x, y, direction):
        super().__init__(x, y, 4, 4, 12, 3)  # 速度を少し遅く
        self.bounce = True
        self.dx = direction  # 方向係数（絶対値が大きいほど水平方向の動きが大きい）
        self.dy = -1 if direction > 0 else -1  # 上向き
    
    def update(self, game):
        # 移動
        self.x += self.dx
        self.y += self.dy * self.speed
        
        # 左右の壁での跳ね返り
        if self.x <= 0 or self.x >= game.WIDTH - self.width:
            self.dx *= -1
            self.bounce_count += 1
        
        # 上下の壁での跳ね返り（上端も跳ね返るように変更）
        if self.y <= 0:
            self.dy *= -1  # 上端でも跳ね返る
            self.bounce_count += 1
        elif self.y >= game.HEIGHT - self.height:
            self.is_active = False  # 下端に到達したら消滅
        
        # 最大跳ね返り回数を超えたら消滅
        if self.bounce_count >= self.max_bounce:
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
        self.start_time = pyxel.frame_count  # ゲーム開始時間を記録
        
        # ゲームオブジェクト
        self.player = Player(self.WIDTH // 2, self.HEIGHT - 20, self.WIDTH)
        self.player_bullets = []
        self.enemy_bullets = []
        self.special_bullets = []  # 必殺技の弾リスト
        self.enemy_manager = EnemyManager(self.WIDTH, self.HEIGHT)
        self.enemy_manager.create_enemies()
    
    def add_player_bullet(self, x, y):
        """プレイヤーの弾を追加"""
        self.player_bullets.append(PlayerBullet(x, y))
    
    def add_enemy_bullet(self, x, y):
        """敵の弾を追加"""
        self.enemy_bullets.append(EnemyBullet(x, y))
    
    def fire_special_weapon(self, special_type):
        """必殺技を発射"""
        if special_type == 0:  # 貫通弾
            self.special_bullets.append(PenetratingBullet(
                self.player.x + self.player.width // 2 - 2,
                self.player.y
            ))
        else:  # バウンス弾（角度を調整して発射）
            # 左右に2発発射、より水平方向に近い角度で
            self.special_bullets.append(BouncingBullet(
                self.player.x + self.player.width // 2 - 2,
                self.player.y,
                -1.5  # より水平に近い角度（左方向）
            ))
            self.special_bullets.append(BouncingBullet(
                self.player.x + self.player.width // 2 - 2,
                self.player.y,
                1.5   # より水平に近い角度（右方向）
            ))
    
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
        
        for bullet in self.special_bullets:
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
        
        # 衝突判定（必殺技の弾と敵）
        for bullet in self.special_bullets[:]:
            if not bullet.is_active:
                continue
                
            for enemy in self.enemy_manager.enemies:
                if enemy.is_active and bullet.collides_with(enemy):
                    enemy.is_active = False
                    self.score += 20  # 必殺技は高得点
                    if not bullet.penetrate:  # 貫通弾でなければ消滅
                        bullet.is_active = False
                        break
        
        # 衝突判定（敵の弾とプレイヤー）
        for bullet in self.enemy_bullets[:]:
            if bullet.is_active and bullet.collides_with(self.player):
                bullet.is_active = False
                if self.player.hit():
                    self.game_over = True
                break
        
        # 衝突判定（必殺技の弾と敵の弾）
        for special in self.special_bullets[:]:
            if not special.is_active:
                continue
                
            for bullet in self.enemy_bullets[:]:
                if bullet.is_active and special.collides_with(bullet):
                    bullet.is_active = False
                    if not special.penetrate:  # 貫通弾でなければ消滅
                        special.is_active = False
                        break
        
        # 敵がプレイヤーに到達したらゲームオーバー
        for enemy in self.enemy_manager.enemies:
            if enemy.is_active and enemy.y + enemy.height >= self.player.y:
                self.game_over = True
                break
        
        # 不要なオブジェクトの削除
        self.player_bullets = [b for b in self.player_bullets if b.is_active]
        self.enemy_bullets = [b for b in self.enemy_bullets if b.is_active]
        self.special_bullets = [b for b in self.special_bullets if b.is_active]
        
        # 連射機能（SPACEキーを押し続けると一定間隔で発射）
        if pyxel.btn(pyxel.KEY_SPACE) and self.player.bullet_cooldown <= 0:
            bullet_x = self.player.x + self.player.width // 2 - 1
            self.add_player_bullet(bullet_x, self.player.y)
            self.player.bullet_cooldown = 8
    
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
        
        for bullet in self.special_bullets:
            bullet.draw()
        
        # プレイ時間の計算（秒単位）
        play_time = (pyxel.frame_count - self.start_time) // 30  # 30FPSとして計算
        minutes = play_time // 60
        seconds = play_time % 60
        
        # スコア、ライフ、プレイ時間の表示（位置を調整）
        pyxel.text(5, 5, f"SCORE: {self.score}", 7)
        pyxel.text(self.WIDTH - 40, 5, f"LIVES: {self.player.lives}", 7)
        pyxel.text(self.WIDTH // 2 - 30, 5, f"TIME: {minutes:02d}:{seconds:02d}", 7)
        
        # 必殺技の情報表示（位置を調整、文字を小さく）
        special_type_name = "PENETRATE" if self.player.special_type == 0 else "BOUNCE"
        pyxel.text(5, self.HEIGHT - 6, f"SP:{special_type_name}", 7)
        
        # 必殺技のクールダウン表示（位置を調整）
        if self.player.special_cooldown > 0:
            cooldown_percent = self.player.special_cooldown / 180
            pyxel.rect(70, self.HEIGHT - 6, 40, 2, 1)
            pyxel.rect(70, self.HEIGHT - 6, int(40 * (1 - cooldown_percent)), 2, 11)
        
        # ゲームオーバー表示
        if self.game_over:
            pyxel.text(self.WIDTH // 2 - 30, self.HEIGHT // 2, "GAME OVER", 8)
            pyxel.text(self.WIDTH // 2 - 40, self.HEIGHT // 2 + 10, "PRESS R TO RESTART", 8)


if __name__ == "__main__":
    InvadersGame()
