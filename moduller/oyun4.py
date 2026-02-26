from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.prefabs.health_bar import HealthBar
from ursina.shaders import lit_with_shadows_shader 
import random

app = Ursina()

# --- 1. SİSTEM VE EKRAN AYARLARI ---
window.shadows = True
window.color = color.black
window.exit_button.visible = False
Entity.default_shader = lit_with_shadows_shader
scene.fog_color = color.black
scene.fog_density = (10, 50)

# Oyun Değişkenleri
score = 0
player_hp = 100
level = 1
attack_speed = 0.1
sword_color = color.cyan
game_over_state = False
game_started = False
selected_map = "dunya"

# --- 2. GİRİŞ VE HARİTA SEÇİM EKRANI ---
start_menu = Entity(parent=camera.ui)
menu_bg = Entity(parent=start_menu, model='quad', scale=(2, 2), color=color.black66)

title = Text(parent=start_menu, text="SHADOW HUNTER", y=0.3, origin=(0,0), scale=5, color=color.cyan)
subtitle = Text(parent=start_menu, text="ALIEN ECOSYSTEM", y=0.22, origin=(0,0), scale=1.5, color=color.violet)

map_info = Text(parent=start_menu, text="SECILI HARITA: DUNYA", y=0.12, origin=(0,0), scale=1.2, color=color.lime)

def set_map(m):
    global selected_map
    selected_map = m
    map_info.text = f"SECILI HARITA: {m.upper()}"
    map_info.color = color.lime if m == "dunya" else color.magenta

Button(parent=start_menu, text='DUNYA SEKTORU', scale=(0.2, 0.05), x=-0.15, y=0.02, on_click=lambda: set_map("dunya"))
Button(parent=start_menu, text='UZAY SEKTORU', scale=(0.2, 0.05), x=0.15, y=0.02, on_click=lambda: set_map("uzay"))

def start_game():
    global game_started
    game_started = True
    start_menu.enabled = False
    player.enabled = True
    mouse.locked = True
    setup_environment()
    spawn_entities()

start_btn = Button(parent=start_menu, text='AVLANMAYA BASLA', scale=(0.35, 0.08), y=-0.1, color=color.cyan, on_click=start_game)

# --- 3. ÇEVRE VE BİTKİ ÖRTÜSÜ SİSTEMİ ---
sky = Sky()
ground = Entity(model='plane', scale=1000, texture='white_cube', texture_scale=(100,100), collider='box')
planet = Entity(model='sphere', color=color.dark_gray, scale=50, position=(150, 80, 200), enabled=False)

def setup_environment():
    if selected_map == "dunya":
        sky.color = color.light_gray
        ground.color = color.green
        ground.texture = 'grass'
    else:
        sky.color = color.black
        ground.color = color.hex("#1a0033") 
        planet.enabled = True
        # Yıldızlar
        for i in range(100):
            Entity(model='sphere', color=color.white, scale=0.1, 
                   position=Vec3(random.uniform(-150,150), random.uniform(20,80), random.uniform(-150,150)), unlit=True)

class AlienPlant(Entity):
    def __init__(self, position):
        super().__init__(position=position)
        self.hp = 2
        
        if selected_map == "dunya":
            # Dünya: Klasik Ağaçlar
            self.model = 'cone'
            self.color = color.green
            self.scale = random.uniform(2, 5)
        else:
            # Uzay: DEV MANTARLAR VE EGZOTİK BİTKİLER
            if random.random() > 0.5: # Mantar Tasarımı
                self.model = 'sphere'
                self.color = random.choice([color.magenta, color.violet, color.cyan])
                self.scale = (random.uniform(4,8), 1.5, random.uniform(4,8))
                self.y = random.uniform(4, 7)
                # Mantar Sapı
                Entity(model='cube', scale=(0.8, self.y, 0.8), color=color.light_gray, position=(self.x, self.y/2, self.z))
            else: # Egzotik Bitki
                self.model = 'sphere'
                self.color = color.lime
                self.scale = random.uniform(1, 3)
                Entity(parent=self, model='sphere', scale=1.2, color=self.color, alpha=0.1, unlit=True)

# --- 4. YARATIKLAR ---
class AlienCreature(Entity):
    def __init__(self, position, is_boss=False):
        super().__init__(model='sphere', color=color.black, scale=8 if is_boss else 2.5, position=position, collider='box')
        self.is_boss = is_boss
        self.hp = 50 if is_boss else 3
        self.core = Entity(parent=self, model='sphere', scale=0.6, 
                          color=color.red if is_boss else random.choice([color.magenta, color.cyan, color.lime]), unlit=True)
        if is_boss: self.hb = HealthBar(parent=self, y=1.2, scale=(1, 0.1), value=50, max_value=50, color=color.red)

    def update(self):
        if not game_started or game_over_state or menu_parent.enabled: return
        self.look_at(player.position)
        self.position += self.forward * time.dt * (3 if self.is_boss else 5 + level)
        if distance(self.position, player.position) < (5 if self.is_boss else 2):
            damage_player(0.4 if self.is_boss else 0.1)

# --- 5. OYUNCU VE KONTROLLER ---
player = FirstPersonController(y=2, speed=12, enabled=False)
sword = Entity(parent=camera, model='cube', scale=(.02, .02, 1.3), position=(.5, -.4, .8), color=sword_color, unlit=True)
sword_aura = Entity(parent=sword, model='cube', scale=(1.5, 1.5, 1), color=sword_color, alpha=0.2)

hp_bar = HealthBar(bar_color=color.lime, value=100, position=(-0.85, 0.4))
score_display = Text(text='DATA: 0 | LVL: 1', position=(-0.85, 0.45), scale=2, color=color.cyan)

menu_parent = Entity(parent=camera.ui, enabled=False)
pause_bg = Entity(parent=menu_parent, model='quad', scale=(0.4, 0.4), color=color.black90)
Button(parent=pause_bg, text='DEVAM ET', scale=(0.8, 0.2), y=0.15, color=color.lime, on_click=lambda: toggle_menu())
Button(parent=pause_bg, text='CIKIS', scale=(0.8, 0.2), y=-0.15, color=color.red, on_click=application.quit)

def damage_player(amount):
    global player_hp, game_over_state
    player_hp -= amount
    hp_bar.value = player_hp
    if player_hp <= 0 and not game_over_state:
        game_over_state = True
        Text(text="SISTEM COKTU", origin=(0,0), scale=5, color=color.red, background=True)

def toggle_menu():
    if not game_started: return
    menu_parent.enabled = not menu_parent.enabled
    mouse.locked = not menu_parent.enabled
    application.pause() if menu_parent.enabled else application.resume()

def input(key):
    global score, level
    if key == 'escape': toggle_menu()
    
    if key == 'left mouse down' and game_started and not menu_parent.enabled:
        sword.animate_rotation((60, 0, 0), duration=attack_speed)
        sword.animate_rotation((0, 0, 0), duration=attack_speed, delay=attack_speed)
        
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'hp'):
            mouse.hovered_entity.hp -= 1
            camera.shake(magnitude=0.4)
            if mouse.hovered_entity.hp <= 0:
                score += 500 if getattr(mouse.hovered_entity, 'is_boss', False) else 250
                if score // 2000 > level - 1:
                    level += 1
                    if level % 5 == 0: AlienCreature(position=(player.x, 5, player.z + 40), is_boss=True)
                destroy(mouse.hovered_entity)

def spawn_entities():
    if game_started and not game_over_state and not menu_parent.enabled:
        if len([e for e in scene.entities if isinstance(e, AlienCreature)]) < 8:
            AlienCreature(position=(player.x+random.uniform(-30,30), 1.2, player.z+random.uniform(30,60)))
        if len([e for e in scene.entities if isinstance(e, AlienPlant)]) < 30:
            AlienPlant(position=(player.x+random.uniform(-60,60), 0, player.z+random.uniform(-60,60)))
    
    if not game_over_state:
        invoke(spawn_entities, delay=2)

def update():
    if game_started and not menu_parent.enabled:
        if planet.enabled: planet.rotation_y += 5 * time.dt
        score_display.text = f'DATA: {int(score)} | LVL: {level}'

app.run()