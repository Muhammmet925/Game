"""
⚽ SUPER FUTBOL - OpenCV Versiyonu
Kamera destekli interaktif futbol oyunu
"""

import cv2
import numpy as np
import random
import time
import math
from collections import deque

# OpenCV başlat
cap = None
try:
    cap = cv2.VideoCapture(0)
    cap.set(3, 1280)
    cap.set(4, 720)
except:
    pass

# Ekran ayarları
WIDTH, HEIGHT = 1280, 720
FRAME_WIDTH = 1280
FRAME_HEIGHT = 720

# Renkler (BGR format)
COLORS = {
    'green': (34, 139, 34),
    'dark_green': (0, 100, 0),
    'white': (255, 255, 255),
    'red': (0, 0, 255),
    'blue': (255, 0, 0),
    'black': (0, 0, 0),
    'yellow': (0, 255, 255),
    'gold': (0, 215, 255),
    'purple': (128, 0, 128),
    'orange': (0, 165, 255),
    'grass': (50, 205, 50),
    'lines': (255, 255, 255),
}

# Oyun durumu
class GameState:
    def __init__(self):
        self.player_score = 0
        self.ai_score = 0
        self.time_left = 90
        self.start_time = time.time()
        self.is_paused = False
        self.is_game_over = False
        self.winner = None
        self.tournament_wins = 0
        self.tournament_losses = 0
        self.mode = 'normal'
        
# Oyuncu sınıfı
class Player:
    def __init__(self, x, y, color, is_ai=False):
        self.x = x
        self.y = y
        self.color = color
        self.radius = 25
        self.speed = 8
        self.is_ai = is_ai
        self.target_x = x
        self.target_y = y
    
    def move(self, dx, dy):
        self.x = max(self.radius, min(WIDTH - self.radius, self.x + dx * self.speed))
        self.y = max(80, min(HEIGHT - self.radius, self.y + dy * self.speed))
    
    def move_to(self, tx, ty, speed=None):
        if speed is None:
            speed = self.speed
        dx = tx - self.x
        dy = ty - self.y
        dist = math.hypot(dx, dy)
        if dist > 5:
            self.x += (dx / dist) * speed
            self.y += (dy / dist) * speed
        self.x = max(self.radius, min(WIDTH - self.radius, self.x))
        self.y = max(80, min(HEIGHT - self.radius, self.y))

# Top sınıfı
class Ball:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.vx = 0
        self.vy = 0
        self.radius = 15
        self.friction = 0.98
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vx *= self.friction
        self.vy *= self.friction
        
        # Duvar çarpışmaları
        if self.y - self.radius < 80:
            self.y = 80 + self.radius
            self.vy *= -0.8
        elif self.y + self.radius > HEIGHT:
            self.y = HEIGHT - self.radius
            self.vy *= -0.8
        
        if self.x - self.radius < 0:
            self.x = self.radius
            self.vx *= -0.8
        elif self.x + self.radius > WIDTH:
            self.x = WIDTH - self.radius
            self.vx *= -0.8
    
    def kick(self, dx, dy, power=15):
        self.vx = dx * power
        self.vy = dy * power

# Güçlendirme sınıfı
class PowerUp:
    def __init__(self):
        self.x = random.randint(200, WIDTH - 200)
        self.y = random.randint(150, HEIGHT - 150)
        self.type = random.choice(['speed', 'power', 'freeze'])
        self.active = True
        self.radius = 20
    
    def draw(self, frame):
        if not self.active:
            return
        
        colors = {
            'speed': COLORS['yellow'],
            'power': COLORS['orange'],
            'freeze': COLORS['purple']
        }
        
        color = colors.get(self.type, COLORS['white'])
        
        # Parlama efekti
        pulse = int(20 + 5 * math.sin(time.time() * 5))
        
        cv2.circle(frame, (self.x, self.y), pulse, color, -1)
        cv2.circle(frame, (self.x, self.y), self.radius, COLORS['white'], 2)
        
        # Sembol
        symbols = {'speed': 'S', 'power': 'P', 'freeze': 'F'}
        cv2.putText(frame, symbols.get(self.type, '?'), 
                   (self.x - 8, self.y + 5), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['black'], 2)

# Konfeti sınıfı
class Confetti:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = random.uniform(-5, 5)
        self.vy = random.uniform(-8, -3)
        self.color = random.choice([COLORS['red'], COLORS['blue'], COLORS['yellow'], COLORS['gold']])
        self.life = 120
    
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.15
        self.life -= 1
    
    def draw(self, frame):
        if self.life > 0:
            cv2.rectangle(frame, 
                         (int(self.x), int(self.y)), 
                         (int(self.x + 8), int(self.y + 8)), 
                         self.color, -1)

# Oyun nesneleri
player = Player(150, HEIGHT // 2, COLORS['red'])
ai = Player(WIDTH - 150, HEIGHT // 2, COLORS['blue'], is_ai=True)
ball = Ball()
game_state = GameState()
powerups = []
confetti = []

# Kamera özellikleri
motion_history = deque(maxlen=30)
last_frame = None
motion_detected = False
hand_position = None

def detect_motion(frame):
    """Hareket algılama"""
    global last_frame, motion_history, motion_detected
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)
    
    if last_frame is not None:
        frame_delta = cv2.absdiff(last_frame, gray)
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            largest = max(contours, key=cv2.contourArea)
            if cv2.contourArea(largest) > 5000:
                x, y, w, h = cv2.boundingRect(largest)
                motion_detected = True
                return x + w//2, y + h//2
    
    last_frame = gray
    motion_detected = False
    return None

def draw_field(frame):
    """Futbol sahası çiz"""
    # Yeşil zemin
    cv2.rectangle(frame, (0, 80), (WIDTH, HEIGHT), COLORS['dark_green'], -1)
    
    # Çizgiler
    cv2.rectangle(frame, (0, 80), (WIDTH, HEIGHT), COLORS['lines'], 4)
    
    # Orta çizgi
    cv2.line(frame, (WIDTH // 2, 80), (WIDTH // 2, HEIGHT), COLORS['lines'], 3)
    
    # Orta daire
    cv2.circle(frame, (WIDTH // 2, HEIGHT // 2), 80, COLORS['lines'], 3)
    
    # Ceza alanları
    cv2.rectangle(frame, (0, HEIGHT // 2 - 100), (100, HEIGHT // 2 + 100), COLORS['lines'], 3)
    cv2.rectangle(frame, (WIDTH - 100, HEIGHT // 2 - 100), (WIDTH, HEIGHT // 2 + 100), COLORS['lines'], 3)
    
    # Kaleler
    cv2.rectangle(frame, (0, HEIGHT // 2 - 70), (15, HEIGHT // 2 + 70), COLORS['white'], 3)
    cv2.rectangle(frame, (WIDTH - 15, HEIGHT // 2 - 70), (WIDTH, HEIGHT // 2 + 70), COLORS['white'], 3)

def draw_player(frame, p, name=""):
    """Oyuncu çiz"""
    # Gol çizgisi
    cv2.circle(frame, (int(p.x), int(p.y)), p.radius, p.color, -1)
    cv2.circle(frame, (int(p.x), int(p.y)), p.radius, COLORS['white'], 3)
    
    # İsim
    if name:
        cv2.putText(frame, name, (int(p.x - 30), int(p.y - p.radius - 10)),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLORS['white'], 2)

def draw_ball(frame, b):
    """Top çiz"""
    cv2.circle(frame, (int(b.x), int(b.y)), b.radius, COLORS['white'], -1)
    cv2.circle(frame, (int(b.x), int(b.y)), b.radius, COLORS['black'], 2)
    
    # Top deseni
    cv2.circle(frame, (int(b.x + 5), int(b.y)), 5, COLORS['black'], -1)

def draw_ui(frame, state):
    """UI çiz"""
    # Üst bar
    cv2.rectangle(frame, (0, 0), (WIDTH, 80), COLORS['black'], -1)
    
    # Skor
    score_text = f"{state.player_score} - {state.ai_score}"
    cv2.putText(frame, score_text, (WIDTH // 2 - 50, 50),
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLORS['white'], 3)
    
    # Süre
    time_text = f"{int(state.time_left)}s"
    color = COLORS['yellow'] if state.time_left < 15 else COLORS['white']
    cv2.putText(frame, time_text, (WIDTH // 2 + 100, 50),
               cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
    
    # Mod
    cv2.putText(frame, f"MOD: {state.mode.upper()}", (20, 50),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLORS['gray'], 2)

def draw_menu(frame):
    """Menü ekranı"""
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), COLORS['black'], -1)
    
    # Başlık
    cv2.putText(frame, "SUPER FUTBOL", (WIDTH // 2 - 180, 200),
               cv2.FONT_HERSHEY_SIMPLEX, 2.5, COLORS['green'], 5)
    
    cv2.putText(frame, "OpenCV Versiyonu", (WIDTH // 2 - 150, 260),
               cv2.FONT_HERSHEY_SIMPLEX, 1.2, COLORS['blue'], 3)
    
    # Talimatlar
    cv2.putText(frame, "WASD: Hareket | SPACE: Pas | ENTER: Sut", (WIDTH // 2 - 250, 400),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['white'], 2)
    
    cv2.putText(frame, "ESC: Dur | R: Yeniden Baslat", (WIDTH // 2 - 180, 450),
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['gray'], 2)
    
    # Kamera durumu
    if cap is not None and cap.isOpened():
        cv2.putText(frame, "KAMERA: AKTIF", (WIDTH // 2 - 100, 550),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['green'], 2)
    else:
        cv2.putText(frame, "KAMERA: YOK", (WIDTH // 2 - 90, 550),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, COLORS['red'], 2)
    
    cv2.putText(frame, "Baslamak icin ENTER tusuna basin", (WIDTH // 2 - 200, 620),
               cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['yellow'], 2)

def draw_game_over(frame, state):
    """Oyun bitişi ekranı"""
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), (0, 0, 0), -1)
    
    # Sonuç
    if state.winner:
        color = COLORS['gold'] if "KAZANDIN" in state.winner else COLORS['red']
        cv2.putText(frame, state.winner, (WIDTH // 2 - 150, HEIGHT // 2 - 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 2, color, 5)
    
    # Skor
    score_text = f"Skor: {state.player_score} - {state.ai_score}"
    cv2.putText(frame, score_text, (WIDTH // 2 - 120, HEIGHT // 2 + 20),
               cv2.FONT_HERSHEY_SIMPLEX, 1.5, COLORS['white'], 3)
    
    cv2.putText(frame, "Yeniden oynamak icin R tusuna basin", (WIDTH // 2 - 220, HEIGHT // 2 + 100),
               cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS['gray'], 2)

# Ana döngü
def main():
    global player, ai, ball, game_state, powerups, confetti
    
    game_started = False
    running = True
    
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
        
        # Klavye kontrolü
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:  # ESC
            if game_started:
                game_state.is_paused = not game_state.is_paused
            else:
                running = False
        
        if key == 13 and not game_started:  # ENTER
            game_started = True
            game_state.start_time = time.time()
        
        if key == ord('r') or key == ord('R'):
            player = Player(150, HEIGHT // 2, COLORS['red'])
            ai = Player(WIDTH - 150, HEIGHT // 2, COLORS['blue'], is_ai=True)
            ball = Ball()
            game_state = GameState()
            powerups = []
            confetti = []
        
        if not game_started:
            draw_menu(frame)
            cv2.imshow("Super Futbol - OpenCV", frame)
            continue
        
        if game_state.is_paused:
            draw_field(frame)
            for c in confetti:
                c.draw(frame)
            draw_player(frame, player, "OYUNCU")
            draw_player(frame, ai, "AI")
            draw_ball(frame, ball)
            draw_ui(frame, game_state)
            
            cv2.putText(frame, "PAUSED", (WIDTH // 2 - 60, HEIGHT // 2),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, COLORS['yellow'], 4)
            
            cv2.imshow("Super Futbol - OpenCV", frame)
            continue
        
        # Oyun mantığı
        current_time = time.time()
        game_state.time_left = max(0, 90 - (current_time - game_state.start_time))
        
        if game_state.time_left <= 0 and not game_state.is_game_over:
            game_state.is_game_over = True
            if game_state.player_score > game_state.ai_score:
                game_state.winner = "KAZANDIN!"
            elif game_state.ai_score > game_state.player_score:
                game_state.winner = "KAYBETTIN!"
            else:
                game_state.winner = "BERABERE!"
        
        if game_state.is_game_over:
            draw_game_over(frame, game_state)
            cv2.imshow("Super Futbol - OpenCV", frame)
            continue
        
        # Hareket kontrolü (WASD)
        keys = {'w': False, 's': False, 'a': False, 'd': False, ' ': False}
        
        if key == ord('w'): player.move(0, -1)
        if key == ord('s'): player.move(0, 1)
        if key == ord('a'): player.move(-1, 0)
        if key == ord('d'): player.move(1, 0)
        
        # AI hareketi
        target_x = ball.x
        target_y = ball.y
        
        if ball.vx < 0:  # Top bizde
            target_x = max(WIDTH // 2 + 50, ball.x - 30)
        
        ai.move_to(target_x, target_y, 5)
        
        # Top güncelleme
        ball.update()
        
        # Çarpışma kontrolü
        for p in [player, ai]:
            dist = math.hypot(p.x - ball.x, p.y - ball.y)
            if dist < p.radius + ball.radius:
                dx = ball.x - p.x
                dy = ball.y - p.y
                d = math.hypot(dx, dy)
                if d > 0:
                    ball.kick(dx / d, dy / d, 12)
        
        # Kale kontrolü
        if ball.x < 30 and HEIGHT // 2 - 70 < ball.y < HEIGHT // 2 + 70:
            game_state.ai_score += 1
            for _ in range(30):
                confetti.append(Confetti(50, HEIGHT // 2))
            ball = Ball()
        
        if ball.x > WIDTH - 30 and HEIGHT // 2 - 70 < ball.y < HEIGHT // 2 + 70:
            game_state.player_score += 1
            for _ in range(30):
                confetti.append(Confetti(WIDTH - 50, HEIGHT // 2))
            ball = Ball()
        
        # Güçlendirme spawn
        if random.random() < 0.002:
            powerups.append(PowerUp())
        
        # Güçlendirme kontrolü
        for pu in powerups[:]:
            for p in [player, ai]:
                dist = math.hypot(p.x - pu.x, p.y - pu.y)
                if dist < p.radius + pu.radius:
                    pu.active = False
                    break
            if not pu.active:
                powerups.remove(pu)
        
        # Konfeti güncelleme
        for c in confetti[:]:
            c.update()
            if c.life <= 0:
                confetti.remove(c)
        
        # Çizim
        draw_field(frame)
        
        for pu in powerups:
            pu.draw(frame)
        
        for c in confetti:
            c.draw(frame)
        
        draw_player(frame, player, "OYUNCU")
        draw_player(frame, ai, "AI")
        draw_ball(frame, ball)
        draw_ui(frame, game_state)
        
        cv2.imshow("Super Futbol - OpenCV", frame)
    
    if cap is not None:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
