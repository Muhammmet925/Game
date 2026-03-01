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

# Oyun Değişkenleri
grid = []  # Izgara verisi
gold = 50  # Başlangıç parası artırıldı
font = pygame.font.SysFont("Arial", 20)

# Oyuncu Değişkenleri
player = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 20, 20)
PLAYER_SPEED = 3
tools = ['hoe', 'water', 'corn', 'tomato']
current_tool = 'hoe' # Başlangıç aleti

# Tohum Verileri
SEEDS = {
    'corn': {'name': 'Mısır', 'cost': 10, 'sell': 18, 'color': YELLOW},
    'tomato': {'name': 'Domates', 'cost': 20, 'sell': 35, 'color': RED}
}

# Hava Durumu Değişkenleri
is_raining = False
next_weather_change = time.time() + 5

# Izgarayı başlat
for row in range(GRID_SIZE):
    grid_row = []
    for col in range(GRID_SIZE):
        # state: 'grass', 'soil', 'growing', 'ready'
        # watered: True/False
        grid_row.append({'state': 'grass', 'watered': False, 'plant_time': 0, 'color': GRASS_COLOR, 'crop_type': None})
    grid.append(grid_row)

def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            
            # Hücre rengini belirle
            cell = grid[row][col]
            
            # Toprak Rengi (Kuru veya Islak)
            base_color = cell['color']
            if cell['state'] != 'grass' and cell['watered']:
                base_color = WET_SOIL_COLOR
            
            pygame.draw.rect(screen, base_color, rect)
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
    pygame.draw.rect(screen, BLACK, (0, 500, SCREEN_WIDTH, 100))
    
    # Altın Göstergesi
    gold_text = font.render(f"Altın: {gold}", True, GOLD_COLOR)
    screen.blit(gold_text, (20, 510))
    
    # Alet Çubuğu (Inventory)
    tools_ui = [
        ("1.Çapa", 'hoe', BROWN),
        ("2.Su", 'water', BLUE),
        ("3.Mısır", 'corn', YELLOW),
        ("4.Domates", 'tomato', RED)
    ]
    
    start_x = 150
    for name, tool_key, color in tools_ui:
        bg_color = (50, 50, 50)
        if current_tool == tool_key:
            bg_color = (100, 100, 100) # Seçili olanı vurgula
            pygame.draw.rect(screen, WHITE, (start_x-2, 510-2, 84, 34), 2)
            
        pygame.draw.rect(screen, bg_color, (start_x, 510, 80, 30))
        text = font.render(name, True, color)
        screen.blit(text, (start_x + 5, 515))
        start_x += 90
    
    # Hava Durumu Bilgisi
    weather_text = font.render(f"Hava: {'YAĞMURLU (Hızlı Büyüme)' if is_raining else 'Güneşli'}", True, BLUE if is_raining else YELLOW)
    screen.blit(weather_text, (20, 545))
    
    info = font.render("WASD: Yürü | 1-4: Alet Seç | Tıkla: Etkileşim", True, (200, 200, 200))
    screen.blit(info, (20, 560))

running = True
clock = pygame.time.Clock()

while running:
    current_time = time.time()
    
    # Hava Durumu Kontrolü (Rastgele Değişim)
    if current_time > next_weather_change:
        is_raining = not is_raining
        next_weather_change = current_time + random.randint(5, 15) # 5-15 saniye arası sürsün

    # Klavye Kontrolleri (Hareket ve Alet Seçimi)
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] and player.y > 0: player.y -= PLAYER_SPEED
    if keys[pygame.K_s] and player.y < 500 - player.height: player.y += PLAYER_SPEED
    if keys[pygame.K_a] and player.x > 0: player.x -= PLAYER_SPEED
    if keys[pygame.K_d] and player.x < SCREEN_WIDTH - player.width: player.x += PLAYER_SPEED

    if keys[pygame.K_1]: current_tool = 'hoe'
    if keys[pygame.K_2]: current_tool = 'water'
    if keys[pygame.K_3]: current_tool = 'corn'
    if keys[pygame.K_4]: current_tool = 'tomato'

    # Olayları İşle
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = pygame.mouse.get_pos()
            
            # Oyuncu tarlaya yakın mı? (Mesafe kontrolü)
            dist = ((player.centerx - x)**2 + (player.centery - y)**2)**0.5
            
            if y < 500 and dist < 100: # Sadece yakındaki karelere işlem yapabilir
                col = x // CELL_SIZE
                row = y // CELL_SIZE
                cell = grid[row][col]
                
                # 1. ÇAPA (HOE): Çimen -> Toprak
                if current_tool == 'hoe':
                    if cell['state'] == 'grass':
                        cell['state'] = 'soil'
                        cell['color'] = BROWN
                
                # 2. SU (WATER): Toprak -> Islak Toprak
                elif current_tool == 'water':
                    if cell['state'] in ['soil', 'growing', 'ready']:
                        cell['watered'] = True

                # 3/4. TOHUM EKME (CORN/TOMATO)
                elif current_tool in ['corn', 'tomato']:
                    if cell['state'] == 'soil': # Sadece sürülmüş toprağa ekilir
                        cost = SEEDS[current_tool]['cost']
                        if gold >= cost:
                            gold -= cost
                            cell['state'] = 'growing'
                            cell['plant_time'] = current_time
                            cell['crop_type'] = current_tool
                            # Renk hemen değişmez, filizlenince değişir
                        else:
                            print("Yetersiz Bakiye!")

                # HASAT (Herhangi bir aletle tıklayınca)
                if cell['state'] == 'ready':
                    crop_type = cell['crop_type']
                    gain = SEEDS[crop_type]['sell']
                    gold += gain
                    
                    cell['state'] = 'soil' # Hasat edilince tekrar toprak olur
                    cell['color'] = BROWN
                    cell['plant_time'] = 0
                    cell['watered'] = False # Hasat sonrası kurur

    # Büyüme Kontrolü
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            cell = grid[row][col]
            
            # Yağmur varsa otomatik sula
            if is_raining and cell['state'] != 'grass':
                cell['watered'] = True

            if cell['state'] == 'growing':
                # Sadece SULANMIŞSA büyür
                if cell['watered']:
                    growth_duration = 3 if is_raining else 6
                    if current_time - cell['plant_time'] >= growth_duration:
                        cell['state'] = 'ready'
                        cell['color'] = GREEN

    # Çizim
    screen.fill(BLACK)
    draw_grid()
    draw_rain() # Yağmuru ızgaranın üzerine çiz
    
    # Oyuncuyu Çiz
    pygame.draw.rect(screen, PLAYER_COLOR, player)
    
    # Fare İmleci Vurgusu (Menzil içindeyse)
    mx, my = pygame.mouse.get_pos()
    dist = ((player.centerx - mx)**2 + (player.centery - my)**2)**0.5
    if my < 500 and dist < 100:
        col = mx // CELL_SIZE
        row = my // CELL_SIZE
        highlight_rect = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, WHITE, highlight_rect, 2)

    draw_ui()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()