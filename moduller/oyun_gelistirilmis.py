import sys, random, math, time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# --- VERI SETI ---
KARAKTERLER = {
    "1": {"ad": "Golge Savasci", "hiz": 6, "goz": Qt.cyan, "hasar": 1, "silah": "tabanca"},
    "2": {"ad": "Hizli Casus", "hiz": 10, "goz": Qt.yellow, "hasar": 0.5, "silah": "lazer"},
    "3": {"ad": "Agir Tank", "hiz": 3, "goz": Qt.red, "hasar": 2, "silah": "pompa"},
}

SILAHLAR = {
    "tabanca": {"renk": Qt.cyan, "boyut": 5, "hiz": 15, "aralik": 0.3, "hasar": 1},
    "pompa": {"renk": Qt.yellow, "boyut": 12, "hiz": 10, "aralik": 0.8, "hasar": 3},
    "lazer": {"renk": Qt.magenta, "boyut": 3, "hiz": 25, "aralik": 0.15, "hasar": 0.5},
}

DUSMAN_TURLERI = {
    "normal": {"hp": 1, "hiz": 2.5, "renk": Qt.red, "boyut": 20, "puan": 10},
    "hizli": {"hp": 0.5, "hiz": 5, "renk": Qt.yellow, "boyut": 15, "puan": 20},
    "tank": {"hp": 5, "hiz": 1.5, "renk": Qt.darkGreen, "boyut": 35, "puan": 50},
    "boss": {"hp": 50, "hiz": 1, "renk": Qt.darkRed, "boyut": 60, "puan": 500},
}

POWER_UPLAR = {
    "can": {"renk": Qt.green, "sembol": "+", "aciklama": "Can +30"},
    "silah_pompa": {"renk": Qt.yellow, "sembol": "P", "aciklama": "Pompa"},
    "silah_lazer": {"renk": Qt.magenta, "sembol": "L", "aciklama": "Lazer"},
    "silah_tabanca": {"renk": Qt.cyan, "sembol": "T", "aciklama": "Tabanca"},
    "zirh": {"renk": Qt.blue, "sembol": "Z", "aciklama": "Zirh +20"},
    "hiz": {"renk": Qt.white, "sembol": "H", "aciklama": " Hiz +50%"},
}

HARITALAR = {
    "Dojo": {"bg": [QColor(30, 30, 30), QColor(5, 5, 5)], "sun": QColor(255, 80, 0, 40), "ad": "DOJO"},
    "Neon City": {"bg": [QColor(15, 0, 30), QColor(2, 0, 5)], "sun": QColor(0, 255, 255, 30), "ad": "NEON SEHIR"},
    "Lava Arena": {"bg": [QColor(60, 10, 0), QColor(20, 0, 0)], "sun": QColor(255, 50, 0, 50), "ad": "LAVA ARENA"},
}

class Particle:
    def __init__(self, pos, color, size=None):
        self.pos = QPointF(pos)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 10)
        self.vel = QPointF(math.cos(angle) * speed, math.sin(angle) * speed)
        self.life = 255
        self.color = color
        self.size = size if size else random.randint(3, 8)

    def update(self):
        self.pos += self.vel
        self.vel *= 0.95
        self.life -= 8

class LaserBeam:
    def __init__(self, start, end, color):
        self.start = QPointF(start)
        self.end = QPointF(end)
        self.color = color
        self.life = 255
        self.width = 3

    def update(self):
        self.life -= 15
        self.width = max(1, self.width * 0.9)

class Shockwave:
    def __init__(self, pos, color):
        self.pos = QPointF(pos)
        self.radius = 10
        self.color = color
        self.life = 255

    def update(self):
        self.radius += 5
        self.life -= 12

class UltimateShadow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1200, 800)
        self.setWindowTitle("Z-HUNTER: SHADOW EVOLUTION - GELISTIRILMIS")
        self.setMouseTracking(True)
        
        self.shake_amount = 0
        self.last_shot_time = 0
        self.init_game()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)

    def init_game(self):
        self.state = "MENU"
        self.p_pos = QPointF(600, 400)
        self.mouse_pos = QPoint(600, 400)
        self.enemies, self.bullets, self.trails, self.particles = [], [], [], []
        self.lasers, self.shockwaves, self.powerups = [], [], []
        self.score, self.level, self.kills = 0, 1, 0
        self.p_can = 100
        self.p_zirh = 0
        self.max_can = 100
        self.sel_char = KARAKTERLER["1"]
        self.sel_map = "Dojo"
        self.silah = "tabanca"
        self.hiz_boost = 1.0
        self.boss_spawned = False
        self.boss = None
        self.silah_degisim_suresi = 0
        self.istatistikler = {
            "toplam_ates": 0,
            "isabet": 0,
            "max_skor": 0,
            "toplam_olan": 0
        }

    def update_game(self):
        if self.state != "PLAY": return
        
        if self.silah_degisim_suresi > 0:
            self.silah_degisim_suresi -= 1
            if self.silah_degisim_suresi <= 0:
                self.silah = self.sel_char.get("silah", "tabanca")
        
        if self.hiz_boost > 1.0:
            self.hiz_boost = max(1.0, self.hiz_boost - 0.001)

        if self.shake_amount > 0: self.shake_amount -= 1

        target = QPointF(self.mouse_pos)
        d = math.hypot(target.x()-self.p_pos.x(), target.y()-self.p_pos.y())
        if d > 5:
            hiz = self.sel_char["hiz"] * self.hiz_boost
            move = QPointF((target.x()-self.p_pos.x())/d * hiz, 
                           (target.y()-self.p_pos.y())/d * hiz)
            self.p_pos += move
            if random.random() > 0.5:
                self.trails.append({'p': QPointF(self.p_pos), 'l': 150, 'renk': self.silah_bilgi()["renk"]})

        if not self.boss_spawned and self.level % 5 == 0 and self.score >= self.level * 100:
            self.boss_spawned = True
            self.spawn_boss()
        
        max_enemies = 3 + self.level * 2
        if len(self.enemies) < max_enemies and not self.boss_spawned:
            spawn_side = random.choice(['T', 'B', 'L', 'R'])
            px = random.randint(0, 1200) if spawn_side in 'TB' else (-50 if spawn_side == 'L' else 1250)
            py = random.randint(0, 800) if spawn_side in 'LR' else (-50 if spawn_side == 'T' else 850)
            
            if self.level >= 3:
                tur = random.choices(["normal", "hizli", "tank"], weights=[60, 25, 15])[0]
            else:
                tur = "normal"
            
            self.enemies.append({
                "p": QPointF(px, py), 
                "hp": DUSMAN_TURLERI[tur]["hp"],
                "max_hp": DUSMAN_TURLERI[tur]["hp"],
                "tur": tur
            })

        for e in self.enemies[:]:
            tur_bilgi = DUSMAN_TURLERI[e["tur"]]
            dist = math.hypot(self.p_pos.x()-e["p"].x(), self.p_pos.y()-e["p"].y())
            if dist > 0:
                e["p"] += QPointF(
                    (self.p_pos.x()-e["p"].x())/dist * tur_bilgi["hiz"], 
                    (self.p_pos.y()-e["p"].y())/dist * tur_bilgi["hiz"]
                )
            
            if dist < 35:
                hasar = 0.5 * (1 if e["tur"] != "tank" else 2)
                self.al_hasar(hasar)
                if random.random() > 0.7:
                    self.particles.append(Particle(self.p_pos, Qt.red, 5))

        for b in self.bullets[:]:
            b['p'] += b['v']
            for e in self.enemies[:]:
                tur_bilgi = DUSMAN_TURLERI[e["tur"]]
                if math.hypot(b['p'].x()-e['p'].x(), b['p'].y()-e['p'].y()) < tur_bilgi["boyut"]:
                    silah_bilgi = self.silah_bilgi()
                    e['hp'] -= silah_bilgi["hasar"]
                    self.istatistikler["isabet"] += 1
                    
                    for _ in range(5): 
                        self.particles.append(Particle(e['p'], tur_bilgi["renk"], 3))
                    
                    if b in self.bullets: self.bullets.remove(b)
                    
                    if e['hp'] <= 0:
                        for _ in range(15): 
                            self.particles.append(Particle(e['p'], tur_bilgi["renk"], 6))
                        self.shockwaves.append(Shockwave(e['p'], tur_bilgi["renk"]))
                        
                        self.enemies.remove(e)
                        self.score += tur_bilgi["puan"]
                        self.kills += 1
                        
                        if random.random() < 0.15:
                            self.spawn_powerup(e['p'])
                        
                        if self.boss and e == self.boss:
                            self.boss = None
                            self.score += 1000
                            self.level += 1
                            self.boss_spawned = False
                            self.show_message("BOSS OLDURULDU!", Qt.green)
                        elif self.score >= self.level * 200:
                            self.level += 1
                            self.show_message(f"SEVIYE {self.level}!", Qt.yellow)
            
            if not self.rect().contains(b['p'].toPoint()): 
                if b in self.bullets: self.bullets.remove(b)

        for l in self.lasers[:]:
            l.update()
            if l.life <= 0: self.lasers.remove(l)

        for s in self.shockwaves[:]:
            s.update()
            if s.life <= 0: self.shockwaves.remove(s)

        for pu in self.powerups[:]:
            dist = math.hypot(self.p_pos.x()-pu["p"].x(), self.p_pos.y()-pu["p"].y())
            if dist < 30:
                self.powerup_uygula(pu)
                self.powerups.remove(pu)

        for p in self.particles[:]:
            p.update()
            if p.life <= 0: self.particles.remove(p)
        
        for t in self.trails[:]:
            t['l'] -= 8
            if t['l'] <= 0: self.trails.remove(t)

        if self.p_can < self.max_can and random.random() < 0.01:
            self.p_can = min(self.max_can, self.p_can + 0.5)

        if self.p_can <= 0: 
            self.state = "OVER"
            self.istatistikler["max_skor"] = max(self.istatistikler["max_skor"], self.score)
        
        self.update()

    def silah_bilgi(self):
        return SILAHLAR[self.silah]

    def spawn_boss(self):
        side = random.choice(['T', 'B', 'L', 'R'])
        if side == 'T':
            px, py = 600, -80
        elif side == 'B':
            px, py = 600, 880
        elif side == 'L':
            px, py = -80, 400
        else:
            px, py = 1280, 400
        
        self.boss = {
            "p": QPointF(px, py),
            "hp": 50 + (self.level // 5) * 25,
            "max_hp": 50 + (self.level // 5) * 25,
            "tur": "boss"
        }
        self.enemies.append(self.boss)
        self.show_message(f"BOSS GELIYOR!", Qt.red)
        self.shake_amount = 20

    def spawn_powerup(self, pos):
        tur = random.choice(list(POWER_UPLAR.keys()))
        self.powerups.append({
            "p": QPointF(pos),
            "tur": tur,
            "bilgi": POWER_UPLAR[tur]
        })

    def powerup_uygula(self, powerup):
        tur = powerup["tur"]
        if tur == "can":
            self.p_can = min(self.max_can + 50, self.p_can + 30)
        elif tur == "zirh":
            self.p_zirh = min(100, self.p_zirh + 20)
        elif tur == "hiz":
            self.hiz_boost = 1.5
        elif tur.startswith("silah_"):
            self.silah = tur.replace("silah_", "")
            self.silah_degisim_suresi = 1000
        
        self.show_message(powerup["bilgi"]["aciklama"], powerup["bilgi"]["renk"])

    def al_hasar(self, miktar):
        if self.p_zirh > 0:
            self.p_zirh -= miktar * 0.5
            miktar *= 0.5
        self.p_can -= miktar
        self.shake_amount = 10
        if random.random() > 0.5:
            self.particles.append(Particle(self.p_pos, Qt.red))

    def show_message(self, text, renk):
        self.aktif_mesaj = {"metin": text, "renk": renk, "sure": 120}
        self.update()

    def mousePressEvent(self, event):
        if self.state == "MENU":
            self.state = "PLAY"
        elif self.state in ["OVER", "WIN"]:
            self.init_game()
            self.state = "PLAY"
        elif self.state == "PLAY":
            self.ates_et()

    def mouseMoveEvent(self, event): 
        self.mouse_pos = event.pos()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            if self.state == "PLAY":
                self.state = "PAUSE"
            elif self.state == "PAUSE":
                self.state = "PLAY"
        elif event.key() == Qt.Key_1:
            self.silah = "tabanca"
        elif event.key() == Qt.Key_2:
            self.silah = "pompa"
        elif event.key() == Qt.Key_3:
            self.silah = "lazer"
        elif event.key() == Qt.Key_H:
            self.harita_degistir()

    def harita_degistir(self):
        haritalar = list(HARITALAR.keys())
        idx = haritalar.index(self.sel_map)
        self.sel_map = haritalar[(idx + 1) % len(haritalar)]

    def ates_et(self):
        simdi = time.time()
        silah_bilgi = self.silah_bilgi()
        
        if simdi - self.last_shot_time < silah_bilgi["aralik"]:
            return
        
        self.last_shot_time = simdi
        self.istatistikler["toplam_ates"] += 1
        
        dx, dy = self.mouse_pos.x()-self.p_pos.x(), self.mouse_pos.y()-self.p_pos.y()
        dist = math.hypot(dx, dy)
        if dist > 0:
            vx, vy = dx/dist * silah_bilgi["hiz"], dy/dist * silah_bilgi["hiz"]
            
            if self.silah == "pompa":
                for _ in range(5):
                    aci = random.uniform(-0.3, 0.3)
                    self.bullets.append({
                        "p": QPointF(self.p_pos), 
                        "v": QPointF(
                            vx * math.cos(aci) - vy * math.sin(aci),
                            vx * math.sin(aci) + vy * math.cos(aci)
                        )
                    })
                self.shake_amount = 5
            elif self.silah == "lazer":
                self.lasers.append(LaserBeam(self.p_pos, self.mouse_pos, silah_bilgi["renk"]))
                for e in self.enemies[:]:
                    if self.lazer_vurus_kontrolu(self.p_pos, self.mouse_pos, e["p"]):
                        e['hp'] -= silah_bilgi["hasar"]
                        if e['hp'] <= 0:
                            self.enemies.remove(e)
                            self.score += DUSMAN_TURLERI[e["tur"]]["puan"]
                            for _ in range(10):
                                self.particles.append(Particle(e['p'], DUSMAN_TURLERI[e["tur"]]["renk"], 5))
            else:
                self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy)})

    def lazer_vurus_kontrolu(self, bas, bit, hedef):
        dx = bit.x() - bas.x()
        dy = bit.y() - bas.y()
        if dx == 0 and dy == 0: return False
        
        t = ((hedef.x() - bas.x()) * dx + (hedef.y() - bas.y()) * dy) / (dx*dx + dy*dy)
        t = max(0, min(1, t))
        
        en_yakin_x = bas.x() + t * dx
        en_yakin_y = bas.y() + t * dy
        
        dist = math.hypot(hedef.x() - en_yakin_x, hedef.y() - en_yakin_y)
        return dist < 30

    def paintEvent(self, event):
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        
        if self.shake_amount > 0:
            p.translate(random.randint(-self.shake_amount, self.shake_amount), 
                        random.randint(-self.shake_amount, self.shake_amount))

        m = HARITALAR[self.sel_map]
        grad = QLinearGradient(0, 0, 0, 800)
        grad.setColorAt(0, m["bg"][0]); grad.setColorAt(1, m["bg"][1])
        p.fillRect(self.rect(), grad)
        
        p.setBrush(m["sun"]); p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(600, 100), 400, 400)
        
        p.setPen(QPen(QColor(255,255,255,10), 1))
        for i in range(0, 1200, 50):
            p.drawLine(i, 0, i, 800)
        for i in range(0, 800, 50):
            p.drawLine(0, i, 1200, i)

        if self.state == "MENU":
            self.ciz_menu(p)
        elif self.state == "PLAY":
            self.ciz_oyun(p)
        elif self.state == "PAUSE":
            self.ciz_oyun(p)
            self.ciz_pause(p)
        elif self.state == "OVER":
            self.ciz_oyun(p)
            self.ciz_game_over(p)

    def ciz_menu(self, p):
        p.fillRect(self.rect(), QColor(0,0,0,180))
        
        p.setPen(Qt.cyan); p.setFont(QFont("Impact", 60))
        p.drawText(self.rect(), Qt.AlignCenter, "Z-HUNTER\nSHADOW EVOLUTION")
        
        p.setPen(Qt.white); p.setFont(QFont("Arial", 20))
        p.drawText(QRect(0, 350, 1200, 50), Qt.AlignCenter, "GELISTIRILMIS VERSIYON")
        
        p.setFont(QFont("Arial", 16))
        y = 420
        for key, kar in KARAKTERLER.items():
            p.setPen(kar["goz"])
            p.drawText(QRect(0, y, 1200, 30), Qt.AlignCenter, 
                      f"[{key}] {kar['ad']} - Hiz: {kar['hiz']} - Hasar: {kar['hasar']}")
            y += 30
        
        p.setPen(Qt.yellow); p.setFont(QFont("Arial", 14))
        p.drawText(QRect(0, 550, 1200, 30), Qt.AlignCenter, f"HARITA: {['ad']} (H ile degistir)")
        
        p.setPen(Qt.green); p.setFont(QFont("Arial", 24))
        p.drawText(QRect(0, 650, 1200, 50), Qt.AlignCenter, "BASLAMAK ICIN TIKLA")
        
        p.setPen(Qt.gray); p.setFont(QFont("Arial", 12))
        p.drawText(QRect(0, 720, 1200, 30), Qt.AlignCenter, 
                  "KONTROLLER: Mouse - Hareket | Tik - Ates | 1/2/3 - Silah | ESC - Dur")

    def ciz_oyun(self, p):
        for t in self.trails:
            renk = t.get('renk', Qt.black)
            c = QColor(renk)
            c.setAlpha(t['l'] // 2)
            p.setBrush(c)
            p.drawEllipse(t['p'], 10, 10)

        for s in self.shockwaves:
            c = QColor(s.color)
            c.setAlpha(s.life)
            p.setPen(QPen(c, 3)); p.setBrush(Qt.NoBrush)
            p.drawEllipse(s.pos, s.radius, s.radius)

        for part in self.particles:
            c = QColor(part.color)
            c.setAlpha(part.life)
            p.setBrush(c)
            p.drawRect(QRectF(part.pos.x()-part.size/2, part.pos.y()-part.size/2, part.size, part.size))

        for pu in self.powerups:
            bilgi = pu["bilgi"]
            c = QColor(bilgi["renk"])
            p.setBrush(c); p.setPen(Qt.white)
            p.drawEllipse(pu["p"], 15, 15)
            p.setFont(QFont("Arial", 12, QFont.Bold))
            p.drawText(pu["p"].x()-4, pu["p"].y()+4, bilgi["sembol"])

        for l in self.lasers:
            c = QColor(l.color)
            c.setAlpha(l.life)
            p.setPen(QPen(c, l.width)); p.setBrush(Qt.NoBrush)
            p.drawLine(l.start, l.end)

        self.draw_shadow_unit(p, self.p_pos, self.sel_char["goz"], True)
        for e in self.enemies:
            tur_bilgi = DUSMAN_TURLERI[e["tur"]]
            self.draw_shadow_unit(p, e["p"], tur_bilgi["renk"], False, tur_bilgi["boyut"])
            
            if e["tur"] == "boss":
                hp_oran = e["hp"] / e["max_hp"]
                p.setBrush(QColor(100, 0, 0)); p.setPen(Qt.NoPen)
                p.drawRect(e["p"].x()-40, e["p"].y()-50, 80, 8)
                p.setBrush(Qt.red)
                p.drawRect(e["p"].x()-40, e["p"].y()-50, 80*hp_oran, 8)

        silah_bilgi = self.silah_bilgi()
        for b in self.bullets:
            p.setBrush(silah_bilgi["renk"]); p.setPen(Qt.NoPen)
            p.drawEllipse(b["p"], silah_bilgi["boyut"], silah_bilgi["boyut"])

        self.ciz_ui(p)

    def ciz_ui(self, p):
        p.setBrush(QColor(0, 0, 0, 150))
        p.drawRect(0, 0, 1200, 50)
        
        p.setPen(Qt.white); p.setFont(QFont("Arial", 14, QFont.Bold))
        p.drawText(20, 32, f"SKOR: {self.score}")
        p.drawText(150, 32, f"SEVIYE: {self.level}")
        p.drawText(280, 32, f"OLDURME: {self.kills}")
        
        p.setFont(QFont("Arial", 12))
        p.setPen(self.silah_bilgi()["renk"])
        silah_isim = {"tabanca": "Tabanca", "pompa": "Pompa", "lazer": "Lazer"}[self.silah]
        p.drawText(450, 32, f"SILAH: {silah_isim.upper()}")
        
        p.setPen(Qt.white); p.setFont(QFont("Arial", 12, QFont.Bold))
        p.drawText(650, 32, "CAN:")
        p.setBrush(QColor(50, 50, 50)); p.setPen(Qt.NoPen)
        p.drawRect(700, 18, 200, 16)
        
        if self.p_can > 60:
            p.setBrush(Qt.green)
        elif self.p_can > 30:
            p.setBrush(Qt.yellow)
        else:
            p.setBrush(Qt.red)
        p.drawRect(702, 20, int(self.p_can * 1.96), 12)
        
        if self.p_zirh > 0:
            p.setBrush(QColor(30, 30, 150)); p.setPen(Qt.NoPen)
            p.drawRect(702, 32, int(self.p_zirh * 1.96), 4)
        
        if self.boss_spawned and self.boss:
            p.setPen(Qt.red); p.setFont(QFont("Arial", 16, QFont.Bold))
            p.drawText(900, 32, "BOSS")

        if hasattr(self, 'aktif_mesaj') and self.aktif_mesaj:
            p.setPen(self.aktif_mesaj["renk"]); p.setFont(QFont("Arial", 28, QFont.Bold))
            p.drawText(self.rect(), Qt.AlignCenter, self.aktif_mesaj["metin"])
            self.aktif_mesaj["sure"] -= 1
            if self.aktif_mesaj["sure"] <= 0:
                del self.aktif_mesaj

    def ciz_pause(self, p):
        p.fillRect(self.rect(), QColor(0,0,0,150))
        p.setPen(Qt.white); p.setFont(QFont("Impact", 60))
        p.drawText(self.rect(), Qt.AlignCenter, "DURAKLADI")
        p.setFont(QFont("Arial", 20))
        p.drawText(QRect(0, 100, 1200, 40), Qt.AlignCenter, "Devam etmek için ESC tusuna bas")

    def ciz_game_over(self, p):
        p.fillRect(self.rect(), QColor(0,0,0,200))
        p.setPen(Qt.red); p.setFont(QFont("Impact", 70))
        p.drawText(self.rect(), Qt.AlignCenter, f"ELDIN\n\nSKOR: {self.score}")
        
        p.setPen(Qt.cyan); p.setFont(QFont("Arial", 16))
        y = 450
        for key, val in self.istatistikler.items():
            p.drawText(QRect(0, y, 1200, 30), Qt.AlignCenter, f"{key.upper()}: {val}")
            y += 30
        
        p.setPen(Qt.green); p.setFont(QFont("Arial", 24))
        p.drawText(QRect(0, 600, 1200, 50), Qt.AlignCenter, "TEKRAR OYNAMAK ICIN TIKLA")

    def draw_shadow_unit(self, p, pos, eye_color, is_player, boyut=None):
        p.save()
        p.translate(pos)
        
        if boyut is None: boyut = 25 if is_player else 20
        
        p.setBrush(QColor(0, 0, 0, 60))
        p.drawEllipse(-boyut, boyut//2, boyut*2, boyut//2)
        
        p.setBrush(Qt.black); p.setPen(QPen(Qt.black, 1))
        p.drawEllipse(-boyut+5, -boyut+5, (boyut-5)*2, (boyut-5)*2)
        
        p.setBrush(eye_color)
        if is_player:
            angle = math.atan2(self.mouse_pos.y()-pos.y(), self.mouse_pos.x()-pos.x())
        else:
            angle = math.atan2(self.p_pos.y()-pos.y(), self.p_pos.x()-pos.x())
        p.rotate(math.degrees(angle))
        
        gz_boyut = boyut // 4
        p.drawRect(boyut//3, -gz_boyut, gz_boyut+2, gz_boyut//2)
        p.drawRect(boyut//3, gz_boyut//2, gz_boyut+2, gz_boyut//2)
        p.restore()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = UltimateShadow()
    w.show()
    sys.exit(app.exec_())
