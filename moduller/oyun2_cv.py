"""
⚔️ SOUL KNIGHT TARZI OYUN - OpenCV Versiyonu
Gerçek zamanlı savaş oyunu
"""

import cv2
import numpy as np
import random
import time
import math
from collections import deque

# OpenCV başlat
cap = None
try:
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
except:
    pass

# Ekran ayarları
WIDTH, HEIGHT = 1280, 720

# Renkler (BGR)
COLORS = {
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'green': (0, 255, 0),
    'cyan': (255, 255, 0),
    'magenta': (255, 0, 255),
    'yellow': (0, 255, 255),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'orange': (0, 165, 255),
    'purple': (128, 0, 128),
}

# Karakterler
CHARACTERS = {
    'knight': {'name': 'Savasci', 'color': COLORS['cyan'], 'hp': 120, 'speed': 4, 'damage': 1.5},
    'wizard': {'name': 'Buyucu', 'color': COLORS['magenta'], 'hp': 80, 'speed': 5, 'damage': 2.0},
    'assassin': {'name': 'Suikastci', 'color': COLORS['green'], 'hp': 70, 'speed': 10, 'damage': 1.8},
    'tank': {'name': 'Tank', 'color': COLORS['red'], 'hp': 150, 'speed': 3, 'damage': 2.0},
}

# Silahlar
WEAPONS = {
    'sword': {'name': 'Kilic', 'damage': 2, 'range': 60, 'color': COLORS['cyan']},
    'bow': {'name': 'Yay', 'damage': 1.5, 'range': 300, 'color': COLORS['orange']},
    'magic': {'name': 'Buyu', 'damage': 2.5, 'range': 200, 'color': COLORS['magenta']},
}

# Düşmanlar
ENEMIES = {
    'slime': {'hp': 2, 'speed': 2, 'color': COLORS['green'], 'size': 20, 'damage': 0.5},
    'bat': {'hp': 1, 'speed': 5, 'color': COLORS['purple'], 'size': 15, 'damage': 0.3},
    'skeleton': {'hp': 3, 'speed': 3, 'color': COLORS['white'], 'size': 25, 'damage': 1.0},
    'orc': {'hp': 5, 'speed': 2.5, 'color': COLORS['orange'], 'size': 30, 'damage': 1.5},
    'boss': {'hp': 30, 'speed': 2, 'color': COLORS['red'], 'size': 50, 'damage': 2.0},
}

# Oyun durumu
class GameState:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.gold = 0
        self.player_hp = 100
        self.max_hp = 100
        self.enemies_killed = 0
        self.is_game_over = False

# Oyuncu
class Player:
    def __init__(self, char_type='knight'):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.char_type = char_type
        self.hp = CHARACTERS[char_type]['hp']
        self.max_hp = CHARACTERS[char_type]['hp']
        self.speed = CHARACTERS[char_type]['speed']
        self.weapon = 'sword'
        self.direction = 0
        self.attack_cooldown = 0
        self.is_attacking = False
        self.attack_frame = 0
    
    def move(self, dx, dy):
        self.x = max(30, min(WIDTH - 30, self.x + dx * self.speed))
        self.y = max(80, min(HEIGHT - 30, self.y + dy * self.speed))
    
    def update(self):
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.is_attacking:
            self.attack_frame += 1
            if self.attack_frame > 10:
                self.is_attacking = False
                self.attack_frame = 0

# Düşman
class Enemy:
    def __init__(self, enemy_type='slime'):
        self.type = enemy_type
        info = ENEMIES[enemy_type]
        
        # Kenarlardan spawn
        side = random.choice(['T', 'B', 'L', 'R'])
        if side == 'T':
            self.x = random.randint(50, WIDTH - 50)
            self.y = random.randint(90, 200)
        elif side == 'B':
            self.x = random.randint(50, WIDTH - 50)
            self.y = random.randint(HEIGHT - 200, HEIGHT - 50)
        elif side == 'L':
            self.x = random.randint(50, 200)
            self.y = random.randint(100, HEIGHT - 50)
        else:
            self.x = random.randint(WIDTH - 200, WIDTH - 50)
            self.y = random.randint(100, HEIGHT - 50)
        
        self.hp = info['hp']
        self.max_hp = info['hp']
        self.speed = info['speed']
        self.color = info['color']
        self.size = info['size']
        self.damage = info['damage']
    
    def move_toward(self, target_x, target_y):
        dx = target_x - self.x
        dy = target_y - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            self.x += (dx / dist) * self.speed
            self.y += (dy / dist) * self.speed

# Mermi
class Bullet:
    def __init__(self, x, y, dx, dy, damage, weapon_color):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.color = weapon_color
        self.speed = 15
        self.life = 60
    
    def update(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        self.life -= 1
        return self.life > 0

# Efekt
class Effect:
    def __init__(self, x, y, color, effect_type='spark'):
        self.x = x
        self.y = y
        self.color = color
        self.life = 20
        self.size = random.randint(3, 8)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0

# Oyun nesneleri
player = Player()
game_state = GameState()
enemies = []
bullets = []
effects = []
spawn_timer = 0

# Kamera
last_frame = None

def draw_field(frame):
    """Oyun alanı çiz"""
    # Arka plan
    cv2.rectangle(frame, (0, 80), (WIDTH, HEIGHT), (20, 10, 30), -1)
    
    # Izgara
    for i in range(0, WIDTH, 50):
        cv2.line(frame, (i, 80), (i, HEIGHT), (50, 30, 60), 1)
    for i in range(80, HEIGHT, 50):
        cv2.line(frame, (0, i), (WIDTH, i), (50, 30, 60), 1)
    
    # Çerçeve
    cv2.rectangle(frame, (0, 80), (WIDTH, HEIGHT), (100, 80, 60), 4)

def draw_player(frame, p):
    """Oyuncu çiz"""
    char_info = CHARACTERS[p.char_type]
    color = char_info['color']
    
    # Vücut
    cv2.circle(frame, (int(p.x), int(p.y)), 25, color, -1)
    cv2.circle(frame, (int(p.x), int(p.y)), 25, (255, 255, 255), 2)
    
    # Yön gösterge
    end_x = int(p.x + math.cos(p.direction) * 30)
    end_y = int(p.y + math.sin(p.direction) * 30)
    cv2.line(frame, (int(p.x), int(p.y)), (end_x, end_y), (255, 255, 255), 3)
    
    # Saldırı efekti
    if p.is_attacking:
        weapon_info = WEAPONS[p.weapon]
        cv2.circle(frame, (int(p.x), int(p.y)), weapon_info['range'], weapon_info['color'], 2)
    
    # HP bar
    hp_ratio = p.hp / p.max_hp
    cv2.rectangle(frame, (int(p.x - 30), int(p.y - 40)), (int(p.x + 30), int(p.y - 32)), (50, 0, 0), -1)
    hp_color = (0, 255, 0) if hp_ratio > 0.5 else (0, 0, 255)
    cv2.rectangle(frame, (int(p.x - 28), int(p.y - 38)), (int(p.x - 28 + 56 * hp_ratio), int(p.y - 34)), hp_color, -1)

def draw_enemy(frame, e):
    """Düşman çiz"""
    cv2.circle(frame, (int(e.x), int(e.y)), e.size, e.color, -1)
    cv2.circle(frame, (int(e.x), int(e.y)), e.size, (255, 255, 255), 2)
    
    # HP bar
    if e.hp < e.max_hp:
        hp_ratio = e.hp / e.max_hp
        cv2.rectangle(frame, (int(e.x - 20), int(e.y - e.size - 10)), 
                     (int(e.x + 20), int(e.y - e.size - 5)), (50, 0, 0), -1)
        cv2.rectangle(frame, (int(e.x - 18), int(e.y - e.size - 8)), 
                     (int(e.x - 18 + 36 * hp_ratio), int(e.y - e.size - 7)), (0, 0, 255), -1)

def draw_bullet(frame, b):
    """Mermi çiz"""
    cv2.circle(frame, (int(b.x), int(b.y)), 6, b.color, -1)

def draw_effect(frame, e):
    """Efekt çiz"""
    if e.life > 0:
        alpha = e.life / 20
        color = tuple(int(c * alpha) for c in e.color)
        cv2.circle(frame, (int(e.x), int(e.y)), e.size, color, -1)

def draw_ui(frame, state, player):
    """UI çiz"""
    # Üst bar
    cv2.rectangle(frame, (0, 0), (WIDTH, 80), (0, 0, 0), -1)
    
    # Skor
    cv2.putText(frame, f"Skor: {state.score}", (20, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Altin
    cv2.putText(frame, f"Altin: {state.gold}", (200, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 215, 255), 2)
    
    # Seviye
    cv2.putText(frame, f"Seviye: {state.level}", (400, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    # Silah
    weapon = WEAPONS[player.weapon]
    cv2.putText(frame, f"Silah: {weapon['name']}", (600, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, weapon['color'], 2)
    
    # HP
    hp_ratio = state.player_hp / state.max_hp
    cv2.rectangle(frame, (800, 20), (1100, 50), (50, 50, 50), -1)
    hp_color = (0, 255, 0) if hp_ratio > 0.5 else (0, 0, 255)
    cv2.rectangle(frame, (805, 25), (805 + 290 * hp_ratio, 45), hp_color, -1)
    cv2.putText(frame, f"Can: {int(state.player_hp)}/{state.max_hp}", (920, 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 1)

def draw_menu(frame):
    """Menü ekranı"""
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), (0, 0, 0), -1)
    
    # Başlık
    cv2.putText(frame, "SOUL KNIGHT TARZI SAVAS", (WIDTH // 2 - 280, 200), 
               cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 255, 255), 5)
    cv2.putText(frame, "OpenCV Versiyonu", (WIDTH // 2 - 150, 260), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 0, 255), 3)
    
    # Karakter seçimi
    y = 350
    cv2.putText(frame, "Karakter Secin:", (WIDTH // 2 - 120, y), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    characters = list(CHARACTERS.items())
    for i, (key, char) in enumerate(characters):
        x = 200 + i * 250
        cv2.rectangle(frame, (x, y + 30), (x + 200, y + 150), char['color'], -1)
        cv2.rectangle(frame, (x, y + 30), (x + 200, y + 150), (255, 255, 255), 2)
        cv2.putText(frame, f"{i+1}. {char['name']}", (x + 20, y + 70), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        cv2.putText(frame, f"HP: {char['hp']}", (x + 20, y + 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.putText(frame, f"HP: {char['speed']}", (x + 20, y + 120), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    cv2.putText(frame, "Baslamak icin ENTER tusuna basin", (WIDTH // 2 - 220, 600), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.putText(frame, "WASD: Hareket | SPACE: Saldiri | 1-3: Karakter", (WIDTH // 2 - 280, 650), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (150, 150, 150), 2)

def draw_game_over(frame, state):
    """Oyun bitişi ekranı"""
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), (0, 0, 0), -1)
    
    cv2.putText(frame, "OYUN BITTI", (WIDTH // 2 - 150, HEIGHT // 2 - 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 3, (0, 0, 255), 5)
    
    cv2.putText(frame, f"Skor: {state.score}", (WIDTH // 2 - 100, HEIGHT // 2 + 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    
    cv2.putText(frame, "Yeniden oynamak icin R tusuna basin", (WIDTH // 2 - 220, HEIGHT // 2 + 100), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, (150, 150, 150), 2)

# Ana döngü
def main():
    global player, game_state, enemies, bullets, effects, spawn_timer
    
    game_started = False
    running = True
    
    while running:
        # Kameradan frame
        if cap is not None and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (WIDTH, HEIGHT))
            else:
                frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        else:
            frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            running = False
        
        if key == ord('r') or key == ord('R'):
            player = Player()
            game_state = GameState()
            enemies = []
            bullets = []
            effects = []
        
        if not game_started:
            if key in [ord(str(i)) for i in range(1, 5)]:
                char_idx = int(chr(key)) - 1
                chars = list(CHARACTERS.keys())
                if char_idx < len(chars):
                    player = Player(chars[char_idx])
                    game_state.max_hp = player.max_hp
                    game_state.player_hp = player.max_hp
            
            if key == 13:  # ENTER
                game_started = True
            
            draw_menu(frame)
            cv2.imshow("Soul Knight - OpenCV", frame)
            continue
        
        if game_state.is_game_over:
            if key == ord('r') or key == ord('R'):
                player = Player()
                game_state = GameState()
                enemies = []
                bullets = []
                effects = []
            
            draw_game_over(frame, game_state)
            cv2.imshow("Soul Knight - OpenCV", frame)
            continue
        
        # Oyun kontrolleri
        dx, dy = 0, 0
        if key == ord('w'): dy = -1
        if key == ord('s'): dy = 1
        if key == ord('a'): dx = -1
        if key == ord('d'): dx = 1
        
        if dx != 0 or dy != 0:
            player.direction = math.atan2(dy, dx)
        
        player.move(dx, dy)
        
        # Saldırı
        if key == 32 and player.attack_cooldown == 0:  # SPACE
            player.is_attacking = True
            player.attack_cooldown = 20
            
            weapon = WEAPONS[player.weapon]
            
            # Yakın dövüş
            if weapon['name'] == 'Kilic':
                for e in enemies[:]:
                    dist = math.hypot(e.x - player.x, e.y - player.y)
                    if dist < weapon['range']:
                        e.hp -= weapon['damage']
                        for _ in range(5):
                            effects.append(Effect(e.x, e.y, weapon['color']))
            else:
                # Uzak dövüş
                bullets.append(Bullet(player.x, player.y, 
                                   math.cos(player.direction), math.sin(player.direction),
                                   weapon['damage'], weapon['color']))
        
        # Silah değiştirme
        if key == ord('1'): player.weapon = 'sword'
        if key == ord('2'): player.weapon = 'bow'
        if key == ord('3'): player.weapon = 'magic'
        
        player.update()
        
        # Spawn
        spawn_timer += 1
        if spawn_timer > 60:
            spawn_timer = 0
            max_enemies = 3 + game_state.level * 2
            if len(enemies) < max_enemies:
                if game_state.level % 5 == 0 and len(enemies) == 0:
                    enemies.append(Enemy('boss'))
                else:
                    enemy_type = random.choice(['slime', 'bat', 'skeleton', 'orc'][:min(2 + game_state.level // 2, 4)])
                    enemies.append(Enemy(enemy_type))
        
        # Düşman hareketi
        for e in enemies:
            e.move_toward(player.x, player.y)
            
            # Oyuncuya çarpma
            dist = math.hypot(e.x - player.x, e.y - player.y)
            if dist < e.size + 25:
                game_state.player_hp -= e.damage
                for _ in range(3):
                    effects.append(Effect(player.x, player.y, (0, 0, 255)))
        
        # Mermi güncelleme
        for b in bullets[:]:
            if not b.update():
                bullets.remove(b)
                continue
            
            for e in enemies[:]:
                dist = math.hypot(b.x - e.x, b.y - e.y)
                if dist < e.size + 6:
                    e.hp -= b.damage
                    bullets.remove(b)
                    for _ in range(3):
                        effects.append(Effect(e.x, e.y, b.color))
                    break
        
        # Düşman ölümü
        for e in enemies[:]:
            if e.hp <= 0:
                enemies.remove(e)
                game_state.score += 10
                game_state.gold += 5
                game_state.enemies_killed += 1
                
                for _ in range(15):
                    effects.append(Effect(e.x, e.y, e.color))
                
                if e.type == 'boss':
                    game_state.score += 100
                    game_state.gold += 50
                    game_state.level += 1
        
        # Efekt güncelleme
        for e in effects[:]:
            if not e.update():
                effects.remove(e)
        
        # Seviye atlama
        if game_state.score >= game_state.level * 200:
            game_state.level += 1
        
        # Oyun bitti
        if game_state.player_hp <= 0:
            game_state.is_game_over = True
        
        # Çizim
        draw_field(frame)
        
        for e in effects:
            draw_effect(frame, e)
        
        for e in enemies:
            draw_enemy(frame, e)
        
        for b in bullets:
            draw_bullet(frame, b)
        
        draw_player(frame, player)
        draw_ui(frame, game_state, player)
        
        cv2.imshow("Soul Knight - OpenCV", frame)
    
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
