import pyxel

# Pyxelリソースファイルを作成するスクリプト
def create_assets():
    # リソースの初期化
    pyxel.init(160, 120)
    
    # プレイヤー (Amazon Q) - 青色
    pyxel.image(0).rect(0, 0, 8, 8, 0)  # 背景を透明に
    pyxel.image(0).rect(2, 1, 4, 6, 12)  # 青い四角形
    pyxel.image(0).pset(1, 2, 12)  # 左側の点
    pyxel.image(0).pset(6, 2, 12)  # 右側の点
    pyxel.image(0).pset(1, 5, 12)  # 左側の点
    pyxel.image(0).pset(6, 5, 12)  # 右側の点
    
    # 敵タイプ1 (EC2) - 赤色
    pyxel.image(0).rect(8, 0, 8, 8, 0)  # 背景を透明に
    pyxel.image(0).rect(10, 1, 4, 6, 8)  # 赤い四角形
    pyxel.image(0).line(10, 3, 13, 3, 7)  # 白い線
    
    # 敵タイプ2 (S3) - オレンジ色
    pyxel.image(0).rect(16, 0, 8, 8, 0)  # 背景を透明に
    pyxel.image(0).rect(18, 1, 4, 6, 9)  # オレンジの四角形
    pyxel.image(0).line(18, 4, 21, 4, 7)  # 白い線
    
    # 敵タイプ3 (Lambda) - 黄色
    pyxel.image(0).rect(24, 0, 8, 8, 0)  # 背景を透明に
    pyxel.image(0).rect(26, 1, 4, 6, 10)  # 黄色の四角形
    pyxel.image(0).line(26, 2, 29, 2, 7)  # 白い線
    pyxel.image(0).line(26, 5, 29, 5, 7)  # 白い線
    
    # 通常弾 - 白色
    pyxel.image(0).rect(0, 8, 2, 4, 0)  # 背景を透明に
    pyxel.image(0).rect(0, 8, 2, 4, 7)  # 白い弾
    
    # 敵の弾 - 赤色
    pyxel.image(0).rect(2, 8, 2, 4, 0)  # 背景を透明に
    pyxel.image(0).rect(2, 8, 2, 4, 8)  # 赤い弾
    
    # 貫通弾 - オレンジ色
    pyxel.image(0).rect(4, 8, 4, 8, 0)  # 背景を透明に
    pyxel.image(0).rect(5, 8, 2, 6, 9)  # オレンジの弾
    pyxel.image(0).tri(5, 8, 7, 8, 6, 6, 9)  # 三角形の先端
    
    # バウンス弾 - 黄色
    pyxel.image(0).rect(8, 8, 4, 4, 0)  # 背景を透明に
    pyxel.image(0).circ(10, 10, 2, 10)  # 黄色の円
    
    # 爆発エフェクト
    pyxel.image(0).rect(12, 8, 8, 8, 0)  # 背景を透明に
    pyxel.image(0).circb(16, 12, 3, 8)  # 赤い円
    pyxel.image(0).circb(16, 12, 2, 10)  # 黄色い円
    pyxel.image(0).circb(16, 12, 1, 7)  # 白い円
    
    # リソースファイルを保存
    pyxel.save("invaders_assets.pyxres")

if __name__ == "__main__":
    create_assets()
    print("Assets created successfully!")
