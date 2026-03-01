import sys, random, math, time, json, os
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# --- VERI SETI ---
KARAKTERLER = {
    "1": {
        "ad": "Gölge Savaşçı", 
        "hiz": 6, 
        "goz": Qt.cyan, 
        "hasar": 1,
        "silah": "tabanca",
        "ozel": "Hızlı Hareket",
        "renk": QColor(0, 200, 255),
        "aciklama": "Dengeli savaşçı",
        "fiyat": 0
    },
    "2": {
        "ad": "Hızlı Casus", 
        "hiz": 10, 
        "goz": Qt.yellow, 
        "hasar": 0.5,
        "silah": "lazer",
        "ozel": "Hayalet",
        "renk": QColor(255, 220, 0),
        "aciklama": "En hızlı karakter",
        "fiyat": 500
    },
    "3": {
        "ad": "Ağır Tank", 
        "hiz": 3, 
        "goz": Qt.red, 
        "hasar": 2,
        "silah": "pompa",
        "ozel": "Zırh",
        "renk": QColor(255, 50, 50),
        "aciklama": "En güçlü",
        "fiyat": 750
    },
    "4": {
        "ad": "Neon Ninja", 
        "hiz": 8, 
        "goz": Qt.magenta, 
        "hasar": 1.5,
        "silah": "çift",
        "ozel": "Çift Atış",
        "renk": QColor(200, 0, 255),
        "aciklama": "İki eliyle ateş eder",
        "fiyat": 1000
    },
    "5": {
        "ad": "Buz Savaşçısı", 
        "hiz": 7, 
        "goz": QColor(100, 200, 255), 
        "hasar": 1.2,
        "silah": "buz",
        "ozel": "Yavaşlatma",
        "renk": QColor(0, 150, 255),
        "aciklama": "Düşmanları yavaşlatır",
        "fiyat": 1500
    },
    "6": {
        "ad": "Ateş Şeytanı", 
        "hiz": 6, 
        "goz": QColor(255, 100, 0), 
        "hasar": 1.8,
        "silah": "ates",
        "ozel": "Yanma Hasarı",
        "renk": QColor(255, 50, 0),
        "aciklama": "Düşmanları yakar",
        "fiyat": 2000
    },
    "7": {
        "ad": "Elektro Savaşçı", 
        "hiz": 9, 
        "goz": QColor(255, 255, 0), 
        "hasar": 1.3,
        "silah": "elektrik",
        "ozel": "Zincirleme",
        "renk": QColor(255, 255, 0),
        "aciklama": "Birden fazla düşmana",
        "fiyat": 2500
    },
}

SILAHLAR = {
    "tabanca": {"renk": Qt.cyan, "boyut": 5, "hiz": 15, "aralik": 0.3, "hasar": 1, "ad": "Tabanca", "fiyat": 0},
    "pompa": {"renk": Qt.yellow, "boyut": 12, "hiz": 10, "aralik": 0.8, "hasar": 3, "ad": "Pompalı", "fiyat": 500},
    "lazer": {"renk": Qt.magenta, "boyut": 3, "hiz": 25, "aralik": 0.15, "hasar": 0.5, "ad": "Lazer", "fiyat": 750},
    "çift": {"renk": Qt.green, "boyut": 4, "hiz": 12, "aralik": 0.2, "hasar": 1, "ad": "Çift Tab", "fiyat": 1000},
    "buz": {"renk": QColor(100, 200, 255), "boyut": 6, "hiz": 14, "aralik": 0.25, "hasar": 1.2, "ad": "Buz Tab", "fiyat": 1500},
    "ates": {"renk": QColor(255, 100, 0), "boyut": 8, "hiz": 12, "aralik": 0.35, "hasar": 2, "ad": "Ateş", "fiyat": 2000},
    "elektrik": {"renk": Qt.yellow, "boyut": 4, "hiz": 20, "aralik": 0.2, "hasar": 1.5, "ad": "Elektrik", "fiyat": 2500},
}

DUSMAN_TURLERI = {
    "normal": {"hp": 1, "hiz": 2.5, "renk": Qt.red, "boyut": 20, "puan": 10, "ad": "Gölge", "efekt": None},
    "hizli": {"hp": 0.5, "hiz": 5, "renk": Qt.yellow, "boyut": 15, "puan": 20, "ad": "Hız", "efekt": None},
    "tank": {"hp": 5, "hiz": 1.5, "renk": Qt.darkGreen, "boyut": 35, "puan": 50, "ad": "Dev", "efekt": None},
    "boss": {"hp": 50, "hiz": 1, "renk": Qt.darkRed, "boyut": 60, "puan": 500, "ad": "BOSS", "efekt": None},
    "atesli": {"hp": 2, "hiz": 2, "renk": QColor(255, 100, 0), "boyut": 25, "puan": 30, "ad": "Ateş", "efekt": "yanma"},
    "elektrikli": {"hp": 1.5, "hiz": 3, "renk": QColor(255, 255, 100), "boyut": 22, "puan": 25, "ad": "Elektrik", "efekt": "çarpma"},
    "hayalet": {"hp": 0.5, "hiz": 4, "renk": QColor(200, 200, 255), "boyut": 18, "puan": 40, "ad": "Hayalet", "efekt": "geçirgen"},
}

POWER_UPLAR = {
    "can": {"renk": Qt.green, "sembol": "+", "aciklama": "Can +30", "fiyat": 100},
    "zirh": {"renk": Qt.blue, "sembol": "Z", "aciklama": "Zırh +25", "fiyat": 150},
    "hiz": {"renk": Qt.white, "sembol": "H", "aciklama": "Hız +50%", "fiyat": 200},
    "silah_pompa": {"renk": Qt.yellow, "sembol": "P", "aciklama": "Pompalı", "fiyat": 300},
    "silah_lazer": {"renk": Qt.magenta, "sembol": "L", "aciklama": "Lazer", "fiyat": 350},
    "silah_buz": {"renk": QColor(100, 200, 255), "sembol": "B", "aciklama": "Buz", "fiyat": 400},
}

HARITALAR = {
    "Dojo": {"bg": [QColor(30, 30, 30), QColor(5, 5, 5)], "sun": QColor(255, 80, 0, 40), "ad": "DOJO", "desen": "izgara"},
    "Neon City": {"bg": [QColor(15, 0, 30), QColor(2, 0, 5)], "sun": QColor(0, 255, 255, 30), "ad": "NEON ŞEHİR", "desen": "izgara"},
    "Lava Arena": {"bg": [QColor(60, 10, 0), QColor(20, 0, 0)], "sun": QColor(255, 50, 0, 50), "ad": "LAVA ARENA", "desen": "daire"},
    "Uzay İstasyonu": {"bg": [QColor(10, 0, 20), QColor(0, 0, 10)], "sun": QColor(100, 100, 255, 30), "ad": "UZAY", "desen": "yildiz"},
}

class Particle:
    def __init__(self, pos, color, size=None, efekt=None):
        self.pos = QPointF(pos)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 12)
        self.vel = QPointF(math.cos(angle) * speed, math.sin(angle) * speed)
        self.life = 255
        self.color = color
        self.size = size if size else random.randint(3, 10)
        self.efekt = efekt
        self.rotation = random.uniform(0, 360)
        self.rot_speed = random.uniform(-10, 10)

    def update(self):
        self.pos += self.vel
        self.vel *= 0.95
        self.life -= 8
        self.rotation += self.rot_speed

class SparkEffect:
    """Kıvılcım efekti"""
    def __init__(self, pos, color):
        self.particles = []
        for _ in range(8):
            p = Particle(pos, color, random.randint(2, 5))
            p.vel *= 1.5
            self.particles.append(p)
    
    def update(self):
        for p in self.particles:
            p.update()
        self.particles = [p for p in self.particles if p.life > 0]
        return len(self.particles) > 0
    
    def draw(self, p):
        for sp in self.particles:
            c = QColor(sp.color)
            c.setAlpha(sp.life)
            p.setBrush(c)
            p.drawRect(QRectF(sp.pos.x()-2, sp.pos.y()-2, 4, 4))

class Trail:
    """Parlak iz efekti"""
    def __init__(self, pos, color):
        self.pos = QPointF(pos)
        self.color = color
        self.life = 200
        self.size = 15
    
    def update(self):
        self.life -= 5
        self.size *= 0.98
        return self.life > 0
    
    def draw(self, p):
        c = QColor(self.color)
        c.setAlpha(self.life // 2)
        p.setBrush(c)
        p.drawEllipse(self.pos, self.size, self.size)

class LaserBeam:
    def __init__(self, start, end, color):
        self.start = QPointF(start)
        self.end = QPointF(end)
        self.color = color
        self.life = 255

    def update(self):
        self.life -= 15

class Shockwave:
    def __init__(self, pos, color):
        self.pos = QPointF(pos)
        self.radius = 10
        self.max_radius = 80
        self.color = color
        self.life = 255

    def update(self):
        self.radius += 5
        self.life -= 12

class GlowEffect:
    """Neon glow efekti"""
    def __init__(self, pos, color, size):
        self.pos = QPointF(pos)
        self.color = color
        self.size = size
        self.life = 255
    
    def update(self):
        self.life -= 10
        self.size += 0.5
        return self.life > 0
    
    def draw(self, p):
        c = QColor(self.color)
        c.setAlpha(self.life // 3)
        p.setPen(QPen(c, 3))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(self.pos, self.size, self.size)

class KayitSistemi:
    """Oyun kayıt sistemi"""
    @staticmethod
    def kaydet(veriler, dosya_adi="oyun_kayit.json"):
        try:
            with open(dosya_adi, 'w', encoding='utf-8') as f:
                json.dump(veriler, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    @staticmethod
    def yukle(dosya_adi="oyun_kayit.json"):
        try:
            with open(dosya_adi, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None

class UltimateShadow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1200, 800)
        self.setWindowTitle("Z-HUNTER: SHADOW EVOLUTION - GELİŞMİŞ")
        self.setMouseTracking(True)
        
        self.shake_amount = 0
        self.last_shot_time = 0
        self.init_game()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)
        
        # Kayıtlı veriler
        self.kayit = KayitSistemi.yukle() or {"para": 0, " satin_alinan_karakterler": ["1"], " satin_alinan_silahlar": ["tabanca"], "en_yuksek_skor": 0}
        self.para = self.kayit.get("para", 0)
        self.satin_alinan_karakterler = self.kayit.get(" satin_alinan_karakterler", ["1"])
        self.satin_alinan_silahlar = self.kayit.get(" satin_alinan_silahlar", ["tabanca"])
        
        # Menü sayfası
        self.menu_sayfa = "karakter"  # karakter, magaza, ayar

    def init_game(self):
        self.state = "MENU"
        self.p_pos = QPointF(600, 400)
        self.mouse_pos = QPoint(600, 400)
        self.enemies, self.bullets = [], []
        self.trails, self.particles = [], []
        self.sparks, self.glows = [], []
        self.lasers, self.shockwaves, self.powerups = [], [], []
        self.score, self.level, self.kills = 0, 1, 0
        self.p_can, self.p_zirh = 100, 0
        self.max_can = 100
        self.sel_char = KARAKTERLER["1"]
        self.sel_map = "Dojo"
        self.silah = "tabanca"
        self.hiz_boost = 1.0
        self.boss_spawned = False
        self.boss = None
        self.silah_suresi = 0
        self.menu_secim = 0
        self.istatistikler = {"ates": 0, "isabet": 0, "max_skor": 0}

    def update_game(self):
        if self.state != "PLAY": 
            self.update()
            return
        
        # Yanma efekti kontrolü
        self.update_efektler()
        
        # Silah süresi
        if self.silah_suresi > 0:
            self.silah_suresi -= 1
            if self.silah_suresi <= 0:
                self.silah = self.sel_char["silah"]

        # Hız boost
        if self.hiz_boost > 1.0:
            self.hiz_boost = max(1.0, self.hiz_boost - 0.001)

        if self.shake_amount > 0: self.shake_amount -= 1

        # Karakter hareketi
        target = QPointF(self.mouse_pos)
        d = math.hypot(target.x()-self.p_pos.x(), target.y()-self.p_pos.y())
        if d > 5:
            hiz = self.sel_char["hiz"] * self.hiz_boost
            move = QPointF((target.x()-self.p_pos.x())/d * hiz, 
                           (target.y()-self.p_pos.y())/d * hiz)
            self.p_pos += move
            
            # İz efekti
            if random.random() > 0.4:
                self.trails.append(Trail(self.p_pos, self.silah_bilgi()["renk"]))

        # Boss spawn
        if not self.boss_spawned and self.level % 5 == 0 and self.score >= self.level * 100:
            self.boss_spawned = True
            self.spawn_boss()
        
        # Düşman spawn
        max_enemies = 3 + self.level * 2
        if len(self.enemies) < max_enemies and not self.boss_spawned:
            spawn_side = random.choice(['T', 'B', 'L', 'R'])
            px = random.randint(0, 1200) if spawn_side in 'TB' else (-50 if spawn_side == 'L' else 1250)
            py = random.randint(0, 800) if spawn_side in 'LR' else (-50 if spawn_side == 'T' else 850)
            
            # Düşman türü seçimi
            if self.level >= 5:
                tur = random.choices(["normal", "hizli", "tank", "atesli", "elektrikli"], weights=[40, 20, 15, 15, 10])[0]
            elif self.level >= 3:
                tur = random.choices(["normal", "hizli", "tank", "atesli"], weights=[50, 25, 15, 10])[0]
            else:
                tur = random.choices(["normal", "hizli", "tank"], weights=[60, 25, 15])[0]
            
            self.enemies.append({
                "p": QPointF(px, py), 
                "hp": DUSMAN_TURLERI[tur]["hp"],
                "max_hp": DUSMAN_TURLERI[tur]["hp"],
                "tur": tur,
                "yavas": False,
                "yaniyor": 0
            })

        # Düşman hareketi
        for e in self.enemies[:]:
            tur_bilgi = DUSMAN_TURLERI[e["tur"]]
            hiz = tur_bilgi["hiz"]
            if e.get("yavas"):
                hiz *= 0.3
            
            # Yanma hasarı
            if e.get("yaniyor", 0) > 0:
                e["hp"] -= 0.02 * e["yaniyor"]
                e["yaniyor"] -= 1
                if random.random() > 0.7:
                    self.particles.append(Particle(e["p"], QColor(255, 100, 0), 3))
            
            dist = math.hypot(self.p_pos.x()-e["p"].x(), self.p_pos.y()-e["p"].y())
            if dist > 0:
                e["p"] += QPointF(
                    (self.p_pos.x()-e["p"].x())/dist * hiz, 
                    (self.p_pos.y()-e["p"].y())/dist * hiz
                )
            
            if dist < 35:
                hasar = 0.5 * (1 if e["tur"] != "tank" else 2)
                self.al_hasar(hasar)
                if random.random() > 0.5:
                    self.particles.append(Particle(self.p_pos, Qt.red, 5))
                    self.sparks.append(SparkEffect(self.p_pos, Qt.red))

        # Mermi kontrolü
        for b in self.bullets[:]:
            b['p'] += b['v']
            for e in self.enemies[:]:
                tur_bilgi = DUSMAN_TURLERI[e["tur"]]
                if math.hypot(b['p'].x()-e['p'].x(), b['p'].y()-e['p'].y()) < tur_bilgi["boyut"]:
                    silah_bilgi = self.silah_bilgi()
                    e['hp'] -= silah_bilgi["hasar"]
                    self.istatistikler["isabet"] += 1
                    
                    # Efektler
                    self.sparks.append(SparkEffect(e['p'], tur_bilgi["renk"]))
                    self.glows.append(GlowEffect(e['p'], silah_bilgi["renk"], 10))
                    
                    # Özel efektler
                    if self.silah == "buz":
                        e["yavas"] = True
                    elif self.silah == "ates":
                        e["yaniyor"] = 100
                    
                    for _ in range(3): 
                        self.particles.append(Particle(e['p'], tur_bilgi["renk"], 3))
                    
                    if b in self.bullets: self.bullets.remove(b)
                    
                    if e['hp'] <= 0:
                        for _ in range(15): 
                            self.particles.append(Particle(e['p'], tur_bilgi["renk"], 6))
                        self.shockwaves.append(Shockwave(e['p'], tur_bilgi["renk"]))
                        
                        self.enemies.remove(e)
                        self.score += tur_bilgi["puan"]
                        self.para += tur_bilgi["puan"] // 2
                        self.kills += 1
                        
                        if random.random() < 0.2:
                            self.spawn_powerup(e['p'])
                        
                        if self.boss and e == self.boss:
                            self.boss = None
                            self.score += 1000
                            self.para += 500
                            self.level += 1
                            self.boss_spawned = False
                            self.show_message("BOSS ÖLDÜ! +1000 SKOR", Qt.green)
                            self.glows.append(GlowEffect(QPointF(600, 400), Qt.green, 100))
                        elif self.score >= self.level * 200:
                            self.level += 1
                            self.show_message(f"SEVİYE {self.level}!", Qt.yellow)
            
            if not self.rect().contains(b['p'].toPoint()): 
                if b in self.bullets: self.bullets.remove(b)

        # Lazer
        for l in self.lasers[:]:
            l.update()
            if l.life <= 0: self.lasers.remove(l)
            else:
                for e in self.enemies[:]:
                    if self.lazer_vurus(l.start, l.end, e["p"]):
                        tur_bilgi = DUSMAN_TURLERI[e["tur"]]
                        e['hp'] -= 0.3
                        if e['hp'] <= 0:
                            self.enemies.remove(e)
                            self.score += tur_bilgi["puan"]
                            self.para += tur_bilgi["puan"] // 2
                            self.kills += 1

        # Efekt güncellemeleri
        self.trails = [t for t in self.trails if t.update()]
        self.particles = [p for p in self.particles if p.life > 0]
        self.sparks = [s for s in self.sparks if s.update()]
        self.glows = [g for g in self.glows if g.update()]
        
        for s in self.shockwaves[:]:
            s.update()
            if s.life <= 0: self.shockwaves.remove(s)

        # Power-up
        for pu in self.powerups[:]:
            dist = math.hypot(self.p_pos.x()-pu["p"].x(), self.p_pos.y()-pu["p"].y())
            if dist < 30:
                self.powerup_uygula(pu)
                self.powerups.remove(pu)

        # Can yenileme
        if self.p_can < self.max_can and random.random() < 0.005:
            self.p_can = min(self.max_can, self.p_can + 0.5)

        if self.p_can <= 0: 
            self.state = "OVER"
            self.istatistikler["max_skor"] = max(self.istatistikler["max_skor"], self.score)
            # Kaydet
            self.kaydet_oyun()
        
        self.update()

    def update_efektler(self):
        # Yanma ve yavaşlatma zamanla geçsin
        for e in self.enemies:
            if e.get("yavas") and random.random() < 0.02:
                e["yavas"] = False

    def spawn_boss(self):
        side = random.choice(['T', 'B', 'L', 'R'])
        px, py = {'T': (600, -80), 'B': (600, 880), 'L': (-80, 400), 'R': (1280, 400)}[side]
        
        self.boss = {
            "p": QPointF(px, py),
            "hp": 50 + (self.level // 5) * 25,
            "max_hp": 50 + (self.level // 5) * 25,
            "tur": "boss"
        }
        self.enemies.append(self.boss)
        self.show_message("⚠️ BOSS GELİYOR! ⚠️", Qt.red)
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
            self.p_zirh = min(100, self.p_zirh + 25)
        elif tur == "hiz":
            self.hiz_boost = 1.5
        elif tur.startswith("silah_"):
            self.silah = tur.replace("silah_", "")
            self.silah_suresi = 1000
        
        self.show_message(powerup["bilgi"]["aciklama"], powerup["bilgi"]["renk"])
        self.glows.append(GlowEffect(self.p_pos, powerup["bilgi"]["renk"], 30))

    def al_hasar(self, miktar):
        if self.p_zirh > 0:
            self.p_zirh -= miktar * 0.5
            miktar *= 0.5
        self.p_can -= miktar
        self.shake_amount = 10
        if random.random() > 0.3:
            self.particles.append(Particle(self.p_pos, Qt.red))
            self.sparks.append(SparkEffect(self.p_pos, Qt.red))

    def show_message(self, text, renk):
        self.aktif_mesaj = {"metin": text, "renk": renk, "sure": 120}
        self.update()

    def kaydet_oyun(self):
        self.kayit["para"] = max(self.kayit.get("para", 0), self.para)
        self.kayit["en_yuksek_skor"] = max(self.kayit.get("en_yuksek_skor", 0), self.score)
        KayitSistemi.kaydet(self.kayit)

    def mousePressEvent(self, event):
        if self.state == "MENU":
            if self.menu_sayfa == "karakter":
                self.state = "PLAY"
            elif self.menu_sayfa == "magaza":
                self.magaza_sec()
        elif self.state in ["OVER", "WIN"]:
            self.init_game()
            self.state = "PLAY"
        elif self.state == "PLAY":
            self.ates_et()

    def mouseMoveEvent(self, event): 
        self.mouse_pos = event.pos()

    def keyPressEvent(self, event):
        if self.state == "MENU":
            if event.key() == Qt.Key_Left:
                self.menu_sayfa = {"magaza": "karakter", "ayar": "magaza", "karakter": "ayar"}.get(self.menu_sayfa, "karakter")
                self.menu_secim = 0
                self.update()
            elif event.key() == Qt.Key_Right:
                self.menu_sayfa = {"karakter": "magaza", "magaza": "ayar", "ayar": "karakter"}.get(self.menu_sayfa, "magaza")
                self.menu_secim = 0
                self.update()
            elif event.key() == Qt.Key_Up:
                self.menu_secim = max(0, self.menu_secim - 1)
                self.update()
            elif event.key() == Qt.Key_Down:
                self.menu_secim += 1
                self.update()
            elif event.key() == Qt.Key_Return:
                if self.menu_sayfa == "karakter":
                    self.state = "PLAY"
        elif event.key() == Qt.Key_Escape:
            if self.state == "PLAY":
                self.state = "PAUSE"
            elif self.state == "PAUSE":
                self.state = "PLAY"
        elif event.key() == Qt.Key_S:
            self.kaydet_oyun()
            self.show_message("OYUN KAYDEDİLDİ!", Qt.green)
        elif event.key() == Qt.Key_1:
            if "tabanca" in self.satin_alinan_silahlar:
                self.silah = "tabanca"
        elif event.key() == Qt.Key_2:
            if "pompa" in self.satin_alinan_silahlar:
                self.silah = "pompa"
        elif event.key() == Qt.Key_3:
            if "lazer" in self.satin_alinan_silahlar:
                self.silah = "lazer"
        elif event.key() == Qt.Key_H:
            haritalar = list(HARITALAR.keys())
            idx = haritalar.index(self.sel_map)
            self.sel_map = haritalar[(idx + 1) % len(haritalar)]

    def magaza_sec(self):
        """Mağazada seçim yap"""
        if self.menu_sayfa == "magaza":
            # Karakter satın al
            karakter_keys = list(KARAKTERLER.keys())
            if self.menu_secim < len(karakter_keys):
                key = karakter_keys[self.menu_secim]
                if key not in self.satin_alinan_karakterler:
                    kar = KARAKTERLER[key]
                    if self.para >= kar["fiyat"]:
                        self.para -= kar["fiyat"]
                        self.satin_alinan_karakterler.append(key)
                        self.kayit[" satin_alinan_karakterler"] = self.satin_alinan_karakterler
                        self.kaydet_oyun()
                        self.show_message(f"{kar['ad']} SATIN ALINDI!", kar["renk"])
                else:
                    # Karakteri seç
                    self.sel_char = KARAKTERLER[key]
                    self.silah = self.sel_char["silah"]
                    self.state = "PLAY"

    def silah_bilgi(self):
        return SILAHLAR.get(self.silah, SILAHLAR["tabanca"])

    def ates_et(self):
        simdi = time.time()
        silah_bilgi = self.silah_bilgi()
        
        if simdi - self.last_shot_time < silah_bilgi["aralik"]:
            return
        
        self.last_shot_time = simdi
        self.istatistikler["ates"] += 1
        
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
                self.glows.append(GlowEffect(self.p_pos, silah_bilgi["renk"], 20))
            elif self.silah == "lazer":
                self.lasers.append(LaserBeam(self.p_pos, self.mouse_pos, silah_bilgi["renk"]))
            elif self.silah == "çift":
                offset = 15
                perp_x, perp_y = -dy/dist * offset, dx/dist * offset
                self.bullets.append({"p": QPointF(self.p_pos.x()+perp_x, self.p_pos.y()+perp_y), "v": QPointF(vx, vy)})
                self.bullets.append({"p": QPointF(self.p_pos.x()-perp_x, self.p_pos.y()-perp_y), "v": QPointF(vx, vy)})
            elif self.silah == "buz":
                self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy)})
            elif self.silah == "ates":
                self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy)})
                self.glows.append(GlowEffect(self.p_pos, QColor(255, 100, 0), 15))
            else:
                self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy)})

    def lazer_vurus(self, bas, bit, hedef):
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
        p.setRenderHint(QPainter.HighQualityAntialiasing)
        
        if self.shake_amount > 0:
            p.translate(random.randint(-self.shake_amount, self.shake_amount), 
                        random.randint(-self.shake_amount, self.shake_amount))

        m = HARITALAR[self.sel_map]
        
        # Arka plan
        grad = QLinearGradient(0, 0, 0, 800)
        grad.setColorAt(0, m["bg"][0]); grad.setColorAt(1, m["bg"][1])
        p.fillRect(self.rect(), grad)
        
        # Dekoratif ışık
        p.setBrush(m["sun"]); p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(600, 100), 400, 400)
        
        # Desenler
        if m.get("desen") == "izgara":
            p.setPen(QPen(QColor(255,255,255,8), 1))
            for i in range(0, 1200, 40):
                p.drawLine(i, 0, i, 800)
            for i in range(0, 800, 40):
                p.drawLine(0, i, 1200, i)
        elif m.get("desen") == "daire":
            for i in range(50, 500, 40):
                p.setPen(QPen(QColor(255,50,0,5), 1))
                p.drawEllipse(QPoint(600, 400), i, i)
        elif m.get("desen") == "yildiz":
            p.setPen(QPen(QColor(255,255,255,15), 1))
            for i in range(0, 1200, 30):
                for j in range(0, 800, 30):
                    if random.random() > 0.7:
                        p.drawPoint(i, j)

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
        
        # Başlık
        grad = QLinearGradient(0, 50, 0, 120)
        grad.setColorAt(0, Qt.cyan)
        grad.setColorAt(1, Qt.magenta)
        p.setPen(QColor(0, 255, 255)); p.setFont(QFont("Impact", 50))
        p.drawText(self.rect().adjusted(0, 30, 0, 0), Qt.AlignCenter, "Z-HUNTER")
        p.setPen(QColor(255, 0, 255)); p.setFont(QFont("Impact", 30))
        p.drawText(self.rect().adjusted(0, 80, 0, 0), Qt.AlignCenter, "SHADOW EVOLUTION")
        
        # Para
        p.setPen(QColor(255, 215, 0)); p.setFont(QFont("Arial", 18, QFont.Bold))
        p.drawText(QRect(0, 120, 1200, 30), Qt.AlignCenter, f"💰 PARA: {self.para}")
        
        # Menü sekmeleri
        sekmeler = ["KARAKTER", "MAĞAZA", "AYAR"]
        secili_index = {"karakter": 0, "magaza": 1, "ayar": 2}[self.menu_sayfa]
        
        p.setFont(QFont("Arial", 14))
        for i, sekme in enumerate(sekmeler):
            x = 300 + i * 200
            if i == secili_index:
                p.setBrush(QColor(0, 100, 150)); p.setPen(QPen(Qt.cyan, 2))
            else:
                p.setBrush(QColor(30, 30, 30)); p.setPen(QPen(Qt.gray, 1))
            p.drawRoundedRect(x, 160, 180, 35, 10, 10)
            p.setPen(Qt.white)
            p.drawText(QRect(x, 160, 180, 35), Qt.AlignCenter, sekme)
        
        # İçerik
        if self.menu_sayfa == "karakter":
            self.ciz_karakter_secim(p)
        elif self.menu_sayfa == "magaza":
            self.ciz_magaza(p)
        
        # Alt bilgi
        p.setPen(Qt.gray); p.setFont(QFont("Arial", 11))
        p.drawText(QRect(0, 720, 1200, 30), Qt.AlignCenter, "← → Sayfa Değiştir | ↑↓ Seç | ENTER Oyna | S Kaydet")

    def ciz_karakter_secim(self, p):
        karakterler = list(KARAKTERLER.items())
        kart_genislik = 160
        kart_yukseklik = 180
        baslangic_x = (1200 - len(karakterler) * kart_genislik) // 2
        
        for i, (key, kar) in enumerate(karakterler):
            x = baslangic_x + i * kart_genislik
            y = 220
            
            # Seçili mi?
            satin_alindi = key in self.satin_alinan_karakterler
            
            if i == self.menu_secim:
                p.setBrush(QColor(0, 100, 150)); p.setPen(QPen(Qt.cyan, 3))
                p.drawRoundedRect(x-5, y-5, kart_genislik+10, kart_yukseklik+10, 15, 15)
            else:
                p.setBrush(QColor(30, 30, 30)); p.setPen(QPen(QColor(80,80,80), 1))
                p.drawRoundedRect(x, y, kart_genislik, kart_yukseklik, 10, 10)
            
            # Karakter ikonu
            p.setBrush(kar["renk"]); p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(x + kart_genislik//2, y + 40), 30, 30)
            
            # Göz
            p.setBrush(kar["goz"])
            p.drawEllipse(QPoint(x + kart_genislik//2 - 8, y + 35), 5, 3)
            p.drawEllipse(QPoint(x + kart_genislik//2 + 8, y + 35), 5, 3)
            
            # İsim
            p.setPen(Qt.white if satin_alindi else Qt.gray); p.setFont(QFont("Arial", 11, QFont.Bold))
            p.drawText(QRect(x, y + 75, kart_genislik, 20), Qt.AlignCenter, kar["ad"])
            
            # Özellik
            p.setPen(kar["goz"]); p.setFont(QFont("Arial", 9))
            p.drawText(QRect(x, y + 95, kart_genislik, 15), Qt.AlignCenter, f"Özel: {kar['ozel']}")
            
            # Durum
            if satin_alindi:
                p.setPen(Qt.green); p.setFont(QFont("Arial", 10, QFont.Bold))
                p.drawText(QRect(x, y + 140, kart_genislik, 20), Qt.AlignCenter, "SEÇ")
            else:
                p.setPen(Qt.yellow); p.setFont(QFont("Arial", 10))
                p.drawText(QRect(x, y + 140, kart_genislik, 20), Qt.AlignCenter, f"{kar['fiyat']} 💰")

    def ciz_magaza(self, p):
        karakterler = list(KARAKTERLER.items())
        kart_genislik = 160
        kart_yukseklik = 150
        baslangic_x = (1200 - len(karakterler) * kart_genislik) // 2
        
        p.setPen(Qt.white); p.setFont(QFont("Arial", 14))
        p.drawText(QRect(0, 210, 1200, 30), Qt.AlignCenter, "🎯 KARAKTER AL | ↑↓ SEÇ | ENTER AL/SEÇ")
        
        for i, (key, kar) in enumerate(karakterler):
            x = baslangic_x + i * kart_genislik
            y = 250
            
            satin_alindi = key in self.satin_alinan_karakterler
            
            if i == self.menu_secim:
                p.setBrush(QColor(100, 50, 0)); p.setPen(QPen(Qt.yellow, 3))
                p.drawRoundedRect(x-5, y-5, kart_genislik+10, kart_yukseklik+10, 15, 15)
            else:
                p.setBrush(QColor(40, 20, 0)); p.setPen(QPen(QColor(100,50,0), 1))
                p.drawRoundedRect(x, y, kart_genislik, kart_yukseklik, 10, 10)
            
            # İkon
            p.setBrush(kar["renk"]); p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(x + kart_genislik//2, y + 35), 25, 25)
            
            # İsim
            p.setPen(Qt.white); p.setFont(QFont("Arial", 10, QFont.Bold))
            p.drawText(QRect(x, y + 65, kart_genislik, 18), Qt.AlignCenter, kar["ad"])
            
            # Fiyat
            if satin_alindi:
                p.setPen(Qt.green); p.setFont(QFont("Arial", 9))
                p.drawText(QRect(x, y + 90, kart_genislik, 15), Qt.AlignCenter, "SATIN ALINDI")
            else:
                p.setPen(Qt.yellow); p.setFont(QFont("Arial", 11))
                p.drawText(QRect(x, y + 90, kart_genislik, 20), Qt.AlignCenter, f"{kar['fiyat']} 💰")
            
            # Yeterli para?
            if self.para < kar["fiyat"] and not satin_alindi:
                p.setPen(QColor(255, 50, 50, 150)); p.setFont(QFont("Arial", 9))
                p.drawText(QRect(x, y + 115, kart_genislik, 15), Qt.AlignCenter, "YETERSİZ PARA")

    def ciz_oyun(self, p):
        # İzler
        for t in self.trails:
            t.draw(p)

        # Glow efektleri
        for g in self.glows:
            g.draw(p)

        # Şok dalgaları
        for s in self.shockwaves:
            c = QColor(s.color)
            c.setAlpha(s.life)
            p.setPen(QPen(c, 3)); p.setBrush(Qt.NoBrush)
            p.drawEllipse(s.pos, s.radius, s.radius)

        # Parçacıklar
        for part in self.particles:
            c = QColor(part.color)
            c.setAlpha(part.life)
            p.setBrush(c)
            p.save()
            p.translate(part.pos)
            p.rotate(part.rotation)
            p.drawRect(QRectF(-part.size/2, -part.size/2, part.size, part.size))
            p.restore()

        # Kıvılcımlar
        for s in self.sparks:
            s.draw(p)

        # Power-up'lar
        for pu in self.powerups:
            bilgi = pu["bilgi"]
            c = QColor(bilgi["renk"])
            p.setBrush(c); p.setPen(Qt.white)
            p.drawEllipse(pu["p"], 15, 15)
            p.setFont(QFont("Arial", 14, QFont.Bold))
            p.drawText(int(pu["p"].x()-5), int(pu["p"].y()+5), bilgi["sembol"])

        # Lazerler
        for l in self.lasers:
            c = QColor(l.color)
            c.setAlpha(l.life)
            # Neon glow çizgisi
            for width in [6, 4, 2]:
                pc = QColor(c)
                pc.setAlpha(l.life // (7-width))
                p.setPen(QPen(pc, width)); p.setBrush(Qt.NoBrush)
                p.drawLine(l.start, l.end)

        # Karakter ve düşmanlar
        self.draw_shadow_unit(p, self.p_pos, self.sel_char["goz"], True)
        for e in self.enemies:
            tur_bilgi = DUSMAN_TURLERI[e["tur"]]
            renk = tur_bilgi["renk"]
            if e.get("yavas"):
                renk = QColor(100, 200, 255)
            if e.get("yaniyor", 0) > 0:
                renk = QColor(255, 100, 0)
            self.draw_shadow_unit(p, e["p"], renk, False, tur_bilgi["boyut"])
            
            if e["tur"] == "boss":
                hp_oran = e["hp"] / e["max_hp"]
                p.setBrush(QColor(100, 0, 0)); p.setPen(Qt.NoPen)
                p.drawRect(e["p"].x()-40, e["p"].y()-50, 80, 8)
                p.setBrush(Qt.red)
                p.drawRect(e["p"].x()-40, e["p"].y()-50, 80*hp_oran, 8)

        # Mermiler
        silah_bilgi = self.silah_bilgi()
        for b in self.bullets:
            # Glow efekti
            c = QColor(silah_bilgi["renk"])
            c.setAlpha(100)
            p.setBrush(c); p.setPen(Qt.NoPen)
            p.drawEllipse(b["p"], silah_bilgi["boyut"]+3, silah_bilgi["boyut"]+3)
            
            p.setBrush(silah_bilgi["renk"])
            p.drawEllipse(b["p"], silah_bilgi["boyut"], silah_bilgi["boyut"])

        self.ciz_ui(p)

    def ciz_ui(self, p):
        # Üst bar
        p.setBrush(QColor(0, 0, 0, 180))
        p.drawRect(0, 0, 1200, 55)
        
        # Skor
        p.setPen(Qt.white); p.setFont(QFont("Consolas", 16, QFont.Bold))
        p.drawText(20, 35, f"🏆 {self.score}")
        
        # Para
        p.setPen(QColor(255, 215, 0)); p.setFont(QFont("Arial", 14))
        p.drawText(150, 35, f"💰 {self.para}")
        
        p.setFont(QFont("Arial", 12))
        p.setPen(Qt.gray)
        p.drawText(280, 32, f"Seviye: {self.level}")
        p.drawText(380, 32, f"Öldürme: {self.kills}")
        
        # Silah
        silah_bilgi = self.silah_bilgi()
        p.setPen(silah_bilgi["renk"]); p.setFont(QFont("Arial", 14, QFont.Bold))
        p.drawText(520, 35, f"🔫 {silah_bilgi['ad'].upper()}")
        
        # Can barı
        p.setPen(Qt.white); p.setFont(QFont("Arial", 12, QFont.Bold))
        p.drawText(700, 32, "❤️")
        
        p.setBrush(QColor(50, 50, 50)); p.setPen(Qt.NoPen)
        p.drawRect(740, 18, 200, 18)
        
        if self.p_can > 60:
            p.setBrush(Qt.green)
        elif self.p_can > 30:
            p.setBrush(Qt.yellow)
        else:
            p.setBrush(Qt.red)
        p.drawRect(742, 20, max(0, int(self.p_can * 1.96)), 14)
        
        p.setPen(Qt.white); p.setFont(QFont("Arial", 11))
        p.drawText(945, 33, f"{int(self.p_can)}/{self.max_can}")
        
        if self.p_zirh > 0:
            p.setBrush(QColor(30, 30, 180)); p.setPen(Qt.NoPen)
            p.drawRect(742, 34, int(self.p_zirh * 1.96), 4)
        
        if self.boss_spawned and self.boss:
            p.setPen(Qt.red); p.setFont(QFont("Arial", 14, QFont.Bold))
            p.drawText(1080, 35, "⚠️ BOSS")

        if hasattr(self, 'aktif_mesaj') and self.aktif_mesaj:
            p.setPen(self.aktif_mesaj["renk"]); p.setFont(QFont("Arial", 28, QFont.Bold))
            p.drawText(self.rect(), Qt.AlignCenter, self.aktif_mesaj["metin"])
            self.aktif_mesaj["sure"] -= 1
            if self.aktif_mesaj["sure"] <= 0:
                del self.aktif_mesaj

    def ciz_pause(self, p):
        p.fillRect(self.rect(), QColor(0,0,0,150))
        
        p.setBrush(QColor(20, 20, 40)); p.setPen(QPen(Qt.cyan, 2))
        p.drawRoundedRect(400, 250, 400, 300, 20, 20)
        
        p.setPen(Qt.white); p.setFont(QFont("Impact", 40))
        p.drawText(QRect(400, 270, 400, 60), Qt.AlignCenter, "⏸️ DURAKLADI")
        
        p.setFont(QFont("Arial", 16))
        p.drawText(QRect(400, 350, 400, 40), Qt.AlignCenter, "Devam için ESC")
        p.drawText(QRect(400, 400, 400, 40), Qt.AlignCenter, "Kaydet için S")
        p.drawText(QRect(400, 450, 400, 40), Qt.AlignCenter, "Çıkış için Q")

    def ciz_game_over(self, p):
        p.fillRect(self.rect(), QColor(0,0,0,220))
        
        p.setPen(Qt.red); p.setFont(QFont("Impact", 70))
        p.drawText(self.rect().adjusted(0, -50, 0, 0), Qt.AlignCenter, "💀 ELENDİN 💀")
        
        p.setPen(Qt.white); p.setFont(QFont("Arial", 30))
        p.drawText(QRect(0, 250, 1200, 50), Qt.AlignCenter, f"Skor: {self.score}")
        
        p.setPen(QColor(255, 215, 0)); p.setFont(QFont("Arial", 24))
        p.drawText(QRect(0, 310, 1200, 40), Qt.AlignCenter, f"Kazanılan Para: +{self.para}")
        
        p.setPen(Qt.cyan); p.setFont(QFont("Arial", 18))
        y = 380
        p.drawText(QRect(0, y, 1200, 30), Qt.AlignCenter, f"Toplam Ateş: {self.istatistikler['ates']}")
        y += 35
        p.drawText(QRect(0, y, 1200, 30), Qt.AlignCenter, f"İsabet: {self.istatistikler['isabet']}")
        y += 35
        p.drawText(QRect(0, y, 1200, 30), Qt.AlignCenter, f"En Yüksek: {self.istatistikler['max_skor']}")
        
        p.setPen(Qt.green); p.setFont(QFont("Arial", 24))
        p.drawText(QRect(0, 520, 1200, 50), Qt.AlignCenter, "🎮 Tekrar oynamak için tıkla 🎮")

    def draw_shadow_unit(self, p, pos, eye_color, is_player, boyut=None):
        p.save()
        p.translate(pos)
        
        if boyut is None: boyut = 25 if is_player else 20
        
        # Gölge
        p.setBrush(QColor(0, 0, 0, 60))
        p.drawEllipse(-boyut, boyut//2, boyut*2, boyut//2)
        
        # Neon glow
        c = QColor(eye_color)
        c.setAlpha(30)
        p.setPen(QPen(c, 4))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(-boyut+5, -boyut+5, (boyut-5)*2, (boyut-5)*2)
        
        # Vücut
        p.setBrush(Qt.black); p.setPen(QPen(Qt.black, 1))
        p.drawEllipse(-boyut+5, -boyut+5, (boyut-5)*2, (boyut-5)*2)
        
        # Gözler
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
