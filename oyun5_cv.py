"""
🌍 SHADOW HUNTER EARTH & SPACE - OpenCV Versiyonu
Gezegen keşif oyunu
"""

import cv2
import numpy as np
import random
import time
import math
import json

# OpenCV başlat
cap = None
try:
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
except:
    pass

WIDTH, HEIGHT = 1280, 720

# Renkler (BGR)
COLORS = {
    'cyan': (255, 255, 0),
    'green': (0, 255, 0),
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'yellow': (0, 255, 255),
    'orange': (0, 165, 255),
    'purple': (255, 0, 255),
    'gray': (128, 128, 128),
}

# Gezegenler
PLANETS = {
    'earth': {
        'name': 'DUNYA',
        'color': (34, 139, 34),
        'sky': (135, 206, 235),
        'fog': (200, 230, 255),
    },
    'mars': {
        'name': 'MARS',
        'color': (139, 69, 19),
        'sky': (255, 100, 50),
        'fog': (200, 100, 80),
    },
    'space': {
        'name': 'UZAY',
        'color': (20, 0, 40),
        'sky': (0, 0, 20),
        'fog': (30, 0, 50),
    },
    'moon': {
        'name': 'AY',
        'color': (169, 169, 169),
        'sky': (0, 0, 10),
        'fog': (80, 80, 100),
    },
}

# Düşmanlar
ENEMIES = {
    'alien': {'hp': 3, 'speed': 4, 'color': COLORS['green'], 'size': 20, 'score': 20},
    'robot': {'hp': 5, 'speed': 2, 'color': COLORS['gray'], 'size': 25, 'score': 30},
    'monster': {'hp': 8, 'speed': 3, 'color': COLORS['purple'], 'size': 30, 'score': 50},
    'boss': {'hp': 50, 'speed': 1.5, 'color': COLORS['red'], 'size': 55, 'score': 500},
}

# Silahlar
WEAPONS = {
    'laser': {'damage': 1.5, 'speed': 25, 'color': COLORS['red'], 'ammo': 50},
    'plasma': {'damage': 3, 'speed': 15, 'color': COLORS['cyan'], 'ammo': 30},
    'missile': {'damage': 5, 'speed': 10, 'color': COLORS['orange'], 'ammo': 10},
}

# Kayıt sistemi
def save_game(data):
    with open('space_hunter_save.json', 'w') as f:
        json.dump(data, f)

def load_game():
    try:
        with open('space_hunter_save.json', 'r') as f:
            return json.load(f)
    except:
        return None

# Oyuncu
class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.hp = 100
        self.max_hp = 100
        self.speed = 15
        self.color = COLORS['cyan']
        self.weapon = 'laser'
        self.ammo = 50
        self.shield = 0
    
    def move(self, dx, dy):
        self.x = max(30, min(WIDTH - 30, self.x + dx * self.speed))
        self.y = max(80, min(HEIGHT - 30, self.y + dy * self.speed))

# Düşman
class Enemy:
    def __init__(self, enemy_type='alien'):
        self.type = enemy_type
        info = ENEMIES[enemy_type]
        
        side = random.choice(['T', 'B', 'L', 'R'])
        if side == 'T':
            self.x = random.randint(50, WIDTH - 50)
            self.y = random.randint(90, 180)
        elif side == 'B':
            self.x = random.randint(50, WIDTH - 50)
            self.y = random.randint(HEIGHT - 180, HEIGHT - 50)
        elif side == 'L':
            self.x = random.randint(50, 180)
            self.y = random.randint(100, HEIGHT - 50)
        else:
            self.x = random.randint(WIDTH - 180, WIDTH - 50)
            self.y = random.randint(100, HEIGHT - 50)
        
        self.hp = info['hp']
        self.max_hp = info['hp']
        self.speed = info['speed']
        self.color = info['color']
        self.size = info['size']
        self.score = info['score']

# Mermi
class Bullet:
    def __init__(self, x, y, dx, dy, damage, color, lifetime=40):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.color = color
        self.life = lifetime
    
    def update(self):
        self.x += self.dx * 25
        self.y += self.dy * 25
        self.life -= 1
        return self.life > 0 and 0 < self.x < WIDTH and 0 < self.y < HEIGHT

# Parçacık
class Particle:
    def __init__(self, x, y, color):
        self.x = x + random.uniform(-8, 8)
        self.y = y + random.uniform(-8, 8)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.color = color
        self.life = random.randint(15, 30)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0

# Yıldız (Uzay için)
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT // 2)
        self.size = random.randint(1, 3)
        self.brightness = random.randint(100, 255)

# Global
player = Player()
score = 0
level = 1
gold = 0
current_planet = 'earth'
enemies = []
bullets = []
particles = []
stars = []
spawn_timer = 0
game_started = False
game_over = False
is_paused = False

# Yıldızları oluştur
for _ in range(100):
    stars.append(Star())

def draw_planet_background(frame, planet_name):
    """Gezegen arka planı"""
    p = PLANETS[planet_name]
    
    # Gökyüzü
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), p['sky'], -1)
    
    # Yıldızlar (sadece uzayda)
    if planet_name == 'space':
        for star in stars:
            cv2.circle(frame, (star.x, star.y), star.size, (star.brightness, star.brightness, star.brightness), -1)
    
    # Zemin
    pts = np.array([[0, HEIGHT // 2], [WIDTH, HEIGHT // 2], 
                    [WIDTH, HEIGHT], [0, HEIGHT]], np.int32)
    cv2.fillPoly(frame, [pts], p['color'])
    
    # Izgara
    for i in range(0, HEIGHT // 2, 25):
        y = HEIGHT // 2 + i
        alpha = 1 - (y - HEIGHT // 2) / (HEIGHT // 2)
        c = tuple(max(0, int(p['color'][j] * alpha)) for j in range(3))
        cv2.line(frame, (0, y), (WIDTH, y), c, 1)
    
    # Ufuk
    cv2.line(frame, (0, HEIGHT // 2), (WIDTH, HEIGHT // 2), (200, 200, 200), 3)

def draw_player(frame, p):
    """Oyuncu"""
    cx, cy = WIDTH // 2, HEIGHT // 2
    
    # Crosshair
    cv2.line(frame, (cx - 25, cy), (cx + 25, cy), p.color, 2)
    cv2.line(frame, (cx, cy - 25), (cx, cy + 25), p.color, 2)
    cv2.circle(frame, (cx, cy), 5, p.color, -1)
    
    # Silah
    wpn = WEAPONS[p.weapon]
    cv2.rectangle(frame, (WIDTH - 120, HEIGHT - 80), (WIDTH - 40, HEIGHT - 30), wpn['color'], -1)

def draw_enemy(frame, e):
    """Düşman"""
    # Perspektif boyut
    size = int(e.size * (1 + (HEIGHT // 2 - e.y) / HEIGHT * 0.5))
    size = max(5, size)
    
    cv2.circle(frame, (int(e.x), int(e.y)), size, e.color, -1)
    cv2.circle(frame, (int(e.x), int(e.y)), size, COLORS['white'], 2)
    
    # HP
    if e.hp < e.max_hp:
        ratio = e.hp / e.max_hp
        cv2.rectangle(frame, (int(e.x - 20), int(e.y - size - 10)), 
                     (int(e.x + 20), int(e.y - size - 3)), (50, 0, 0), -1)
        cv2.rectangle(frame, (int(e.x - 18), int(e.y - size - 8)), 
                     (int(e.x - 18 + 36 * ratio), int(e.y - size - 5)), COLORS['red'], -1)

def draw_bullet(frame, b):
    """Mermi"""
    cv2.circle(frame, (int(b.x), int(b.y)), 5, b.color, -1)
    # Işık efekti
    cv2.circle(frame, (int(b.x), int(b.y)), 10, b.color, 1)

def draw_particle(frame, p):
    """Parçacık"""
    if p.life > 0:
        alpha = p.life / 30
        c = tuple(int(cl * alpha) for cl in p.color)
        cv2.circle(frame, (int(p.x), int(p.y)), 3, c, -1)

def draw_ui(frame, hp, ammo, shield, score, level, gold, planet):
    """UI"""
    cv2.rectangle(frame, (0, 0), (WIDTH, 55), (0, 0, 0), -1)
    
    # Gezegen
    cv2.putText(frame, f"Gezegen: {PLANETS[planet]['name']}", (20, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['white'], 2)
    
    # HP
    ratio = hp / 100
    cv2.rectangle(frame, (250, 20), (400, 45), (50, 50, 50), -1)
    hp_color = COLORS['green'] if ratio > 0.5 else COLORS['red']
    cv2.rectangle(frame, (252, 22), (252 + 146 * ratio, 43), hp_color, -1)
    cv2.putText(frame, f"HP: {int(hp)}", (410, 38), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['white'], 1)
    
    # Kalkan
    if shield > 0:
        cv2.putText(frame, f"Kalkan: {int(shield)}", (500, 38), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['cyan'], 1)
    
    # Cephane
    cv2.putText(frame, f"Ammo: {ammo}", (650, 38), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['yellow'], 1)
    
    # Skor
    cv2.putText(frame, f"Skor: {score}", (800, 38), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['white'], 1)
    
    # Altın
    cv2.putText(frame, f"Altin: {gold}", (950, 38), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['orange'], 1)
    
    # Seviye
    cv2.putText(frame, f"Seviye: {level}", (1100, 38), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['green'], 1)

def draw_menu(frame):
    """Menü"""
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), (5, 5, 15), -1)
    
    # Başlık
    cv2.putText(frame, "SHADOW HUNTER", (WIDTH // 2 - 200, 150), 
               cv2.FONT_HERSHEY_SIMPLEX, 2.5, COLORS['cyan'], 5)
    
    cv2.putText(frame, "UZAY KEŞİF MACERASI", (WIDTH // 2 - 180, 210), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS['purple'], 2)
    
    # Gezegen seçimi
    cv2.putText(frame, "Gezegen Sec:", (WIDTH // 2 - 100, 320), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['white'], 2)
    
    planets = list(PLANETS.items())
    for i, (key, p) in enumerate(planets):
        x = 150 + i * 300
        y = 360
        color = p['color'] if key == current_planet else (80, 80, 80)
        cv2.circle(frame, (x + 50, y + 40), 50, color, -1)
        cv2.circle(frame, (x + 50, y + 40), 50, COLORS['white'], 2)
        cv2.putText(frame, p['name'], (x + 10, y + 110), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['white'], 2)
    
    # Talimatlar
    cv2.putText(frame, "WASD: Hareket | SPACE: Ateş | 1-3: Silah", (WIDTH // 2 - 250, 500), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['gray'], 2)
    
    cv2.putText(frame, "Baslamak icin ENTER", (WIDTH // 2 - 150, 600), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS['green'], 2)

def draw_game_over(frame, score, gold):
    """Oyun bitişi"""
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), (0, 0, 0), -1)
    
    cv2.putText(frame, "UZAYDA HAYAT YOK", (WIDTH // 2 - 200, HEIGHT // 2 - 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 2.5, COLORS['red'], 5)
    
    cv2.putText(frame, f"Skor: {score}", (WIDTH // 2 - 80, HEIGHT // 2 + 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLORS['white'], 3)
    
    cv2.putText(frame, f"Toplanan: {gold}", (WIDTH // 2 - 100, HEIGHT // 2 + 80), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS['orange'], 2)

def main():
    global player, score, level, gold, enemies, bullets, particles
    global spawn_timer, game_started, game_over, is_paused, current_planet
    
    running = True
    
    while running:
        # Frame al
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
            if game_started:
                is_paused = not is_paused
            else:
                running = False
        
        if key == ord('r') or key == ord('R'):
            if game_over:
                player = Player()
                score = 0
                level = 1
                gold = 0
                enemies = []
                bullets = []
                particles = []
                game_over = False
                game_started = True
        
        if not game_started:
            # Gezegen seçimi
            if key == ord('1'): current_planet = 'earth'
            if key == ord('2'): current_planet = 'mars'
            if key == ord('3'): current_planet = 'space'
            if key == ord('4'): current_planet = 'moon'
            
            if key == 13:  # ENTER
                game_started = True
            
            draw_menu(frame)
            cv2.imshow("Space Hunter CV", frame)
            continue
        
        if game_over:
            draw_game_over(frame, score, gold)
            cv2.imshow("Space Hunter CV", frame)
            continue
        
        if is_paused:
            draw_planet_background(frame, current_planet)
            for e in enemies: draw_enemy(frame, e)
            for b in bullets: draw_bullet(frame, b)
            for p in particles: draw_particle(frame, p)
            draw_player(frame, player)
            draw_ui(frame, player.hp, player.ammo, player.shield, score, level, gold, current_planet)
            cv2.putText(frame, "PAUSED", (WIDTH // 2 - 60, HEIGHT // 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, COLORS['yellow'], 4)
            cv2.imshow("Space Hunter CV", frame)
            continue
        
        # Hareket
        dx, dy = 0, 0
        if key == ord('w'): dy = -1
        if key == ord('s'): dy = 1
        if key == ord('a'): dx = -1
        if key == ord('d'): dx = 1
        
        player.move(dx, dy)
        
        # Silah değiştir
        if key == ord('1'): player.weapon = 'laser'
        if key == ord('2'): player.weapon = 'plasma'
        if key == ord('3'): player.weapon = 'missile'
        
        # Ateş
        if key == 32:  # SPACE
            wpn = WEAPONS[player.weapon]
            if player.ammo > 0:
                player.ammo -= 1
                bullets.append(Bullet(
                    player.x, player.y - 20,
                    random.uniform(-0.05, 0.05), -1,
                    wpn['damage'], wpn['color']
                ))
        
        # Spawn
        spawn_timer += 1
        if spawn_timer > 35:
            spawn_timer = 0
            max_enemies = 2 + level
            if len(enemies) < max_enemies:
                if level % 5 == 0 and len(enemies) == 0:
                    enemies.append(Enemy('boss'))
                else:
                    enemies.append(Enemy(random.choice(['alien', 'robot', 'monster'])))
        
        # Düşman hareketi
        for e in enemies:
            e.move_toward = lambda tx, ty, s=e.speed: (
                setattr(e, 'x', e.x + (tx - e.x) / math.hypot(tx - e.x, ty - e.y) * s if math.hypot(tx - e.x, ty - e.y) > 0 else 0),
                setattr(e, 'y', e.y + (ty - e.y) / math.hypot(tx - e.x, ty - e.y) * s if math.hypot(tx - e.x, ty - e.y) > 0 else 0)
            )
            e.move_toward(player.x, player.y)
            
            if math.hypot(e.x - player.x, e.y - player.y) < e.size + 20:
                damage = 0.5
                if player.shield > 0:
                    player.shield -= 0.3
                    damage *= 0.3
                player.hp -= damage
                for _ in range(3):
                    particles.append(Particle(player.x, player.y, COLORS['red']))
        
        # Mermi güncelleme
        for b in bullets[:]:
            if not b.update():
                bullets.remove(b)
                continue
            
            for e in enemies[:]:
                if math.hypot(b.x - e.x, b.y - e.y) < e.size + 5:
                    e.hp -= b.damage
                    bullets.remove(b)
                    for _ in range(5):
                        particles.append(Particle(e.x, e.y, b.color))
                    break
        
        # Düşman ölümü
        for e in enemies[:]:
            if e.hp <= 0:
                enemies.remove(e)
                score += e.score
                gold += e.score // 2
                
                for _ in range(15):
                    particles.append(Particle(e.x, e.y, e.color))
                
                if e.type == 'boss':
                    level += 1
        
        # Parçacık güncelleme
        for p in particles[:]:
            if not p.update():
                particles.remove(p)
        
        # Oyun bitti
        if player.hp <= 0:
            game_over = True
        
        # Çizim
        draw_planet_background(frame, current_planet)
        
        for p in particles:
            draw_particle(frame, p)
        
        for e in enemies:
            draw_enemy(frame, e)
        
        for b in bullets:
            draw_bullet(frame, b)
        
        draw_player(frame, player)
        draw_ui(frame, player.hp, player.ammo, player.shield, score, level, gold, current_planet)
        
        cv2.imshow("Space Hunter CV", frame)
    
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
