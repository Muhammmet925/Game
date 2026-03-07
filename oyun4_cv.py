"""SHADOW HUNTER 3D CV - OpenCV FPS Oyunu"""

import cv2
import numpy as np
import random
import time
import math
import json

# OpenCV başlat
cap = cv2.VideoCapture(0) if cv2.VideoCapture(0).isOpened() else None
WIDTH, HEIGHT = 1280, 720

# Renkler
CYAN = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
BLUE = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (0, 255, 255)
ORANGE = (0, 165, 255)
PURPLE = (255, 0, 128)

# Haritalar
MAPS = {
    'dunya': {'ground': (34, 139, 34), 'sky': (135, 206, 235)},
    'uzay': {'ground': (20, 0, 40), 'sky': (0, 0, 20)},
    'cehennem': {'ground': (40, 10, 0), 'sky': (60, 20, 0)},
}

# Silahlar
WEAPONS = {
    'sword': {'damage': 2, 'range': 50, 'color': WHITE},
    'pistol': {'damage': 1, 'range': 300, 'color': YELLOW, 'ammo': 50},
    'magic': {'damage': 3, 'range': 200, 'color': PURPLE, 'ammo': 30},
}

# Düşmanlar
ENEMIES = {
    'goblin': {'hp': 2, 'speed': 3, 'color': GREEN, 'size': 15, 'score': 10},
    'orc': {'hp': 5, 'speed': 2, 'color': ORANGE, 'size': 25, 'score': 30},
    'dragon': {'hp': 50, 'speed': 1.5, 'color': RED, 'size': 50, 'score': 500},
}

# Oyuncu
player_x, player_y = WIDTH // 2, HEIGHT // 2
player_hp = 100
player_weapon = 'sword'
player_ammo = 100

# Oyun değişkenleri
score = 0
level = 1
gold = 0
enemies = []
bullets = []
particles = []
spawn_timer = 0
game_started = False
game_over = False
selected_map = 'dunya'

def draw_3d_field(frame, map_name):
    m = MAPS[map_name]
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT//2), m['sky'], -1)
    pts = np.array([[0, HEIGHT//2], [WIDTH, HEIGHT//2], [WIDTH, HEIGHT], [0, HEIGHT]], np.int32)
    cv2.fillPoly(frame, [pts], m['ground'])
    for i in range(0, HEIGHT//2, 30):
        y = HEIGHT//2 + i
        cv2.line(frame, (0, y), (WIDTH, y), (m['ground'][0]-20, m['ground'][1]-20, m['ground'][2]-20), 1)
    cv2.line(frame, (0, HEIGHT//2), (WIDTH, HEIGHT//2), (200, 200, 200), 3)

def draw_player(frame):
    cx, cy = WIDTH // 2, HEIGHT // 2
    cv2.line(frame, (cx-20, cy), (cx+20, cy), CYAN, 2)
    cv2.line(frame, (cx, cy-20), (cx, cy+20), CYAN, 2)
    wpn = WEAPONS[player_weapon]
    cv2.rectangle(frame, (WIDTH-150, HEIGHT-100), (WIDTH-50, HEIGHT-30), wpn['color'], -1)

def draw_enemy(frame, e):
    info = ENEMIES[e['type']]
    size = int(info['size'] * (1 + (HEIGHT//2 - e['y']) / HEIGHT))
    size = max(5, size)
    cv2.circle(frame, (int(e['x']), int(e['y'])), size, info['color'], -1)
    cv2.circle(frame, (int(e['x']), int(e['y'])), size, WHITE, 2)

def draw_bullet(frame, b):
    cv2.circle(frame, (int(b['x']), int(b['y'])), 4, b['color'], -1)

def draw_particle(frame, p):
    if p['life'] > 0:
        alpha = p['life'] / 25
        c = tuple(int(c1 * alpha) for c1 in p['color'])
        cv2.circle(frame, (int(p['x']), int(p['y'])), 3, c, -1)

def draw_ui(frame):
    cv2.rectangle(frame, (0, 0), (WIDTH, 60), BLACK, -1)
    ratio = player_hp / 100
    cv2.rectangle(frame, (20, 20), (220, 45), (50, 50, 50), -1)
    hp_color = GREEN if ratio > 0.5 else RED
    bar_width = int(196 * ratio)
    cv2.rectangle(frame, (22, 22), (22 + bar_width, 43), hp_color, -1)
    cv2.putText(frame, f"HP: {int(player_hp)}", (230, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 1)
    cv2.putText(frame, f"Ammo: {player_ammo}", (400, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, YELLOW, 1)
    cv2.putText(frame, f"Skor: {score}", (600, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 1)
    cv2.putText(frame, f"Altin: {gold}", (800, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, ORANGE, 1)
    cv2.putText(frame, f"Seviye: {level}", (1000, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, GREEN, 1)

def draw_menu(frame):
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), (10, 10, 20), -1)
    cv2.putText(frame, "SHADOW HUNTER", (WIDTH//2-200, 150), cv2.FONT_HERSHEY_SIMPLEX, 2.5, CYAN, 5)
    cv2.putText(frame, "FPS MACERA", (WIDTH//2-130, 210), cv2.FONT_HERSHEY_SIMPLEX, 1.2, PURPLE, 2)
    cv2.putText(frame, "1: Dunya | 2: Uzay | 3: Cehennem", (WIDTH//2-250, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2)
    cv2.putText(frame, "WASD: Hareket | SPACE: Saldiri | 1-3: Silah", (WIDTH//2-280, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.7, WHITE, 2)
    cv2.putText(frame, "Baslamak icin ENTER", (WIDTH//2-150, 520), cv2.FONT_HERSHEY_SIMPLEX, 1, YELLOW, 2)

def draw_game_over(frame):
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), BLACK, -1)
    cv2.putText(frame, "OYUN BITTI", (WIDTH//2-150, HEIGHT//2-50), cv2.FONT_HERSHEY_SIMPLEX, 3, RED, 5)
    cv2.putText(frame, f"Skor: {score}", (WIDTH//2-80, HEIGHT//2+20), cv2.FONT_HERSHEY_SIMPLEX, 1.5, WHITE, 3)
    cv2.putText(frame, f"Altin: +{gold}", (WIDTH//2-100, HEIGHT//2+80), cv2.FONT_HERSHEY_SIMPLEX, 1.2, ORANGE, 2)

def main():
    global player_x, player_y, player_hp, player_weapon, player_ammo, score, level, gold
    global enemies, bullets, particles, spawn_timer, game_started, game_over, selected_map
    
    running = True
    
    while running:
        if cap:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (WIDTH, HEIGHT))
            else:
                frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        else:
            frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:
            running = False
        
        if key == ord('r') or key == ord('R'):
            if game_over:
                player_x, player_y = WIDTH // 2, HEIGHT // 2
                player_hp = 100
                player_ammo = 100
                score = 0
                level = 1
                gold = 0
                enemies = []
                bullets = []
                particles = []
                game_over = False
                game_started = True
        
        if not game_started:
            if key == ord('1'): selected_map = 'dunya'
            if key == ord('2'): selected_map = 'uzay'
            if key == ord('3'): selected_map = 'cehennem'
            if key == 13:
                game_started = True
            draw_menu(frame)
            cv2.imshow("Shadow Hunter 3D CV", frame)
            continue
        
        if game_over:
            draw_game_over(frame)
            cv2.imshow("Shadow Hunter 3D CV", frame)
            continue
        
        if key == ord('1'): player_weapon = 'sword'
        if key == ord('2'): player_weapon = 'pistol'
        if key == ord('3'): player_weapon = 'magic'
        
        dx, dy = 0, 0
        if key == ord('w'): dy = -1
        if key == ord('s'): dy = 1
        if key == ord('a'): dx = -1
        if key == ord('d'): dx = 1
        
        player_x = max(50, min(WIDTH-50, player_x + dx * 12))
        player_y = max(100, min(HEIGHT-50, player_y + dy * 12))
        
        if key == 32:  # SPACE
            wpn = WEAPONS[player_weapon]
            if player_weapon == 'sword':
                for e in enemies[:]:
                    dist = math.hypot(e['x'] - player_x, e['y'] - player_y)
                    if dist < wpn['range']:
                        e['hp'] -= wpn['damage']
                        for _ in range(5):
                            particles.append({'x': e['x'], 'y': e['y'], 'vx': random.uniform(-2, 2),
                                          'vy': random.uniform(-2, 2), 'color': wpn['color'], 'life': 20, 'size': 3})
            else:
                if player_ammo > 0:
                    player_ammo -= 1
                    bullets.append({'x': player_x, 'y': player_y-20, 'dx': random.uniform(-0.1, 0.1), 'dy': -1,
                                  'damage': wpn['damage'], 'color': wpn['color']})
        
        spawn_timer += 1
        if spawn_timer > 40:
            spawn_timer = 0
            max_enemies = 3 + level * 2
            if len(enemies) < max_enemies:
                if level % 5 == 0 and len(enemies) == 0:
                    enemies.append({'type': 'dragon', 'x': WIDTH-100, 'y': 200, 'hp': 50})
                else:
                    etype = random.choice(['goblin', 'orc'])
                    info = ENEMIES[etype]
                    side = random.choice(['T', 'B', 'L', 'R'])
                    if side == 'T': ex, ey = random.randint(50, WIDTH-50), random.randint(90, 150)
                    elif side == 'B': ex, ey = random.randint(50, WIDTH-50), random.randint(HEIGHT-150, HEIGHT-50)
                    elif side == 'L': ex, ey = random.randint(50, 150), random.randint(100, HEIGHT-50)
                    else: ex, ey = random.randint(WIDTH-150, WIDTH-50), random.randint(100, HEIGHT-50)
                    enemies.append({'type': etype, 'x': ex, 'y': ey, 'hp': info['hp']})
        
        for e in enemies:
            info = ENEMIES[e['type']]
            dx = player_x - e['x']
            dy = player_y - e['y']
            dist = math.hypot(dx, dy)
            if dist > 0:
                e['x'] += (dx / dist) * info['speed']
                e['y'] += (dy / dist) * info['speed']
            if dist < info['size'] + 20:
                player_hp -= 0.5
                for _ in range(3):
                    particles.append({'x': player_x, 'y': player_y, 'vx': random.uniform(-2, 2),
                                  'vy': random.uniform(-2, 2), 'color': RED, 'life': 15, 'size': 3})
        
        for b in bullets[:]:
            b['x'] += b['dx'] * 20
            b['y'] += b['dy'] * 20
            if b['y'] < 0:
                bullets.remove(b)
                continue
            for e in enemies[:]:
                info = ENEMIES[e['type']]
                if math.hypot(b['x'] - e['x'], b['y'] - e['y']) < info['size'] + 5:
                    e['hp'] -= b['damage']
                    bullets.remove(b)
                    for _ in range(3):
                        particles.append({'x': e['x'], 'y': e['y'], 'vx': random.uniform(-2, 2),
                                      'vy': random.uniform(-2, 2), 'color': b['color'], 'life': 15, 'size': 3})
                    break
        
        for e in enemies[:]:
            if e['hp'] <= 0:
                info = ENEMIES[e['type']]
                enemies.remove(e)
                score += info['score']
                gold += info['score'] // 2
                for _ in range(10):
                    particles.append({'x': e['x'], 'y': e['y'], 'vx': random.uniform(-3, 3),
                                  'vy': random.uniform(-3, 3), 'color': info['color'], 'life': 25, 'size': 5})
                if e['type'] == 'dragon':
                    level += 1
        
        for p in particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                particles.remove(p)
        
        if player_hp <= 0:
            game_over = True
        
        draw_3d_field(frame, selected_map)
        for p in particles: draw_particle(frame, p)
        for e in enemies: draw_enemy(frame, e)
        for b in bullets: draw_bullet(frame, b)
        draw_player(frame)
        draw_ui(frame)
        
        cv2.imshow("Shadow Hunter 3D CV", frame)
    
    if cap:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
