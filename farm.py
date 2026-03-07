import pygame
import time
import random
import json
import os

# Pygame başlatma
pygame.init()

# Ekran Ayarları
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 700
GRID_SIZE = 12
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("🌾 SUPER ÇİFTLİK - Hayvanlar ve Ürünler")

# Renkler
COLORS = {
    'brown': (139, 69, 19),
    'yellow': (255, 215, 0),
    'red': (220, 20, 60),
    'green': (34, 139, 34),
    'white': (255, 255, 255),
    'black': (0, 0, 0),
    'blue': (0, 191, 255),
    'gold': (255, 223, 0),
    'grass': (50, 205, 50),
    'wet_soil': (80, 40, 10),
    'orange': (255, 165, 0),
    'purple': (128, 0, 128),
    'pink': (255, 192, 203),
    'gray': (100, 100, 100),
    'dark_brown': (101, 67, 33),
    'light_blue': (173, 216, 230),
}

# Ses Efektleri
class SoundManager:
    def __init__(self):
        self.enabled = True
        try:
            pygame.mixer.init(frequency=44100, size=-16, channels=1)
        except:
            self.enabled = False
    
    def create_beep(self, freq=440, duration=0.1):
        if not self.enabled: return None
        try:
            import array
            sample_rate = 44100
            n_samples = int(sample_rate * duration)
            buffer = array.array('h', [int(8000 * (1 if (t % (sample_rate // freq)) < (sample_rate // freq) // 2 else -1)) for t in range(n_samples)])
            return pygame.mixer.Sound(buffer=buffer)
        except:
            return None

sound_mgr = SoundManager()
harvest_sound = sound_mgr.create_beep(600, 0.1)
plant_sound = sound_mgr.create_beep(400, 0.05)
water_sound = sound_mgr.create_beep(300, 0.15)

# Oyun Verileri
class GameData:
    def __init__(self):
        self.gold = 100
        self.xp = 0
        self.level = 1
        self.inventory = {
            'corn': 5, 'tomato': 3, 'wheat': 2, 'carrot': 0,
            'bread': 0, 'soup': 0, 'juice': 0
        }
        self.animals = {
            'chicken': 2, 'cow': 0, 'sheep': 0
        }
        self.unlocked_crops = ['corn', 'tomato']
        self.unlocked_animals = ['chicken']
    
    def save(self):
        data = {
            'gold': self.gold,
            'xp': self.xp,
            'level': self.level,
            'inventory': self.inventory,
            'animals': self.animals,
            'unlocked_crops': self.unlocked_crops,
            'unlocked_animals': self.unlocked_animals
        }
        try:
            with open('farm_save.json', 'w') as f:
                json.dump(data, f)
            return True
        except:
            return False
    
    def load(self):
        try:
            with open('farm_save.json', 'r') as f:
                data = json.load(f)
                self.gold = data.get('gold', 100)
                self.xp = data.get('xp', 0)
                self.level = data.get('level', 1)
                self.inventory = data.get('inventory', {})
                self.animals = data.get('animals', {})
                self.unlocked_crops = data.get('unlocked_crops', ['corn', 'tomato'])
                self.unlocked_animals = data.get('unlocked_animals', ['chicken'])
                return True
        except:
            return False

game_data = GameData()
game_data.load()

# Tohum Verileri
SEEDS = {
    'corn': {'name': 'Mısır', 'cost': 5, 'sell': 15, 'color': COLORS['yellow'], 'grow_time': 8, 'xp': 5},
    'tomato': {'name': 'Domates', 'cost': 12, 'sell': 30, 'color': COLORS['red'], 'grow_time': 10, 'xp': 8},
    'wheat': {'name': 'Buğday', 'cost': 8, 'sell': 20, 'color': COLORS['orange'], 'grow_time': 12, 'xp': 6},
    'carrot': {'name': 'Havuç', 'cost': 15, 'sell': 40, 'color': COLORS['orange'], 'grow_time': 14, 'xp': 10},
}

# Hayvan Verileri
ANIMALS = {
    'chicken': {'name': 'Tavuk', 'cost': 50, 'product': 'egg', 'product_name': 'Yumurta', 'produce_time': 15, 'xp': 10},
    'cow': {'name': 'İnek', 'cost': 150, 'product': 'milk', 'product_name': 'Süt', 'produce_time': 25, 'xp': 20},
    'sheep': {'name': 'Koyun', 'cost': 100, 'product': 'wool', 'product_name': 'Yün', 'produce_time': 20, 'xp': 15},
}

# Ürün İşleme Tarifleri
RECIPES = {
    'bread': {'ingredients': {'wheat': 3}, 'sell': 50, 'xp': 15},
    'soup': {'ingredients': {'carrot': 2, 'wheat': 1}, 'sell': 80, 'xp': 25},
    'juice': {'ingredients': {'tomato': 3}, 'sell': 60, 'xp': 20},
}

# Ürün Fiyatları
PRODUCT_PRICES = {
    'egg': 10, 'milk': 25, 'wool': 30
}

# Oyuncu
player = pygame.Rect(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2, 24, 24)
PLAYER_SPEED = 4

# Tarla Sistemi
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

# Hayvan Alanları
animal_pens = [
    {'rect': pygame.Rect(550, 100, 100, 80), 'type': 'chicken', 'last_produce': 0},
    {'rect': pygame.Rect(550, 200, 100, 80), 'type': 'cow', 'last_produce': 0},
    {'rect': pygame.Rect(550, 300, 100, 80), 'type': 'sheep', 'last_produce': 0},
]

# Binalar
buildings = {
    'kitchen': {'rect': pygame.Rect(550, 400, 100, 80), 'name': 'Mutfak', 'unlocked': True},
    'shop': {'rect': pygame.Rect(550, 500, 100, 80), 'name': 'Dükkan', 'unlocked': True},
    'barn': {'rect': pygame.Rect(650, 100, 80, 200), 'name': 'Ahır', 'unlocked': True},
}

# Sipariş Sistemi
current_order = {}
def generate_order():
    global current_order
    items = random.sample(list(SEEDS.keys()), min(3, len(SEEDS)))
    order = {}
    total_value = 0
    for item in items:
        qty = random.randint(1, 3)
        order[item] = qty
        total_value += SEEDS[item]['sell'] * qty
    
    current_order = {
        'items': order,
        'reward': total_value + 20,
        'xp': total_value // 5,
        'time_left': 60
    }

generate_order()

# Hava Durumu
is_raining = False
weather_timer = time.time() + 10

# UI Değişkenleri
current_tool = 'hoe'
show_shop = False
show_recipes = False
message = ""
message_timer = 0
font = pygame.font.SysFont("Arial", 18)
title_font = pygame.font.SysFont("Arial", 24, bold=True)
small_font = pygame.font.SysFont("Arial", 14)

def draw_message():
    global message, message_timer
    if message and message_timer > 0:
        text = font.render(message, True, COLORS['gold'])
        screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 50))
        message_timer -= 1

def show_msg(text, duration=60):
    global message, message_timer
    message = text
    message_timer = duration

# Menü Sistemi
current_menu = 'main'  # main, shop, animals, recipes

def draw_menu():
    global current_menu, show_shop, show_recipes
    
    # Arka plan
    pygame.draw.rect(screen, COLORS['dark_brown'], (520, 50, 260, 600))
    
    # Başlık
    title = title_font.render("🎮 MENÜ", True, COLORS['white'])
    screen.blit(title, (SCREEN_WIDTH - 250, 60))
    
    # Butonlar
    menu_items = [
        ("🏪 Dükkan", 100, lambda: set_current_menu('shop')),
        ("🐔 Hayvanlar", 140, lambda: set_current_menu('animals')),
        ("🍞 Tarifler", 180, lambda: set_current_menu('recipes')),
        ("💾 Kaydet", 220, save_game),
        ("📥 Yükle", 260, load_game),
    ]
    
    for text, y, action in menu_items:
        btn_rect = pygame.Rect(530, y, 240, 35)
        
        # Hover efekti
        mx, my = pygame.mouse.get_pos()
        if btn_rect.collidepoint(mx, my):
            color = COLORS['green']
            if pygame.mouse.get_pressed()[0]:
                action()
        else:
            color = COLORS['gray']
        
        pygame.draw.rect(screen, color, btn_rect, border_radius=5)
        
        btn_text = font.render(text, True, COLORS['white'])
        screen.blit(btn_text, (btn_rect.x + 10, btn_rect.y + 8))
    
    # Ana menü butonu
    if current_menu != 'main':
        back_rect = pygame.Rect(530, 580, 240, 40)
        pygame.draw.rect(screen, COLORS['red'], back_rect, border_radius=5)
        back_text = font.render("🔙 Geri", True, COLORS['white'])
        screen.blit(back_text, (back_rect.x + 80, back_rect.y + 10))

def set_current_menu(menu):
    global current_menu
    current_menu = menu

def save_game():
    if game_data.save():
        show_msg("💾 Oyun Kaydedildi!")
    else:
        show_msg("❌ Kayıt Hatası!")

def load_game():
    if game_data.load():
        show_msg("📥 Oyun Yüklendi!")
    else:
        show_msg("❌ Yükleme Hatası!")

def draw_shop():
    if current_menu != 'shop': return
    
    # Dükkan arka planı
    pygame.draw.rect(screen, COLORS['brown'], (50, 50, 450, 300), border_radius=10)
    
    title = title_font.render("🏪 TOHUM DÜKKANI", True, COLORS['yellow'])
    screen.blit(title, (80, 60))
    
    # Tohumlar
    y = 100
    for seed_key, seed_data in SEEDS.items():
        unlocked = seed_key in game_data.unlocked_crops
        
        # Bilgi
        name = small_font.render(f"{seed_data['name']} - {seed_data['cost']} Altın", True, COLORS['white'] if unlocked else COLORS['gray'])
        screen.blit(name, (70, y))
        
        # Satın al butonu
        if unlocked:
            btn_color = COLORS['green']
            btn_text = "Satın Al"
        else:
            btn_color = COLORS['purple']
            btn_text = f"Aç ({seed_data['cost'] * 3})"
        
        btn_rect = pygame.Rect(350, y - 5, 100, 30)
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=3)
        
        btn_lbl = small_font.render(btn_text, True, COLORS['white'])
        screen.blit(btn_lbl, (btn_rect.x + 5, btn_rect.y + 7))
        
        y += 40
    
    # Para bilgisi
    gold_text = font.render(f"💰 Altın: {game_data.gold} | XP: {game_data.xp}", True, COLORS['gold'])
    screen.blit(gold_text, (70, 320))

def draw_animals():
    if current_menu != 'animals': return
    
    # Hayvanlar arka planı
    pygame.draw.rect(screen, COLORS['gray'], (50, 50, 450, 300), border_radius=10)
    
    title = title_font.render("🐔 HAYVANLAR", True, COLORS['white'])
    screen.blit(title, (80, 60))
    
    y = 100
    for animal_key, animal_data in ANIMALS.items():
        count = game_data.animals.get(animal_key, 0)
        
        name = small_font.render(f"{animal_data['name']}: {count} adet", True, COLORS['white'])
        screen.blit(name, (70, y))
        
        # Satın al butonu
        cost = animal_data['cost']
        can_buy = game_data.gold >= cost
        
        btn_rect = pygame.Rect(350, y - 5, 100, 30)
        btn_color = COLORS['green'] if can_buy else COLORS['red']
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=3)
        
        btn_lbl = small_font.render(f"Al {cost}💰", True, COLORS['white'])
        screen.blit(btn_lbl, (btn_rect.x + 15, btn_rect.y + 7))
        
        y += 40

def draw_recipes():
    if current_menu != 'recipes': return
    
    # Tarifler arka planı
    pygame.draw.rect(screen, COLORS['purple'], (50, 50, 450, 400), border_radius=10)
    
    title = title_font.render("🍞 MUTFAK - TARİFLER", True, COLORS['white'])
    screen.blit(title, (80, 60))
    
    y = 100
    for recipe_key, recipe_data in RECIPES.items():
        ingredients = ", ".join([f"{v} {SEEDS[k]['name']}" if k in SEEDS else f"{v} {k}" for k, v in recipe_data['ingredients'].items()])
        
        name = small_font.render(f"{recipe_key.capitalize()}: {ingredients}", True, COLORS['yellow'])
        screen.blit(name, (70, y))
        
        sell = small_font.render(f"Sat: {recipe_data['sell']}💰 | XP: {recipe_data['xp']}", True, COLORS['light_blue'])
        screen.blit(sell, (70, y + 20))
        
        # Yap butonu
        can_make = all(game_data.inventory.get(k, 0) >= v for k, v in recipe_data['ingredients'].items())
        
        btn_rect = pygame.Rect(350, y, 100, 30)
        btn_color = COLORS['green'] if can_make else COLORS['red']
        pygame.draw.rect(screen, btn_color, btn_rect, border_radius=3)
        
        btn_lbl = small_font.render("Yap", True, COLORS['white'])
        screen.blit(btn_lbl, (btn_rect.x + 35, btn_rect.y + 7))
        
        y += 50

def draw_grid():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            x = col * CELL_SIZE
            y = row * CELL_SIZE
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)
            
            cell = grid[row][col]
            
            # Renk belirleme
            if cell['state'] == 'grass':
                color = COLORS['grass']
            elif cell['state'] == 'soil':
                color = COLORS['wet_soil'] if cell['watered'] else COLORS['brown']
            elif cell['state'] in ['growing', 'ready']:
                seed = SEEDS.get(cell['crop_type'])
                if cell['state'] == 'ready':
                    color = seed['color']
                else:
                    # Büyüme oranına göre renk
                    growth_ratio = cell['growth']
                    color = COLORS['brown'] if growth_ratio < 0.5 else seed['color']
            
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (50, 50, 50), rect, 1)
            
            # Büyüme çubuğu
            if cell['state'] == 'growing' and cell['growth'] > 0:
                bar_width = int((CELL_SIZE - 10) * cell['growth'])
                pygame.draw.rect(screen, COLORS['black'], (x + 5, y + CELL_SIZE - 8, CELL_SIZE - 10, 5))
                pygame.draw.rect(screen, COLORS['green'], (x + 5, y + CELL_SIZE - 8, bar_width, 5))

def draw_animals_pens():
    for pen in animal_pens:
        animal_type = pen['type']
        count = game_data.animals.get(animal_type, 0)
        
        # Ahır çizimi
        pygame.draw.rect(screen, COLORS['gray'], pen['rect'])
        pygame.draw.rect(screen, COLORS['black'], pen['rect'], 2)
        
        # Hayvan sayısı
        name = ANIMALS[animal_type]['name']
        text = font.render(f"{name}: {count}", True, COLORS['white'])
        screen.blit(text, (pen['rect'].x + 10, pen['rect'].y + 30))
        
        # Üretim durumu
        last = pen['last_produce']
        if last > 0:
            elapsed = time.time() - last
            produce_time = ANIMALS[animal_type]['produce_time']
            if elapsed >= produce_time:
                ready_text = font.render("✅ Hazır!", True, COLORS['green'])
                screen.blit(ready_text, (pen['rect'].x + 10, pen['rect'].y + 55))
            else:
                percent = int((elapsed / produce_time) * 100)
                progress_text = small_font.render(f"{percent}%", True, COLORS['yellow'])
                screen.blit(progress_text, (pen['rect'].x + 10, pen['rect'].y + 55))

def draw_ui():
    # Alt panel
    pygame.draw.rect(screen, COLORS['black'], (0, 600, SCREEN_WIDTH, 100))
    
    # Para ve XP
    info = font.render(f"💰 {game_data.gold} | ✨ XP: {game_data.xp} | Seviye: {game_data.level}", True, COLORS['gold'])
    screen.blit(info, (10, 610))
    
    # Envanter
    inv_text = "📦 " + " | ".join([f"{k}: {v}" for k, v in game_data.inventory.items() if v > 0])
    inv_surf = small_font.render(inv_text, True, COLORS['white'])
    screen.blit(inv_surf, (10, 640))
    
    # Alet seçimi
    tools = [
        ("1:Çapa", 'hoe', COLORS['brown']),
        ("2:Sulama", 'water', COLORS['blue']),
        ("3:Mısır", 'corn', COLORS['yellow']),
        ("4:Domates", 'tomato', COLORS['red']),
        ("5:Buğday", 'wheat', COLORS['orange']),
        ("6:Havuç", 'carrot', COLORS['orange']),
    ]
    
    x = 10
    for name, tool, color in tools:
        bg = COLORS['dark_brown'] if current_tool == tool else COLORS['gray']
        pygame.draw.rect(screen, bg, (x, 665, 70, 25), border_radius=3)
        
        if current_tool == tool:
            pygame.draw.rect(screen, COLORS['white'], (x, 665, 70, 25), 2)
        
        lbl = small_font.render(name, True, color)
        screen.blit(lbl, (x + 5, 670))
        x += 80
    
    # Hava durumu
    weather = "🌧️ Yağmurlu" if is_raining else "☀️ Güneşli"
    weather_text = font.render(weather, True, COLORS['blue'] if is_raining else COLORS['yellow'])
    screen.blit(weather_text, (SCREEN_WIDTH - 180, 665))

def draw_order_board():
    # Sipariş panosu
    order_rect = pygame.Rect(550, 400, 230, 100)
    pygame.draw.rect(screen, COLORS['brown'], order_rect, border_radius=5)
    
    title = font.render("📋 Sipariş", True, COLORS['white'])
    screen.blit(title, (order_rect.x + 10, order_rect.y + 5))
    
    if current_order:
        y = order_rect.y + 30
        for item, qty in current_order['items'].items():
            item_text = small_font.render(f"{SEEDS[item]['name']}: {qty}", True, COLORS['white'])
            screen.blit(item_text, (order_rect.x + 10, y))
            y += 18
        
        reward_text = small_font.render(f"Ödül: {current_order['reward']}💰", True, COLORS['gold'])
        screen.blit(reward_text, (order_rect.x + 10, y + 5))

def draw_rain():
    if is_raining:
        for _ in range(30):
            rx = random.randint(0, SCREEN_WIDTH)
            ry = random.randint(0, 600)
            pygame.draw.line(screen, COLORS['blue'], (rx, ry), (rx, ry + 15), 2)

# Ana Döngü
clock = pygame.time.Clock()
running = True

while running:
    current_time = time.time()
    
    # Hava durumu değişimi
    if current_time > weather_timer:
        is_raining = not is_raining
        weather_timer = current_time + random.randint(8, 20)
    
    # Sipariş zamanı
    if current_order and current_order.get('time_left', 0) > 0:
        current_order['time_left'] -= 1/60
        if current_order['time_left'] <= 0:
            generate_order()
    
    # Etkinlik kontrolü
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            mx, my = pygame.mouse.get_pos()
            
            # Menü kontrolü
            if mx > 520:
                # Menü butonları kontrolü
                menu_actions = {
                    (530, 100): lambda: set_current_menu('shop'),
                    (530, 140): lambda: set_current_menu('animals'),
                    (530, 180): lambda: set_current_menu('recipes'),
                    (530, 220): save_game,
                    (530, 260): load_game,
                }
                
                for rect, action in menu_actions.items():
                    if pygame.Rect(rect[0], rect[1], 240, 35).collidepoint(mx, my):
                        action()
                        break
                
                # Geri butonu
                if current_menu != 'main' and pygame.Rect(530, 580, 240, 40).collidepoint(mx, my):
                    set_current_menu('main')
                
                # Dükkan butonları
                if current_menu == 'shop':
                    y = 100
                    for seed_key in SEEDS.keys():
                        if pygame.Rect(350, y - 5, 100, 30).collidepoint(mx, my):
                            if seed_key in game_data.unlocked_crops:
                                # Tohum satın al
                                cost = SEEDS[seed_key]['cost']
                                if game_data.gold >= cost:
                                    game_data.gold -= cost
                                    game_data.inventory[seed_key] = game_data.inventory.get(seed_key, 0) + 1
                                    show_msg(f"{SEEDS[seed_key]['name']} tohumu alındı!")
                            else:
                                # Yeni tohum aç
                                cost = SEEDS[seed_key]['cost'] * 3
                                if game_data.gold >= cost:
                                    game_data.gold -= cost
                                    game_data.unlocked_crops.append(seed_key)
                                    show_msg(f"{SEEDS[seed_key]['name']} açıldı!")
                            break
                        y += 40
                
                # Hayvan butonları
                if current_menu == 'animals':
                    y = 100
                    for animal_key in ANIMALS.keys():
                        if pygame.Rect(350, y - 5, 100, 30).collidepoint(mx, my):
                            cost = ANIMALS[animal_key]['cost']
                            if game_data.gold >= cost:
                                game_data.gold -= cost
                                game_data.animals[animal_key] = game_data.animals.get(animal_key, 0) + 1
                                show_msg(f"{ANIMALS[animal_key]['name']} satın alındı!")
                            break
                        y += 40
                
                # Tarif butonları
                if current_menu == 'recipes':
                    y = 100
                    for recipe_key, recipe_data in RECIPES.items():
                        if pygame.Rect(350, y, 100, 30).collidepoint(mx, my):
                            can_make = all(game_data.inventory.get(k, 0) >= v for k, v in recipe_data['ingredients'].items())
                            if can_make:
                                for k, v in recipe_data['ingredients'].items():
                                    game_data.inventory[k] -= v
                                game_data.inventory[recipe_key] = game_data.inventory.get(recipe_key, 0) + 1
                                game_data.xp += recipe_data['xp']
                                show_msg(f"{recipe_key} yapıldı!")
                            else:
                                show_msg("Malzeme yok!")
                            break
                        y += 50
                
                # Sipariş teslim
                if pygame.Rect(550, 400, 230, 100).collidepoint(mx, my):
                    if current_order:
                        can_deliver = all(game_data.inventory.get(k, 0) >= v for k, v in current_order['items'].items())
                        if can_deliver:
                            for k, v in current_order['items'].items():
                                game_data.inventory[k] -= v
                            game_data.gold += current_order['reward']
                            game_data.xp += current_order['xp']
                            show_msg(f"Sipariş teslim edildi! +{current_order['reward']}💰")
                            generate_order()
                        else:
                            show_msg("Sipariş için yeterli ürün yok!")
                
                # Hayvanlardan ürün al
                for pen in animal_pens:
                    if pen['rect'].collidepoint(mx, my) and pen['last_produce'] > 0:
                        elapsed = current_time - pen['last_produce']
                        produce_time = ANIMALS[pen['type']]['produce_time']
                        if elapsed >= produce_time:
                            product = ANIMALS[pen['type']]['product']
                            game_data.inventory[product] = game_data.inventory.get(product, 0) + 1
                            pen['last_produce'] = 0
                            show_msg(f"{ANIMALS[pen['type']]['product_name']} alındı!")
                
                continue
            
            # Tarla etkileşimi
            if my < 600:
                col = mx // CELL_SIZE
                row = my // CELL_SIZE
                
                if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
                    cell = grid[row][col]
                    
                    # Mesafe kontrolü
                    dist = ((player.centerx - mx)**2 + (player.centery - my)**2)**0.5
                    if dist > 80: continue
                    
                    # Çapa - Çimeni sür
                    if current_tool == 'hoe':
                        if cell['state'] == 'grass':
                            cell['state'] = 'soil'
                            if plant_sound: plant_sound.play()
                    
                    # Sulama
                    elif current_tool == 'water':
                        if cell['state'] in ['soil', 'growing', 'ready']:
                            cell['watered'] = True
                            if water_sound: water_sound.play()
                    
                    # Ekim
                    elif current_tool in SEEDS:
                        if cell['state'] == 'soil' and cell['crop_type'] is None:
                            cost = SEEDS[current_tool]['cost']
                            if game_data.gold >= cost:
                                game_data.gold -= cost
                                cell['state'] = 'growing'
                                cell['crop_type'] = current_tool
                                cell['plant_time'] = current_time
                                cell['growth'] = 0
                                if plant_sound: plant_sound.play()
                    
                    # Hasat
                    elif cell['state'] == 'ready':
                        crop = cell['crop_type']
                        game_data.inventory[crop] = game_data.inventory.get(crop, 0) + 1
                        game_data.xp += SEEDS[crop]['xp']
                        
                        cell['state'] = 'soil'
                        cell['watered'] = False
                        cell['crop_type'] = None
                        cell['growth'] = 0
                        
                        if harvest_sound: harvest_sound.play()
                        show_msg(f"+1 {SEEDS[crop]['name']}!")
    
    # Klavye kontrolü
    keys = pygame.key.get_pressed()
    
    # Hareket
    if keys[pygame.K_w] and player.y > 0:
        player.y -= PLAYER_SPEED
    if keys[pygame.K_s] and player.y < 580:
        player.y += PLAYER_SPEED
    if keys[pygame.K_a] and player.x > 0:
        player.x -= PLAYER_SPEED
    if keys[pygame.K_d] and player.x < 500:
        player.x += PLAYER_SPEED
    
    # Alet seçimi
    tool_map = {'1': 'hoe', '2': 'water', '3': 'corn', '4': 'tomato', '5': 'wheat', '6': 'carrot'}
    for key, tool in tool_map.items():
        if keys[getattr(pygame, f'K_{key}')]:
            current_tool = tool
    
    # Büyüme güncellemesi
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            cell = grid[row][col]
            
            # Yağmur otomatik sulama
            if is_raining and cell['state'] != 'grass':
                cell['watered'] = True
            
            if cell['state'] == 'growing' and cell['watered']:
                seed = SEEDS[cell['crop_type']]
                grow_time = seed['grow_time'] if not is_raining else seed['grow_time'] / 2
                
                elapsed = current_time - cell['plant_time']
                cell['growth'] = min(1.0, elapsed / grow_time)
                
                if cell['growth'] >= 1.0:
                    cell['state'] = 'ready'
    
    # Hayvan üretimi
    for pen in animal_pens:
        if game_data.animals.get(pen['type'], 0) > 0 and pen['last_produce'] == 0:
            if random.random() < 0.01:  # Rastgele üretim başlasın
                pen['last_produce'] = current_time
    
    # Seviye kontrolü
    xp_needed = game_data.level * 100
    if game_data.xp >= xp_needed:
        game_data.level += 1
        game_data.xp -= xp_needed
        show_msg(f"🎉 Seviye Atladın! Seviye: {game_data.level}")
    
    # Çizim
    screen.fill(COLORS['black'])
    
    draw_grid()
    draw_rain()
    draw_animals_pens()
    draw_order_board()
    
    # Oyuncu
    pygame.draw.rect(screen, COLORS['blue'], player)
    pygame.draw.rect(screen, COLORS['white'], player, 2)
    
    # Fare vurgusu
    mx, my = pygame.mouse.get_pos()
    if my < 600 and mx < 520:
        col = mx // CELL_SIZE
        row = my // CELL_SIZE
        highlight = pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, COLORS['white'], highlight, 2)
    
    draw_ui()
    draw_menu()
    
    if current_menu == 'shop':
        draw_shop()
    elif current_menu == 'animals':
        draw_animals()
    elif current_menu == 'recipes':
        draw_recipes()
    
    draw_message()
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
