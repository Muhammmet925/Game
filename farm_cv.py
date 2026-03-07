"""
🌾 SUPER ÇİFTLİK - OpenCV Versiyonu
Görüntü işlemeli çiftlik oyunu
"""

import cv2
import numpy as np
import random
import time
import json

# Oyun değişkenleri
WIDTH, HEIGHT = 1280, 720
GRID_SIZE = 10
CELL_SIZE = WIDTH // GRID_SIZE

# Renkler (BGR)
COLORS = {
    'brown': (19, 69, 139),
    'yellow': (0, 215, 255),
    'red': (60, 20, 220),
    'green': (34, 139, 34),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'blue': (255, 191, 0),
    'gold': (0, 223, 255),
    'grass': (50, 205, 50),
    'wet_soil': (10, 40, 80),
    'orange': (0, 165, 255),
    'purple': (128, 0, 128),
}

# Oyun verileri
gold = 100
xp = 0
level = 1
inventory = {'corn': 5, 'tomato': 3, 'wheat': 2}
tools = ['hoe', 'water', 'corn', 'tomato', 'wheat']
current_tool = 'corn'

# Tarla sistemi
grid = []
for row in range(GRID_SIZE):
    grid_row = []
    for col in range(GRID_SIZE):
        grid_row.append({
            'state': 'grass',
            'watered': False,
            'plant_time': 0,
            'crop_type': None,
            'growth': 0
        })
    grid.append(grid_row)

# Tohumlar
SEEDS = {
    'corn': {'name': 'Misir', 'cost': 5, 'color': COLORS['yellow'], 'grow_time': 8},
    'tomato': {'name': 'Domates', 'cost': 12, 'color': COLORS['red'], 'grow_time': 10},
    'wheat': {'name': 'Bugday', 'cost': 8, 'color': COLORS['orange'], 'grow_time': 12},
}

# Oyuncu
player_x, player_y = WIDTH // 2, HEIGHT // 2
player_radius = 20
player_speed = 5

# Kamera
cap = None
try:
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
except:
    pass

# Hareket algılama
last_frame = None
motion_center = None

def detect_motion(frame):
    """Hareket algılama"""
    global last_frame, motion_center
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    
    if last_frame is not None:
        frame_delta = cv2.absdiff(last_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 3000:
                x, y, w, h = cv2.boundingRect(largest)
                motion_center = (x + w//2, y + h//2)
                last_frame = gray
                return motion_center
    
    last_frame = gray
    return None

def draw_grid(frame):
    """Tarla çiz"""
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            cell = grid[row][col]
            
            # Renk belirle
            if cell['state'] == 'grass':
                color = COLORS['grass']
            elif cell['state'] == 'soil':
                color = COLORS['wet_soil'] if cell['watered'] else COLORS['brown']
            elif cell['state'] in ['growing', 'ready']:
                seed = SEEDS.get(cell['crop_type'])
                if cell['state'] == 'ready':
                    color = seed['color']
                else:
                    color = COLORS['brown']
            
            cv2.rectangle(frame, (x, y), (x + CELL_SIZE, y + CELL_SIZE), color, -1)
            cv2.rectangle(frame, (x, y), (x + CELL_SIZE, y + CELL_SIZE), (50, 50, 50), 1)
            
            # Büyüme çubuğu
            if cell['state'] == 'growing' and cell['growth'] > 0:
                bar_width = int((CELL_SIZE - 10) * cell['growth'])
                cv2.rectangle(frame, (x + 5, y + CELL_SIZE - 8), (x + 5 + bar_width, y + CELL_SIZE - 3), COLORS['green'], -1)

def draw_player(frame, x, y):
    """Oyuncu çiz"""
    cv2.circle(frame, (x, y), player_radius, COLORS['blue'], -1)
    cv2.circle(frame, (x, y), player_radius, COLORS['white'], 3)

def draw_ui(frame):
    """UI çiz"""
    # Alt bar
    cv2.rectangle(frame, (0, HEIGHT - 80), (WIDTH, HEIGHT), COLORS['black'], -1)
    
    # Para ve XP
    info = f"Altin: {gold} | XP: {xp} | Seviye: {level}"
    cv2.putText(frame, info, (20, HEIGHT - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['gold'], 2)
    
    # Envanter
    inv_text = " | ".join([f"{k}: {v}" for k, v in inventory.items() if v > 0])
    cv2.putText(frame, inv_text, (20, HEIGHT - 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['white'], 1)
    
    # Alet seçimi
    tool_names = {'hoe': 'Capa', 'water': 'Sulama', 'corn': 'Misir', 'tomato': 'Domates', 'wheat': 'Bugday'}
    for i, tool in enumerate(tools):
        x = 600 + i * 120
        color = COLORS['green'] if current_tool == tool else COLORS['gray']
        cv2.rectangle(frame, (x, HEIGHT - 75), (x + 100, HEIGHT - 30), color, -1)
        cv2.putText(frame, f"{i+1}:{tool_names[tool]}", (x + 10, HEIGHT - 50), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, COLORS['white'], 1)

def draw_menu(frame):
    """Menü ekranı"""
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), COLORS['black'], -1)
    
    # Başlık
    cv2.putText(frame, "SUPER CIFTLIK", (WIDTH // 2 - 200, 200), 
               cv2.FONT_HERSHEY_SIMPLEX, 2.5, COLORS['green'], 5)
    cv2.putText(frame, "OpenCV Versiyonu", (WIDTH // 2 - 150, 260), 
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS['blue'], 3)
    
    # Talimatlar
    cv2.putText(frame, "WASD: Hareket | 1-5: Alet Sec | TIKLA: Etkilesim", (WIDTH // 2 - 300, 400), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['white'], 2)
    
    cv2.putText(frame, "ESC: Cikis", (WIDTH // 2 - 80, 500), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['gray'], 2)
    
    # Kamera durumu
    if cap is not None and cap.isOpened():
        cv2.putText(frame, "Hareket Kontrolu: AKTIF", (WIDTH // 2 - 140, 600), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['green'], 2)
    else:
        cv2.putText(frame, "Kamera: YOK", (WIDTH // 2 - 80, 600), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['red'], 2)
    
    cv2.putText(frame, "Baslamak icin ENTER tusuna basin", (WIDTH // 2 - 220, 660), 
               cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['yellow'], 2)

def handle_click(event, x, y, flags, param):
    """Tıklama işlemleri"""
    global current_tool
    
    if event == cv2.EVENT_LBUTTONDOWN:
        if y < HEIGHT - 80:
            col = x // CELL_SIZE
            row = y // CELL_SIZE
            
            if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                cell = grid[row][col]
                
                # Mesafe kontrolü
                dist = ((player_x - x)**2 + (player_y - y)**2)**0.5
                if dist > 80:
                    return
                
                # Çapa
                if current_tool == 'hoe':
                    if cell['state'] == 'grass':
                        cell['state'] = 'soil'
                
                # Sulama
                elif current_tool == 'water':
                    if cell['state'] in ['soil', 'growing', 'ready']:
                        cell['watered'] = True
                
                # Ekim
                elif current_tool in SEEDS:
                    if cell['state'] == 'soil' and cell['crop_type'] is None:
                        cost = SEEDS[current_tool]['cost']
                        if gold >= cost:
                            gold -= cost
                            cell['state'] = 'growing'
                            cell['crop_type'] = current_tool
                            cell['plant_time'] = time.time()
                            cell['growth'] = 0
                
                # Hasat
                elif cell['state'] == 'ready':
                    crop = cell['crop_type']
                    inventory[crop] = inventory.get(crop, 0) + 1
                    gold += SEEDS[crop]['cost']
                    xp += 5
                    
                    cell['state'] = 'soil'
                    cell['watered'] = False
                    cell['crop_type'] = None
                    cell['growth'] = 0

# Ana döngü
def main():
    global player_x, player_y, current_tool, gold, xp, level
    
    game_started = False
    running = True
    
    cv2.namedWindow("Super Ciftlik")
    cv2.setMouseCallback("Super Ciftlik", handle_click)
    
    while running:
        # Kameradan frame al
        if cap is not None and cap.isOpened():
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (WIDTH, HEIGHT))
            else:
                frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        else:
            frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        
        # Klavye
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            running = False
        
        if key == 13 and not game_started:  # ENTER
            game_started = True
        
        # Alet seçimi
        if key == ord('1'): current_tool = 'hoe'
        if key == ord('2'): current_tool = 'water'
        if key == ord('3'): current_tool = 'corn'
        if key == ord('4'): current_tool = 'tomato'
        if key == ord('5'): current_tool = 'wheat'
        
        if not game_started:
            draw_menu(frame)
            cv2.imshow("Super Ciftlik", frame)
            continue
        
        # Hareket kontrolü (WASD)
        if key == ord('w') and player_y > player_radius:
            player_y -= player_speed
        if key == ord('s') and player_y < HEIGHT - 100:
            player_y += player_speed
        if key == ord('a') and player_x > player_radius:
            player_x -= player_speed
        if key == ord('d') and player_x < WIDTH - player_radius:
            player_x += player_speed
        
        # Kamera hareket kontrolü
        if cap is not None and cap.isOpened():
            ret, temp_frame = cap.read()
            if ret:
                temp_frame = cv2.flip(temp_frame, 1)
                motion = detect_motion(temp_frame)
                if motion:
                    mx, my = motion
                    # Hareket yönü
                    if mx < WIDTH // 3:
                        player_x = max(player_radius, player_x - 3)
                    elif mx > 2 * WIDTH // 3:
                        player_x = min(WIDTH - player_radius, player_x + 3)
                    if my < HEIGHT // 3:
                        player_y = max(player_radius, player_y - 3)
                    elif my > 2 * HEIGHT // 3:
                        player_y = min(HEIGHT - 100, player_y + 3)
        
        # Büyüme güncellemesi
        current_time = time.time()
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                cell = grid[row][col]
                
                if cell['state'] == 'growing' and cell['watered']:
                    seed = SEEDS[cell['crop_type']]
                    elapsed = current_time - cell['plant_time']
                    cell['growth'] = min(1.0, elapsed / seed['grow_time'])
                    
                    if cell['growth'] >= 1.0:
                        cell['state'] = 'ready'
        
        # Seviye kontrolü
        if xp >= level * 50:
            level += 1
            xp = 0
        
        # Çizim
        draw_grid(frame)
        draw_player(frame, player_x, player_y)
        
        # Fare vurgusu (ileride eklenebilir)
        
        draw_ui(frame)
        
        cv2.imshow("Super Ciftlik", frame)
    
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
