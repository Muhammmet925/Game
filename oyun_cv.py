"""
🎮 Z-HUNTER - OpenCV Versiyonu
Gölge Avcısı - Görüntü işlemeli arcade oyunu
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

# Ekran
WIDTH, HEIGHT = 1280, 720

# Renkler
COLORS = {
    'cyan': (255, 255, 0),
    'magenta': (255, 0, 255),
    'yellow': (0, 255, 255),
    'green': (0, 255, 0),
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'purple': (128, 0, 128),
    'gold': (0, 215, 255),
}

# Haritalar
MAPS = {
    'dojo': {'name': 'DOJO', 'bg': (20, 20, 30), 'accent': (255, 100, 0)},
    'neon': {'name': 'NEON', 'bg': (10, 0, 20), 'accent': (0, 255, 255)},
    'lava': {'name': 'LAVA', 'bg': (40, 5, 0), 'accent': (255, 50, 0)},
    'space': {'name': 'UZAY', 'bg': (5, 0, 10), 'accent': (100, 100, 255)},
}

# Karakterler
CHARACTERS = {
    '1': {'name': 'Golge Savasci', 'hp': 100, 'speed': 6, 'damage': 1, 'weapon': 'pistol', 'color': COLORS['cyan']},
    '2': {'name': 'Hizli Casus', 'hp': 80, 'speed': 10, 'damage': 0.5, 'weapon': 'laser', 'color': COLORS['yellow']},
    '3': {'name': 'Agir Tank', 'hp': 150, 'speed': 3, 'damage': 2, 'weapon': 'shotgun', 'color': COLORS['red']},
    '4': {'name': 'Neon Ninja', 'hp': 90, 'speed': 8, 'damage': 1.5, 'weapon': 'dual', 'color': COLORS['magenta']},
    '5': {'name': 'Buz Savascisi', 'hp': 95, 'speed': 7, 'damage': 1.2, 'weapon': 'ice', 'color': COLORS['blue']},
    '6': {'name': 'Ates Seytani', 'hp': 85, 'speed': 6, 'damage': 1.8, 'weapon': 'fire', 'color': (0, 100, 255)},
    '7': {'name': 'Elektro Savasci', 'hp': 75, 'speed': 9, 'damage': 1.3, 'weapon': 'electric', 'color': COLORS['gold']},
}

# Silahlar
WEAPONS = {
    'pistol': {'damage': 1, 'speed': 15, 'rate': 0.3, 'color': COLORS['cyan'], 'size': 5},
    'laser': {'damage': 0.5, 'speed': 25, 'rate': 0.15, 'color': COLORS['magenta'], 'size': 3},
    'shotgun': {'damage': 3, 'speed': 10, 'rate': 0.8, 'color': COLORS['yellow'], 'size': 12},
    'dual': {'damage': 1, 'speed': 12, 'rate': 0.2, 'color': COLORS['green'], 'size': 4},
    'ice': {'damage': 1.2, 'speed': 14, 'rate': 0.25, 'color': COLORS['blue'], 'size': 6},
    'fire': {'damage': 2, 'speed': 12, 'rate': 0.35, 'color': (0, 100, 255), 'size': 8},
    'electric': {'damage': 1.5, 'speed': 20, 'rate': 0.2, 'color': COLORS['gold'], 'size': 4},
}

# Düşmanlar
ENEMIES = {
    'normal': {'hp': 1, 'speed': 2.5, 'color': COLORS['red'], 'size': 20, 'score': 10},
    'fast': {'hp': 0.5, 'speed': 5, 'color': COLORS['yellow'], 'size': 15, 'score': 20},
    'tank': {'hp': 5, 'speed': 1.5, 'color': COLORS['green'], 'size': 35, 'score': 50},
    'boss': {'hp': 50, 'speed': 1, 'color': COLORS['red'], 'size': 60, 'score': 500},
    'fire': {'hp': 2, 'speed': 2, 'color': (0, 100, 255), 'size': 25, 'score': 30},
    'electric': {'hp': 1.5, 'speed': 3, 'color': COLORS['gold'], 'size': 22, 'score': 25},
}

# Kayıt sistemi
def save_game(data, filename='z_hunter_save.json'):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f)
        return True
    except:
        return False

def load_game(filename='z_hunter_save.json'):
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except:
        return None

# Oyun durumu
class GameState:
    def __init__(self):
        self.score = 0
        self.level = 1
        self.gold = 0
        self.player_hp = 100
        self.max_hp = 100
        self.kills = 0
        self.is_game_over = False
        self.paused = False
        
        # Kayıtlı veri
        save_data = load_game()
        if save_data:
            self.gold = save_data.get('gold', 0)
            self.unlocked_chars = save_data.get('chars', ['1'])
            self.unlocked_weapons = save_data.get('weapons', ['pistol'])
        else:
            self.gold = 0
            self.unlocked_chars = ['1']
            self.unlocked_weapons = ['pistol']
        
        self.selected_char = '1'
        self.selected_map = 'dojo'
        self.selected_weapon = 'pistol'

# Oyuncu
class Player:
    def __init__(self, char_id='1'):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.char_id = char_id
        info = CHARACTERS[char_id]
        self.hp = info['hp']
        self.max_hp = info['hp']
        self.speed = info['speed']
        self.damage = info['damage']
        self.weapon = info['weapon']
        self.color = info['color']
        self.radius = 25
        self.direction = 0
        self.last_shot = 0
    
    def move(self, dx, dy):
        self.x = max(self.radius, min(WIDTH - self.radius, self.x + dx * self.speed))
        self.y = max(80, min(HEIGHT - self.radius, self.y + dy * self.speed))

# Düşman
class Enemy:
    def __init__(self, enemy_type='normal', level=1):
        self.type = enemy_type
        info = ENEMIES[enemy_type]
        
        side = random.choice(['T', 'B', 'L', 'R'])
        if side == 'T':
            self.x = random.randint(50, WIDTH - 50)
            self.y = random.randint(90, 150)
        elif side == 'B':
            self.x = random.randint(50, WIDTH - 50)
            self.y = random.randint(HEIGHT - 150, HEIGHT - 50)
        elif side == 'L':
            self.x = random.randint(50, 150)
            self.y = random.randint(100, HEIGHT - 50)
        else:
            self.x = random.randint(WIDTH - 150, WIDTH - 50)
            self.y = random.randint(100, HEIGHT - 50)
        
        self.hp = info['hp'] * (1 + (level - 1) * 0.3)
        self.max_hp = self.hp
        self.speed = info['speed']
        self.color = info['color']
        self.size = info['size']
        self.score = info['score']
        self.slowed = False
    
    def move_toward(self, tx, ty):
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            sp = self.speed * 0.3 if self.slowed else self.speed
            self.x += (dx / dist) * sp
            self.y += (dy / dist) * sp

# Mermi
class Bullet:
    def __init__(self, x, y, dx, dy, damage, color, size, speed):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.damage = damage
        self.color = color
        self.size = size
        self.speed = speed
    
    def update(self):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        return 0 < self.x < WIDTH and 0 < self.y < HEIGHT

# Efekt
class Particle:
    def __init__(self, x, y, color):
        self.x = x + random.uniform(-10, 10)
        self.y = y + random.uniform(-10, 10)
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.color = color
        self.life = random.randint(10, 30)
        self.size = random.randint(2, 5)
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        return self.life > 0

# Global değişkenler
player = Player()
game_state = GameState()
enemies = []
bullets = []
particles = []
spawn_timer = 0
menu_page = 'char'  # char, shop, map
menu_selection = 0

def draw_background(frame, map_name):
    """Arka plan çiz"""
    map_info = MAPS[map_name]
    bg = map_info['bg']
    
    cv2.rectangle(frame, (0, 80), (WIDTH, HEIGHT), bg, -1)
    
    # Izgara
    for i in range(0, WIDTH, 40):
        cv2.line(frame, (i, 80), (i, HEIGHT), (bg[0]+10, bg[1]+10, bg[2]+10), 1)
    for i in range(80, HEIGHT, 40):
        cv2.line(frame, (0, i), (WIDTH, i), (bg[0]+10, bg[1]+10, bg[2]+10), 1)
    
    # Çerçeve
    cv2.rectangle(frame, (0, 80), (WIDTH, HEIGHT), map_info['accent'], 4)

def draw_player(frame, p):
    """Oyuncu çiz"""
    # Gövde
    cv2.circle(frame, (int(p.x), int(p.y)), p.radius, p.color, -1)
    cv2.circle(frame, (int(p.x), int(p.y)), p.radius, COLORS['white'], 3)
    
    # Yön
    end_x = int(p.x + math.cos(p.direction) * 35)
    end_y = int(p.y + math.sin(p.direction) * 35)
    cv2.line(frame, (int(p.x), int(p.y)), (end_x, end_y), COLORS['white'], 4)

def draw_enemy(frame, e):
    """Düşman çiz"""
    cv2.circle(frame, (int(e.x), int(e.y)), e.size, e.color, -1)
    cv2.circle(frame, (int(e.x), int(e.y)), e.size, COLORS['white'], 2)
    
    # HP
    if e.hp < e.max_hp:
        ratio = e.hp / e.max_hp
        cv2.rectangle(frame, (int(e.x - 20), int(e.y - e.size - 8)), 
                     (int(e.x + 20), int(e.y - e.size)), (50, 0, 0), -1)
        cv2.rectangle(frame, (int(e.x - 18), int(e.y - e.size - 6)), 
                     (int(e.x - 18 + 36 * ratio), int(e.y - e.size - 2)), (0, 0, 255), -1)

def draw_bullet(frame, b):
    """Mermi çiz"""
    cv2.circle(frame, (int(b.x), int(b.y)), b.size, b.color, -1)

def draw_particle(frame, p):
    """Parçacık çiz"""
    if p.life > 0:
        alpha = p.life / 30
        color = tuple(int(c * alpha) for c in p.color)
        cv2.circle(frame, (int(p.x), int(p.y)), p.size, color, -1)

def draw_ui(frame, state, player):
    """UI çiz"""
    cv2.rectangle(frame, (0, 0), (WIDTH, 80), (0, 0, 0), -1)
    
    # Skor
    cv2.putText(frame, f"Skor: {state.score}", (20, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['white'], 2)
    
    # Altın
    cv2.putText(frame, f"Altin: {state.gold}", (180, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['gold'], 2)
    
    # Seviye
    cv2.putText(frame, f"Seviye: {state.level}", (350, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['green'], 2)
    
    # Silah
    weapon = WEAPONS[player.weapon]
    cv2.putText(frame, f"Silah: {player.weapon.upper()}", (500, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, weapon['color'], 2)
    
    # HP
    ratio = state.player_hp / state.max_hp
    cv2.rectangle(frame, (750, 20), (1050, 50), (50, 50, 50), -1)
    hp_color = COLORS['green'] if ratio > 0.5 else COLORS['red']
    cv2.rectangle(frame, (755, 25), (755 + 290 * ratio, 45), hp_color, -1)
    cv2.putText(frame, f"{int(state.player_hp)}/{state.max_hp}", (940, 40), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['white'], 1)
    
    # Düşman sayısı
    cv2.putText(frame, f"Dusman: {len(enemies)}", (1100, 35), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['red'], 1)

def draw_menu(frame, page, selection, state):
    """Menü çiz"""
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), (10, 5, 20), -1)
    
    # Başlık
    cv2.putText(frame, "Z-HUNTER", (WIDTH // 2 - 150, 120), 
               cv2.FONT_HERSHEY_SIMPLEX, 2.5, COLORS['cyan'], 5)
    cv2.putText(frame, "GOLGE AVCISI", (WIDTH // 2 - 130, 170), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLORS['magenta'], 3)
    
    # Altın
    cv2.putText(frame, f"Altin: {state.gold}", (WIDTH // 2 - 60, 210), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['gold'], 2)
    
    # Sayfalar
    pages = ['KARAKTER', 'SILAH', 'HARITA']
    page_idx = {'char': 0, 'weapon': 1, 'map': 2}[page]
    
    for i, p in enumerate(pages):
        x = 200 + i * 300
        color = COLORS['green'] if i == page_idx else COLORS['white']
        cv2.rectangle(frame, (x, 240), (x + 200, 280), color, -1)
        cv2.putText(frame, p, (x + 30, 268), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2)
    
    # İçerik
    if page == 'char':
        chars = list(CHARACTERS.items())
        for i, (key, char) in enumerate(chars):
            x = 100 + (i % 4) * 280
            y = 320 + (i // 4) * 100
            
            unlocked = key in state.unlocked_chars
            color = char['color'] if unlocked else (80, 80, 80)
            border = 3 if i == selection else 1
            border_color = COLORS['green'] if i == selection else COLORS['white']
            
            cv2.rectangle(frame, (x, y), (x + 250, y + 80), color, -1)
            cv2.rectangle(frame, (x, y), (x + 250, y + 80), border_color, border)
            
            cv2.putText(frame, char['name'], (x + 10, y + 30), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['white'], 2)
            cv2.putText(frame, f"HP:{char['hp']} Hiz:{char['speed']}", (x + 10, y + 55), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['white'], 1)
            
            if not unlocked:
                cv2.putText(frame, f"Fiyat: {i * 250}", (x + 130, y + 55), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['gold'], 1)
    
    elif page == 'weapon':
        weapons = list(WEAPONS.items())
        for i, (key, weapon) in enumerate(weapons):
            x = 100 + (i % 4) * 300
            y = 320 + (i // 4) * 80
            
            unlocked = key in state.unlocked_weapons
            color = weapon['color'] if unlocked else (80, 80, 80)
            border = 3 if i == selection else 1
            
            cv2.rectangle(frame, (x, y), (x + 270, y + 60), color, -1)
            cv2.rectangle(frame, (x, y), (x + 270, y + 60), border_color if i == selection else COLORS['white'], border)
            
            cv2.putText(frame, key.upper(), (x + 10, y + 35), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['white'], 2)
    
    elif page == 'map':
        maps = list(MAPS.items())
        for i, (key, m) in enumerate(maps):
            x = 150 + i * 300
            y = 320
            
            border = 3 if i == selection else 1
            color = m['accent']
            
            cv2.rectangle(frame, (x, y), (x + 250, y + 150), color, -1)
            cv2.rectangle(frame, (x, y), (x + 250, y + 150), COLORS['white'], border)
            
            cv2.putText(frame, m['name'], (x + 50, y + 80), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['white'], 2)
    
    # Alt
    cv2.putText(frame, "ENTER: Sec/Oyna | ESC: Cikus | ←→: Sayfa", (WIDTH // 2 - 250, 680), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['white'], 2)

def draw_game_over(frame, state):
    """Oyun bitişi"""
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), (0, 0, 0), -1)
    
    cv2.putText(frame, "ELENDIN", (WIDTH // 2 - 120, HEIGHT // 2 - 50), 
               cv2.FONT_HERSHEY_SIMPLEX, 3, COLORS['red'], 5)
    
    cv2.putText(frame, f"Skor: {state.score}", (WIDTH // 2 - 80, HEIGHT // 2 + 20), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLORS['white'], 3)
    
    cv2.putText(frame, f"Altin: +{state.gold}", (WIDTH // 2 - 90, HEIGHT // 2 + 70), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS['gold'], 2)
    
    cv2.putText(frame, "Yeniden icin R tusuna basin", (WIDTH // 2 - 180, HEIGHT // 2 + 150), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['gray'], 2)

# Ana döngü
def main():
    global player, game_state, enemies, bullets, particles, spawn_timer, menu_page, menu_selection
    
    game_started = False
    running = True
    mouse_x, mouse_y = WIDTH // 2, HEIGHT // 2
    
    while running:
        # Frame
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
                game_state.paused = not game_state.paused
            else:
                running = False
        
        if key == ord('r') or key == ord('R'):
            if game_state.is_game_over:
                player = Player(game_state.selected_char)
                game_state.score = 0
                game_state.level = 1
                game_state.player_hp = player.max_hp
                game_state.max_hp = player.max_hp
                enemies = []
                bullets = []
                particles = []
                game_state.is_game_over = False
                game_started = True
        
        if not game_started:
            # Menü navigasyonu
            if key == ord('a') or key == ord('A'):
                menu_page = {'char': 'map', 'weapon': 'char', 'map': 'weapon'}.get(menu_page, 'char')
                menu_selection = 0
            if key == ord('d') or key == ord('D'):
                menu_page = {'char': 'weapon', 'weapon': 'map', 'map': 'char'}.get(menu_page, 'weapon')
                menu_selection = 0
            if key == ord('w') or key == ord('W'):
                menu_selection = max(0, menu_selection - 1)
            if key == ord('s') or key == ord('S'):
                menu_selection += 1
            
            if key == 13:  # ENTER
                if menu_page == 'char':
                    chars = list(CHARACTERS.keys())
                    if menu_selection < len(chars):
                        char_id = chars[menu_selection]
                        if char_id in game_state.unlocked_chars:
                            game_state.selected_char = char_id
                            player = Player(char_id)
                            game_state.player_hp = player.max_hp
                            game_state.max_hp = player.max_hp
                            game_started = True
                        else:
                            price = menu_selection * 250
                            if game_state.gold >= price:
                                game_state.gold -= price
                                game_state.unlocked_chars.append(char_id)
                                save_game({'gold': game_state.gold, 'chars': game_state.unlocked_chars})
                
                elif menu_page == 'weapon':
                    weapons = list(WEAPONS.keys())
                    if menu_selection < len(weapons):
                        wpn = weapons[menu_selection]
                        if wpn in game_state.unlocked_weapons:
                            game_state.selected_weapon = wpn
                            player.weapon = wpn
                            game_started = True
                
                elif menu_page == 'map':
                    maps = list(MAPS.keys())
                    if menu_selection < len(maps):
                        game_state.selected_map = maps[menu_selection]
                        game_started = True
            
            draw_menu(frame, menu_page, menu_selection, game_state)
            cv2.imshow("Z-HUNTER - OpenCV", frame)
            continue
        
        if game_state.is_game_over:
            draw_game_over(frame, game_state)
            cv2.imshow("Z-HUNTER - OpenCV", frame)
            continue
        
        if game_state.paused:
            draw_background(frame, game_state.selected_map)
            for e in enemies:
                draw_enemy(frame, e)
            for b in bullets:
                draw_bullet(frame, b)
            for p in particles:
                draw_particle(frame, p)
            draw_player(frame, player)
            draw_ui(frame, game_state, player)
            
            cv2.putText(frame, "PAUSED", (WIDTH // 2 - 60, HEIGHT // 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 2, COLORS['yellow'], 4)
            cv2.imshow("Z-HUNTER - OpenCV", frame)
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
        
        # Ateş
        if key == 32:  # SPACE
            now = time.time()
            weapon = WEAPONS[player.weapon]
            if now - player.last_shot > weapon['rate']:
                player.last_shot = now
                
                mx, my = mouse_x, mouse_y
                dir_x = mx - player.x
                dir_y = my - player.y
                dist = math.hypot(dir_x, dir_y)
                
                if dist > 0:
                    bullets.append(Bullet(
                        player.x, player.y,
                        dir_x / dist, dir_y / dist,
                        player.damage * weapon['damage'],
                        weapon['color'], weapon['size'], weapon['speed']
                    ))
        
        # Spawn
        spawn_timer += 1
        if spawn_timer > 50:
            spawn_timer = 0
            max_enemies = 3 + game_state.level * 2
            if len(enemies) < max_enemies:
                if game_state.level % 5 == 0 and len(enemies) == 0:
                    enemies.append(Enemy('boss', game_state.level))
                else:
                    etype = random.choices(['normal', 'fast', 'tank', 'fire', 'electric'],
                                          [40, 25, 15, 12, 8])[0]
                    enemies.append(Enemy(etype, game_state.level))
        
        # Düşman hareketi
        for e in enemies:
            e.move_toward(player.x, player.y)
            if math.hypot(e.x - player.x, e.y - player.y) < e.size + player.radius:
                game_state.player_hp -= 0.5
                for _ in range(3):
                    particles.append(Particle(player.x, player.y, COLORS['red']))
        
        # Mermi güncelleme
        for b in bullets[:]:
            if not b.update():
                bullets.remove(b)
                continue
            
            for e in enemies[:]:
                if math.hypot(b.x - e.x, b.y - e.y) < e.size + b.size:
                    e.hp -= b.damage
                    bullets.remove(b)
                    
                    for _ in range(3):
                        particles.append(Particle(e.x, e.y, b.color))
                    break
        
        # Düşman ölümü
        for e in enemies[:]:
            if e.hp <= 0:
                enemies.remove(e)
                game_state.score += e.score
                game_state.gold += e.score // 2
                game_state.kills += 1
                
                for _ in range(10):
                    particles.append(Particle(e.x, e.y, e.color))
                
                if e.type == 'boss':
                    game_state.score += 1000
                    game_state.level += 1
        
        # Parçacık güncelleme
        for p in particles[:]:
            if not p.update():
                particles.remove(p)
        
        # Oyun bitti
        if game_state.player_hp <= 0:
            game_state.is_game_over = True
            save_game({'gold': game_state.gold, 'chars': game_state.unlocked_chars, 'weapons': game_state.unlocked_weapons})
        
        # Çizim
        draw_background(frame, game_state.selected_map)
        
        for p in particles:
            draw_particle(frame, p)
        
        for e in enemies:
            draw_enemy(frame, e)
        
        for b in bullets:
            draw_bullet(frame, b)
        
        draw_player(frame, player)
        draw_ui(frame, game_state, player)
        
        cv2.imshow("Z-HUNTER - OpenCV", frame)
    
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
