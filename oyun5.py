# SHADOW HUNTER - Enhanced Version with Maps, Trees, Houses, Towers
# =====================================================
from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar
from ursina.shaders import lit_with_shadows_shader
from ursina.shaders import unlit_shader
import random
from panda3d.core import load_prc_file_data
import math

# Quality settings
load_prc_file_data('', 'multisamples 4')
app = Ursina()

# =====================================================
# MAP SETTINGS - Earth and Space
# =====================================================
MAPS = {
    'earth': {
        'name': 'Dunya',
        'sky_color': color.cyan,
        'ground_color': color.green.tint(-.3),
        'fog_color': color.cyan,
        'tree_trunk': color.brown,
        'tree_leaves': color.green,
        'house_wall': color.orange,
        'house_roof': color.red,
        'tower_color': color.gray,
        'plant_colors': [color.green, color.lime, color.green.tint(-.3)],
        'rock_color': color.gray,
        'flower_colors': [color.red, color.yellow, color.magenta]
    },
    'space': {
        'name': 'Uzay',
        'sky_color': color.black,
        'ground_color': color.dark_gray,
        'fog_color': color.violet,
        'tree_trunk': color.violet.tint(.3),
        'tree_leaves': color.violet,
        'house_wall': color.blue.tint(.3),
        'house_roof': color.cyan,
        'tower_color': color.blue.tint(.2),
        'plant_colors': [color.magenta, color.violet, color.cyan],
        'rock_color': color.blue.tint(.5),
        'flower_colors': [color.magenta, color.cyan, color.yellow]
    }
}

current_map = 'earth'

# =====================================================
# SYSTEM SETTINGS
# =====================================================
window.title = 'Shadow Hunter - Enhanced'
window.borderless = False
window.fullscreen = False
window.exit_button.visible = False
window.shadows = True
window.vsync = True
window.fps_counter.enabled = True

Entity.default_shader = lit_with_shadows_shader

# =====================================================
# GAME VARIABLES
# =====================================================
score = 0
player_hp = 100
max_player_hp = 100
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

speed_level = 0
health_level = 0
damage_level = 0

dash_cooldown = 1.5
last_dash_time = -999

player_inventory = {'health_pack': 2, 'ammo_pack': 2}

# =====================================================
# SOUND EFFECTS
# =====================================================
try:
    background_music = Audio('assets/music.mp3', loop=True, autoplay=False, volume=0.3)
    pistol_shot = Audio('assets/pistol.wav', autoplay=False, volume=0.5)
    laser_shot = Audio('assets/laser.wav', autoplay=False, volume=0.4)
    hit_sfx = Audio('assets/hit.wav', autoplay=False, volume=0.6)
    sword_sfx = Audio('assets/sword_swing.wav', autoplay=False, volume=0.5)
except:
    background_music = None
    pistol_shot = None
    laser_shot = None
    hit_sfx = None
    sword_sfx = None

def play_sound(sound):
    if sound:
        sound.play()

# =====================================================
# ENVIRONMENT CLASSES - Using only 'cube' and 'sphere' models
# =====================================================

class Tree(Entity):
    def __init__(self, position, map_type='earth'):
        super().__init__()
        map_data = MAPS[map_type]
        trunk_height = random.uniform(3, 6)
        self.trunk = Entity(
            model='cube',
            color=map_data['tree_trunk'],
            scale=(0.8, trunk_height, 0.8),
            position=position,
            collider='box'
        )
        for i in range(3):
            leaves = Entity(
                parent=self.trunk,
                model='sphere',
                color=map_data['tree_leaves'],
                scale=(random.uniform(2, 3.5), random.uniform(1.5, 2.5), random.uniform(2, 3.5)),
                position=(0, trunk_height/2 + i * 1.2, 0)
            )

class House(Entity):
    def __init__(self, position, map_type='earth'):
        super().__init__()
        map_data = MAPS[map_type]
        if isinstance(position, (tuple, list)):
            px, py, pz = position[0], position[1], position[2]
        else:
            px, py, pz = position.x, position.y, position.z
        self.walls = Entity(
            model='cube',
            color=map_data['house_wall'],
            scale=(4, 3, 4),
            position=(px, py, pz),
            collider='box'
        )
        # Roof - using cube instead of cone
        self.roof = Entity(
            model='cube',
            color=map_data['house_roof'],
            scale=(5, 1.5, 5),
            position=(px, py + 3.5, pz)
        )
        # Door
        Entity(
            model='cube',
            color=color.brown,
            scale=(0.8, 1.8, 0.1),
            position=(px, py + 0.9, pz + 2.05)
        )

class Tower(Entity):
    def __init__(self, position, map_type='earth'):
        super().__init__()
        map_data = MAPS[map_type]
        if isinstance(position, (tuple, list)):
            px, py, pz = position[0], position[1], position[2]
        else:
            px, py, pz = position.x, position.y, position.z
        self.base = Entity(
            model='cube',
            color=map_data['tower_color'],
            scale=(3, 8, 3),
            position=(px, py, pz),
            collider='box'
        )
        # Top platform - using cube instead of cone
        Entity(
            model='cube',
            color=map_data['tower_color'],
            scale=(4, 0.3, 4),
            position=(px, py + 4.15, pz)
        )

class Rock(Entity):
    def __init__(self, position, map_type='earth'):
        super().__init__()
        map_data = MAPS[map_type]
        if isinstance(position, (tuple, list)):
            px, py, pz = position[0], position[1], position[2]
        else:
            px, py, pz = position.x, position.y, position.z
        Entity(
            model='sphere',
            color=map_data['rock_color'],
            scale=(random.uniform(0.5, 1.5), random.uniform(0.3, 0.8), random.uniform(0.5, 1.5)),
            position=(px, py, pz),
            collider='box'
        )

class Flower(Entity):
    def __init__(self, position, map_type='earth'):
        super().__init__()
        map_data = MAPS[map_type]
        if isinstance(position, (tuple, list)):
            px, py, pz = position[0], position[1], position[2]
        else:
            px, py, pz = position.x, position.y, position.z
        flower_color = random.choice(map_data['flower_colors'])
        # Stem - using cube instead of cylinder
        Entity(model='cube', color=color.green, scale=(0.05, 0.5, 0.05), position=(px, py, pz))
        # Flower - using sphere
        Entity(model='sphere', color=flower_color, scale=0.25, position=(px, py + 0.4, pz))

class AlienPlant(Entity):
    def __init__(self, position, map_type='earth'):
        super().__init__()
        map_data = MAPS[map_type]
        plant_color = random.choice(map_data['plant_colors'])
        Entity(
            model=random.choice(['cube', 'sphere']),
            color=plant_color,
            scale=random.uniform(0.5, 2),
            position=position
        )

# =====================================================
# ENEMY CLASSES
# =====================================================

class EnemyBullet(Entity):
    def __init__(self, position, direction, damage):
        super().__init__(
            model='sphere',
            scale=0.3,
            color=color.red,
            position=position,
            collider='box',
            shader=unlit_shader
        )
        self.direction = direction
        self.damage = damage
        self.speed = 25
        self.look_at(self.position + direction)
        destroy(self, delay=3)

    def update(self):
        self.position += self.direction * time.dt * self.speed
        if distance(self.position, player.position) < 1.5:
            damage_player(self.damage)
            destroy(self)
        hit_info = self.intersects()
        if hit_info.hit and hit_info.entity != self:
            destroy(self)

class AlienCreature(Entity):
    def __init__(self, position, is_boss=False):
        super().__init__(
            model='sphere',
            color=color.black,
            scale=8 if is_boss else 2.5,
            position=position,
            collider='box',
            shader=lit_with_shadows_shader
        )
        self.is_boss = is_boss
        if is_boss:
            self.ai_type = 'boss'
        else:
            self.ai_type = random.choice(['chaser', 'shooter', 'tactical'])
        
        if self.ai_type == 'shooter':
            self.color = color.orange
        elif self.ai_type == 'tactical':
            self.color = color.blue
        
        base_hp = 50 if is_boss else 3
        self.hp = base_hp * difficulty_settings[current_difficulty]['hp_mul']
        
        self.core = Entity(parent=self, model='sphere', scale=0.6, color=color.red if is_boss else color.magenta, shader=unlit_shader)
        
        if is_boss:
            self.hb = HealthBar(parent=self, y=1.2, scale=(1, 0.1), value=self.hp, max_value=self.hp, color=color.red)
        
        self.marker = Entity(parent=minimap, model='circle', scale=0.05, color=color.red if is_boss else color.orange)
        
        self.last_shot_time = 0
        self.shoot_cooldown = 2.0 if self.ai_type == 'shooter' else 3.0

    def update(self):
        if not game_started or game_over_state or menu_parent.enabled:
            return
        
        dist = distance(self.position, player.position)
        self.look_at(player.position)
        
        if self.ai_type == 'chaser' or self.ai_type == 'boss':
            self.position += self.forward * time.dt * (3 if self.is_boss else 5 + level)
            if dist < (5 if self.is_boss else 2):
                base_dmg = 0.4 if self.is_boss else 0.1
                damage_player(base_dmg * difficulty_settings[current_difficulty]['dmg_mul'])
        elif self.ai_type == 'shooter':
            if dist > 15:
                self.position += self.forward * time.dt * (4 + level)
            elif dist < 10:
                self.position -= self.forward * time.dt * (3 + level)
            if time.time() - self.last_shot_time > self.shoot_cooldown and dist < 30:
                self.shoot()
        elif self.ai_type == 'tactical':
            self.position += self.forward * time.dt * (2 + level)
            self.position += self.right * time.dt * math.sin(time.time() * 3) * 5
            if dist < 2:
                damage_player(0.1 * difficulty_settings[current_difficulty]['dmg_mul'])
            if time.time() - self.last_shot_time > self.shoot_cooldown and dist < 20:
                self.shoot()
        
        rel_x = self.x - player.x
        rel_z = self.z - player.z
        self.marker.x = rel_x / 100
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

# =====================================================
# PLAYER AND WEAPONS
# =====================================================
player = FirstPersonController(y=2, speed=12, enabled=False)

weapons = []

sword = Entity(parent=camera, model='cube', scale=(0.02, 0.02, 1.3), position=(0.5, -0.4, 0.8), color=sword_color, shader=unlit_shader)
sword_aura = Entity(parent=sword, model='cube', scale=(1.5, 1.5, 1), color=sword_color, alpha=0.2, shader=unlit_shader)
sword.type = 'melee'
sword.damage = 1 + damage_level
weapons.append(sword)

pistol = Entity(parent=camera, model='cube', scale=(0.05, 0.05, 0.3), position=(0.5, -0.4, 0.8), color=color.gray, shader=unlit_shader, visible=False)
pistol.type = 'ranged'
pistol.damage = 2
pistol.ammo = 12
pistol.max_ammo = 12
weapons.append(pistol)

laser = Entity(parent=camera, model='cube', scale=(0.05, 0.05, 0.8), position=(0.5, -0.4, 0.8), color=color.red, shader=unlit_shader, visible=False)
laser.type = 'ranged'
laser.damage = 5
laser.ammo = 5
laser.max_ammo = 5
weapons.append(laser)

current_weapon = weapons[0]

# =====================================================
# UI ELEMENTS
# =====================================================
hp_bar = HealthBar(bar_color=color.lime, value=100, position=(-0.85, 0.4))
score_display = Text(text='DATA: 0 | LVL: 1', position=(-0.85, 0.45), scale=2, color=color.cyan)
weapon_info = Text(text='[1] KILIC [2] TABANCA [3] LAZER', position=(-0.85, 0.38), scale=1, color=color.white)
ammo_text = Text(text='', position=(-0.85, 0.30), scale=1.5, color=color.yellow)
fuel_bar = HealthBar(bar_color=color.azure, value=100, position=(-0.85, 0.33))
Text(text='JETPACK', position=(-0.85, 0.36), scale=0.8, color=color.azure)
minimap = Entity(parent=camera.ui, model='quad', scale=(0.2, 0.2), position=(0.75, 0.35), color=color.black90)
minimap_player_marker = Entity(parent=minimap, model='circle', scale=0.05, color=color.green)

# =====================================================
# START MENU
# =====================================================
start_menu = Entity(parent=camera.ui)
menu_bg = Entity(parent=start_menu, model='quad', scale=(2, 2), color=color.black66)

title = Text(parent=start_menu, text="SHADOW HUNTER", y=0.35, origin=(0, 0), scale=5, color=color.cyan, shader=unlit_shader)
subtitle = Text(parent=start_menu, text="ENHANCED EDITION", y=0.27, origin=(0, 0), scale=1.5, color=color.violet, shader=unlit_shader)

Text(parent=start_menu, text="HARITA SEC", y=0.18, scale=1.2, color=color.white, shader=unlit_shader)

def select_map(map_name):
    global current_map
    current_map = map_name
    btn_earth.color = color.green if map_name == 'earth' else color.gray
    btn_space.color = color.green if map_name == 'space' else color.gray
    update_environment()

btn_earth = Button(parent=start_menu, text='DUNYA', scale=(0.2, 0.08), position=(-0.12, 0.12), color=color.green, on_click=lambda: select_map('earth'))
btn_space = Button(parent=start_menu, text='UZAY', scale=(0.2, 0.08), position=(0.12, 0.12), color=color.gray, on_click=lambda: select_map('space'))

Text(parent=start_menu, text="ZORLUK", y=0.02, scale=1.2, color=color.white, shader=unlit_shader)

def set_difficulty(diff):
    global current_difficulty
    current_difficulty = diff
    btn_easy.color = color.green if diff == 'KOLAY' else color.gray
    btn_medium.color = color.yellow if diff == 'ORTA' else color.gray
    btn_hard.color = color.red if diff == 'ZOR' else color.gray

btn_easy = Button(parent=start_menu, text='KOLAY', scale=(0.12, 0.06), position=(-0.18, -0.06), color=color.gray, on_click=lambda: set_difficulty('KOLAY'))
btn_medium = Button(parent=start_menu, text='ORTA', scale=(0.12, 0.06), position=(0, -0.06), color=color.yellow, on_click=lambda: set_difficulty('ORTA'))
btn_hard = Button(parent=start_menu, text='ZOR', scale=(0.12, 0.06), position=(0.18, -0.06), color=color.gray, on_click=lambda: set_difficulty('ZOR'))

start_btn = Button(parent=start_menu, text='OYUNA BASLA', scale=(0.35, 0.08), position=(0, -0.16), color=color.cyan, on_click=lambda: start_game())
quit_btn = Button(parent=start_menu, text='CIKIS', scale=(0.35, 0.08), position=(0, -0.26), color=color.red, on_click=application.quit)

# =====================================================
# ENVIRONMENT
# =====================================================
sky = Sky()
ground = Entity(model='plane', scale=1000, texture='white_cube', texture_scale=(100, 100), collider='box')
sun = DirectionalLight()
sun.rotation = (45, 45, 0)

environment_objects = []

def update_environment():
    map_data = MAPS[current_map]
    sky.color = map_data['sky_color']
    ground.color = map_data['ground_color']
    if current_map == 'space':
        scene.fog_density = 0.02
        scene.fog_color = map_data['fog_color']
    else:
        scene.fog_density = 0.01
        scene.fog_color = map_data['fog_color']
    
    for obj in environment_objects:
        destroy(obj)
    environment_objects.clear()
    generate_environment()

def generate_environment():
    map_data = MAPS[current_map]
    for _ in range(30):
        x = random.uniform(-80, 80)
        z = random.uniform(-80, 80)
        if abs(x) > 5 or abs(z) > 5:
            tree = Tree(position=(x, 0, z), map_type=current_map)
            environment_objects.append(tree.trunk)
    for _ in range(10):
        x = random.uniform(-60, 60)
        z = random.uniform(-60, 60)
        if abs(x) > 10 or abs(z) > 10:
            house = House(position=(x, 1.5, z), map_type=current_map)
            environment_objects.append(house.walls)
            environment_objects.append(house.roof)
    for _ in range(5):
        x = random.uniform(-70, 70)
        z = random.uniform(-70, 70)
        if abs(x) > 15 or abs(z) > 15:
            tower = Tower(position=(x, 4, z), map_type=current_map)
            environment_objects.append(tower.base)
    for _ in range(20):
        x = random.uniform(-70, 70)
        z = random.uniform(-70, 70)
        rock = Rock(position=(x, 0.3, z), map_type=current_map)
        environment_objects.append(rock)
    for _ in range(30):
        x = random.uniform(-50, 50)
        z = random.uniform(-50, 50)
        if abs(x) > 3 or abs(z) > 3:
            flower = Flower(position=(x, 0.25, z), map_type=current_map)
            environment_objects.append(flower)

# =====================================================
# GAME FUNCTIONS
# =====================================================

def start_game():
    global game_started
    game_started = True
    start_menu.enabled = False
    player.enabled = True
    mouse.locked = True
    update_environment()
    spawn_entities()
    if background_music:
        background_music.play()

def spawn_entities():
    if game_started and not game_over_state and not menu_parent.enabled:
        if not boss_active:
            enemy_count = len([e for e in scene.entities if isinstance(e, AlienCreature)])
            if enemy_count < 8:
                x = player.x + random.uniform(-30, 30)
                z = player.z + random.uniform(30, 60)
                AlienCreature(position=(x, 1.2, z))
        plant_count = len([e for e in scene.entities if isinstance(e, AlienPlant)])
        if plant_count < 40:
            x = player.x + random.uniform(-60, 60)
            z = player.z + random.uniform(-60, 60)
            AlienPlant(position=(x, 0.5, z), map_type=current_map)
    if not game_over_state:
        invoke(spawn_entities, delay=2)

# =====================================================
# MENUS
# =====================================================

menu_parent = Entity(parent=camera.ui, enabled=False)
pause_bg = Entity(parent=menu_parent, model='quad', scale=(0.4, 0.4), color=color.black90)
Button(parent=pause_bg, text='DEVAM ET', scale=(0.8, 0.2), y=0.15, color=color.lime, on_click=lambda: toggle_menu())
Button(parent=pause_bg, text='CIKIS', scale=(0.8, 0.2), y=-0.15, color=color.red, on_click=application.quit)

inventory_parent = Entity(parent=camera.ui, enabled=False)
inventory_bg = Entity(parent=inventory_parent, model='quad', scale=(0.6, 0.7), color=color.black90)
Text(parent=inventory_bg, text="ENVANTER", y=0.4, scale=1.5, shader=unlit_shader)

health_pack_btn = Button(parent=inventory_bg, model='quad', color=color.lime, scale=(0.2, 0.2), position=(-0.2, 0.05), on_click=lambda: use_item('health_pack'))
Text(parent=health_pack_btn, text="Can Paketi\nKullan", y=0.6, origin=(0, 0), scale=1, shader=unlit_shader)
health_pack_count = Text(parent=health_pack_btn, text='x2', y=-0.6, origin=(0, 0), scale=1.5, shader=unlit_shader)

ammo_pack_btn = Button(parent=inventory_bg, model='quad', color=color.yellow, scale=(0.2, 0.2), position=(0.2, 0.05), on_click=lambda: use_item('ammo_pack'))
Text(parent=ammo_pack_btn, text="Mermi Paketi\nKullan", y=0.6, origin=(0, 0), scale=1, shader=unlit_shader)
ammo_pack_count = Text(parent=ammo_pack_btn, text='x2', y=-0.6, origin=(0, 0), scale=1.5, shader=unlit_shader)

Button(parent=inventory_bg, text='KAPAT', scale=(0.8, 0.1), y=-0.3, color=color.red, on_click=lambda: toggle_inventory())

def use_item(item_type):
    global player_hp
    if item_type == 'health_pack':
        if player_inventory.get('health_pack', 0) > 0 and player_hp < max_player_hp:
            player_inventory['health_pack'] -= 1
            player_hp = min(player_hp + 50, max_player_hp)
            hp_bar.value = player_hp
            FloatingText('+50 HP', player.position + Vec3(0, 1, 0))
            update_inventory_ui()
        else:
            msg = 'Can Full!' if player_hp >= max_player_hp else 'Can Paketi Yok!'
            FloatingText(msg, player.position + Vec3(0, 1, 0))
    elif item_type == 'ammo_pack':
        if player_inventory.get('ammo_pack', 0) > 0:
            player_inventory['ammo_pack'] -= 1
            for weapon in weapons:
                if hasattr(weapon, 'max_ammo'):
                    weapon.ammo = weapon.max_ammo
            FloatingText('Mermiler Doldu!', player.position + Vec3(0, 1, 0))
            update_inventory_ui()
        else:
            FloatingText('Mermi Paketi Yok!', player.position + Vec3(0, 1, 0))

def update_inventory_ui():
    health_pack_count.text = f"x{player_inventory.get('health_pack', 0)}"
    ammo_pack_count.text = f"x{player_inventory.get('ammo_pack', 0)}"

def toggle_inventory():
    if menu_parent.enabled and not inventory_parent.enabled:
        return
    inventory_parent.enabled = not inventory_parent.enabled
    mouse.locked = not inventory_parent.enabled
    if inventory_parent.enabled:
        update_inventory_ui()
        application.pause()
    else:
        application.resume()

# Skill tree
skill_parent = Entity(parent=camera.ui, enabled=False)
skill_bg = Entity(parent=skill_parent, model='quad', scale=(0.6, 0.7), color=color.black90)
Text(parent=skill_bg, text="YETENEK AGACI", y=0.4, scale=1.5, shader=unlit_shader)

def buy_upgrade(upgrade_type):
    global score, max_player_hp, player_hp, speed_level, health_level, damage_level
    if upgrade_type == 'speed':
        cost = 1000 * (speed_level + 1)
        if score >= cost:
            score -= cost
            speed_level += 1
            player.speed += 1
            FloatingText(f'HIZ ARTTI! (Lvl {speed_level})', player.position + Vec3(0, 1, 0))
            update_skill_ui()
        else:
            FloatingText('Yetersiz Puan!', player.position + Vec3(0, 1, 0))
    elif upgrade_type == 'health':
        cost = 1000 * (health_level + 1)
        if score >= cost:
            score -= cost
            health_level += 1
            max_player_hp += 20
            player_hp += 20
            hp_bar.max_value = max_player_hp
            hp_bar.value = player_hp
            FloatingText(f'CAN ARTTI! (Lvl {health_level})', player.position + Vec3(0, 1, 0))
            update_skill_ui()
        else:
            FloatingText('Yetersiz Puan!', player.position + Vec3(0, 1, 0))
    elif upgrade_type == 'damage':
        cost = 1500 * (damage_level + 1)
        if score >= cost:
            score -= cost
            damage_level += 1
            sword.damage = 1 + damage_level
            FloatingText(f'HASAR ARTTI! (Lvl {damage_level})', player.position + Vec3(0, 1, 0))
            update_skill_ui()
        else:
            FloatingText('Yetersiz Puan!', player.position + Vec3(0, 1, 0))

btn_speed = Button(parent=skill_bg, text='HIZ (+1) - 1000', scale=(0.5, 0.1), y=0.15, color=color.azure, on_click=lambda: buy_upgrade('speed'))
btn_health = Button(parent=skill_bg, text='CAN (+20) - 1000', scale=(0.5, 0.1), y=0, color=color.red, on_click=lambda: buy_upgrade('health'))
btn_damage = Button(parent=skill_bg, text='HASAR (+1) - 1500', scale=(0.5, 0.1), y=-0.15, color=color.orange, on_click=lambda: buy_upgrade('damage'))
Button(parent=skill_bg, text='KAPAT', scale=(0.8, 0.1), y=-0.3, color=color.red, on_click=lambda: toggle_skill_tree())

def update_skill_ui():
    btn_speed.text = f'HIZ (+1) - {1000 * (speed_level + 1)}'
    btn_health.text = f'CAN (+20) - {1000 * (health_level + 1)}'
    btn_damage.text = f'HASAR (+1) - {1500 * (damage_level + 1)}'

def toggle_skill_tree():
    if menu_parent.enabled and not skill_parent.enabled:
        return
    if inventory_parent.enabled and not skill_parent.enabled:
        return
    skill_parent.enabled = not skill_parent.enabled
    mouse.locked = not skill_parent.enabled
    if skill_parent.enabled:
        update_skill_ui()
        application.pause()
    else:
        application.resume()

# =====================================================
# GAME MECHANICS
# =====================================================

class FloatingText(Text):
    def __init__(self, text, position):
        super().__init__(text=text, position=position, billboard=True, origin=(0, 0), color=color.red, scale=2.5, shader=unlit_shader)
        self.animate_position(self.position + Vec3(random.uniform(-0.5, 0.5), 2, random.uniform(-0.5, 0.5)), duration=0.8, curve=curve.out_quad)
        self.animate_color(color.clear, duration=0.8, curve=curve.in_quad)
        destroy(self, delay=0.8)

class Explosion(Entity):
    def __init__(self, position):
        super().__init__(position=position)
        for _ in range(8):
            p = Entity(parent=self, model='cube', scale=random.uniform(0.1, 0.4), color=random.choice([color.red, color.orange, color.yellow]), position=Vec3(random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5), random.uniform(-0.5, 0.5)), shader=unlit_shader)
            p.animate_position(p.position + Vec3(random.uniform(-2, 2), random.uniform(-2, 2), random.uniform(-2, 2)), duration=0.5)
            p.animate_scale(0, duration=0.5)
        destroy(self, delay=0.6)

class Loot(Entity):
    def __init__(self, position):
        self.loot_type = random.choice(['health_pack', 'score', 'ammo_pack'])
        loot_color = color.yellow
        if self.loot_type == 'health_pack':
            loot_color = color.lime
        elif self.loot_type == 'ammo_pack':
            loot_color = color.azure
        super().__init__(model='cube', color=loot_color, scale=0.5, position=position + Vec3(0, 0.5, 0), collider='box', shader=unlit_shader)
        self.animate_rotation((0, 360, 0), duration=2, loop=True)

    def update(self):
        if distance(self.position, player.position) < 2:
            if self.loot_type == 'health_pack':
                player_inventory['health_pack'] = player_inventory.get('health_pack', 0) + 1
                FloatingText('+1 Can Paketi', player.position + Vec3(0, 1, 0))
            elif self.loot_type == 'ammo_pack':
                player_inventory['ammo_pack'] = player_inventory.get('ammo_pack', 0) + 1
                FloatingText('+1 Mermi Paketi', player.position + Vec3(0, 1, 0))
            elif self.loot_type == 'score':
                global score
                score += 500
                FloatingText('+500 DATA', player.position + Vec3(0, 1, 0))
            destroy(self)

def on_enemy_death(enemy):
    global score, level, boss_active
    is_boss = getattr(enemy, 'is_boss', False)
    score += 500 if is_boss else 250
    Explosion(enemy.position)
    if is_boss:
        boss_active = False
        destroy(Text(text="BOSS YENILDI!", origin=(0, 0), scale=3, color=color.green, background=True, shader=unlit_shader), delay=3)
    if random.random() < 0.4:
        Loot(enemy.position)
    if score // 2000 > level - 1:
        level += 1
        if level % 5 == 0:
            boss_active = True
            AlienCreature(position=(player.x, 5, player.z + 40), is_boss=True)
            destroy(Text(text="BOSS SAVASI!", origin=(0, 0), scale=3, color=color.red, background=True, shader=unlit_shader), delay=3)
    if hasattr(enemy, 'marker'):
        destroy(enemy.marker)
    destroy(enemy)

class Bullet(Entity):
    def __init__(self, position, direction, damage):
        super().__init__(model='cube', scale=(0.05, 0.05, 1), color=color.yellow, position=position, collider='box', shader=unlit_shader)
        self.direction = direction
        self.damage = damage
        self.speed = 50
        self.look_at(self.position + direction)
        destroy(self, delay=2)

    def update(self):
        self.position += self.direction * time.dt * self.speed
        hit_info = self.intersects()
        if hit_info.hit and hasattr(hit_info.entity, 'get_hit'):
            enemy_pos = hit_info.entity.world_position + Vec3(0, 2, 0)
            hit_info.entity.get_hit(self.damage)
            if hit_info.entity and hit_info.entity.enabled:
                FloatingText(str(self.damage), enemy_pos)
            destroy(self)

def restart_game():
    global player_hp, score, level, game_over_state, boss_active, max_player_hp, speed_level, health_level, damage_level
    player_hp = 100
    max_player_hp = 100
    score = 0
    level = 1
    speed_level = 0
    health_level = 0
    damage_level = 0
    game_over_state = False
    boss_active = False
    hp_bar.value = 100
    hp_bar.max_value = 100
    player.speed = 12
    sword.damage = 1
    restart_btn.enabled = False
    game_over_text.enabled = False
    mouse.locked = True
    player.position = (0, 2, 0)
    for e in scene.entities:
        if isinstance(e, (AlienCreature, AlienPlant, Loot, Bullet, EnemyBullet)):
            destroy(e)
    spawn_entities()

restart_btn = Button(text='YENIDEN BASLA', color=color.azure, scale=(0.3, 0.1), y=-0.2, enabled=False, on_click=restart_game)
game_over_text = Text(text="SISTEM COKTU", origin=(0, 0), scale=5, color=color.red, background=True, enabled=False, shader=unlit_shader)

def damage_player(amount):
    global player_hp
    player_hp -= amount
    play_sound(hit_sfx)
    hp_bar.value = player_hp
    if player_hp <= 0 and not game_over_state:
        game_over_state = True
        game_over_text.enabled = True
        restart_btn.enabled = True
        mouse.locked = False

def toggle_menu():
    if not game_started:
        return
    menu_parent.enabled = not menu_parent.enabled
    mouse.locked = not menu_parent.enabled
    application.pause() if menu_parent.enabled else application.resume()

# =====================================================
# INPUT HANDLING
# =====================================================

def input(key):
    global current_weapon, last_dash_time
    if key == 'escape':
        toggle_menu()
    if key == 'i':
        toggle_inventory()
    if key == 'k':
        toggle_skill_tree()
    if not game_started or menu_parent.enabled or inventory_parent.enabled or skill_parent.enabled:
        return
    if key == '1':
        current_weapon.visible = False
        current_weapon = weapons[0]
        current_weapon.visible = True
    if key == '2':
        current_weapon.visible = False
        current_weapon = weapons[1]
        current_weapon.visible = True
    if key == '3':
        current_weapon.visible = False
        current_weapon = weapons[2]
        current_weapon.visible = True
    if key == 'r':
        if current_weapon.type == 'ranged':
            current_weapon.ammo = current_weapon.max_ammo
            FloatingText("RELOADED", player.position + player.forward * 2 + Vec3(0, 1, 0))
    if key == 'left mouse down' and game_started and not menu_parent.enabled:
        if current_weapon.type == 'melee':
            current_weapon.animate_rotation((60, 0, 0), duration=attack_speed)
            current_weapon.animate_rotation((0, 0, 0), duration=attack_speed, delay=attack_speed)
            play_sound(sword_sfx)
            hit_info = mouse.hovered_entity
            if hit_info and hasattr(hit_info, 'get_hit') and distance(player.position, hit_info.position) < 6:
                dmg = current_weapon.damage
                hit_info.get_hit(dmg)
                enemy_pos = hit_info.world_position + Vec3(0, 2, 0)
                if hit_info and hit_info.enabled:
                    FloatingText(str(dmg), enemy_pos)
                camera.shake(magnitude=0.4)
        elif current_weapon.type == 'ranged':
            if current_weapon.ammo > 0:
                current_weapon.ammo -= 1
                Bullet(position=camera.world_position + camera.forward * 2, direction=camera.forward, damage=current_weapon.damage)
                current_weapon.animate_position(current_weapon.position + Vec3(0, 0, -0.1), duration=0.05)
                current_weapon.animate_position(current_weapon.position, duration=0.05, delay=0.05)
                player.camera_pivot.rotation_x -= 2
                player.camera_pivot.animate_rotation_x(player.camera_pivot.rotation_x + 2, duration=0.2, delay=0.05)
                if current_weapon == pistol:
                    play_sound(pistol_shot)
                elif current_weapon == laser:
                    play_sound(laser_shot)
            else:
                FloatingText("NO AMMO! (R)", player.position + player.forward * 2 + Vec3(0, 1, 0))
    if key == 'left shift' and time.time() - last_dash_time > dash_cooldown:
        dash_dir = player.forward * held_keys['w'] + player.left * held_keys['a'] + player.back * held_keys['s'] + player.right * held_keys['d']
        dash_dir = (dash_dir if dash_dir.length() > 0 else player.forward).normalized()
        player.animate_position(player.position + dash_dir * 15, duration=0.2, curve=curve.out_quad)
        # Dash effect - screen shake instead of fov change
        camera.shake(magnitude=0.3)
        last_dash_time = time.time()

# =====================================================
# UPDATE LOOP
# =====================================================

def update():
    if game_started and not menu_parent.enabled:
        score_display.text = f'DATA: {int(score)} | LVL: {level}'
        if current_weapon.type == 'ranged':
            ammo_text.text = f'AMMO: {current_weapon.ammo}/{current_weapon.max_ammo}'
        else:
            ammo_text.text = ''
        global day_time
        day_time += time.dt * 10
        sun.rotation_x = day_time
        intensity = max(0.2, -sun.forward.y)
        sun.intensity = intensity
        sky.color = lerp(color.black, MAPS[current_map]['sky_color'], intensity - 0.2)
        global jetpack_fuel
        if held_keys['space'] and jetpack_fuel > 0:
            player.y += 15 * time.dt
            jetpack_fuel -= 40 * time.dt
        else:
            jetpack_fuel += 10 * time.dt
        jetpack_fuel = clamp(jetpack_fuel, 0, 100)
        fuel_bar.value = jetpack_fuel

# =====================================================
# RUN THE GAME
# =====================================================
app.run()
