import pygame
import random
import array

from pygame.math import Vector2

pygame.init()

# Ekran Ayarları
WIDTH, HEIGHT = 900, 650
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("⚽ SUPER FUTBOL - Turnuva Modu")

# Renkler
COLORS = {
    'green': (34, 139, 34),
    'dark_green': (0, 100, 0),
    'white': (255, 255, 255),
    'red': (200, 0, 0),
    'blue': (0, 0, 200),
    'black': (0, 0, 0),
    'yellow': (255, 255, 0),
    'gold': (255, 215, 0),
    'purple': (128, 0, 128),
    'orange': (255, 165, 0),
    'gray': (100, 100, 100),
}

# Ses Efektleri
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
    
    def create_sound(freq, duration, volume=0.3):
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buffer = array.array('h', [int(8000 * (1 if (t % (sample_rate // freq)) < (sample_rate // freq) // 2 else -1)) for t in range(n_samples)])
        return pygame.mixer.Sound(buffer=buffer)
    
    whistle_sound = create_sound(800, 0.3, 0.4)
    kick_sound = create_sound(200, 0.1, 0.5)
    goal_sound = create_sound(600, 0.5, 0.6)
except:
    whistle_sound = None
    kick_sound = None
    goal_sound = None

# Oyun Modları
class GameMode:
    NORMAL = 'normal'
    PENALTY = 'penalty'
    TOURNAMENT = 'tournament'

# Oyuncu Sınıfı
class Player:
    def __init__(self, x, y, color, is_ai=False):
        self.start_pos = Vector2(x, y)
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.color = color
        self.radius = 20
        self.speed = 5
        self.is_ai = is_ai
        self.power = 100
        self.stamina = 100
        self.dribble_skill = random.randint(50, 80)
    
    def reset(self):
        self.pos = Vector2(self.start_pos)
        self.vel = Vector2(0, 0)
    
    def move(self, dx, dy):
        if dx != 0 or dy != 0:
            self.pos += Vector2(dx, dy) * self.speed
            self.stamina = max(0, self.stamina - 0.1)
        else:
            self.stamina = min(100, self.stamina + 0.2)
        
        # Saha sınırları
        self.pos.x = max(self.radius, min(WIDTH - self.radius, self.pos.x))
        self.pos.y = max(50, min(HEIGHT - 50, self.pos.y))
    
    def draw(self, surface):
        # Oyuncu gövdesi
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surface, COLORS['white'], (int(self.pos.x), int(self.pos.y)), self.radius, 3)
        
        # Güç çubuğu
        if self.power < 100:
            bar_width = 30
            bar_height = 4
            bar_x = self.pos.x - bar_width // 2
            bar_y = self.pos.y - self.radius - 10
            
            pygame.draw.rect(surface, COLORS['gray'], (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(surface, COLORS['yellow'], (bar_x, bar_y, bar_width * self.power / 100, bar_height))

# Top Sınıfı
class Ball:
    def __init__(self):
        self.pos = Vector2(WIDTH // 2, HEIGHT // 2)
        self.vel = Vector2(0, 0)
        self.radius = 12
        self.spin = 0
    
    def reset(self):
        self.pos = Vector2(WIDTH // 2, HEIGHT // 2)
        self.vel = Vector2(0, 0)
        self.spin = 0
    
    def update(self, friction=0.985):
        self.pos += self.vel
        self.vel *= friction
        
        # Spin etkisi
        if abs(self.vel.x) > 0.5:
            self.spin += self.vel.x * 0.1
        
        # Duvar çarpışmaları
        if self.pos.y - self.radius < 50:
            self.pos.y = 50 + self.radius
            self.vel.y *= -0.8
        elif self.pos.y + self.radius > HEIGHT:
            self.pos.y = HEIGHT - self.radius
            self.vel.y *= -0.8
        
        if self.pos.x - self.radius < 0:
            self.pos.x = self.radius
            self.vel.x *= -0.8
        elif self.pos.x + self.radius > WIDTH:
            self.pos.x = WIDTH - self.radius
            self.vel.x *= -0.8
    
    def draw(self, surface):
        # Spin efekti
        spin_offset = int(self.spin) % 10
        
        pygame.draw.circle(surface, COLORS['white'], (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surface, COLORS['black'], (int(self.pos.x), int(self.pos.y)), self.radius, 2)
        
        # Top deseni
        pygame.draw.circle(surface, COLORS['black'], (int(self.pos.x + spin_offset - 5), int(self.pos.y)), 4)

# Güçlendirme Sınıfı
class PowerUp:
    def __init__(self, pos, ptype):
        self.pos = Vector2(pos)
        self.type = ptype
        self.radius = 15
        self.active = True
        self.timer = 600  # 10 saniye
    
    def update(self):
        self.timer -= 1
        if self.timer <= 0:
            self.active = False
    
    def draw(self, surface):
        if not self.active: return
        
        colors = {
            'speed': COLORS['yellow'],
            'power': COLORS['orange'],
            'freeze': COLORS['purple']
        }
        
        color = colors.get(self.type, COLORS['white'])
        
        # Parlama efekti
        pulse = abs(pygame.time.get_ticks() % 1000 - 500) / 500
        
        pygame.draw.circle(surface, color, (int(self.pos.x), int(self.pos.y)), int(self.radius * (0.8 + pulse * 0.4)))
        pygame.draw.circle(surface, COLORS['white'], (int(self.pos.x), int(self.pos.y)), int(self.radius * (0.8 + pulse * 0.4)), 2)
        
        # Sembol
        symbols = {'speed': '⚡', 'power': '💪', 'freeze': '❄️'}
        font = pygame.font.SysFont("Arial", 16)
        text = font.render(symbols.get(self.type, '?'), True, COLORS['black'])
        surface.blit(text, (self.pos.x - 8, self.pos.y - 8))

# Konfeti Sistemi
class Confetti:
    def __init__(self, x, y):
        self.pos = Vector2(x, y)
        self.vel = Vector2(random.uniform(-5, 5), random.uniform(-8, -3))
        self.color = random.choice([COLORS['red'], COLORS['blue'], COLORS['yellow'], COLORS['gold'], COLORS['purple'], COLORS['orange']])
        self.life = random.randint(60, 120)
        self.rotation = random.uniform(0, 360)
    
    def update(self):
        self.pos += self.vel
        self.vel.y += 0.15  # Yerçekimi
        self.life -= 1
        self.rotation += 5
    
    def draw(self, surface, camera_y=0):
        if self.life <= 0: return
        alpha = min(255, self.life * 2)
        
        # Döndürülmüş kare çizimi
        rect = pygame.Rect(int(self.pos.x), int(self.pos.y - camera_y), 8, 8)
        pygame.draw.rect(surface, self.color, rect)

# Kale Sınıfı
class Goal:
    def __init__(self, x, is_left):
        self.x = x
        self.is_left = is_left
        self.width = 15
        self.height = 140
        self.y = HEIGHT // 2 - self.height // 2
    
    def check_goal(self, ball):
        if self.is_left:
            return ball.pos.x < self.x + self.width and self.y < ball.pos.y < self.y + self.height
        else:
            return ball.pos.x > self.x - self.width and self.y < ball.pos.y < self.y + self.height
    
    def draw(self, surface):
        # Kale çerçevesi
        pygame.draw.rect(surface, COLORS['white'], (self.x, self.y, self.width, self.height), 3)
        
        # Ağ deseni
        for i in range(0, self.height, 10):
            pygame.draw.line(surface, (200, 200, 200), (self.x, self.y + i), (self.x + self.width, self.y + i), 1)

# Oyun Durumu
class GameState:
    def __init__(self):
        self.mode = GameMode.NORMAL
        self.player_score = 0
        self.ai_score = 0
        self.time_left = 90  # 90 saniye
        self.start_ticks = pygame.time.get_ticks()
        self.is_paused = False
        self.is_game_over = False
        self.winner = None
        
        # Turnuva
        self.tournament_round = 1
        self.tournament_wins = 0
        self.tournament_losses = 0
        
        # Güçlendirmeler
        self.powerups = []
        self.active_powerups = {'player': None, 'ai': None}
        
        # Konfeti
        self.confetti = []
    
    def reset(self, full=False):
        if full:
            self.player_score = 0
            self.ai_score = 0
            self.time_left = 90
            self.start_ticks = pygame.time.get_ticks()
            self.powerups = []
            self.active_powerups = {'player': None, 'ai': None}
        self.is_paused = False
        self.is_game_over = False
        self.winner = None

# Nesneler
player = Player(100, HEIGHT // 2, COLORS['red'])
ai = Player(WIDTH - 100, HEIGHT // 2, COLORS['blue'], is_ai=True)
ball = Ball()
left_goal = Goal(0, True)
right_goal = Goal(WIDTH, False)
game_state = GameState()

# Fontlar
font = pygame.font.SysFont("Arial", 28, bold=True)
title_font = pygame.font.SysFont("Impact", 48)
small_font = pygame.font.SysFont("Arial", 16)

def reset_positions():
    player.reset()
    ai.reset()
    ball.reset()
    game_state.confetti = []

def spawn_confetti(x, y):
    for _ in range(30):
        game_state.confetti.append(Confetti(x, y))

def spawn_powerup():
    ptype = random.choice(['speed', 'power', 'freeze'])
    pos = Vector2(random.randint(150, WIDTH - 150), random.randint(100, HEIGHT - 100))
    game_state.powerups.append(PowerUp(pos, ptype))

# Ana Döngü
clock = pygame.time.Clock()
running = True

while running:
    current_time = pygame.time.get_ticks()
    
    # Etkinlikler
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                game_state.is_paused = not game_state.is_paused
            if event.key == pygame.K_r:
                reset_positions()
                game_state.reset(full=True)
            if event.key == pygame.K_t:
                # Turnuva modu
                game_state.mode = GameMode.TOURNAMENT
                game_state.reset(full=True)
            if event.key == pygame.K_p:
                # Penalty modu
                game_state.mode = GameMode.PENALTY
                game_state.reset(full=True)
            if event.key == pygame.K_n:
                # Normal mod
                game_state.mode = GameMode.NORMAL
                game_state.reset(full=True)
    
    if not game_state.is_paused and not game_state.is_game_over:
        # Süre
        seconds = (current_time - game_state.start_ticks) / 1000
        game_state.time_left = max(0, 90 - seconds)
        
        if game_state.time_left <= 0:
            game_state.is_game_over = True
            if game_state.player_score > game_state.ai_score:
                game_state.winner = "KAZANDIN!"
                game_state.tournament_wins += 1
                if goal_sound: goal_sound.play()
            elif game_state.ai_score > game_state.player_score:
                game_state.winner = "KAYBETTİN!"
                game_state.tournament_losses += 1
            else:
                game_state.winner = "BERABERE!"
        
        # Oyuncu Hareketi
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_LEFT]: dx = -1
        if keys[pygame.K_RIGHT]: dx = 1
        if keys[pygame.K_UP]: dy = -1
        if keys[pygame.K_DOWN]: dy = 1
        
        # Güçlendirme etkisi
        if game_state.active_powerups.get('player') == 'speed':
            player.speed = 8
        else:
            player.speed = 5
        
        player.move(dx, dy)
        
        # AI Hareketi (Gelişmiş)
        target = ball.pos.copy()
        
        # AI savunma pozisyonu
        if ball.vel.x < 0:  # Top rakipteyken
            target.y = ball.pos.y
            target.x = max(WIDTH - 200, ball.pos.x + 50)
        
        # AI hücum
        if ball.vel.x > 0:  # Top bizdeyken
            target.x = min(WIDTH - 50, ball.pos.x - 30)
        
        ai_dir = target - ai.pos
        if ai_dir.length() > 0:
            ai_dir = ai_dir.normalize()
        
        # AI hızı
        ai_speed = 3.5
        if game_state.active_powerups.get('ai') == 'freeze':
            ai_speed = 1
        elif game_state.active_powerups.get('ai') == 'speed':
            ai_speed = 6
        
        ai.pos += ai_dir * ai_speed
        ai.pos.x = max(WIDTH // 2 + 50, min(WIDTH - ai.radius, ai.pos.x))
        ai.pos.y = max(50, min(HEIGHT - 50, ai.pos.y))
        
        # Top güncelleme
        ball.update()
        
        # Çarpışma - Oyuncu vs Top
        for p in [player, ai]:
            dist = p.pos.distance_to(ball.pos)
            if dist < p.radius + ball.radius:
                # Çarpışma vektörü
                collision = ball.pos - p.pos
                if collision.length() > 0:
                    collision = collision.normalize()
                    
                    # Vuruş gücü
                    power = 10
                    if game_state.active_powerups.get('player' if p == player else 'ai') == 'power':
                        power = 18
                    
                    ball.vel = collision * power
                    ball.pos = p.pos + collision * (p.radius + ball.radius + 2)
                    
                    if kick_sound: kick_sound.play()
        
        # Kale kontrolü
        if left_goal.check_goal(ball):
            game_state.ai_score += 1
            spawn_confetti(0, HEIGHT // 2)
            if goal_sound: goal_sound.play()
            reset_positions()
        
        if right_goal.check_goal(ball):
            game_state.player_score += 1
            spawn_confetti(WIDTH, HEIGHT // 2)
            if goal_sound: goal_sound.play()
            reset_positions()
        
        # Güçlendirme spawn
        if random.random() < 0.002:
            spawn_powerup()
        
        # Güçlendirme güncelleme
        for pu in game_state.powerups[:]:
            pu.update()
            if not pu.active:
                game_state.powerups.remove(pu)
                continue
            
            # Toplama kontrolü
            for p, pname in [(player, 'player'), (ai, 'ai')]:
                if p.pos.distance_to(pu.pos) < p.radius + pu.radius:
                    game_state.active_powerups[pname] = pu.type
                    pu.active = False
                    game_state.powerups.remove(pu)
                    
                    # Güçlendirme süresi
                    def clear_powerup(name):
                        if game_state.active_powerups.get(name) == pu.type:
                            game_state.active_powerups[name] = None
                    
                    pygame.time.set_timer(pygame.USEREVENT + (1 if pname == 'player' else 2), 8000)
        
        # Konfeti güncelleme
        for c in game_state.confetti[:]:
            c.update()
            if c.life <= 0:
                game_state.confetti.remove(c)
    
    # Çizim
    screen.fill(COLORS['dark_green'])
    
    # Saha çizgileri
    pygame.draw.rect(screen, COLORS['green'], (0, 50, WIDTH, HEIGHT - 50))
    pygame.draw.rect(screen, COLORS['white'], (0, 50, WIDTH, HEIGHT - 50), 4)  # Dış çizgi
    
    # Orta çizgi
    pygame.draw.line(screen, COLORS['white'], (WIDTH // 2, 50), (WIDTH // 2, HEIGHT), 3)
    
    # Orta daire
    pygame.draw.circle(screen, COLORS['white'], (WIDTH // 2, HEIGHT // 2), 80, 3)
    
    # Ceza alanları
    pygame.draw.rect(screen, COLORS['white'], (0, HEIGHT // 2 - 100, 80, 200), 3)
    pygame.draw.rect(screen, COLORS['white'], (WIDTH - 80, HEIGHT // 2 - 100, 80, 200), 3)
    
    # Kaleler
    left_goal.draw(screen)
    right_goal.draw(screen)
    
    # Güçlendirmeler
    for pu in game_state.powerups:
        pu.draw(screen)
    
    # Konfeti
    for c in game_state.confetti:
        c.draw(screen)
    
    # Oyuncular
    player.draw(screen)
    ai.draw(screen)
    
    # Top
    ball.draw(screen)
    
    # Skor paneli
    pygame.draw.rect(screen, COLORS['black'], (0, 0, WIDTH, 50))
    
    # Skor
    score_text = font.render(f"{game_state.player_score} - {game_state.ai_score}", True, COLORS['white'])
    screen.blit(score_text, (WIDTH // 2 - score_text.get_width() // 2, 8))
    
    # Süre
    time_text = font.render(f"⏱ {int(game_state.time_left)}", True, COLORS['yellow'] if game_state.time_left < 15 else COLORS['white'])
    screen.blit(time_text, (WIDTH // 2 + 80, 10))
    
    # Mod
    mode_text = small_font.render(f"Mod: {game_state.mode.upper()}", True, COLORS['gray'])
    screen.blit(mode_text, (10, 15))
    
    # Turnuva bilgisi
    if game_state.mode == GameMode.TOURNAMENT:
        tour_text = small_font.render(f"Galibiyet: {game_state.tournament_wins} | Mağlubiyet: {game_state.tournament_losses}", True, COLORS['gold'])
        screen.blit(tour_text, (10, 32))
    
    # Oyuncu isimleri
    p1_text = small_font.render("OYUNCU (KIRMIZI)", True, COLORS['red'])
    screen.blit(p1_text, (player.pos.x - 50, player.pos.y + 25))
    
    ai_text = small_font.render("AI (MAVİ)", True, COLORS['blue'])
    screen.blit(ai_text, (ai.pos.x - 30, ai.pos.y + 25))
    
    # Aktif güçlendirmeler
    if game_state.active_powerups.get('player'):
        pw_text = small_font.render(f"⚡ {game_state.active_powerups['player'].upper()}", True, COLORS['yellow'])
        screen.blit(pw_text, (100, 55))
    
    if game_state.active_powerups.get('ai'):
        pw_text = small_font.render(f"⚡ {game_state.active_powerups['ai'].upper()}", True, COLORS['purple'])
        screen.blit(pw_text, (WIDTH - 150, 55))
    
    # Duraklatma ekranı
    if game_state.is_paused:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(COLORS['black'])
        screen.blit(overlay, (0, 0))
        
        pause_text = title_font.render("⏸️ DURAKLADI", True, COLORS['white'])
        screen.blit(pause_text, (WIDTH // 2 - pause_text.get_width() // 2, HEIGHT // 2 - 50))
        
        help_text = small_font.render("ESC: Devam | R: Yeniden Başlat | T: Turnuva | P: Penalty | N: Normal", True, COLORS['gray'])
        screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, HEIGHT // 2 + 20))
    
    # Oyun bitişi ekranı
    if game_state.is_game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(COLORS['black'])
        screen.blit(overlay, (0, 0))
        
        result_text = title_font.render(game_state.winner, True, COLORS['gold'] if "KAZANDIN" in game_state.winner else COLORS['red'])
        screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, HEIGHT // 2 - 80))
        
        final_score = font.render(f"Skor: {game_state.player_score} - {game_state.ai_score}", True, COLORS['white'])
        screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2))
        
        restart_text = small_font.render("Yeniden oynamak için R tuşuna bas", True, COLORS['gray'])
        screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 60))
        
        if game_state.mode == GameMode.TOURNAMENT:
            tour_result = font.render(f"Turnuva: {game_state.tournament_wins}G {game_state.tournament_losses}M", True, COLORS['gold'])
            screen.blit(tour_result, (WIDTH // 2 - tour_result.get_width() // 2, HEIGHT // 2 + 100))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
