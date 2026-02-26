import sys, random, math
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# --- VERİ SETİ ---
KARAKTERLER = {
    "1": {"ad": "Gölge Savaşçı", "hiz": 6, "goz": Qt.cyan, "hasar": 1},
    "2": {"ad": "Hızlı Casus", "hiz": 10, "goz": Qt.yellow, "hasar": 0.5},
}

HARITALAR = {
    "Dojo": {"bg": [QColor(30, 30, 30), QColor(5, 5, 5)], "sun": QColor(255, 80, 0, 40)},
    "Neon City": {"bg": [QColor(15, 0, 30), QColor(2, 0, 5)], "sun": QColor(0, 255, 255, 30)}
}

class Particle:
    """Patlama ve efektler için parçacık sınıfı"""
    def __init__(self, pos, color):
        self.pos = QPointF(pos)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 7)
        self.vel = QPointF(math.cos(angle) * speed, math.sin(angle) * speed)
        self.life = 255
        self.color = color

    def update(self):
        self.pos += self.vel
        self.life -= 10

class UltimateShadow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1200, 800)
        self.setWindowTitle("Z-HUNTER: SHADOW EVOLUTION")
        self.setMouseTracking(True)
        
        # Ekran sallanması için offset
        self.shake_amount = 0
        self.init_game()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)

    def init_game(self):
        self.state = "START"
        self.p_pos = QPointF(600, 400)
        self.mouse_pos = QPoint(600, 400)
        self.enemies, self.bullets, self.trails, self.particles = [], [], [], []
        self.score, self.level = 0, 1
        self.p_can = 100
        self.sel_char = KARAKTERLER["1"]
        self.sel_map = "Dojo"

    def update_game(self):
        if self.state != "PLAY": return
        
        # 1. Ekran Sallanması Azaltma
        if self.shake_amount > 0: self.shake_amount -= 1

        # 2. Karakter Hareketi
        target = QPointF(self.mouse_pos)
        d = math.hypot(target.x()-self.p_pos.x(), target.y()-self.p_pos.y())
        if d > 5:
            move = QPointF((target.x()-self.p_pos.x())/d * self.sel_char["hiz"], 
                           (target.y()-self.p_pos.y())/d * self.sel_char["hiz"])
            self.p_pos += move
            if random.random() > 0.6:
                self.trails.append({'p': QPointF(self.p_pos), 'l': 150})

        # 3. Düşman Yönetimi
        if len(self.enemies) < 5 + self.level:
            spawn_side = random.choice(['T', 'B', 'L', 'R'])
            px = random.randint(0, 1200) if spawn_side in 'TB' else (-50 if spawn_side == 'L' else 1250)
            py = random.randint(0, 800) if spawn_side in 'LR' else (-50 if spawn_side == 'T' else 850)
            self.enemies.append({"p": QPointF(px, py), "hp": 1})

        for e in self.enemies[:]:
            dist = math.hypot(self.p_pos.x()-e["p"].x(), self.p_pos.y()-e["p"].y())
            e["p"] += QPointF((self.p_pos.x()-e["p"].x())/dist * 2.5, (self.p_pos.y()-e["p"].y())/dist * 2.5)
            
            # Oyuncu hasar alma
            if dist < 35:
                self.p_can -= 0.5
                self.shake_amount = 10
                if random.random() > 0.8:
                    self.particles.append(Particle(self.p_pos, Qt.red))

        # 4. Mermi ve Çarpışma Kontrolü
        for b in self.bullets[:]:
            b['p'] += b['v']
            # Düşman vuruş kontrolü
            for e in self.enemies[:]:
                if math.hypot(b['p'].x()-e['p'].x(), b['p'].y()-e['p'].y()) < 30:
                    if b in self.bullets: self.bullets.remove(b)
                    # Patlama efekti
                    for _ in range(8): self.particles.append(Particle(e['p'], self.sel_char["goz"]))
                    self.enemies.remove(e)
                    self.score += 10
                    if self.score % 100 == 0: self.level += 1
            
            if not self.rect().contains(b['p'].toPoint()): 
                if b in self.bullets: self.bullets.remove(b)

        # 5. Parçacık ve İz Güncelleme
        for p in self.particles[:]:
            p.update()
            if p.life <= 0: self.particles.remove(p)
        
        for t in self.trails[:]:
            t['l'] -= 10
            if t['l'] <= 0: self.trails.remove(t)

        if self.p_can <= 0: self.state = "OVER"
        self.update()

    def mousePressEvent(self, event):
        if self.state in ["START", "OVER"]: self.init_game(); self.state = "PLAY"
        elif self.state == "PLAY":
            dx, dy = self.mouse_pos.x()-self.p_pos.x(), self.mouse_pos.y()-self.p_pos.y()
            dist = math.hypot(dx, dy)
            if dist > 0:
                self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(dx/dist*15, dy/dist*15)})

    def mouseMoveEvent(self, event): self.mouse_pos = event.pos()

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        
        # Ekran sallama efekti uygulaması
        if self.shake_amount > 0:
            p.translate(random.randint(-self.shake_amount, self.shake_amount), 
                        random.randint(-self.shake_amount, self.shake_amount))

        # Arka Plan
        m = HARITALAR[self.sel_map]
        grad = QLinearGradient(0, 0, 0, 800)
        grad.setColorAt(0, m["bg"][0]); grad.setColorAt(1, m["bg"][1])
        p.fillRect(self.rect(), grad)
        
        # Atmosferik Işık
        p.setBrush(m["sun"]); p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(600, 100), 400, 400)

        if self.state == "PLAY":
            # Hareket İzleri
            for t in self.trails:
                p.setBrush(QColor(0, 0, 0, t['l'] // 2))
                p.drawEllipse(t['p'], 10, 10)

            # Parçacıklar
            for part in self.particles:
                c = QColor(part.color)
                c.setAlpha(part.life)
                p.setBrush(c)
                p.drawRect(QRectF(part.pos.x(), part.pos.y(), 4, 4))

            # Karakter ve Düşmanlar
            self.draw_shadow_unit(p, self.p_pos, self.sel_char["goz"], True)
            for e in self.enemies:
                self.draw_shadow_unit(p, e["p"], Qt.red, False)

            # Mermiler
            for b in self.bullets:
                p.setBrush(self.sel_char["goz"]); p.setPen(Qt.NoPen)
                p.drawEllipse(b["p"], 5, 5)

            # UI (Modern Görünüm)
            p.setPen(Qt.white); p.setFont(QFont("Arial", 12, QFont.Bold))
            p.drawText(20, 40, f"SCORE: {self.score} | LEVEL: {self.level}")
            p.setBrush(QColor(255, 255, 255, 50)); p.drawRect(20, 55, 200, 10)
            p.setBrush(QColor(0, 255, 100)); p.drawRect(20, 55, int(self.p_can * 2), 10)

        elif self.state == "OVER":
            p.fillRect(self.rect(), QColor(0,0,0,200))
            p.setPen(Qt.red); p.setFont(QFont("Impact", 70))
            p.drawText(self.rect(), Qt.AlignCenter, f"ELENDİN\nSKOR: {self.score}")

        elif self.state == "START":
            p.setPen(Qt.white); p.setFont(QFont("Impact", 50))
            p.drawText(self.rect(), Qt.AlignCenter, "Z-HUNTER\nBAŞLAMAK İÇİN TIKLA")

    def draw_shadow_unit(self, p, pos, eye_color, is_player):
        p.save()
        p.translate(pos)
        
        # Gölge Halkası (Yerdeki gölge)
        p.setBrush(QColor(0, 0, 0, 60))
        p.drawEllipse(-25, 25, 50, 15)
        
        # Vücut
        p.setBrush(Qt.black); p.setPen(QPen(Qt.black, 1))
        p.drawEllipse(-18, -18, 36, 36) # Kafa
        
        # Gözler
        p.setBrush(eye_color)
        angle = math.atan2(self.mouse_pos.y()-pos.y(), self.mouse_pos.x()-pos.x())
        p.rotate(math.degrees(angle))
        p.drawRect(6, -6, 7, 3)
        p.drawRect(6, 3, 7, 3)
        p.restore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = UltimateShadow()
    w.show()
    sys.exit(app.exec_())