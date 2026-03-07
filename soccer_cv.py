"""SOCCER CV - OpenCV Futbol Oyunu"""

import cv2
import numpy as np
import random
import time
import math

# OpenCV başlat
cap = cv2.VideoCapture(0) if cv2.VideoCapture(0).isOpened() else None
WIDTH, HEIGHT = 1280, 720

# Renkler (BGR)
GREEN = (34, 139, 34)
DARK_GREEN = (0, 100, 0)
WHITE = (255, 255, 255)
RED = (0, 0, 255)
BLUE = (255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (0, 255, 255)

# Oyun değişkenleri
player_x, player_y = 150, HEIGHT // 2
ai_x, ai_y = WIDTH - 150, HEIGHT // 2
ball_x, ball_y = WIDTH // 2, HEIGHT // 2
ball_vx, ball_vy = 0, 0
score_player, score_ai = 0, 0
time_left = 90
start_time = time.time()
game_started = False

def draw_field(frame):
    """Futbol sahası çiz"""
    cv2.rectangle(frame, (0, 80), (WIDTH, HEIGHT), DARK_GREEN, -1)
    cv2.rectangle(frame, (0, 80), (WIDTH, HEIGHT), WHITE, 4)
    cv2.line(frame, (WIDTH//2, 80), (WIDTH//2, HEIGHT), WHITE, 3)
    cv2.circle(frame, (WIDTH//2, HEIGHT//2), 80, WHITE, 3)
    cv2.rectangle(frame, (0, HEIGHT//2-100), (100, HEIGHT//2+100), WHITE, 3)
    cv2.rectangle(frame, (WIDTH-100, HEIGHT//2-100), (WIDTH, HEIGHT//2+100), WHITE, 3)

def draw_player(frame, x, y, color, name=""):
    cv2.circle(frame, (int(x), int(y)), 25, color, -1)
    cv2.circle(frame, (int(x), int(y)), 25, WHITE, 3)
    if name:
        cv2.putText(frame, name, (int(x-30), int(y-35)), cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 2)

def draw_ball(frame, x, y):
    cv2.circle(frame, (int(x), int(y)), 15, WHITE, -1)
    cv2.circle(frame, (int(x), int(y)), 15, BLACK, 2)

def draw_ui(frame, score_p, score_ai, time_left):
    cv2.rectangle(frame, (0, 0), (WIDTH, 80), BLACK, -1)
    cv2.putText(frame, f"{score_p} - {score_ai}", (WIDTH//2-50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.5, WHITE, 3)
    cv2.putText(frame, f"{int(time_left)}s", (WIDTH//2+100, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, YELLOW, 2)

def draw_menu(frame):
    cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), BLACK, -1)
    cv2.putText(frame, "SUPER FUTBOL - OpenCV", (WIDTH//2-200, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, GREEN, 5)
    cv2.putText(frame, "WASD: Hareket | ENTER: Basla | ESC: Cikis", (WIDTH//2-280, 400), cv2.FONT_HERSHEY_SIMPLEX, 0.8, WHITE, 2)
    cv2.putText(frame, "Baslamak icin ENTER tusuna basin", (WIDTH//2-220, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, YELLOW, 2)

def main():
    global player_x, player_y, ai_x, ai_y, ball_x, ball_y, ball_vx, ball_vy
    global score_player, score_ai, time_left, start_time, game_started
    
    while True:
        # Frame al
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
        
        if key == 27:  # ESC
            break
        
        if key == ord('r'):
            player_x, player_y = 150, HEIGHT//2
            ai_x, ai_y = WIDTH-150, HEIGHT//2
            ball_x, ball_y = WIDTH//2, HEIGHT//2
            ball_vx, ball_vy = 0, 0
            score_player, score_ai = 0, 0
            start_time = time.time()
        
        if not game_started:
            if key == 13:
                game_started = True
                start_time = time.time()
            draw_menu(frame)
            cv2.imshow("Soccer CV", frame)
            continue
        
        if time_left <= 0:
            cv2.rectangle(frame, (0, 0), (WIDTH, HEIGHT), BLACK, -1)
            if score_player > score_ai:
                cv2.putText(frame, "KAZANDIN!", (WIDTH//2-100, HEIGHT//2), cv2.FONT_HERSHEY_SIMPLEX, 2, GREEN, 4)
            elif score_ai > score_player:
                cv2.putText(frame, "KAYBETTIN!", (WIDTH//2-120, HEIGHT//2), cv2.FONT_HERSHEY_SIMPLEX, 2, RED, 4)
            else:
                cv2.putText(frame, "BERABERE!", (WIDTH//2-100, HEIGHT//2), cv2.FONT_HERSHEY_SIMPLEX, 2, WHITE, 4)
            cv2.imshow("Soccer CV", frame)
            continue
        
        # Oyun mantığı
        time_left = max(0, 90 - (time.time() - start_time))
        
        # Oyuncu hareketi
        if key == ord('w'): player_y = max(105, player_y - 8)
        if key == ord('s'): player_y = min(HEIGHT-25, player_y + 8)
        if key == ord('a'): player_x = max(25, player_x - 8)
        if key == ord('d'): player_x = min(WIDTH-25, player_x + 8)
        
        # AI hareketi
        ai_x += (ball_x - ai_x) * 0.02
        ai_y += (ball_y - ai_y) * 0.02
        ai_x = max(WIDTH//2+50, min(WIDTH-25, ai_x))
        ai_y = max(105, min(HEIGHT-25, ai_y))
        
        # Top hareketi
        ball_x += ball_vx
        ball_y += ball_vy
        ball_vx *= 0.98
        ball_vy *= 0.98
        
        # Duvar çarpışmaları
        if ball_y < 80: ball_y = 80; ball_vy *= -0.8
        if ball_y > HEIGHT-15: ball_y = HEIGHT-15; ball_vy *= -0.8
        if ball_x < 15: ball_x = 15; ball_vx *= -0.8
        if ball_x > WIDTH-15: ball_x = WIDTH-15; ball_vx *= -0.8
        
        # Çarpışma - oyuncu
        dist = math.hypot(ball_x-player_x, ball_y-player_y)
        if dist < 40:
            dx = ball_x - player_x
            dy = ball_y - player_y
            d = math.hypot(dx, dy)
            if d > 0:
                ball_vx = dx/d * 12
                ball_vy = dy/d * 12
        
        # Çarpışma - AI
        dist = math.hypot(ball_x-ai_x, ball_y-ai_y)
        if dist < 40:
            dx = ball_x - ai_x
            dy = ball_y - ai_y
            d = math.hypot(dx, dy)
            if d > 0:
                ball_vx = dx/d * 12
                ball_vy = dy/d * 12
        
        # Kale kontrolü
        if ball_x < 30 and HEIGHT//2-70 < ball_y < HEIGHT//2+70:
            score_ai += 1
            ball_x, ball_y = WIDTH//2, HEIGHT//2
            ball_vx, ball_vy = 0, 0
        
        if ball_x > WIDTH-30 and HEIGHT//2-70 < ball_y < HEIGHT//2+70:
            score_player += 1
            ball_x, ball_y = WIDTH//2, HEIGHT//2
            ball_vx, ball_vy = 0, 0
        
        # Çizim
        draw_field(frame)
        draw_player(frame, player_x, player_y, RED, "OYUNCU")
        draw_player(frame, ai_x, ai_y, BLUE, "AI")
        draw_ball(frame, ball_x, ball_y)
        draw_ui(frame, score_player, score_ai, time_left)
        
        cv2.imshow("Soccer CV", frame)
    
    if cap:
        cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
