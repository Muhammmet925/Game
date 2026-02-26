from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar
from ursina.shaders import lit_with_shadows_shader
from panda3d.core import load_prc_file_data
import random
import math
import sqlite3
import json

load_prc_file_data('', 'multisamples 4') # Kalite ayarı (Kenar yumuşatma)
app = Ursina()

# --- 1. SİSTEM VE EKRAN AYARLARI ---
window.shadows = True
window.color = color.black
window.exit_button.visible = False
Entity.default_shader = lit_with_shadows_shader

# Oyun Değişkenleri
score = 0
player_hp = 100
level = 1
attack_speed = 0.1
sword_color = color.cyan
game_over_state = False
game_started = False
difficulty_settings = {
    'KOLAY': {'hp_mul': 0.6, 'dmg_mul': 0.5},
    'ORTA': {'hp_mul': 1.0, 'dmg_mul': 1.0},
    'ZOR': {'hp_mul': 1.5, 'dmg_mul': 2.0}
}
current_difficulty = 'ORTA'
boss_active = False
day_time = 0
jetpack_fuel = 100
player_inventory = {'health_pack': 1, 'ammo_pack': 1, 'food': 2, 'water': 2} # Envanter verisi
resources = {'wood': 0, 'metal': 0}
max_player_hp = 100
speed_level = 0
health_level = 0
selected_map = 'dunya'
player_stamina = 100
night_vision_active = False
player_hunger = 100
player_thirst = 100
current_block_type = 'grass'
block_types = ['grass', 'brick', 'white_cube', 'shore']
nv_overlay = Entity(parent=camera.ui, model='quad', color=color.rgba(0, 255, 0, 60), scale=99, z=10, enabled=False)
in_vehicle = False

# Modernizasyon Değişkenleri
stats = {
    'kills': 0,
    'boss_kills': 0
}
achievements = {
    'KILL_10': {'name': 'Acemi Avcı', 'description': '10 yaratık yok et.', 'condition': lambda: stats['kills'] >= 10, 'unlocked': False, 'reward': lambda: globals().update(score=globals()['score'] + 1000)},
    'REACH_LVL_5': {'name': 'Kıdemli Avcı', 'description': 'Seviye 5\'e ulaş.', 'condition': lambda: level >= 5, 'unlocked': False, 'reward': lambda: globals().update(score=globals()['score'] + 2500)},
    'KILL_BOSS': {'name': 'Patron Katili', 'description': 'İlk boss\'u yen.', 'condition': lambda: stats['boss_kills'] >= 1, 'unlocked': False, 'reward': lambda: globals().update(score=globals()['score'] + 5000)},
    'HIGH_SCORE': {'name': 'Veri Madencisi', 'description': '10000 puana ulaş.', 'condition': lambda: score >= 10000, 'unlocked': False, 'reward': lambda: player_inventory.update(health_pack=player_inventory.get('health_pack', 0) + 1)},
}

dash_cooldown = 1.5
last_dash_time = -999


# --- SES EFEKTLERİ (Bu dosyaların projenizde 'assets' klasöründe olması gerekir) ---
background_music = Audio('assets/music.mp3', loop=True, autoplay=False, volume=0.5)
pistol_shot_sound = Audio('assets/pistol.wav', autoplay=False, volume=0.8)
laser_shot_sound = Audio('assets/laser.wav', autoplay=False, volume=0.6)
hit_sound = Audio('assets/hit.wav', autoplay=False, volume=0.9)
sword_swing_sound = Audio('assets/sword_swing.wav', autoplay=False, volume=0.7)
footstep_sound = Audio('assets/footstep.wav', loop=False, autoplay=False, volume=0.5)
footstep_timer = 0
achievement_sound = Audio('assets/achievement.wav', autoplay=False, volume=0.8)

# --- VERİTABANI SİSTEMİ (SQLite) ---
def init_db():
    conn = sqlite3.connect('shadow_hunter.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS game_save (
        id INTEGER PRIMARY KEY,
        score INTEGER,
        level INTEGER,
        player_hp REAL,
        max_player_hp REAL,
        speed_level INTEGER,
        health_level INTEGER,
        jetpack_fuel REAL,
        player_stamina REAL,
        player_hunger REAL,
        player_thirst REAL,
        selected_map TEXT,
        current_difficulty TEXT,
        inventory TEXT,
        stats TEXT,
        achievements TEXT
    )''')
    conn.commit()
    conn.close()

init_db()

def save_game():
    conn = sqlite3.connect('shadow_hunter.db')
    c = conn.cursor()
    # Başarımların sadece kilit durumunu kaydet
    ach_status = {k: v['unlocked'] for k, v in achievements.items()}
    
    c.execute('''INSERT OR REPLACE INTO game_save (
        id, score, level, player_hp, max_player_hp, speed_level, health_level, 
        jetpack_fuel, player_stamina, player_hunger, player_thirst, selected_map, current_difficulty, inventory, stats, achievements
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', (
        1, score, level, player_hp, max_player_hp, speed_level, health_level,
        jetpack_fuel, player_stamina, player_hunger, player_thirst, selected_map, current_difficulty,
        json.dumps(player_inventory), json.dumps(stats), json.dumps(ach_status)
    ))
    conn.commit()
    conn.close()
    FloatingText("OYUN KAYDEDILDI", player.position + Vec3(0,2,0))

def load_game():
    global score, level, player_hp, max_player_hp, speed_level, health_level, jetpack_fuel, player_stamina, player_hunger, player_thirst, selected_map, current_difficulty, player_inventory, stats, achievements
    
    conn = sqlite3.connect('shadow_hunter.db')
    c = conn.cursor()
    c.execute("SELECT * FROM game_save WHERE id=1")
    row = c.fetchone()
    conn.close()
    
    if row:
        score, level, player_hp, max_player_hp, speed_level, health_level = row[1], row[2], row[3], row[4], row[5], row[6]
        jetpack_fuel, player_stamina = row[7], row[8]
        # Veritabanı yapısı değiştiği için eski kayıtları kontrol et
        if len(row) > 14:
            player_hunger, player_thirst = row[9], row[10]
            selected_map, current_difficulty = row[11], row[12]
            player_inventory = json.loads(row[13])
            stats = json.loads(row[14])
            ach_status = json.loads(row[15])
        else:
            # Eski kayıt uyumluluğu (Hunger/Thirst yoksa varsayılan)
            selected_map, current_difficulty = row[9], row[10]
            player_inventory = json.loads(row[11])
            stats = json.loads(row[12])
            ach_status = json.loads(row[13])
            player_hunger, player_thirst = 100, 100
        
        for k, v in ach_status.items():
            if k in achievements: achievements[k]['unlocked'] = v
        
        if not game_started:
            start_game()
        else:
            setup_environment() # Harita değişmiş olabilir
            
        player.speed = 12 + speed_level
        FloatingText("OYUN YUKLENDI", player.position + Vec3(0,2,0))
        if menu_parent.enabled: toggle_menu()
    else:
        FloatingText("KAYIT BULUNAMADI", player.position + Vec3(0,2,0))

# --- 2. GİRİŞ EKRANI (START MENU) ---
start_menu = Entity(parent=camera.ui)

# Arka Plan Karartma (Görseldeki atmosferi vermek için)
menu_bg = Entity(parent=start_menu, model='quad', scale=(2, 2), color=color.black66)

# Başlık (Görseldeki yazı tipi stili)
title = Text(parent=start_menu, text="SHADOW HUNTER", y=0.3, origin=(0,0), scale=5, color=color.cyan)
subtitle = Text(parent=start_menu, text="ALIEN ECOSYSTEM", y=0.22, origin=(0,0), scale=1.5, color=color.violet)

def start_game():
    global game_started
    game_started = True
    start_menu.enabled = False
    player.enabled = True
    mouse.locked = True
    spawn_entities() # Oyun başlayınca doğurma başlar
    setup_environment()
    background_music.play()

def set_difficulty(diff):
    global current_difficulty
    current_difficulty = diff
    btn_easy.color = color.green if diff == 'KOLAY' else color.gray
    btn_medium.color = color.yellow if diff == 'ORTA' else color.gray
    btn_hard.color = color.red if diff == 'ZOR' else color.gray

def set_map(m):
    global selected_map
    selected_map = m
    btn_dunya.color = color.green if m == 'dunya' else color.gray
    btn_uzay.color = color.violet if m == 'uzay' else color.gray

Text(parent=start_menu, text="ZORLUK SEVIYESI", y=0.15, scale=1.2, color=color.white)
btn_easy = Button(parent=start_menu, text='KOLAY', scale=(0.15, 0.08), position=(-0.2, 0.08), color=color.gray, on_click=lambda: set_difficulty('KOLAY'))
btn_medium = Button(parent=start_menu, text='ORTA', scale=(0.15, 0.08), position=(0, 0.08), color=color.yellow, on_click=lambda: set_difficulty('ORTA'))
btn_hard = Button(parent=start_menu, text='ZOR', scale=(0.15, 0.08), position=(0.2, 0.08), color=color.gray, on_click=lambda: set_difficulty('ZOR'))

Text(parent=start_menu, text="HARITA SECIMI", y=-0.02, scale=1.2, color=color.white)
btn_dunya = Button(parent=start_menu, text='DUNYA', scale=(0.2, 0.08), position=(-0.15, -0.1), color=color.green, on_click=lambda: set_map('dunya'))
btn_uzay = Button(parent=start_menu, text='UZAY', scale=(0.2, 0.08), position=(0.15, -0.1), color=color.gray, on_click=lambda: set_map('uzay'))

start_btn = Button(parent=start_menu, text='OYUNA BASLA', scale=(0.35, 0.08), y=-0.22, color=color.cyan, on_click=start_game)
load_btn_menu = Button(parent=start_menu, text='KAYITLI OYUNU YUKLE', scale=(0.35, 0.08), y=-0.32, color=color.orange, on_click=load_game)
quit_btn = Button(parent=start_menu, text='CIKIS', scale=(0.35, 0.08), y=-0.42, color=color.red, on_click=application.quit)

# --- 3. KOZMİK ÇEVRE (Yıldızlar, Gezegenler, Bitkiler) ---
sky = Sky(color=color.black, visible=False)
stars = []
planet = Entity(model='sphere', color=color.dark_gray, scale=50, position=(150, 80, 200), texture='shore', visible=False)
planet_ring = Entity(parent=planet, model='cube', scale=(1.2, 0.01, 1.2), rotation=(45, 0, 0), color=color.cyan, alpha=0.2, unlit=True)

class Tree(Entity):
    def __init__(self, position):
        super().__init__(position=position, tag='env')
        Entity(parent=self, model='cube', scale=(1, random.uniform(4,8), 1), color=color.brown, y=2, collider='box')
        Entity(parent=self, model='sphere', scale=random.uniform(3,5), color=color.green, y=random.uniform(5,7))

class House(Entity):
    def __init__(self, position):
        super().__init__(position=position, tag='env')
        Entity(parent=self, model='cube', scale=(6, 4, 6), color=color.gray, texture='brick', y=2, collider='box')
        Entity(parent=self, model='cone', scale=(7, 3, 7), color=color.red, y=5)

class Vehicle(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            color=color.orange,
            scale=(2, 1, 4),
            position=position,
            collider='box',
            tag='vehicle'
        )
        self.speed = 30
        self.rotation_speed = 100
        
    def update(self):
        if in_vehicle and self.enabled:
            self.position = player.position - Vec3(0, 1, 0)
            self.rotation_y = player.rotation_y

            if held_keys['w']:
                player.position += player.forward * time.dt * self.speed
            if held_keys['s']:
                player.position -= player.forward * time.dt * self.speed
            if held_keys['a']:
                player.rotation_y -= self.rotation_speed * time.dt
            if held_keys['d']:
                player.rotation_y += self.rotation_speed * time.dt

class TraderNPC(Entity):
    def __init__(self, position):
        super().__init__(
            model='cube',
            color=color.gold,
            scale=(1, 2, 1),
            position=position,
            collider='box',
            tag='env'
        )
        self.text = Text(parent=self, text='TÜCCAR (E)', y=1.2, billboard=True, scale=5, color=color.gold, enabled=False)

    def update(self):
        if distance(self.position, player.position) < 5:
            self.text.enabled = True
        else:
            self.text.enabled = False

class Voxel(Entity):
    def __init__(self, position=(0,0,0), texture='grass'):
        super().__init__(
            parent=scene,
            position=position,
            model='cube',
            origin_y=0.5,
            texture=texture,
            color=color.white,
            collider='box',
            scale=1
        )

def setup_environment():
    # Eski çevre nesnelerini temizle
    for e in scene.entities:
        if hasattr(e, 'tag') and e.tag == 'env':
            destroy(e)
            
    sky.visible = True
    # Bulutlar
    for i in range(20):
        Entity(model='cube', scale=(random.randint(2,5), 1, random.randint(2,5)), color=color.white, position=(random.randint(-100,100), random.randint(20,40), random.randint(-100,100)), alpha=0.8, tag='env')

    if selected_map == 'dunya':
        sky.color = color.azure
        ground.texture = 'grass'
        ground.color = color.white
        planet.visible = False
        scene.fog_density = (0, 100)
        scene.fog_color = color.white
        for s in stars: destroy(s)
        
        # Dunya Nesneleri
        for i in range(30):
            Tree(position=(random.randint(-100,100), 0, random.randint(-100,100)))
        for i in range(5):
            House(position=(random.randint(-80,80), 0, random.randint(-80,80)))
        
        # Tüccar Ekle
        TraderNPC(position=(5, 0, 5))
        
        # Araç Ekle
        Vehicle(position=(10, 1, 10))
            
    elif selected_map == 'uzay':
        sky.color = color.black
        ground.texture = 'white_cube'
        ground.color = color.dark_gray
        planet.visible = True
        scene.fog_density = (0, 200)
        scene.fog_color = color.black
        
        # Yildizlar
        if not stars:
            for i in range(200):
                stars.append(Entity(model='sphere', color=color.white, scale=random.uniform(0.05, 0.1),
                       position=Vec3(random.uniform(-200, 200), random.uniform(20, 100), random.uniform(-200, 200)), unlit=True))

class AlienPlant(Entity):
    def __init__(self, position):
        super().__init__(model=random.choice(['cube', 'sphere', 'cone']), 
                         color=random.choice([color.lime, color.magenta, color.blue, color.violet]),
                         scale=random.uniform(1, 4), position=position, unlit=True)
        self.y += self.scale_y / 2
        if random.random() > 0.6: # Bazı bitkilere parlama ekle
            Entity(parent=self, model='sphere', scale=1.2, color=self.color, alpha=0.1, unlit=True)

# --- 4. YARATIKLAR VE BOSS ---
class EnemyBullet(Entity):
    def __init__(self, position, direction, damage):
        super().__init__(
            model='sphere',
            scale=0.3,
            color=color.red,
            position=position,
            collider='box',
            unlit=True
        )
        self.direction = direction
        self.damage = damage
        self.speed = 20
        self.look_at(self.position + direction)
        destroy(self, delay=3)

    def update(self):
        self.position += self.direction * time.dt * self.speed
        if distance(self.position, player.position) < 1.5:
            damage_player(self.damage)
            destroy(self)
            return
        
        hit_info = self.intersects()
        if hit_info.hit and hit_info.entity != self:
             destroy(self)

class AlienCreature(Entity):
    def __init__(self, position, is_boss=False):
        super().__init__(model='sphere', color=color.black, scale=8 if is_boss else 2.5, position=position, collider='box')
        self.is_boss = is_boss
        
        # AI Tipi Belirleme
        if is_boss:
            self.ai_type = 'boss'
        else:
            self.ai_type = random.choice(['chaser', 'shooter', 'tactical'])
            
        # Görsel farklılık (AI tipini anlamak için)
        if self.ai_type == 'shooter':
            self.color = color.orange
        elif self.ai_type == 'tactical':
            self.color = color.blue
            
        base_hp = 50 if is_boss else 3
        self.hp = base_hp * difficulty_settings[current_difficulty]['hp_mul']
        self.core = Entity(parent=self, model='sphere', scale=0.6, color=color.red if is_boss else color.magenta, unlit=True)
        if is_boss: self.hb = HealthBar(parent=self, y=1.2, scale=(1, 0.1), value=self.hp, max_value=self.hp, color=color.red)
        self.marker = Entity(parent=minimap, model='circle', scale=0.05, color=color.red if is_boss else color.orange)
        
        self.last_shot_time = 0
        self.shoot_cooldown = 2.0 if self.ai_type == 'shooter' else 3.0

    def update(self):
        if not game_started or game_over_state or menu_parent.enabled: return
        
        dist = distance(self.position, player.position)
        self.look_at(player.position)
        # Hareket ve Saldırı Mantığı
        if self.ai_type == 'chaser' or self.ai_type == 'boss':
            self.position += self.forward * time.dt * (3 if self.is_boss else 5 + level)
            if dist < (5 if self.is_boss else 2):
                base_dmg = 0.4 if self.is_boss else 0.1
                damage_player(base_dmg * difficulty_settings[current_difficulty]['dmg_mul'])
                
        elif self.ai_type == 'shooter':
            # Mesafeyi koru (Uzaktan ateş)
            if dist > 15:
                self.position += self.forward * time.dt * (4 + level)
            elif dist < 10:
                self.position -= self.forward * time.dt * (3 + level)
            
            if time.time() - self.last_shot_time > self.shoot_cooldown and dist < 30:
                self.shoot()
                
        elif self.ai_type == 'tactical':
            # Siper alma / Strafe (Yan yan gitme)
            self.position += self.forward * time.dt * (2 + level)
            self.position += self.right * time.dt * math.sin(time.time() * 3) * 5
            
            if dist < 2:
                damage_player(0.1 * difficulty_settings[current_difficulty]['dmg_mul'])
            
            if time.time() - self.last_shot_time > self.shoot_cooldown and dist < 20:
                self.shoot()
            
        # Minimap Guncelleme
        rel_x = self.x - player.x
        rel_z = self.z - player.z
        self.marker.x = rel_x / 100 # 50 birim yaricap
        self.marker.y = rel_z / 100
        self.marker.enabled = abs(self.marker.x) < 0.5 and abs(self.marker.y) < 0.5

    def shoot(self):
        self.last_shot_time = time.time()
        EnemyBullet(position=self.position + Vec3(0,1,0), direction=(player.position - self.position).normalized(), damage=5)

    def get_hit(self, damage):
        self.hp -= damage
        self.blink(color.white, duration=0.1)
        if hasattr(self, 'hb'):
            self.hb.value = self.hp
        if self.hp <= 0 and self.enabled:
            on_enemy_death(self)

# --- 5. OYUNCU VE EKİPMAN ---
player = FirstPersonController(y=2, speed=12, enabled=False) # Başta kapalı

# SİLAH SİSTEMİ
weapons = []
# 1. Kılıç
sword = Entity(parent=camera, model='cube', scale=(.02, .02, 1.3), position=(.5, -.4, .8), color=sword_color, unlit=True)
sword_aura = Entity(parent=sword, model='cube', scale=(1.5, 1.5, 1), color=sword_color, alpha=0.2)
sword.type = 'melee'; sword.damage = 1
weapons.append(sword)

# 2. Tabanca
pistol = Entity(parent=camera, model='cube', scale=(.05, .05, .3), position=(.5, -.4, .8), color=color.gray, unlit=True, visible=False)
pistol.type = 'ranged'; pistol.damage = 2; pistol.ammo = 12; pistol.max_ammo = 12
weapons.append(pistol)

# 3. Lazer
laser = Entity(parent=camera, model='cube', scale=(.05, .05, .8), position=(.5, -.4, .8), color=color.red, unlit=True, visible=False)
laser.type = 'ranged'; laser.damage = 5; laser.ammo = 5; laser.max_ammo = 5
weapons.append(laser)

# 4. İnşaat Aracı (Builder)
builder = Entity(parent=camera, model='cube', scale=(.2, .2, .2), position=(.5, -.4, .8), texture='brick', unlit=True, visible=False)
builder.type = 'builder'; builder.damage = 0
weapons.append(builder)

current_weapon = weapons[0]

hp_bar = HealthBar(bar_color=color.lime, value=100, position=(-0.85, 0.4))
score_display = Text(text='DATA: 0 | LVL: 1', position=(-0.85, 0.45), scale=2, color=color.cyan)
weapon_info = Text(text='[1] KILIC [2] TABANCA [3] LAZER [4] INSAAT', position=(-0.85, 0.38), scale=1, color=color.white)
block_info = Text(text='', position=(-0.85, 0.35), scale=1, color=color.orange)
ammo_text = Text(text='', position=(-0.85, 0.30), scale=1.5, color=color.yellow)
fuel_bar = HealthBar(bar_color=color.azure, value=100, position=(-0.85, 0.33))
Text(text='JETPACK', position=(-0.85, 0.36), scale=0.8, color=color.azure)
stamina_bar = HealthBar(bar_color=color.yellow, value=100, position=(-0.85, 0.26))
Text(text='STAMINA', position=(-0.85, 0.29), scale=0.8, color=color.yellow)
hunger_bar = HealthBar(bar_color=color.rgb(139,69,19), value=100, position=(-0.85, 0.19))
Text(text='ACLIK', position=(-0.85, 0.22), scale=0.8, color=color.rgb(139,69,19))
thirst_bar = HealthBar(bar_color=color.cyan, value=100, position=(-0.85, 0.12))
Text(text='SUSUZLUK', position=(-0.85, 0.15), scale=0.8, color=color.cyan)

# MINIMAP
minimap = Entity(parent=camera.ui, model='quad', scale=(0.2, 0.2), position=(0.75, 0.35), color=color.black90)
minimap_player = Entity(parent=minimap, model='circle', scale=0.05, color=color.green)

ground = Entity(model='plane', scale=1000, texture='white_cube', texture_scale=(100,100), color=color.dark_gray, collider='box')
sun = DirectionalLight()
sun.rotation = (45, 45, 0)

# PAUSE MENU (ESC)
menu_parent = Entity(parent=camera.ui, enabled=False)
menu_bg = Entity(parent=menu_parent, model='quad', scale=(0.4, 0.4), color=color.black90)
Button(parent=menu_bg, text='DEVAM ET', scale=(0.8, 0.15), y=0.25, color=color.lime, on_click=lambda: toggle_menu())
Button(parent=menu_bg, text='KAYDET', scale=(0.8, 0.15), y=0.08, color=color.azure, on_click=save_game)
Button(parent=menu_bg, text='YUKLE', scale=(0.8, 0.15), y=-0.09, color=color.orange, on_click=load_game)
Button(parent=menu_bg, text='CIKIS', scale=(0.8, 0.15), y=-0.26, color=color.red, on_click=application.quit)

# --- ENVANTER SİSTEMİ (I) ---
inventory_parent = Entity(parent=camera.ui, enabled=False)
inventory_bg = Entity(parent=inventory_parent, model='quad', scale=(0.6, 0.7), color=color.black90)
Text(parent=inventory_bg, text="ENVANTER", y=0.4, scale=1.5)

def use_item(item_type):
    global player_hp, player_hunger, player_thirst
    if item_type == 'health_pack':
        if player_inventory.get('health_pack', 0) > 0 and player_hp < max_player_hp:
            player_inventory['health_pack'] -= 1
            player_hp = min(player_hp + 50, max_player_hp)
            hp_bar.value = player_hp
            FloatingText('+50 HP', player.position + Vec3(0,1,0))
            update_inventory_ui()
        else:
            message = 'Can Full!' if player_hp >= max_player_hp else 'Can Paketi Yok!'
            FloatingText(message, player.position + Vec3(0,1,0))
    
    elif item_type == 'ammo_pack':
        if player_inventory.get('ammo_pack', 0) > 0:
            player_inventory['ammo_pack'] -= 1
            for weapon in weapons:
                if hasattr(weapon, 'max_ammo'):
                    weapon.ammo = weapon.max_ammo
            FloatingText('Mermiler Doldu!', player.position + Vec3(0,1,0))
            update_inventory_ui()
        else:
            FloatingText('Mermi Paketi Yok!', player.position + Vec3(0,1,0))
            
    elif item_type == 'food':
        if player_inventory.get('food', 0) > 0 and player_hunger < 100:
            player_inventory['food'] -= 1
            player_hunger = min(player_hunger + 30, 100)
            hunger_bar.value = player_hunger
            FloatingText('+30 Tokluk', player.position + Vec3(0,1,0))
            update_inventory_ui()
        else:
            message = 'Toksun!' if player_hunger >= 100 else 'Yemek Yok!'
            FloatingText(message, player.position + Vec3(0,1,0))
            
    elif item_type == 'water':
        if player_inventory.get('water', 0) > 0 and player_thirst < 100:
            player_inventory['water'] -= 1
            player_thirst = min(player_thirst + 40, 100)
            thirst_bar.value = player_thirst
            FloatingText('+40 Su', player.position + Vec3(0,1,0))
            update_inventory_ui()
        else:
            message = 'Susamadın!' if player_thirst >= 100 else 'Su Yok!'
            FloatingText(message, player.position + Vec3(0,1,0))

health_pack_button = Button(parent=inventory_bg, model='quad', color=color.lime, scale=(0.2, 0.2), position=(-0.2, 0.15), text="KULLAN", on_click=lambda: use_item('health_pack'))
Text(parent=health_pack_button, text="Can Paketi", y=0.6, origin=(0,0), scale=1.2)
health_pack_count_text = Text(parent=health_pack_button, text='x0', y=-0.6, origin=(0,0), scale=1.5)

ammo_pack_button = Button(parent=inventory_bg, model='quad', color=color.yellow, scale=(0.2, 0.2), position=(0.2, 0.15), text="KULLAN", on_click=lambda: use_item('ammo_pack'))
Text(parent=ammo_pack_button, text="Mermi Paketi", y=0.6, origin=(0,0), scale=1.2)
ammo_pack_count_text = Text(parent=ammo_pack_button, text='x0', y=-0.6, origin=(0,0), scale=1.5)

food_button = Button(parent=inventory_bg, model='quad', color=color.orange, scale=(0.2, 0.2), position=(-0.2, -0.1), text="YE", on_click=lambda: use_item('food'))
Text(parent=food_button, text="Yemek", y=0.6, origin=(0,0), scale=1.2)
food_count_text = Text(parent=food_button, text='x0', y=-0.6, origin=(0,0), scale=1.5)

water_button = Button(parent=inventory_bg, model='quad', color=color.blue, scale=(0.2, 0.2), position=(0.2, -0.1), text="IC", on_click=lambda: use_item('water'))
Text(parent=water_button, text="Su", y=0.6, origin=(0,0), scale=1.2)
water_count_text = Text(parent=water_button, text='x0', y=-0.6, origin=(0,0), scale=1.5)

Button(parent=inventory_bg, text='KAPAT', scale=(0.8, 0.1), y=-0.3, color=color.red, on_click=lambda: toggle_inventory())

def update_inventory_ui():
    health_pack_count_text.text = f"x{player_inventory.get('health_pack', 0)}"
    ammo_pack_count_text.text = f"x{player_inventory.get('ammo_pack', 0)}"
    food_count_text.text = f"x{player_inventory.get('food', 0)}"
    water_count_text.text = f"x{player_inventory.get('water', 0)}"

def toggle_night_vision():
    global night_vision_active
    night_vision_active = not night_vision_active
    nv_overlay.enabled = night_vision_active
    
    if night_vision_active:
        scene.fog_density = (0, 50)
        scene.fog_color = color.rgba(0, 200, 0, 100)
        sky.color = color.green
    else:
        setup_environment()

def toggle_inventory():
    if menu_parent.enabled and not inventory_parent.enabled: return
    if skill_tree_parent.enabled and not inventory_parent.enabled: return
    inventory_parent.enabled = not inventory_parent.enabled
    mouse.locked = not inventory_parent.enabled
    if inventory_parent.enabled:
        update_inventory_ui()
        application.pause()
    else:
        application.resume()

# --- YETENEK AĞACI (K) ---
skill_tree_parent = Entity(parent=camera.ui, enabled=False)
skill_bg = Entity(parent=skill_tree_parent, model='quad', scale=(0.6, 0.7), color=color.black90)
Text(parent=skill_bg, text="YETENEK AGACI", y=0.4, scale=1.5)

def buy_upgrade(upgrade_type):
    global score, player_hp, max_player_hp, speed_level, health_level
    
    if upgrade_type == 'speed':
        cost = 1000 * (speed_level + 1)
        if score >= cost:
            score -= cost
            speed_level += 1
            player.speed += 1
            FloatingText(f'HIZ ARTTI! (Lvl {speed_level})', player.position + Vec3(0,1,0))
            update_skill_ui()
        else:
            FloatingText('Yetersiz Puan!', player.position + Vec3(0,1,0))
            
    elif upgrade_type == 'health':
        cost = 1000 * (health_level + 1)
        if score >= cost:
            score -= cost
            health_level += 1
            max_player_hp += 20
            player_hp += 20
            hp_bar.max_value = max_player_hp
            hp_bar.value = player_hp
            FloatingText(f'CAN KAPASITESI ARTTI! (Lvl {health_level})', player.position + Vec3(0,1,0))
            update_skill_ui()
        else:
            FloatingText('Yetersiz Puan!', player.position + Vec3(0,1,0))

btn_speed = Button(parent=skill_bg, text='HIZ (+1)', scale=(0.4, 0.1), y=0.15, color=color.azure, on_click=lambda: buy_upgrade('speed'))
txt_speed_cost = Text(parent=btn_speed, text='Bedel: 1000', y=-0.5, scale=1, origin=(0,0))

btn_health = Button(parent=skill_bg, text='CAN (+20)', scale=(0.4, 0.1), y=-0.05, color=color.red, on_click=lambda: buy_upgrade('health'))
txt_health_cost = Text(parent=btn_health, text='Bedel: 1000', y=-0.5, scale=1, origin=(0,0))

Button(parent=skill_bg, text='KAPAT', scale=(0.8, 0.1), y=-0.3, color=color.red, on_click=lambda: toggle_skill_tree())

def update_skill_ui():
    txt_speed_cost.text = f'Bedel: {1000 * (speed_level + 1)}'
    txt_health_cost.text = f'Bedel: {1000 * (health_level + 1)}'

def toggle_skill_tree():
    if menu_parent.enabled and not skill_tree_parent.enabled: return
    if inventory_parent.enabled and not skill_tree_parent.enabled: return
    
    skill_tree_parent.enabled = not skill_tree_parent.enabled
    mouse.locked = not skill_tree_parent.enabled
    if skill_tree_parent.enabled:
        update_skill_ui()
        application.pause()
    else:
        application.resume()

# --- TİCARET SİSTEMİ (E) ---
trade_parent = Entity(parent=camera.ui, enabled=False)
trade_bg = Entity(parent=trade_parent, model='quad', scale=(0.8, 0.7), color=color.black90)
Text(parent=trade_bg, text="TICARET", y=0.4, scale=1.5)

def buy_trade_item(item_type, cost):
    global score
    if score >= cost:
        score -= cost
        player_inventory[item_type] = player_inventory.get(item_type, 0) + 1
        FloatingText(f'+1 {item_type}', player.position + Vec3(0,1,0))
        update_trade_ui()
    else:
        FloatingText('Yetersiz DATA!', player.position + Vec3(0,1,0))

def sell_trade_item(item_type, value):
    global score
    if player_inventory.get(item_type, 0) > 0:
        player_inventory[item_type] -= 1
        score += value
        FloatingText(f'+{value} DATA', player.position + Vec3(0,1,0))
        update_trade_ui()
    else:
        FloatingText('Eşya Yok!', player.position + Vec3(0,1,0))

Text(parent=trade_bg, text="SATIN AL", x=-0.25, y=0.25, scale=1.2)
Button(parent=trade_bg, text='Can Paketi (500)', scale=(0.3, 0.1), x=-0.25, y=0.1, color=color.green, on_click=lambda: buy_trade_item('health_pack', 500))
Button(parent=trade_bg, text='Mermi Paketi (300)', scale=(0.3, 0.1), x=-0.25, y=-0.05, color=color.azure, on_click=lambda: buy_trade_item('ammo_pack', 300))

Text(parent=trade_bg, text="SAT", x=0.25, y=0.25, scale=1.2)
Button(parent=trade_bg, text='Can Paketi (250)', scale=(0.3, 0.1), x=0.25, y=0.1, color=color.dark_gray, on_click=lambda: sell_trade_item('health_pack', 250))
Button(parent=trade_bg, text='Mermi Paketi (150)', scale=(0.3, 0.1), x=0.25, y=-0.05, color=color.dark_gray, on_click=lambda: sell_trade_item('ammo_pack', 150))

trade_info_text = Text(parent=trade_bg, text='', y=-0.2, scale=1)
Button(parent=trade_bg, text='KAPAT', scale=(0.8, 0.1), y=-0.3, color=color.red, on_click=lambda: toggle_trade())

def update_trade_ui():
    trade_info_text.text = f"DATA: {int(score)} | Can P.: {player_inventory.get('health_pack', 0)} | Mermi P.: {player_inventory.get('ammo_pack', 0)}"

def toggle_trade():
    if menu_parent.enabled and not trade_parent.enabled: return
    if inventory_parent.enabled or skill_tree_parent.enabled: return
    
    trade_parent.enabled = not trade_parent.enabled
    mouse.locked = not trade_parent.enabled
    if trade_parent.enabled:
        update_trade_ui()
        application.pause()
    else:
        application.resume()

# --- CRAFTING SİSTEMİ (C) ---
crafting_parent = Entity(parent=camera.ui, enabled=False)
crafting_bg = Entity(parent=crafting_parent, model='quad', scale=(0.8, 0.7), color=color.black90)
Text(parent=crafting_bg, text="URETIM (CRAFTING)", y=0.4, scale=1.5)

def craft_item(item_type, cost_wood, cost_metal):
    if resources['wood'] >= cost_wood and resources['metal'] >= cost_metal:
        resources['wood'] -= cost_wood
        resources['metal'] -= cost_metal
        player_inventory[item_type] = player_inventory.get(item_type, 0) + 1
        FloatingText(f'+1 {item_type}', player.position + Vec3(0,1,0))
        update_crafting_ui()
    else:
        FloatingText('Yetersiz Kaynak!', player.position + Vec3(0,1,0))

Text(parent=crafting_bg, text="URETILEBILIR ESYALAR", y=0.25, scale=1.2)
Button(parent=crafting_bg, text='Can Paketi (2 Odun)', scale=(0.4, 0.1), y=0.1, color=color.green, on_click=lambda: craft_item('health_pack', 2, 0))
Button(parent=crafting_bg, text='Mermi Paketi (1 Metal)', scale=(0.4, 0.1), y=-0.05, color=color.azure, on_click=lambda: craft_item('ammo_pack', 0, 1))

crafting_info_text = Text(parent=crafting_bg, text='', y=-0.2, scale=1)
Button(parent=crafting_bg, text='KAPAT', scale=(0.8, 0.1), y=-0.3, color=color.red, on_click=lambda: toggle_crafting())

def update_crafting_ui():
    crafting_info_text.text = f"Odun: {resources['wood']} | Metal: {resources['metal']}"

def toggle_crafting():
    if menu_parent.enabled and not crafting_parent.enabled: return
    if inventory_parent.enabled or skill_tree_parent.enabled or trade_parent.enabled: return
    
    crafting_parent.enabled = not crafting_parent.enabled
    mouse.locked = not crafting_parent.enabled
    if crafting_parent.enabled:
        update_crafting_ui()
        application.pause()
    else:
        application.resume()

# --- 6. OYUN MANTIĞI ---

# MODERNİZASYON: Kayan Hasar Yazıları
class FloatingText(Text):
    def __init__(self, text, position):
        super().__init__(
            text=text,
            position=position,
            billboard=True,
            origin=(0,0),
            color=color.red,
            scale=2.5
        )
        self.animate_position(self.position + Vec3(random.uniform(-0.5,0.5), 2, random.uniform(-0.5,0.5)), duration=0.8, curve=curve.out_quad)
        self.animate_color(color.clear, duration=0.8, curve=curve.in_quad)
        destroy(self, delay=0.8)

class Explosion(Entity):
    def __init__(self, position):
        super().__init__(position=position)
        for i in range(8):
            p = Entity(parent=self, model='cube', scale=random.uniform(0.1, 0.4), color=random.choice([color.red, color.orange, color.yellow]), position=Vec3(random.uniform(-0.5,0.5), random.uniform(-0.5,0.5), random.uniform(-0.5,0.5)))
            p.animate_position(p.position + Vec3(random.uniform(-2,2), random.uniform(-2,2), random.uniform(-2,2)), duration=0.5)
            p.animate_scale(0, duration=0.5)
        destroy(self, delay=0.6)

class Loot(Entity):
    def __init__(self, position):
        self.loot_type = random.choice(['health_pack', 'score', 'ammo_pack', 'wood', 'metal', 'food', 'water'])
        
        loot_color = color.yellow
        if self.loot_type == 'health_pack': loot_color = color.lime
        elif self.loot_type == 'ammo_pack': loot_color = color.azure
        elif self.loot_type == 'wood': loot_color = color.brown
        elif self.loot_type == 'metal': loot_color = color.gray
        elif self.loot_type == 'food': loot_color = color.orange
        elif self.loot_type == 'water': loot_color = color.blue

        super().__init__(
            model='cube',
            color=loot_color,
            scale=0.5,
            position=position + Vec3(0, 0.5, 0),
            collider='box'
        )
        self.animate_rotation((0, 360, 0), duration=2, loop=True)

    def update(self):
        if distance(self.position, player.position) < 2:
            if self.loot_type == 'health_pack':
                player_inventory['health_pack'] = player_inventory.get('health_pack', 0) + 1
                FloatingText('+1 Can Paketi', player.position + Vec3(0,1,0))
            elif self.loot_type == 'ammo_pack':
                player_inventory['ammo_pack'] = player_inventory.get('ammo_pack', 0) + 1
                FloatingText('+1 Mermi Paketi', player.position + Vec3(0,1,0))
            elif self.loot_type == 'score':
                global score
                score += 500
                FloatingText('+500 DATA', player.position + Vec3(0,1,0))
            elif self.loot_type == 'wood':
                resources['wood'] += 1
                FloatingText('+1 Odun', player.position + Vec3(0,1,0))
            elif self.loot_type == 'metal':
                resources['metal'] += 1
                FloatingText('+1 Metal', player.position + Vec3(0,1,0))
            elif self.loot_type == 'food':
                player_inventory['food'] = player_inventory.get('food', 0) + 1
                FloatingText('+1 Yemek', player.position + Vec3(0,1,0))
            elif self.loot_type == 'water':
                player_inventory['water'] = player_inventory.get('water', 0) + 1
                FloatingText('+1 Su', player.position + Vec3(0,1,0))
            destroy(self)

def show_achievement_notification(name):
    achievement_sound.play()
    notification = Entity(parent=camera.ui, y=0.6)
    bg = Entity(parent=notification, model='quad', scale=(0.6, 0.12), color=color.black90)
    Text(parent=notification, text=f"🏆 BAŞARIM AÇILDI 🏆\n<gold>{name}", origin=(0,0), scale=1.2)
    
    notification.animate_y(0.4, duration=0.5, curve=curve.out_quad)
    notification.animate_y(0.6, duration=0.5, delay=4, curve=curve.in_quad)
    destroy(notification, delay=4.6)

def check_achievements():
    for key, ach in achievements.items():
        if not ach['unlocked'] and ach['condition']():
            ach['unlocked'] = True
            show_achievement_notification(ach['name'])
            if 'reward' in ach:
                ach['reward']()

def on_enemy_death(enemy):
    global score, level, boss_active, stats
    is_boss = getattr(enemy, 'is_boss', False)
    score += 500 if is_boss else 250
    Explosion(enemy.position)
    stats['kills'] += 1
    
    if is_boss:
        boss_active = False
        stats['boss_kills'] += 1
        destroy(Text(text="BOSS YENILDI!", origin=(0,0), scale=3, color=color.green, background=True), delay=3)
    
    if random.random() < 0.4: # %40 sansla esya duser
        Loot(enemy.position)

    if score // 2000 > level - 1:
        level += 1
        if level % 5 == 0: 
            boss_active = True
            AlienCreature(position=(player.x, 5, player.z + 40), is_boss=True)
            destroy(Text(text="BOSS SAVASI!", origin=(0,0), scale=3, color=color.red, background=True), delay=3)
    if hasattr(enemy, 'marker'):
        destroy(enemy.marker)
    destroy(enemy)

class Bullet(Entity):
    def __init__(self, position, direction, damage):
        super().__init__(
            model='cube',
            scale=(0.05, 0.05, 1),
            color=color.yellow,
            position=position,
            collider='box',
            unlit=True
        )
        self.direction = direction
        self.damage = damage
        self.speed = 50
        self.look_at(self.position + direction)
        destroy(self, delay=2)

    def update(self):
        self.position += self.direction * time.dt * self.speed
        hit_info = self.intersects()
        if hit_info.hit and hasattr(hit_info.entity, 'get_hit'):
            hit_pos = hit_info.entity.world_position
            hit_info.entity.get_hit(self.damage)
            FloatingText(str(self.damage), hit_pos + Vec3(0, 2, 0))
            destroy(self)

def restart_game():
    global player_hp, score, level, game_over_state, boss_active, max_player_hp, speed_level, health_level, player_stamina, stats, player_hunger, player_thirst
    player_hp = 100
    max_player_hp = 100
    score = 0
    level = 1
    speed_level = 0
    health_level = 0
    stats = {'kills': 0, 'boss_kills': 0}
    for key, ach in achievements.items():
        ach['unlocked'] = False
    player_stamina = 100
    player_hunger = 100
    player_thirst = 100
    game_over_state = False
    boss_active = False
    hp_bar.value = 100
    hp_bar.max_value = 100
    stamina_bar.value = 100
    hunger_bar.value = 100
    thirst_bar.value = 100
    player.speed = 12
    restart_btn.enabled = False
    game_over_text.enabled = False
    mouse.locked = True
    player.position = (0, 2, 0)
    for e in scene.entities:
        if isinstance(e, AlienCreature) or isinstance(e, AlienPlant) or isinstance(e, Loot) or isinstance(e, Bullet) or isinstance(e, EnemyBullet):
            destroy(e)
    spawn_entities()

restart_btn = Button(text='YENIDEN BASLA', color=color.azure, scale=(0.3, 0.1), y=-0.2, enabled=False, on_click=restart_game)
game_over_text = Text(text="SISTEM COKTU", origin=(0,0), scale=5, color=color.red, background=True, enabled=False)

def damage_player(amount):
    global player_hp, game_over_state
    player_hp -= amount
    hit_sound.play()
    hp_bar.value = player_hp
    if player_hp <= 0 and not game_over_state:
        game_over_state = True
        game_over_text.enabled = True
        restart_btn.enabled = True
        mouse.locked = False

def toggle_menu():
    if not game_started: return
    if inventory_parent.enabled and not menu_parent.enabled: return
    if skill_tree_parent.enabled and not menu_parent.enabled: return
    if trade_parent.enabled and not menu_parent.enabled: return
    if crafting_parent.enabled and not menu_parent.enabled: return
    menu_parent.enabled = not menu_parent.enabled
    mouse.locked = not menu_parent.enabled
    application.pause() if menu_parent.enabled else application.resume()

def input(key):
    global current_weapon, last_dash_time, current_block_type, in_vehicle
    if key == 'escape': toggle_menu()
    if key == 'i': toggle_inventory()
    if key == 'n': toggle_night_vision()
    if key == 'k': toggle_skill_tree()
    if key == 'e':
        for e in scene.entities:
            if isinstance(e, TraderNPC) and distance(e.position, player.position) < 5:
                toggle_trade()
                break
    if key == 'c': toggle_crafting()
    
    if key == 'f':
        if in_vehicle:
            in_vehicle = False
            player.y += 2
        else:
            for e in scene.entities:
                if hasattr(e, 'tag') and e.tag == 'vehicle' and distance(e.position, player.position) < 5:
                    in_vehicle = True
                    player.position = e.position + Vec3(0, 1, 0)
                    break

    # Menüler açıkken diğer tuşların çalışmasını engelle
    if not game_started or menu_parent.enabled or inventory_parent.enabled or skill_tree_parent.enabled or trade_parent.enabled or crafting_parent.enabled:
        return
    
    if key == '1': current_weapon.visible = False; current_weapon = weapons[0]; current_weapon.visible = True
    if key == '2': current_weapon.visible = False; current_weapon = weapons[1]; current_weapon.visible = True
    if key == '3': current_weapon.visible = False; current_weapon = weapons[2]; current_weapon.visible = True
    if key == '4': current_weapon.visible = False; current_weapon = weapons[3]; current_weapon.visible = True

    if key == 'b': # Blok değiştir
        idx = block_types.index(current_block_type)
        current_block_type = block_types[(idx + 1) % len(block_types)]
        builder.texture = current_block_type

    if key == 'r':
        if current_weapon.type == 'ranged':
            current_weapon.ammo = current_weapon.max_ammo
            FloatingText("RELOADED", player.position + player.forward * 2 + Vec3(0,1,0))

    if key == 'left mouse down' and game_started and not menu_parent.enabled:
        if current_weapon.type == 'melee':
            current_weapon.animate_rotation((60, 0, 0), duration=attack_speed)
            current_weapon.animate_rotation((0, 0, 0), duration=attack_speed, delay=attack_speed)
            sword_swing_sound.play()
            hit_info = mouse.hovered_entity
            if hit_info and hasattr(hit_info, 'get_hit') and distance(player.position, hit_info.position) < 6:
                damage = current_weapon.damage
                hit_pos = hit_info.world_position
                hit_info.get_hit(damage)
                FloatingText(str(damage), hit_pos + Vec3(0, 2, 0))
                camera.shake(magnitude=0.4)
        
        elif current_weapon.type == 'ranged':
            if current_weapon.ammo > 0:
                current_weapon.ammo -= 1
                Bullet(position=camera.world_position + camera.forward * 2, direction=camera.forward, damage=current_weapon.damage)
                current_weapon.animate_position(current_weapon.position + Vec3(0,0,-0.1), duration=0.05)
                current_weapon.animate_position(current_weapon.position, duration=0.05, delay=0.05)
                # Geri tepme (Recoil)
                player.camera_pivot.rotation_x -= 2
                player.camera_pivot.animate_rotation_x(player.camera_pivot.rotation_x + 2, duration=0.2, delay=0.05)

                if current_weapon == pistol:
                    pistol_shot_sound.play()
                elif current_weapon == laser:
                    laser_shot_sound.play()
        
        elif current_weapon.type == 'builder':
            if mouse.hovered_entity and isinstance(mouse.hovered_entity, Voxel):
                destroy(mouse.hovered_entity)

    if key == 'right mouse down' and game_started and not menu_parent.enabled:
        if current_weapon.type == 'builder' and mouse.hovered_entity:
            if isinstance(mouse.hovered_entity, Voxel):
                place_pos = mouse.hovered_entity.position + mouse.normal
            else:
                place_pos = mouse.world_point + mouse.normal
                place_pos = Vec3(math.floor(place_pos.x), math.floor(place_pos.y), math.floor(place_pos.z))
            
            Voxel(position=place_pos, texture=current_block_type)

    # MODERNİZASYON: Dash Mekaniği
    if key == 'left shift' and time.time() - last_dash_time > dash_cooldown:
        dash_direction = player.forward * held_keys['w'] + player.left * held_keys['a'] + player.back * held_keys['s'] + player.right * held_keys['d']
        dash_direction = (dash_direction if dash_direction.length() > 0 else player.forward).normalized()
        player.animate_position(player.position + dash_direction * 15, duration=0.2, curve=curve.out_quad)
        camera.animate('fov', 100, duration=0.2)
        camera.animate('fov', 90, duration=0.1, delay=0.2)
        last_dash_time = time.time()

def spawn_entities():
    if game_started and not game_over_state and not menu_parent.enabled:
        # Rastgele Bitki ve Yaratık Doğurma
        if not boss_active and len([e for e in scene.entities if isinstance(e, AlienCreature)]) < 8:
            AlienCreature(position=(player.x+random.uniform(-30,30), 1.2, player.z+random.uniform(30,60)))
        if len([e for e in scene.entities if isinstance(e, AlienPlant)]) < 40:
            AlienPlant(position=(player.x+random.uniform(-60,60), 0, player.z+random.uniform(-60,60)))
    
    if not game_over_state:
        invoke(spawn_entities, delay=2)

def update():
    if game_started and not menu_parent.enabled:
        planet.rotation_y += 5 * time.dt
        score_display.text = f'DATA: {int(score)} | LVL: {level}'
        
        if current_weapon.type == 'ranged':
            ammo_text.text = f'AMMO: {current_weapon.ammo}/{current_weapon.max_ammo}'
        else:
            ammo_text.text = ''

        if current_weapon.type == 'builder':
            block_info.text = f'BLOK: {current_block_type.upper()} (B ile degistir)'
        else:
            block_info.text = ''

        # Başarımları kontrol et
        check_achievements()

        # Gece-Gündüz Döngüsü
        global day_time
        day_time += time.dt * 10 # Zaman hızı
        sun.rotation_x = day_time
        
        # Işık şiddeti ve gökyüzü rengi
        intensity = max(0.2, -sun.forward.y) 
        
        if night_vision_active:
            sun.intensity = 1.5
            sky.color = color.green
            window.color = color.green
        else:
            sun.intensity = intensity
            if selected_map == 'dunya':
                sky.color = lerp(color.black, color.azure, intensity - 0.2)
            else:
                sky.color = lerp(color.black, color.cyan, intensity - 0.2)
            window.color = sky.color
        
        # Jetpack Mantığı
        global jetpack_fuel
        if held_keys['space'] and jetpack_fuel > 0:
            player.y += 15 * time.dt
            jetpack_fuel -= 40 * time.dt
        else:
            jetpack_fuel += 10 * time.dt
        jetpack_fuel = clamp(jetpack_fuel, 0, 100)
        fuel_bar.value = jetpack_fuel
        
        # Koşma (Sprint) ve Dayanıklılık (Stamina)
        global player_stamina, footstep_timer
        is_moving = held_keys['w'] or held_keys['a'] or held_keys['s'] or held_keys['d']
        
        if held_keys['left shift'] and is_moving and player_stamina > 0 and not in_vehicle:
            player.speed = 20
            player_stamina -= 30 * time.dt
            camera.fov = lerp(camera.fov, 100, 4 * time.dt)
        else:
            player.speed = 12
            player_stamina += 10 * time.dt
            camera.fov = lerp(camera.fov, 90, 4 * time.dt)
            
        player_stamina = clamp(player_stamina, 0, 100)
        stamina_bar.value = player_stamina
        
        # Açlık ve Susuzluk
        global player_hunger, player_thirst
        player_hunger -= time.dt * 0.5 # 200 saniyede biter
        player_thirst -= time.dt * 0.8 # 125 saniyede biter
        
        player_hunger = clamp(player_hunger, 0, 100)
        player_thirst = clamp(player_thirst, 0, 100)
        
        hunger_bar.value = player_hunger
        thirst_bar.value = player_thirst
        
        if player_hunger <= 0 or player_thirst <= 0:
            damage_player(5 * time.dt)
        
        # Ayak Sesleri
        if is_moving and player.grounded:
            footstep_timer -= time.dt
            if footstep_timer <= 0:
                footstep_sound.pitch = random.uniform(0.8, 1.2)
                footstep_sound.play()
                footstep_timer = 0.35 if player.speed > 15 else 0.5
        
        # Hava Durumu (Yagmur/Kar) - Sadece Dunyada
        if selected_map == 'dunya':
            if random.random() < 0.1: # Yagmur efekti
                drop = Entity(model='cube', scale=(0.05, 0.5, 0.05), color=color.rgba(200,200,255,150), 
                              position=player.position + Vec3(random.uniform(-20,20), 20, random.uniform(-20,20)))
                drop.animate_y(player.y - 5, duration=1, curve=curve.linear)
                destroy(drop, delay=1)

app.run()