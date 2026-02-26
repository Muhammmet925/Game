from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar
from ursina.shaders import lit_with_shadows_shader 
import random

app = Ursina()

# --- 1. AYARLAR ---
window.shadows = True
window.color = color.black
window.exit_button.visible = False
Entity.default_shader = lit_with_shadows_shader

# Oyun Değişkenleri
score = 0
player_hp = 100
ammo = 20
resources = {"kristal": 0, "metal": 0}
level = 1
game_time = 0 
game_over_state = False
game_started = False
selected_map = "dunya"

# --- 2. MERMİ VE SİLAH SİSTEMİ ---
class Bullet(Entity):
    def __init__(self, position, direction):
        super().__init__(model='sphere', color=color.cyan, scale=0.2, position=position, collider='box')
        self.direction = direction
        destroy(self, delay=3)

    def update(self):
        self.position += self.direction * time.dt * 50
        hit_info = self.intersects()
        if hit_info.hit:
            if hasattr(hit_info.entity, 'hp'):
                hit_info.entity.hp -= 1
                if hit_info.entity.hp <= 0:
                    spawn_loot(hit_info.entity.position)
                    destroy(hit_info.entity)
            destroy(self)

# --- 3. GANİMET VE CRAFTING ---
def spawn_loot(pos):
    item_type = random.choice(["kristal", "metal"])
    loot = Entity(model='octahedron', color=color.cyan if item_type=="kristal" else color.gray, 
                  scale=0.4, position=pos + Vec3(0,1,0), collider='box')
    loot.item_type = item_type
    loot.animate_y(loot.y + 0.5, duration=1, loop=True, curve=curve.in_out_sine)

class AlienPlant(Entity):
    def __init__(self, position):
        self.hp = 2
        if selected_map == "dunya":
            super().__init__(model='cone', color=color.green, scale=random.uniform(2, 5), position=position, collider='box')
            self.y += self.scale_y / 2
        else:
            is_mushroom = random.random() > 0.4
            if is_mushroom:
                super().__init__(model='sphere', color=random.choice([color.magenta, color.violet, color.cyan]), 
                                 scale=(random.uniform(4, 8), 1.5, random.uniform(4, 8)), 
                                 position=(position[0], random.uniform(4, 7), position[2]), collider='box')
                self.stem = Entity(model='cube', scale=(0.8, self.y, 0.8), color=color.light_gray, position=(self.x, self.y/2, self.z))
            else:
                super().__init__(model='sphere', color=color.lime, scale=random.uniform(1, 3), position=position, unlit=True)

# --- 4. GİRİŞ EKRANI ---
start_menu = Entity(parent=camera.ui)
menu_bg = Entity(parent=start_menu, model='quad', scale=(2, 2), color=color.black66)
title = Text(parent=start_menu, text="SHADOW HUNTER", y=0.3, origin=(0,0), scale=5, color=color.cyan)
map_info = Text(parent=start_menu, text="SECILI HARITA: DUNYA", y=0.15, origin=(0,0), scale=1.5, color=color.lime)

def set_map(map_name):
    global selected_map
    selected_map = map_name
    map_info.text = f"SECILI HARITA: {map_name.upper()}"
    map_info.color = color.lime if map_name == "dunya" else color.violet

Button(parent=start_menu, text='DUNYA', scale=(0.2, 0.05), x=-0.15, y=0.05, on_click=lambda: set_map("dunya"))
Button(parent=start_menu, text='UZAY', scale=(0.2, 0.05), x=0.15, y=0.05, on_click=lambda: set_map("uzay"))

def start_game():
    global game_started
    game_started = True
    start_menu.enabled = False
    player.enabled = True
    mouse.locked = True
    if selected_map == "uzay": 
        planet.enabled = True
        ground.color = color.hex("#1a0033")
    spawn_entities()

Button(parent=start_menu, text='BASLAT', scale=(0.35, 0.08), y=-0.1, color=color.cyan, on_click=start_game)

# --- 5. OYUN DÜNYASI ---
sky = Sky()
sun = DirectionalLight()
sun.look_at(Vec3(1,-1,1))
ground = Entity(model='plane', scale=1000, texture='white_cube', texture_scale=(100,100), collider='box', color=color.green)
planet = Entity(model='sphere', color=color.dark_gray, scale=50, position=(150, 80, 200), enabled=False)

player = FirstPersonController(y=2, speed=12, enabled=False)
sword = Entity(parent=camera, model='cube', scale=(.02, .02, 1), position=(.5, -.4, .8), color=color.cyan)
gun = Entity(parent=camera, model='cube', scale=(.1, .1, .4), position=(.6, -.3, 1), color=color.dark_gray)

hp_bar = HealthBar(bar_color=color.lime, value=100, position=(-0.85, 0.4))
info_panel = Text(text='', position=(-0.85, 0.45), scale=1.5, color=color.cyan)

def input(key):
    global ammo, score
    if not game_started or game_over_state: return

    # SOL TIK: KILIÇ
    if key == 'left mouse down':
        sword.animate_rotation((60, 0, 0), duration=0.1)
        sword.animate_rotation((0, 0, 0), duration=0.1, delay=0.1)
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 1
            if mouse.hovered_entity.hp <= 0:
                spawn_loot(mouse.hovered_entity.position)
                destroy(mouse.hovered_entity)

    # SAĞ TIK: SİLAH ATEŞLEME
    if key == 'right mouse down' and ammo > 0:
        ammo -= 1
        Bullet(position=player.position + Vec3(0,1.5,0) + player.forward, direction=player.forward)
        gun.blink(color.cyan, duration=0.1)

# --- 6. GECE-GÜNDÜZ VE DÖNGÜ ---
def update():
    global game_time, ammo, player_hp
    if not game_started or game_over_state: return

    # Zaman Döngüsü (Hızlandırılmış)
    game_time += time.dt * 0.1
    cycle = (math.sin(game_time) + 1) / 2 # 0 ile 1 arası
    sky.color = color.rgb(cycle*100, cycle*150, cycle*255)
    sun.rotation_x = cycle * 180

    # Loot Toplama
    for e in scene.entities:
        if hasattr(e, 'item_type') and distance(e.position, player.position) < 2:
            resources[e.item_type] += 1
            if e.item_type == "kristal": ammo += 5
            destroy(e)

    info_panel.text = f"AMMO: {ammo} | METAL: {resources['metal']} | KRISTAL: {resources['kristal']}"

class AlienCreature(Entity):
    def __init__(self, position):
        super().__init__(model='sphere', color=color.black, scale=2.5, position=position, collider='box')
        self.hp = 3
    def update(self):
        if not game_started: return
        self.look_at(player.position)
        self.position += self.forward * time.dt * 5
        if distance(self.position, player.position) < 2:
            global player_hp
            player_hp -= 0.1
            hp_bar.value = player_hp

def spawn_entities():
    if game_started and not game_over_state:
        if len([e for e in scene.entities if isinstance(e, AlienCreature)]) < 6:
            AlienCreature(position=(player.x+random.uniform(-30,30), 1, player.z+random.uniform(30,60)))
        if len([e for e in scene.entities if isinstance(e, AlienPlant)]) < 30:
            AlienPlant(position=(player.x+random.uniform(-50,50), 0, player.z+random.uniform(-50,50)))
    invoke(spawn_entities, delay=3)

app.run()