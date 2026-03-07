"""Z-HUNTER CV - OpenCV Savaş Oyunu"""

import cv2
import numpy as np
import random
import time
import math
import json

# OpenCV başlat
cap = cv2.VideoCapture(0) if cv2.VideoCapture(0).isOpened() else None
WIDTH, HEIGHT = 1280, 720

# Renkler (BGR)
CYAN = (255, 255, 0)
MAGENTA = (255, 0, 255)
YELLOW = (0, 255, 255)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GOLD = (0, 215, 255)

# Haritalar
MAPS = {
    'dojo': {'bg': (20, 20, 30), 'accent': (255, 100, 0)},
    'neon': {'bg': (10, 0, 20), 'accent': (0, 255, 255)},
    'lava': {'bg': (40, 5, 0), 'accent': (255, 50, 0)},
}

# Silahlar
WEAPONS = {
    'pistol': {'damage': 1, 'speed': 15, 'rate': 0.3, 'color': CYAN, 'size': 5},
    'laser': {'damage': 0.5, 'speed': 25, 'rate': 0.15, 'color': MAGENTA, 'size': 3},
    'shotgun': {'damage': 3, 'speed': 10, 'rate': 0.8, 'color': YELLOW, 'size': 12},
}

# Düşmanlar
ENEMIES = {
    'normal': {'hp': 1, 'speed': 2.5, 'color': RED, 'size': 20, 'score': 10},
    'fast': {'hp': 0.5, 'speed': 5, 'color': YELLOW, 'size': 15, 'score': 20},
    'tank': {'hp': 5, 'speed': 1.5, 'color': GREEN, 'size': 35, 'score': 50},
    'boss': {'hp': 50, 'speed': 1, 'color': RED, 'size': 60, 'score': 500},
}

# Oyuncu
player_x, player_y = WIDTH // 2, HEIGHT // 2
player_hp = 100
player_weapon = 'pistol'
player_direction = 0
last_shot = 0

# Oyun değişkenleri
score = 0
level = 1
gold = 0
kills = 0

# Nesneler
enemies = []
bullets = []
particles = []
spawn_timer = 0
game_started = False
game_over = False
current_map = 'dojo'

# Kayıt
def load_save():
    try:
        with open('z_hunter_save.json', 'r') as f:
            return json.load(f)
    except:
        return {'gold': 0}

def save_game():
    with open('z_hunter_save.json', 'w') as f:
        json.dump({'gold': gold}, f)

save_data = load_save()
gold = save_data.get('gold', 0)

def draw_background(frame, map_name):
    m = MAPS[map_name]
    cv2.rectangle(frame, (0, 80), (WIDTH, HEIGHT), m['bg'], -1)
    for i in range(0, WIDTH, 40):
        cv2.line(frame, (i, 80), (i, HEIGHT), (m['bg'][0]+10, m['bg'][1]+10, m['bg'][2]+10), 1)
    for i in range(80, HEIGHT, 40):
        cv2.line(frame, (0, i), (WIDTH, i), (m['bg'][0]+10, m['bg'][1]+10, m['bg'][2]+10), 1)
    cv2.rectangle(frame, (0, 80), (WIDTH, HEIGHT), m['accent'], 4)

def draw_player(frame, x, y, direction):
    cv2.circle(frame, (int(x), int(y)), 25, CYAN, -1)
    cv2.circle(frame, (int(x), int(y)), 25, WHITE, 3)
    end_x = int(x + math.cos(direction) * 35)
    end_y = int(y + math.sin(direction) * 35)
    cv2.line(frame, (int(x), int(y)), (end_x, end_y), WHITE, 4)

def draw_enemy(frame, e):
    info = ENEMIES[e['type']]
    cv2.circle(frame, (int(e['x']), int(e['y'])), info['size'], info['color'], -1)
    cv2.circle(frame, (int(e['x']), int(e['y'])), info['size'], WHITE, 2)
    if e['hp'] < info['hp']:
        ratio = e['hp'] / info['hp']
        cv2.rectangle(frame, (int(e['x']-20), int(e['y']-info['size']-10)), 
                     (int(e['x']+20), int(e['y']-info['size']-3)), (50, 0, 0), -1)
        cv2.rectangle(frame, (int(e['x']-18), int(e['y']-info['size']-8)), 
                     (int(e['x']-18+36*ratio), int(e['y']-info['size']-5)), RED, -1)

def draw_bullet(frame, b):
    cv2.circle(frame, (int(b['x']), int(b['y'])), 5, b['color'], -1)

def draw_particle(frame, p):
    if p['life'] > 0:
        alpha = p['life'] / 30
        c = tuple(int(c1 * alpha) for c1 in p['color'])
        cv2.circle(frame, (int(p['x']), int(p['y'])), p['size'], c, -1)

def draw_ui(frame, hp, score, level, gold, weapon, kills):
    cv2.rectangle(frame, (0, 0), (WIDTH, 80), BLACK, -1)
    cv2.putText(frame, f"Skor: {score}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2)
    cv2.putText(frame, f"Altin: {gold}", (180, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, GOLD, 2)
    cv2.putText(frame, f"Seviye: {level}", (350, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, GREEN, 2)
    wpn = WEAPONS[weapon]
    cv2.putText(frame, f"Silah: {weapon.upper()}", (500, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, wpn['color'], 2)
    ratio = hp / 100
    cv2.rectangle(frame, (750, 20), (1050, 50), (50, 50, 50), -1)
    hp_color = GREEN if ratio > 0.5 else RED
    cv2.rectangle(frame, (755, 25), (755 + 290*ratio, 45), hp_color, -1)
    cv2.putText(frame, f"{int(hp)}/100", (940, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 1)
    cv2.putText(frame, f"Oldurme: {kills}", (1100, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED, 1)

def draw_menu(frame):
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), (10, 5, 20), -1)
    cv2.putText(frame, "Z-HUNTER", (WIDTH//2-150, 150), cv2.FONT_HERSHEY_SIMPLEX, 2.5, CYAN, 5)
    cv2.putText(frame, "GOLGE AVCISI", (WIDTH//2-130, 200), cv2.FONT_HERSHEY_SIMPLEX, 1.5, MAGENTA, 3)
    cv2.putText(frame, f"Altin: {gold}", (WIDTH//2-60, 260), cv2.FONT_HERSHEY_SIMPLEX, 1, GOLD, 2)
    cv2.putText(frame, "WASD: Hareket | SPACE: Ates | 1-3: Silah", (WIDTH//2-280, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2)
    cv2.putText(frame, "Baslamak icin ENTER", (WIDTH//2-180, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, YELLOW, 2)

def draw_game_over(frame, score, gold, kills):
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), BLACK, -1)
    cv2.putText(frame, "OLUM", (WIDTH//2-80, HEIGHT//2-50), cv2.FONT_HERSHEY_SIMPLEX, 3, RED, 5)
    cv2.putText(frame, f"Skor: {score}", (WIDTH//2-80, HEIGHT//2+20), cv2.FONT_HERSHEY_SIMPLEX, 1.5, WHITE, 3)
    cv2.putText(frame, f"Altin: +{gold}", (WIDTH//2-100, HEIGHT//2+70), cv2.FONT_HERSHEY_SIMPLEX, 1.2, GOLD, 2)

def main():
    global player_x, player_y, player_hp, player_weapon, player_direction, last_shot
    global score, level, gold, kills, enemies, bullets, particles, spawn_timer, game_started, game_over
    
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
                score = 0
                level = 1
                kills = 0
                enemies = []
                bullets = []
                particles = []
                game_over = False
                game_started = True
        
        if not game_started:
            if key == 13:
                game_started = True
            draw_menu(frame)
            cv2.imshow("Z-HUNTER CV", frame)
            continue
        
        if game_over:
            draw_game_over(frame, score, gold, kills)
            cv2.imshow("Z-HUNTER CV", frame)
            continue
        
        if key == ord('1'): player_weapon = 'pistol'
        if key == ord('2'): player_weapon = 'laser'
        if key == ord('3'): player_weapon = 'shotgun'
        
        dx, dy = 0, 0
        if key == ord('w'): dy = -1
        if key == ord('s'): dy = 1
        if key == ord('a'): dx = -1
        if key == ord('d'): dx = 1
        
        if dx != 0 or dy != 0:
            player_direction = math.atan2(dy, dx)
        
        player_x = max(30, min(WIDTH-30, player_x + dx * 6))
        player_y = max(110, min(HEIGHT-30, player_y + dy * 6))
        
        now = time.time()
        wpn = WEAPONS[player_weapon]
        if key == 32 and now - last_shot > wpn['rate']:
            last_shot = now
            
            if player_weapon == 'shotgun':
                for i in range(5):
                    angle = player_direction + random.uniform(-0.3, 0.3)
                    bullets.append({'x': player_x, 'y': player_y,
                                 'dx': math.cos(angle) * wpn['speed'],
                                 'dy': math.sin(angle) * wpn['speed'],
                                 'damage': wpn['damage'], 'color': wpn['color']})
            else:
                bullets.append({'x': player_x, 'y': player_y,
                             'dx': math.cos(player_direction) * wpn['speed'],
                             'dy': math.sin(player_direction) * wpn['speed'],
                             'damage': wpn['damage'], 'color': wpn['color']})
        
        spawn_timer += 1
        if spawn_timer > 50:
            spawn_timer = 0
            max_enemies = 3 + level * 2
            if len(enemies) < max_enemies:
                if level % 5 == 0 and len(enemies) == 0:
                    enemies.append({'type': 'boss', 'x': WIDTH-100, 'y': 200, 'hp': 50})
                else:
                    etype = random.choices(['normal', 'fast', 'tank'], [50, 30, 20])[0]
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
            if dist < info['size'] + 25:
                player_hp -= 0.3
                for _ in range(2):
                    particles.append({'x': player_x, 'y': player_y, 'vx': random.uniform(-2, 2),
                                  'vy': random.uniform(-2, 2), 'color': RED, 'life': 20, 'size': 3})
        
        for b in bullets[:]:
            b['x'] += b['dx']
            b['y'] += b['dy']
            if b['x'] < 0 or b['x'] > WIDTH or b['y'] < 80 or b['y'] > HEIGHT:
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
                kills += 1
                for _ in range(10):
                    particles.append({'x': e['x'], 'y': e['y'], 'vx': random.uniform(-3, 3),
                                  'vy': random.uniform(-3, 3), 'color': info['color'], 'life': 25, 'size': 5})
                if e['type'] == 'boss':
                    score += 1000
                    level += 1
        
        for p in particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= 1
            if p['life'] <= 0:
                particles.remove(p)
        
        if player_hp <= 0:
            game_over = True
            save_game()
        
        draw_background(frame, current_map)
        for p in particles: draw_particle(frame, p)
        for e in enemies: draw_enemy(frame, e)
        for b in bullets: draw_bullet(frame, b)
        draw_player(frame, player_x, player_y, player_direction)
        draw_ui(frame, player_hp, score, level, gold, player_weapon, kills)
        
        cv2.imshow("Z-HUNTER CV", frame)
    
    if cap:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
