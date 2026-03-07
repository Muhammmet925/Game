"""FARM CV - OpenCV Çiftlik Oyunu"""

import cv2
import numpy as np
import random
import time
import math

# OpenCV başlat
cap = cv2.VideoCapture(0) if cv2.VideoCapture(0).isOpened() else None
WIDTH, HEIGHT = 1280, 720

# Renkler (BGR)
BROWN = (19, 69, 139)
YELLOW = (0, 215, 255)
RED = (60, 20, 220)
GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (255, 191, 0)
GOLD = (0, 223, 255)
GRASS = (50, 205, 50)

# Oyun değişkenleri
GRID_SIZE = 8
CELL_SIZE = WIDTH // GRID_SIZE

# Tarla (grass=toprak, soil=ekili, growing=büyüyor, ready=hasat)
grid = [[{'state': 'grass', 'crop': None, 'growth': 0, 'water': False} for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Tohumlar
SEEDS = {
    'corn': {'name': 'Mısır', 'color': YELLOW, 'cost': 5, 'grow_time': 8},
    'tomato': {'name': 'Domates', 'color': RED, 'cost': 10, 'grow_time': 10},
    'wheat': {'name': 'Buğday', 'color': GOLD, 'cost': 8, 'grow_time': 12},
}

# Oyuncu
player_x, player_y = WIDTH // 2, HEIGHT // 2
player_radius = 20

# Para ve envanter
gold = 100
xp = 0
level = 1
inventory = {'corn': 3, 'tomato': 2, 'wheat': 2}
current_tool = 'corn'  # corn, tomato, wheat, water, hoe

# Zaman
start_time = time.time()
last_growth_time = time.time()

def draw_grid(frame):
    """Tarla çiz"""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * CELL_SIZE
            y = row * CELL_SIZE + 80
            cell = grid[row][col]
            
            # Renk belirle
            if cell['state'] == 'grass':
                color = GRASS
            elif cell['state'] == 'soil':
                color = BROWN if not cell['water'] else BLUE
            elif cell['state'] == 'growing':
                color = BROWN
            elif cell['state'] == 'ready':
                color = SEEDS[cell['crop']]['color']
            
            cv2.rectangle(frame, (x, y), (x + CELL_SIZE, y + CELL_SIZE), color, -1)
            cv2.rectangle(frame, (x, y), (x + CELL_SIZE, y + CELL_SIZE), (50, 50, 50), 2)
            
            # Büyüme çubuğu
            if cell['state'] == 'growing' and cell['growth'] > 0:
                bar_width = int((CELL_SIZE - 20) * cell['growth'])
                cv2.rectangle(frame, (x + 10, y + CELL_SIZE - 15), (x + 10 + bar_width, y + CELL_SIZE - 8), GREEN, -1)

def draw_player(frame, x, y):
    """Oyuncu çiz"""
    cv2.circle(frame, (x, y), player_radius, BLUE, -1)
    cv2.circle(frame, (x, y), player_radius, WHITE, 3)

def draw_ui(frame):
    """UI çiz"""
    cv2.rectangle(frame, (0, 0), (WIDTH, 80), BLACK, -1)
    
    # Para ve XP
    info = f"Altın: {gold} | XP: {xp} | Seviye: {level}"
    cv2.putText(frame, info, (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, GOLD, 2)
    
    # Envanter
    inv_text = " | ".join([f"{k}: {v}" for k, v in inventory.items()])
    cv2.putText(frame, inv_text, (20, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)
    
    # Alet seçimi
    tools = [('1', 'Corn', SEEDS['corn']['color']), ('2', 'Tomato', SEEDS['tomato']['color']), 
             ('3', 'Wheat', SEEDS['wheat']['color']), ('4', 'Su', BLUE), ('5', 'Çapa', BROWN)]
    for i, (key, name, color) in enumerate(tools):
        x = 500 + i * 130
        is_selected = (current_tool == key.lower() or 
                     (key == '1' and current_tool == 'corn') or
                     (key == '2' and current_tool == 'tomato') or
                     (key == '3' and current_tool == 'wheat') or
                     (key == '4' and current_tool == 'water') or
                     (key == '5' and current_tool == 'hoe'))
        
        cv2.rectangle(frame, (x, 20), (x + 120, 60), color if is_selected else (80, 80, 80), -1)
        cv2.putText(frame, f"{key}:{name}", (x + 10, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.5, WHITE, 1)

def draw_menu(frame):
    """Menü ekranı"""
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), BLACK, -1)
    cv2.putText(frame, "SUPER ÇİFTLİK - OpenCV", (WIDTH//2-220, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, GREEN, 5)
    cv2.putText(frame, "WASD: Hareket | 1-5: Alet | TIKLA: Etkileşim", (WIDTH//2-280, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.7, WHITE, 2)
    cv2.putText(frame, "ENTER: Başla | ESC: Çıkış", (WIDTH//2-150, 420), cv2.FONT_HERSHEY_SIMPLEX, 0.8, GOLD, 2)
    cv2.putText(frame, "Başlamak için ENTER tuşuna basın", (WIDTH//2-220, 520), cv2.FONT_HERSHEY_SIMPLEX, 1, YELLOW, 2)

def handle_click(event, x, y, flags, param):
    """Tıklama işlemleri"""
    global current_tool, gold, xp, level, inventory, grid
    
    if y < 80 or y > HEIGHT:
        return
    
    col = x // CELL_SIZE
    row = (y - 80) // CELL_SIZE
    
    if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
        cell = grid[row][col]
        
        # Mesafe kontrolü
        cell_center_x = col * CELL_SIZE + CELL_SIZE // 2
        cell_center_y = row * CELL_SIZE + 80 + CELL_SIZE // 2
        dist = math.hypot(player_x - cell_center_x, player_y - cell_center_y)
        
        if dist > 100:
            return
        
        # Çapa (toprak aç)
        if current_tool == 'hoe' and cell['state'] == 'grass':
            cell['state'] = 'soil'
        
        # Su (sulama)
        elif current_tool == 'water' and cell['state'] in ['soil', 'growing']:
            cell['water'] = True
        
        # Ekim
        elif current_tool in SEEDS and cell['state'] == 'soil' and cell['crop'] is None:
            cost = SEEDS[current_tool]['cost']
            if gold >= cost:
                gold -= cost
                cell['state'] = 'growing'
                cell['crop'] = current_tool
                cell['growth'] = 0
        
        # Hasat
        elif cell['state'] == 'ready':
            crop = cell['crop']
            inventory[crop] = inventory.get(crop, 0) + 1
            gold += SEEDS[crop]['cost']
            xp += 5
            
            cell['state'] = 'soil'
            cell['crop'] = None
            cell['growth'] = 0
            cell['water'] = False

def main():
    global player_x, player_y, current_tool, gold, xp, level, grid, start_time, last_growth_time
    
    game_started = False
    running = True
    
    cv2.namedWindow("Farm CV")
    cv2.setMouseCallback("Farm CV", handle_click)
    
    while running:
        # Frame al
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
        
        if key == 27:  # ESC
            running = False
        
        if not game_started:
            if key == 13:  # ENTER
                game_started = True
                start_time = time.time()
                last_growth_time = time.time()
            
            draw_menu(frame)
            cv2.imshow("Farm CV", frame)
            continue
        
        # Alet seçimi
        if key == ord('1'): current_tool = 'corn'
        if key == ord('2'): current_tool = 'tomato'
        if key == ord('3'): current_tool = 'wheat'
        if key == ord('4'): current_tool = 'water'
        if key == ord('5'): current_tool = 'hoe'
        
        # Hareket
        if key == ord('w') and player_y > player_radius + 80:
            player_y -= 5
        if key == ord('s') and player_y < HEIGHT - player_radius:
            player_y += 5
        if key == ord('a') and player_x > player_radius:
            player_x -= 5
        if key == ord('d') and player_x < WIDTH - player_radius:
            player_x += 5
        
        # Büyüme güncellemesi
        current_time = time.time()
        if current_time - last_growth_time > 1:
            last_growth_time = current_time
            for row in range(GRID_SIZE):
                for col in range(GRID_SIZE):
                    cell = grid[row][col]
                    if cell['state'] == 'growing' and cell['water']:
                        seed = SEEDS[cell['crop']]
                        cell['growth'] += 1 / seed['grow_time']
                        if cell['growth'] >= 1.0:
                            cell['state'] = 'ready'
                            cell['growth'] = 1.0
        
        # Seviye kontrolü
        if xp >= level * 50:
            level += 1
            xp = 0
        
        # Çizim
        draw_grid(frame)
        draw_player(frame, player_x, player_y)
        draw_ui(frame)
        
        cv2.imshow("Farm CV", frame)
    
    if cap:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
