import pygame
import time
import random

# Pygame başlatma
pygame.init()

# Ekran Ayarları
SCREEN_WIDTH = 500
SCREEN_HEIGHT = 600  # Alt kısımda bilgi paneli için yer
GRID_SIZE = 10
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Çiftlik Yönetimi")

# Renkler
BROWN = (139, 69, 19)      # Toprak
YELLOW = (255, 215, 0)     # Mısır
RED = (220, 20, 60)        # Domates
GREEN = (34, 139, 34)      # Hasada Hazır
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 191, 255)       # Yağmur
GOLD_COLOR = (255, 223, 0)
GRASS_COLOR = (50, 205, 50) # Çimen
WET_SOIL_COLOR = (80, 40, 10) # Islak Toprak
PLAYER_COLOR = (0, 0, 255) # Oyuncu Karakteri
GRAY = (100, 100, 100)     # Fırın Rengi
ORANGE = (255, 165, 0)     # Ekmek Rengi

# Oyun Değişkenleri
grid = []  # Izgara verisi
gold = 100  # Başlangıç parası
xp = 0
font = pygame.font.SysFont("Arial", 20)
small_font = pygame.font.SysFont("Arial", 16)

# Envanter ve Durum
inventory = {'corn': 5, 'tomato': 5, 'bread': 0} # Başlangıçta biraz ürün var
selected_action = 'harvest' # harvest, corn, tomato

# Fırın Değişkenleri
bakery = {'state': 'idle', 'start_time': 0, 'duration': 5, 'rect': pygame.Rect(380, 50, 100, 80)}

# Tohum Verileri
SEEDS = {
    'corn': {'name': 'Mısır', 'cost': 2, 'sell': 5, 'color': YELLOW, 'grow_time': 3},
    'tomato': {'name': 'Domates', 'cost': 5, 'sell': 10, 'color': RED, 'grow_time': 5}
}

# Hava Durumu Değişkenleri
is_raining = False
next_weather_change = time.time() + 5

# Sipariş Panosu
current_order = {'corn': 2, 'bread': 1, 'reward': 50}
def generate_new_order():
    global current_order
    corn_req = random.randint(1, 5)
    bread_req = random.randint(0, 2)
    reward = (corn_req * 6) + (bread_req * 25) + 10
    current_order = {'corn': corn_req, 'bread': bread_req, 'reward': reward}

# Izgarayı başlat
for row in range(GRID_SIZE):
    grid_row = []
    for col in range(GRID_SIZE):
        # state: 'grass', 'soil', 'growing', 'ready'
        # watered: True/False
        grid_row.append({'state': 'soil', 'watered': False, 'plant_time': 0, 'color': BROWN, 'crop_type': None})
    grid.append(grid_row)

def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            # Hücre rengini belirle
            cell = grid[row][col]
            
            # Toprak Rengi (Kuru veya Islak)
            pygame.draw.rect(screen, cell['color'], rect)
            pygame.draw.rect(screen, BLACK, rect, 1) # Çerçeve
            
            # Ekin Çizimi (Eğer büyüyorsa veya hazırsa)
            if cell['state'] in ['growing', 'ready']:
                crop_color = cell['color'] if cell['state'] == 'ready' else SEEDS[cell['crop_type']]['color']
                # Büyüme aşamasına göre boyut (Hazırsa tam, büyüyorsa küçük)
                size_offset = 10 if cell['state'] == 'growing' else 5
                pygame.draw.circle(screen, crop_color, rect.center, CELL_SIZE//2 - size_offset)

def draw_rain():
    if is_raining:
        for _ in range(20): # Her karede 20 damla çiz
            rx = random.randint(0, SCREEN_WIDTH)
            ry = random.randint(0, 500)
            pygame.draw.line(screen, BLUE, (rx, ry), (rx, ry+10), 2)

def draw_ui():
    # Alt Panel (Kontroller)
    pygame.draw.rect(screen, BLACK, (0, 500, SCREEN_WIDTH, 100))
    
    # Bilgiler
    stats = f"Altın: {gold} | XP: {xp}"
    screen.blit(font.render(stats, True, GOLD_COLOR), (10, 510))
    
    # Envanter Göstergesi
    inv_text = f"Depo: Mısır:{inventory['corn']} Domates:{inventory['tomato']} Ekmek:{inventory['bread']}"
    screen.blit(small_font.render(inv_text, True, WHITE), (10, 535))

    # Aksiyon Butonları
    actions = [
        ("1.Biç (Hasat)", 'harvest', GREEN),
        ("2.Mısır Ek (-2)", 'corn', YELLOW),
        ("3.Domates Ek (-5)", 'tomato', RED)
    ]
    
    start_x = 10
    for name, key, color in actions:
        bg_color = (50, 50, 50)
        if selected_action == key:
            bg_color = (100, 100, 100)
            pygame.draw.rect(screen, WHITE, (start_x-2, 560-2, 144, 34), 2)
            
        pygame.draw.rect(screen, bg_color, (start_x, 560, 140, 30))
        text = font.render(name, True, color)
        screen.blit(text, (start_x + 5, 565))
        start_x += 150

    # --- FIRIN ÇİZİMİ ---
    pygame.draw.rect(screen, GRAY, bakery['rect'])
    pygame.draw.rect(screen, BLACK, bakery['rect'], 2)
    screen.blit(font.render("FIRIN", True, WHITE), (bakery['rect'].x + 20, bakery['rect'].y + 10))
    
    if bakery['state'] == 'baking':
        remaining = int(bakery['duration'] - (time.time() - bakery['start_time']))
        screen.blit(font.render(f"{remaining}s", True, ORANGE), (bakery['rect'].x + 35, bakery['rect'].y + 40))
    elif bakery['state'] == 'ready':
        pygame.draw.circle(screen, ORANGE, bakery['rect'].center, 15) # Ekmek ikonu
    else:
        screen.blit(small_font.render("2 Mısır -> Ekmek", True, WHITE), (bakery['rect'].x + 5, bakery['rect'].y + 40))

    # --- SİPARİŞ PANOSU ---
    board_rect = pygame.Rect(350, 200, 140, 120)
    pygame.draw.rect(screen, (139, 69, 19), board_rect)
    pygame.draw.rect(screen, WHITE, (360, 210, 120, 100))
    
    screen.blit(small_font.render("SİPARİŞ:", True, BLACK), (365, 215))
    y_off = 235
    if current_order['corn'] > 0:
        screen.blit(small_font.render(f"- {current_order['corn']} Mısır", True, BLACK), (365, y_off))
        y_off += 20
    if current_order['bread'] > 0:
        screen.blit(small_font.render(f"- {current_order['bread']} Ekmek", True, BLACK), (365, y_off))
        y_off += 20
    
    screen.blit(small_font.render(f"Ödül: {current_order['reward']} Altın", True, GREEN), (365, 280))

running = True
clock = pygame.time.Clock()

while running:
    current_time = time.time()
    
    # Hava Durumu Kontrolü (Rastgele Değişim)
    if current_time > next_weather_change:
        is_raining = not is_raining
        next_weather_change = current_time + random.randint(5, 15) # 5-15 saniye arası sürsün

    # Klavye Kontrolleri (Alet Seçimi)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_1]: selected_action = 'harvest'
    if keys[pygame.K_2]: selected_action = 'corn'
    if keys[pygame.K_3]: selected_action = 'tomato'

    # Olayları İşle
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            
            # 1. TARLA ETKİLEŞİMİ
            if x < 350 and y < 500: # Sağ tarafı UI için ayırdık
                col = x // CELL_SIZE
                row = y // CELL_SIZE
                cell = grid[row][col]
                
                # EKİM YAPMA
                if selected_action in ['corn', 'tomato']:
                    if cell['state'] == 'soil':
                        cost = SEEDS[selected_action]['cost']
                        if gold >= cost:
                            gold -= cost
                            cell['state'] = 'growing'
                            cell['plant_time'] = current_time
                            cell['crop_type'] = selected_action
                            cell['color'] = SEEDS[selected_action]['color']

                # HASAT ETME
                elif selected_action == 'harvest':
                    if cell['state'] == 'ready':
                        crop_type = cell['crop_type']
                        inventory[crop_type] += 1 # Depoya ekle
                        xp += 2
                        
                        cell['state'] = 'soil'
                        cell['color'] = BROWN
                        cell['plant_time'] = 0
            
            # 2. FIRIN ETKİLEŞİMİ
            elif bakery['rect'].collidepoint(x, y):
                if bakery['state'] == 'idle':
                    if inventory['corn'] >= 2:
                        inventory['corn'] -= 2
                        bakery['state'] = 'baking'
                        bakery['start_time'] = current_time
                elif bakery['state'] == 'ready':
                    inventory['bread'] += 1
                    xp += 10
                    bakery['state'] = 'idle'
            
            # 3. SİPARİŞ PANOSU ETKİLEŞİMİ
            elif 350 < x < 490 and 200 < y < 320:
                # Siparişi tamamla
                if (inventory['corn'] >= current_order['corn'] and 
                    inventory['bread'] >= current_order['bread']):
                    
                    inventory['corn'] -= current_order['corn']
                    inventory['bread'] -= current_order['bread']
                    gold += current_order['reward']
                    xp += 20
                    generate_new_order()

    # Büyüme Kontrolü
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            cell = grid[row][col]

            if cell['state'] == 'growing':
                base_time = SEEDS[cell['crop_type']]['grow_time']
                growth_duration = base_time / 2 if is_raining else base_time
                
                if current_time - cell['plant_time'] >= growth_duration:
                    cell['state'] = 'ready'
                    cell['color'] = GREEN
    
    # Fırın Kontrolü
    if bakery['state'] == 'baking':
        if current_time - bakery['start_time'] >= bakery['duration']:
            bakery['state'] = 'ready'

    # Çizim
    screen.fill(BLACK)
    draw_grid()
    draw_rain() # Yağmuru ızgaranın üzerine çiz
    draw_ui()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()