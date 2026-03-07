"""SPACE HUNTER CV - OpenCV Uzay Oyunu"""

import cv2
import numpy as np
import random
import math

# OpenCV başlat
cap = cv2.VideoCapture(0) if cv2.VideoCapture(0).isOpened() else None
WIDTH, HEIGHT = 1280, 720

# Renkler
CYAN = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (0, 255, 255)
ORANGE = (0, 165, 255)
PURPLE = (255, 0, 255)

# Gezegenler
PLANETS = {
    'earth': {'color': (34, 139, 34), 'sky': (135, 206, 235)},
    'mars': {'color': (139, 69, 19), 'sky': (255, 100, 50)},
    'space': {'color': (20, 0, 40), 'sky': (0, 0, 20)},
}

# Oyun
player_x, player_y = WIDTH//2, HEIGHT//2
player_hp = 100
score = 0
gold = 0
level = 1
enemies = []
bullets = []
particles = []
game_started = False
game_over = False
current_planet = 'earth'

def draw_bg(f, planet):
    p = PLANETS[planet]
    cv2.rectangle(f, (0, 0), (WIDTH, HEIGHT), p['sky'], -1)
    pts = np.array([[0, HEIGHT//2], [WIDTH, HEIGHT//2], [WIDTH, HEIGHT], [0, HEIGHT]], np.int32)
    cv2.fillPoly(f, [pts], p['color'])
    cv2.line(f, (0, HEIGHT//2), (WIDTH, HEIGHT//2), (200,200,200), 3)

def draw_player(f):
    cx, cy = WIDTH//2, HEIGHT//2
    cv2.line(f, (cx-20, cy), (cx+20, cy), CYAN, 2)
    cv2.line(f, (cx, cy-20), (cx, cy+20), CYAN, 2)

def draw_enemy(f, e):
    cv2.circle(f, (int(e['x']), int(e['y'])), e['size'], e['color'], -1)
    cv2.circle(f, (int(e['x']), int(e['y'])), e['size'], WHITE, 2)

def draw_bullet(f, b):
    cv2.circle(f, (int(b['x']), int(b['y'])), 5, b['color'], -1)

def draw_ui(f):
    cv2.rectangle(f, (0, 0), (WIDTH, 60), BLACK, -1)
    cv2.putText(f, f"HP: {int(player_hp)}", (20, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, GREEN, 2)
    cv2.putText(f, f"Skor: {score}", (200, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2)
    cv2.putText(f, f"Altin: {gold}", (400, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, ORANGE, 2)
    cv2.putText(f, f"Seviye: {level}", (600, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, PURPLE, 2)

def draw_menu(f):
    cv2.rectangle(f, (0, 0), (WIDTH, HEIGHT), BLACK, -1)
    cv2.putText(f, "SPACE HUNTER", (WIDTH//2-180, 200), cv2.FONT_HERSHEY_SIMPLEX, 2.5, CYAN, 5)
    cv2.putText(f, "1: Dunya | 2: Mars | 3: Uzay", (WIDTH//2-250, 350), cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2)
    cv2.putText(f, "ENTER: Basla | ESC: Cikis", (WIDTH//2-180, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, YELLOW, 2)

def main():
    global player_x, player_y, player_hp, score, gold, level, enemies, bullets, particles
    global game_started, game_over, current_planet
    
    while True:
        if cap:
            ret, frame = cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                frame = cv2.resize(frame, (WIDTH, HEIGHT))
            else:
                frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        else:
            frame = np.zeros((HEIGHT, WIDTH, 3), dtype=np.uint8)
        
        key = cv2.waitKey(1) & 0xFF
        
        if key == 27:
            break
        
        if not game_started:
            if key == ord('1'): current_planet = 'earth'
            if key == ord('2'): current_planet = 'mars'
            if key == ord('3'): current_planet = 'space'
            if key == 13:
                game_started = True
            draw_menu(frame)
            cv2.imshow("Space Hunter CV", frame)
            continue
        
        if game_over:
            cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), BLACK, -1)
            cv2.putText(frame, "OYUN BITTI", (WIDTH//2-150, HEIGHT//2), cv2.FONT_HERSHEY_SIMPLEX, 3, RED, 5)
            cv2.imshow("Space Hunter CV", frame)
            continue
        
        # Hareket
        if key == ord('w') and player_y > 100: player_y -= 8
        if key == ord('s') and player_y < HEIGHT-30: player_y += 8
        if key == ord('a') and player_x > 30: player_x -= 8
        if key == ord('d') and player_x < WIDTH-30: player_x += 8
        
        # Ateş
        if key == 32:
            bullets.append({'x': player_x, 'y': player_y-20, 'vx': 0, 'vy': -15, 'color': RED})
        
        # Spawn
        if random.random() < 0.03:
            ex = random.randint(50, WIDTH-50)
            ey = random.randint(90, 150)
            enemies.append({'x': ex, 'y': ey, 'hp': 2, 'size': 20, 'color': GREEN, 'score': 10})
        
        # Düşman hareketi
        for e in enemies:
            e['y'] += 2
            if e['y'] > HEIGHT-50:
                player_hp -= 1
        
        # Mermi güncelleme
        for b in bullets[:]:
            b['y'] += b['vy']
            if b['y'] < 0:
                bullets.remove(b)
                continue
            for e in enemies[:]:
                if math.hypot(b['x']-e['x'], b['y']-e['y']) < e['size']+5:
                    e['hp'] -= 1
                    bullets.remove(b)
                    break
        
        # Düşman ölümü
        for e in enemies[:]:
            if e['hp'] <= 0:
                enemies.remove(e)
                score += e['score']
                gold += e['score']//2
        
        if player_hp <= 0:
            game_over = True
        
        draw_bg(frame, current_planet)
        for e in enemies: draw_enemy(frame, e)
        for b in bullets: draw_bullet(frame, b)
        draw_player(frame)
        draw_ui(frame)
        
        cv2.imshow("Space Hunter CV", frame)
    
    if cap:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
