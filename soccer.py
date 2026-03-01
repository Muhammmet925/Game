import pygame
import random
import array

# Vektör işlemleri için
from pygame.math import Vector2

pygame.init()

# Ekran Ayarları
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Arcade Futbol")

# Renkler
GREEN = (34, 139, 34)    # Saha
WHITE = (255, 255, 255)  # Çizgiler ve Top
RED = (255, 0, 0)        # Oyuncu
BLUE = (0, 0, 255)       # Rakip (AI)
BLACK = (0, 0, 0)

# Oyun Ayarları
PLAYER_SPEED = 5
AI_SPEED = 3
BALL_FRICTION = 0.99
PLAYER_RADIUS = 20
BALL_RADIUS = 10
GOAL_WIDTH = 150
GAME_DURATION = 60  # Oyun süresi (saniye)

# Ses Efekti Oluşturma (Dosyasız)
try:
    pygame.mixer.init(frequency=44100, size=-16, channels=1)
    # Basit bir "bip" sesi için dalga formu oluşturuyoruz
    duration = 0.1  # saniye
    frequency = 440  # Hz
    sample_rate = 44100
    n_samples = int(sample_rate * duration)
    buffer = array.array('h', [int(10000 * (1 if (t % (sample_rate // frequency)) < (sample_rate // frequency) // 2 else -1)) for t in range(n_samples)])
    hit_sound = pygame.mixer.Sound(buffer=buffer)
    hit_sound.set_volume(0.3)
except:
    hit_sound = None

class GameEntity:
    def __init__(self, x, y, color, radius):
        self.pos = Vector2(x, y)
        self.vel = Vector2(0, 0)
        self.color = color
        self.radius = radius

    def draw(self, surface):
        pygame.draw.circle(surface, self.color, (int(self.pos.x), int(self.pos.y)), self.radius)

def reset_positions():
    player.pos = Vector2(100, HEIGHT//2)
    ai.pos = Vector2(WIDTH - 100, HEIGHT//2)
    ball.pos = Vector2(WIDTH//2, HEIGHT//2)
    ball.vel = Vector2(0, 0)

# Nesneleri Oluştur
player = GameEntity(100, HEIGHT//2, RED, PLAYER_RADIUS)
ai = GameEntity(WIDTH - 100, HEIGHT//2, BLUE, PLAYER_RADIUS)
ball = GameEntity(WIDTH//2, HEIGHT//2, WHITE, BALL_RADIUS)

# Konfeti Sistemi
confetti_particles = []

def spawn_confetti(x, y):
    for _ in range(50):
        confetti_particles.append({
            'pos': Vector2(x, y),
            'vel': Vector2(random.uniform(-5, 5), random.uniform(-5, 5)),
            'color': (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255)),
            'life': random.randint(60, 120)
        })

player_score = 0
ai_score = 0
font = pygame.font.SysFont("Arial", 36)
game_over_font = pygame.font.SysFont("Arial", 64)
start_ticks = pygame.time.get_ticks() # Başlangıç zamanı

running = True
clock = pygame.time.Clock()

while running:
    # Olay Kontrolü
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Süre Hesaplama
    seconds_passed = (pygame.time.get_ticks() - start_ticks) / 1000
    time_left = GAME_DURATION - seconds_passed
    
    if time_left <= 0:
        time_left = 0
        game_active = False
    else:
        game_active = True

    # --- GÜNCELLEME ---
    
    if game_active:
        # Oyuncu Hareketi (Yön Tuşları)
        keys = pygame.key.get_pressed()
        move = Vector2(0, 0)
        if keys[pygame.K_LEFT]: move.x = -1
        if keys[pygame.K_RIGHT]: move.x = 1
        if keys[pygame.K_UP]: move.y = -1
        if keys[pygame.K_DOWN]: move.y = 1
        
        if move.length() > 0:
            player.pos += move.normalize() * PLAYER_SPEED

        # AI Hareketi (Topu Takip Et)
        # AI sadece top kendi sahasındaysa veya yakındaysa hareket etsin
        direction = ball.pos - ai.pos
        if direction.length() > 0:
            ai.pos += direction.normalize() * AI_SPEED

        # Top Fiziği
        ball.pos += ball.vel
        ball.vel *= BALL_FRICTION  # Sürtünme

        # Çarpışma Kontrolü (Top vs Oyuncular)
        for p in [player, ai]:
            distance = p.pos.distance_to(ball.pos)
            if distance < p.radius + ball.radius:
                # Çarpışma vektörü
                collision_vec = ball.pos - p.pos
                if collision_vec.length() > 0:
                    collision_vec = collision_vec.normalize()
                    # Topa hız ver (Vurma etkisi)
                    ball.vel = collision_vec * 8
                    # Topu oyuncunun içinden çıkar
                    ball.pos = p.pos + collision_vec * (p.radius + ball.radius + 1)
                    if hit_sound:
                        hit_sound.play()

    # Duvar Çarpışmaları (Top)
    if ball.pos.y - ball.radius < 0:
        ball.pos.y = ball.radius
        ball.vel.y *= -1
    elif ball.pos.y + ball.radius > HEIGHT:
        ball.pos.y = HEIGHT - ball.radius
        ball.vel.y *= -1

    if ball.pos.x - ball.radius < 0:
        # Sol Kale Kontrolü
        if HEIGHT//2 - GOAL_WIDTH//2 < ball.pos.y < HEIGHT//2 + GOAL_WIDTH//2:
            ai_score += 1
            spawn_confetti(0, HEIGHT//2)
            reset_positions()
        else:
            ball.pos.x = ball.radius
            ball.vel.x *= -1
            
    elif ball.pos.x + ball.radius > WIDTH:
        # Sağ Kale Kontrolü
        if HEIGHT//2 - GOAL_WIDTH//2 < ball.pos.y < HEIGHT//2 + GOAL_WIDTH//2:
            player_score += 1
            spawn_confetti(WIDTH, HEIGHT//2)
            reset_positions()
        else:
            ball.pos.x = WIDTH - ball.radius
            ball.vel.x *= -1

    # Oyuncuları Sahada Tut
    for p in [player, ai]:
        p.pos.x = max(p.radius, min(WIDTH - p.radius, p.pos.x))
        p.pos.y = max(p.radius, min(HEIGHT - p.radius, p.pos.y))

    # Konfeti Güncelleme
    for p in confetti_particles[:]:
        p['pos'] += p['vel']
        p['vel'].y += 0.1  # Yerçekimi
        p['life'] -= 1
        if p['life'] <= 0:
            confetti_particles.remove(p)

    # --- ÇİZİM ---
    screen.fill(GREEN)
    
    # Saha Çizgileri
    pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, HEIGHT), 5) # Dış Çizgi
    pygame.draw.line(screen, WHITE, (WIDTH//2, 0), (WIDTH//2, HEIGHT), 3) # Orta Saha
    pygame.draw.circle(screen, WHITE, (WIDTH//2, HEIGHT//2), 70, 3) # Orta Yuvarlak
    
    # Kaleler
    pygame.draw.rect(screen, BLACK, (0, HEIGHT//2 - GOAL_WIDTH//2, 5, GOAL_WIDTH))
    pygame.draw.rect(screen, BLACK, (WIDTH-5, HEIGHT//2 - GOAL_WIDTH//2, 5, GOAL_WIDTH))

    # Nesneler
    player.draw(screen)
    ai.draw(screen)
    ball.draw(screen)

    # Konfeti Çizimi
    for p in confetti_particles:
        pygame.draw.rect(screen, p['color'], (int(p['pos'].x), int(p['pos'].y), 5, 5))

    # Skor ve Süre Tabelası
    score_text = font.render(f"Kırmızı: {player_score}  |  Mavi: {ai_score}", True, WHITE)
    time_text = font.render(f"Süre: {int(time_left)}", True, (255, 255, 0) if time_left < 10 else WHITE)
    
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 20))
    screen.blit(time_text, (WIDTH//2 - time_text.get_width()//2, 60))

    # Oyun Bitti Ekranı
    if not game_active:
        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        screen.blit(overlay, (0,0))
        
        end_text = game_over_font.render("OYUN BİTTİ", True, WHITE)
        screen.blit(end_text, (WIDTH//2 - end_text.get_width()//2, HEIGHT//2 - 50))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()