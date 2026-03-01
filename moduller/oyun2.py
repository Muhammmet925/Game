import sys, random, math, time, json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ==================== SOUL KNIGHT TARZI OYUN ====================

# --- KARAKTERLER (Soul Knight Karakterleri) ---
KARAKTERLER = {
    "1": {
        "ad": "Şövalye", 
        "hiz": 4, 
        "goz": Qt.cyan, 
        "hasar": 1.5,
        "silah": "kilic",
        "ozel": "Kalkan",
        "renk": QColor(100, 149, 237),  # Cornflower Blue
        "aciklama": "Dengeli savaşçı +20% hasar",
        "fiyat": 0,
        "baslangic_hp": 120
    },
    "2": {
        "ad": "Büyücü", 
        "hiz": 5, 
        "goz": Qt.magenta, 
        "hasar": 2.0,
        "silah": "deynek",
        "ozel": "Büyü Hasarı",
        "renk": QColor(138, 43, 226),  # Blue Violet
        "aciklama": "Güçlü büyü saldırıları",
        "fiyat": 500,
        "baslangic_hp": 80
    },
    "3": {
        "ad": "Suikastçı", 
        "hiz": 10, 
        "goz": Qt.yellow, 
        "hasar": 1.8,
        "silah": "yay",
        "ozel": "Gölge Adımı",
        "renk": QColor(50, 205, 50),  # Lime Green
        "aciklama": "En hızlı + kritik vuruş",
        "fiyat": 750,
        "baslangic_hp": 70
    },
    "4": {
        "ad": "Mühendis", 
        "hiz": 4, 
        "goz": QColor(255, 165, 0),  # Orange
        "hasar": 1.2,
        "silah": "tabanca",
        "ozel": "Tamir",
        "renk": QColor(255, 140, 0),  # Dark Orange
        "aciklama": "İstasyon kurar + tamir",
        "fiyat": 1000,
        "baslangic_hp": 100
    },
    "5": {
        "ad": "Rahip", 
        "hiz": 5, 
        "goz": QColor(255, 255, 240),  # Ivory
        "hasar": 1.0,
        "silah": "deynek",
        "ozel": "İyileştirme",
        "renk": QColor(255, 215, 0),  # Gold
        "aciklama": "Oto iyileşme + can",
        "fiyat": 1500,
        "baslangic_hp": 90
    },
    "6": {
        "ad": "Elf", 
        "hiz": 7, 
        "goz": QColor(0, 255, 127),  # Spring Green
        "hasar": 1.6,
        "silah": "yay",
        "ok": True,
        "ozel": "Çift Ok",
        "renk": QColor(34, 139, 34),  # Forest Green
        "aciklama": "İki ok birden atar",
        "fiyat": 2000,
        "baslangic_hp": 85
    },
    "7": {
        "ad": "Paladin", 
        "hiz": 3, 
        "goz": QColor(255, 215, 0),  # Gold
        "hasar": 2.0,
        "silah": "kilic",
        "ozel": "Kutsal Kalkan",
        "renk": QColor(255, 250, 205),  # Lemon Chiffon
        "aciklama": "Yüksek hasar + zırh",
        "fiyat": 2500,
        "baslangic_hp": 150
    },
    "8": {
        "ad": "Vampir", 
        "hiz": 6, 
        "goz": Qt.red, 
        "hasar": 1.4,
        "silah": "kilic",
        "ozel": "Can Emme",
        "renk": QColor(139, 0, 0),  # Dark Red
        "aciklama": "Düşmandan can çalar",
        "fiyat": 3000,
        "baslangic_hp": 95
    },
}

# --- SİLAHLAR ---
SILAHLAR = {
    "kilic": {"renk": Qt.cyan, "boyut": 8, "hiz": 20, "aralik": 0.4, "hasar": 2, "ad": "Kılıç", "fiyat": 0, "tur": "yakın"},
    "yay": {"renk": QColor(139, 90, 43), "boyut": 4, "hiz": 18, "aralik": 0.5, "hasar": 1.5, "ad": " Yay", "fiyat": 500, "tur": "uzak"},
    "deynek": {"renk": Qt.magenta, "boyut": 5, "hiz": 15, "aralik": 0.6, "hasar": 2.5, "ad": "Sihirli Değnek", "fiyat": 750, "tur": "büyü"},
    "tabanca": {"renk": Qt.yellow, "boyut": 5, "hiz": 25, "aralik": 0.2, "hasar": 1, "ad": "Tabanca", "fiyat": 0, "tur": "ates"},
    "pompali": {"renk": QColor(205, 92, 92), "boyut": 12, "hiz": 10, "aralik": 0.8, "hasar": 3, "ad": "Pompalı", "fiyat": 500, "tur": "ates"},
    "lazer": {"renk": Qt.red, "boyut": 3, "hiz": 30, "aralik": 0.15, "hasar": 0.8, "ad": "Lazer", "fiyat": 1000, "tur": "lazer"},
    "asit": {"renk": QColor(0, 255, 0), "boyut": 6, "hiz": 12, "aralik": 0.3, "hasar": 1.5, "ad": "Asit Tabancası", "fiyat": 1500, "tur": "kimyasal"},
    "alev": {"renk": QColor(255, 69, 0), "boyut": 10, "hiz": 8, "aralik": 0.05, "hasar": 0.5, "ad": "Alev Makinesi", "fiyat": 2000, "tur": "alev"},
    "buz": {"renk": QColor(135, 206, 250), "boyut": 5, "hiz": 14, "aralik": 0.4, "hasar": 1.2, "ad": "Buz Asası", "fiyat": 1800, "tur": "buz"},
    "yildirim": {"renk": QColor(255, 255, 0), "boyut": 4, "hiz": 22, "aralik": 0.25, "hasar": 1.8, "ad": "Yıldırım", "fiyat": 2500, "tur": "elektrik"},
}

# --- DÜŞMAN TÜRLERİ ---
DUSMAN_TURLERI = {
    "slime": {"hp": 2, "hiz": 1.5, "renk": QColor(0, 255, 0), "boyut": 18, "puan": 10, "ad": "Slime", "efekt": "yavas"},
    "yarasa": {"hp": 1, "hiz": 4, "renk": QColor(100, 100, 100), "boyut": 14, "puan": 15, "ad": "Yarasa", "efekt": None},
    "iskelet": {"hp": 3, "hiz": 2, "renk": QColor(240, 240, 240), "boyut": 20, "puan": 20, "ad": "İskelet", "efekt": None},
    "orc": {"hp": 5, "hiz": 2.5, "renk": QColor(139, 69, 19), "boyut": 28, "puan": 35, "ad": "Ork", "efekt": "carpma"},
    "hayalet": {"hp": 1.5, "hiz": 3, "renk": QColor(200, 200, 255), "boyut": 16, "puan": 25, "ad": "Hayalet", "efekt": "gecirgen"},
    "bug": {"hp": 2, "hiz": 2, "renk": QColor(255, 0, 255), "boyut": 15, "puan": 20, "ad": " Böcek", "efekt": "zeka"},
    "golem": {"hp": 10, "hiz": 1, "renk": QColor(105, 105, 105), "boyut": 40, "puan": 80, "ad": "Golem", "efekt": "darbe"},
    "boss1": {"hp": 30, "hiz": 1.5, "renk": QColor(139, 0, 0), "boyut": 50, "puan": 500, "ad": "Karanlık Lord", "efekt": "boss"},
    "boss2": {"hp": 50, "hiz": 2, "renk": QColor(75, 0, 130), "boyut": 60, "puan": 1000, "ad": "Ejderha Kral", "efekt": "boss"},
}

# --- ODALAR ---
ODALAR = {
    "normal": {"ad": "Savaş Odası", "dusman_sayisi": 5, "zorluk": 1, "renk": QColor(80, 80, 80)},
    "elite": {"ad": "Elit Oda", "dusman_sayisi": 8, "zorluk": 2, "renk": QColor(139, 69, 19)},
    "boss": {"ad": "Boss Odası", "dusman_sayisi": 1, "zorluk": 3, "renk": QColor(139, 0, 0)},
    "magaza": {"ad": "Dükkan", "dusman_sayisi": 0, "zorluk": 0, "renk": QColor(0, 100, 0)},
    "dinlenme": {"ad": "İstirahat", "dusman_sayisi": 0, "zorluk": 0, "renk": QColor(0, 0, 139)},
    "hazine": {"ad": "Hazine Odası", "dusman_sayisi": 3, "zorluk": 1.5, "renk": QColor(218, 165, 32)},
}

# --- GÜÇLENDİRMELER ---
POWER_UPLAR = {
    "can": {"renk": Qt.green, "sembol": "+", "aciklama": "Can +50", "fiyat": 100, "deger": 50},
    "zirh": {"renk": Qt.blue, "sembol": "Z", "aciklama": "Zırh +30", "fiyat": 150, "deger": 30},
    "hasar": {"renk": Qt.red, "sembol": "H", "aciklama": "Hasar +25%", "fiyat": 200, "deger": 0.25},
    "hiz": {"renk": Qt.yellow, "sembol": "⚡", "aciklama": "Hız +20%", "fiyat": 150, "deger": 0.2},
    "savurma": {"renk": QColor(255, 0, 255), "sembol": "S", "aciklama": "Savurma +30%", "fiyat": 250, "deger": 0.3},
    "kritik": {"renk": QColor(255, 165, 0), "sembol": "K", "aciklama": "Kritik +15%", "fiyat": 300, "deger": 0.15},
}

# --- PARÇACIK SİSTEMİ ---
class Particle:
    def __init__(self, pos, color, size=None):
        self.pos = QPointF(pos)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 8)
        self.vel = QPointF(math.cos(angle) * speed, math.sin(angle) * speed)
        self.life = 255
        self.color = color
        self.size = size if size else random.randint(3, 8)

    def update(self):
        self.pos += self.vel
        self.vel *= 0.95
        self.life -= 10
        return self.life > 0

class SparkEffect:
    def __init__(self, pos, color):
        self.particles = []
        for _ in range(10):
            p = Particle(pos, color, random.randint(2, 5))
            p.vel *= 2
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

class GlowEffect:
    def __init__(self, pos, color, size):
        self.pos = QPointF(pos)
        self.color = color
        self.size = size
        self.life = 255
    
    def update(self):
        self.life -= 8
        self.size += 0.3
        return self.life > 0
    
    def draw(self, p):
        c = QColor(self.color)
        c.setAlpha(self.life // 4)
        p.setPen(QPen(c, 2))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(self.pos, self.size, self.size)

# --- KAYIT SİSTEMİ ---
class KayitSistemi:
    @staticmethod
    def kaydet(veriler, dosya_adi="soul_knight_kayit.json"):
        try:
            with open(dosya_adi, 'w', encoding='utf-8') as f:
                json.dump(veriler, f, indent=2, ensure_ascii=False)
            return True
        except:
            return False
    
    @staticmethod
    def yukle(dosya_adi="soul_knight_kayit.json"):
        try:
            with open(dosya_adi, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return None

# --- ANA OYUN SINIFI ---
class SoulKnight(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1200, 800)
        self.setWindowTitle("SOUL KNIGHT - KADERİNİ KENDİN ÇİZ")
        self.setMouseTracking(True)
        
        self.shake_amount = 0
        self.last_shot_time = 0
        self.init_game()
        
        # Oyun zamanlayıcısı
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)
        
        # Kayıtlı verileri yükle
        self.kayit = KayitSistemi.yukle() or {
            "para": 0, 
            "karakterler": ["1"], 
            "silahlar": ["kilic"],
            "en_yuksek_seviye": 1,
            "toplam_odul": 0
        }
        self.para = self.kayit.get("para", 0)
        self.acilan_karakterler = self.kayit.get("karakterler", ["1"])
        self.acilan_silahlar = self.kayit.get("silahlar", ["kilic"])
        
        # Menü durumu
        self.menu_sayfa = "karakter"

    def init_game(self):
        self.state = "MENU"
        self.p_pos = QPointF(600, 400)
        self.mouse_pos = QPoint(600, 400)
        
        # Oyun nesneleri
        self.enemies = []
        self.bullets = []
        self.particles = []
        self.sparks = []
        self.glows = []
        self.powerups = []
        
        # İstatistikler
        self.para = 0
        self.skor = 0
        self.seviye = 1
        self.oda_numarasi = 1
        self.kill_count = 0
        
        # Karakter özellikleri
        self.p_can = 100
        self.p_zirh = 0
        self.max_can = 100
        self.sel_char = KARAKTERLER["1"]
        self.silah = "kilic"
        
        # Güçlendirmeler
        self.hasar_boost = 1.0
        self.hiz_boost = 1.0
        self.savurma_boost = 1.0
        self.kritik_sans = 0.0
        
        # Oda sistemi
        self.oda_turu = "normal"
        self.oda_temizlendi = False
        self.oda_dusman_sayisi = 0
        self.oda_dusman_olen = 0
        self.su_anki_oda = None
        
        # Diğer
        self.menu_secim = 0
        self.oyuncu_yonu = 0
        self.ates_edildi = False
        self.silah_animasyon = 0
        self.odul_kazanildi = False

    def update_game(self):
        if self.state != "PLAY": 
            self.update()
            return
        
        # Ekran sallantısı
        if self.shake_amount > 0: 
            self.shake_amount -= 1
        
        # Silah animasyonu
        if self.silah_animasyon > 0:
            self.silah_animasyon -= 1
        
        # Rahip iyileşmesi
        if self.sel_char["ad"] == "Rahip" and self.p_can < self.max_can:
            if random.random() < 0.02:
                self.p_can = min(self.max_can, self.p_can + 0.5)
                self.glows.append(GlowEffect(self.p_pos, QColor(0, 255, 0), 15))
        
        # Karakter hareketi
        target = QPointF(self.mouse_pos)
        d = math.hypot(target.x()-self.p_pos.x(), target.y()-self.p_pos.y())
        if d > 5:
            hiz = self.sel_char["hiz"] * self.hiz_boost
            move = QPointF((target.x()-self.p_pos.x())/d * hiz, 
                           (target.y()-self.p_pos.y())/d * hiz)
            self.p_pos += move
            
            # Karakter yönü
            self.oyuncu_yonu = math.atan2(target.y()-self.p_pos.y(), target.x()-self.p_pos.x())

        # Oda temiz mi kontrolü
        if not self.oda_temizlendi and len(self.enemies) == 0 and self.oda_dusman_sayisi > 0:
            self.oda_temizlendi = True
            self.odul_kazanildi = True
            self.para += 50 + self.seviye * 10  # Oda ödülü
            self.show_message("ODA TEMİZLENDİ! +{} Para".format(50 + self.seviye * 10), Qt.green)
            
            # Sonraki odayı hazırla
            QTimer.singleShot(2000, self.sonraki_oda)
        
        # Düşman spawn (oda dolu değilse ve oda temizlenmemişse)
        if not self.oda_temizlendi and len(self.enemies) < self.oda_dusman_sayisi:
            if random.random() < 0.03:
                self.spawn_dusman()
        
        # Düşman hareketi
        for e in self.enemies[:]:
            tur_bilgi = DUSMAN_TURLERI[e["tur"]]
            hiz = tur_bilgi["hiz"] * (1 + self.seviye * 0.1)
            
            if e.get("yavas"):
                hiz *= 0.3
            
            dist = math.hypot(self.p_pos.x()-e["p"].x(), self.p_pos.y()-e["p"].y())
            if dist > 0:
                e["p"] += QPointF(
                    (self.p_pos.x()-e["p"].x())/dist * hiz, 
                    (self.p_pos.y()-e["p"].y())/dist * hiz
                )
            
            # Çarpışma hasarı
            if dist < 30:
                hasar = 0.3 * (1 if e["tur"] != "boss1" and e["tur"] != "boss2" else 2)
                self.al_hasar(hasar)
                self.shake_amount = 5
        
        # Mermi kontrolü
        for b in self.bullets[:]:
            b['p'] += b['v']
            
            # Mermi ömrü
            b['omr'] -= 1
            if b['omr'] <= 0:
                self.bullets.remove(b)
                continue
            
            # Düşman çarpışması
            for e in self.enemies[:]:
                tur_bilgi = DUSMAN_TURLERI[e["tur"]]
                if math.hypot(b['p'].x()-e['p'].x(), b['p'].y()-e['p'].y()) < tur_bilgi["boyut"]:
                    silah_bilgi = self.silah_bilgi()
                    
                    # Kritik vuruş hesapla
                    kritik = random.random() < self.kritik_sans
                    hasar = silah_bilgi["hasar"] * self.hasar_boost * self.sel_char["hasar"]
                    if kritik:
                        hasar *= 2
                        self.sparks.append(SparkEffect(e['p'], Qt.yellow))
                    
                    e['hp'] -= hasar
                    
                    # Efektler
                    self.sparks.append(SparkEffect(e['p'], tur_bilgi["renk"]))
                    
                    # Özel silah efektleri
                    if self.silah == "buz":
                        e["yavas"] = True
                    elif self.silah == "alev":
                        e["yaniyor"] = 50
                    elif self.silah == "asit":
                        e["asitli"] = 30
                    
                    if b in self.bullets:
                        self.bullets.remove(b)
                    
                    # Düşman ölümü
                    if e['hp'] <= 0:
                        self.dusman_oldu(e)
            
            # Ekran dışı
            if not self.rect().contains(b['p'].toPoint()): 
                if b in self.bullets: 
                    self.bullets.remove(b)

        # Yanma efekti
        for e in self.enemies:
            if e.get("yaniyor", 0) > 0:
                e["hp"] -= 0.03
                e["yaniyor"] -= 1
                if random.random() > 0.7:
                    self.particles.append(Particle(e["p"], QColor(255, 100, 0), 3))
                if e["hp"] <= 0:
                    self.dusman_oldu(e)
            
            if e.get("asitli", 0) > 0:
                e["hp"] -= 0.02
                e["asitli"] -= 1
                if e["hp"] <= 0:
                    self.dusman_oldu(e)

        # Efekt güncellemeleri
        self.particles = [p for p in self.particles if p.update()]
        self.sparks = [s for s in self.sparks if s.update()]
        self.glows = [g for g in self.glows if g.update()]
        
        # Güçlendirme toplama
        for pu in self.powerups[:]:
            dist = math.hypot(self.p_pos.x()-pu["p"].x(), self.p_pos.y()-pu["p"].y())
            if dist < 25:
                self.powerup_al(pu)
                self.powerups.remove(pu)

        # Can yenileme (düşük ihtimal)
        if self.p_can < self.max_can and random.random() < 0.003:
            self.p_can = min(self.max_can, self.p_can + 1)

        # Oyun bitişi kontrolü
        if self.p_can <= 0: 
            self.oyun_bitti()
        
        self.update()

    def spawn_dusman(self):
        """Düşman spawn et"""
        # Oda kenarlarından spawn olsun
        side = random.choice(['T', 'B', 'L', 'R'])
        if side == 'T':
            px = random.randint(100, 1100)
            py = random.randint(50, 150)
        elif side == 'B':
            px = random.randint(100, 1100)
            py = random.randint(650, 750)
        elif side == 'L':
            px = random.randint(50, 150)
            py = random.randint(150, 650)
        else:
            px = random.randint(1050, 1150)
            py = random.randint(150, 650)
        
        # Düşman türü seçimi
        if self.oda_turu == "boss":
            tur = "boss1" if self.seviye < 5 else "boss2"
        elif self.oda_turu == "elite":
            tur = random.choice(["orc", "iskelet", "golem"])
        elif self.oda_turu == "hazina":
            tur = random.choice(["yarasa", "bug"])
        else:
            tur = random.choices(["slime", "yarasa", "iskelet"], weights=[50, 30, 20])[0]
        
        hp_carpani = 1 + (self.seviye - 1) * 0.3
        
        self.enemies.append({
            "p": QPointF(px, py), 
            "hp": DUSMAN_TURLERI[tur]["hp"] * hp_carpani,
            "max_hp": DUSMAN_TURLERI[tur]["hp"] * hp_carpani,
            "tur": tur,
            "yavas": False,
            "yaniyor": 0,
            "asitli": 0
        })

    def dusman_oldu(self, e):
        """Düşman öldüğünde"""
        tur_bilgi = DUSMAN_TURLERI[e["tur"]]
        
        # Ölüm efektleri
        for _ in range(15):
            self.particles.append(Particle(e["p"], tur_bilgi["renk"], random.randint(4, 8)))
        
        # Para ve skor
        self.para += tur_bilgi["puan"] // 2
        self.skor += tur_bilgi["puan"]
        self.kill_count += 1
        
        # Vampir karakteri için can emme
        if self.sel_char["ad"] == "Vampir":
            self.p_can = min(self.max_can, self.p_can + 5)
            self.glows.append(GlowEffect(self.p_pos, Qt.red, 20))
        
        # Boss ölümü
        if e["tur"] in ["boss1", "boss2"]:
            self.para += 200 * self.seviye
            self.skor += 1000 * self.seviye
            self.show_message("BOSS ÖLDÜ! +{} Para".format(200 * self.seviye), Qt.yellow)
            self.glows.append(GlowEffect(QPointF(600, 400), Qt.yellow, 150))
            self.seviye += 1
            self.oda_temizlendi = True
            QTimer.singleShot(3000, self.sonraki_oda)
        
        if e in self.enemies:
            self.enemies.remove(e)
        
        self.oda_dusman_olen += 1

    def sonraki_oda(self):
        """Sonraki odayı hazırla"""
        self.oda_numarasi += 1
        
        # Oda türü belirleme
        if self.oda_numarasi % 10 == 0:
            self.oda_turu = "boss"
        elif self.oda_numarasi % 5 == 0:
            self.oda_turu = random.choice(["elite", "magaza", "dinlenme"])
        elif self.oda_numarasi % 3 == 0:
            self.oda_turu = random.choice(["hazina", "normal"])
        else:
            self.oda_turu = "normal"
        
        oda_bilgi = ODALAR[self.oda_turu]
        
        if self.oda_turu in ["magaza", "dinlenme"]:
            self.oda_dusman_sayisi = 0
            self.oda_temizlendi = True
            
            if self.oda_turu == "dinlenme":
                self.p_can = min(self.max_can, self.p_can + 50)
                self.show_message("İSTİRAAT! Can +50", Qt.green)
            else:
                self.state = "SHOP"
                self.show_message("DÜKKAN - Silah/Güçlendirme Al", Qt.cyan)
        else:
            self.oda_dusman_sayisi = oda_bilgi["dusman_sayisi"]
            self.oda_temizlendi = False
        
        # Oyuncu pozisyonunu sıfırla
        self.p_pos = QPointF(600, 400)
        
        # Temizlik
        self.bullets = []
        self.powerups = []
        
        self.show_message("ODA {} - {}".format(self.oda_numarasi, oda_bilgi["ad"]), Qt.white)

    def al_hasar(self, miktar):
        if self.p_zirh > 0:
            self.p_zirh -= miktar
            if self.p_zirh < 0:
                miktar = -self.p_zirh
                self.p_zirh = 0
            else:
                miktar = 0
        
        if miktar > 0:
            self.p_can -= miktar
        
        self.shake_amount = 8
        if random.random() > 0.5:
            self.particles.append(Particle(self.p_pos, Qt.red))
            self.sparks.append(SparkEffect(self.p_pos, Qt.red))

    def powerup_al(self, powerup):
        tur = powerup["tur"]
        bilgi = POWER_UPLAR[tur]
        
        if tur == "can":
            self.p_can = min(self.max_can + 50, self.p_can + bilgi["deger"])
        elif tur == "zirh":
            self.p_zirh = min(100, self.p_zirh + bilgi["deger"])
        elif tur == "hasar":
            self.hasar_boost += bilgi["deger"]
        elif tur == "hiz":
            self.hiz_boost += bilgi["deger"]
        elif tur == "savurma":
            self.savurma_boost += bilgi["deger"]
        elif tur == "kritik":
            self.kritik_sans += bilgi["deger"]
        
        self.show_message(bilgi["aciklama"], bilgi["renk"])
        self.glows.append(GlowEffect(self.p_pos, bilgi["renk"], 25))

    def show_message(self, text, renk):
        self.aktif_mesaj = {"metin": text, "renk": renk, "sure": 180}
        self.update()

    def oyun_bitti(self):
        self.state = "OVER"
        self.kaydet()
        self.update()

    def kaydet(self):
        self.kayit["para"] = max(self.kayit.get("para", 0), self.para)
        self.kayit["en_yuksek_seviye"] = max(self.kayit.get("en_yuksek_seviye", 1), self.seviye)
        KayitSistemi.kaydet(self.kayit)

    def mousePressEvent(self, event):
        if self.state == "MENU":
            if self.menu_sayfa == "karakter":
                self.karakter_sec()
            elif self.menu_sayfa == "magaza":
                self.magaza_sec()
            elif self.menu_sayfa == "silah":
                self.silah_sec()
        elif self.state == "SHOP":
            self.shop_sec()
        elif self.state in ["OVER", "WIN"]:
            self.init_game()
            self.state = "MENU"
        elif self.state == "PLAY":
            self.ates_et()

    def karakter_sec(self):
        karakter_keys = list(KARAKTERLER.keys())
        if self.menu_secim < len(karakter_keys):
            key = karakter_keys[self.menu_secim]
            if key in self.acilan_karakterler:
                self.sel_char = KARAKTERLER[key]
                self.silah = self.sel_char["silah"]
                self.max_can = self.sel_char["baslangic_hp"]
                self.p_can = self.max_can
                self.oyun_baslat()

    def silah_sec(self):
        silah_keys = list(SILAHLAR.keys())
        if self.menu_secim < len(silah_keys):
            key = silah_keys[self.menu_secim]
            if key in self.acilan_silahlar:
                self.silah = key

    def magaza_sec(self):
        # Karakter satın al
        karakter_keys = list(KARAKTERLER.keys())
        if self.menu_secim < len(karakter_keys):
            key = karakter_keys[self.menu_secim]
            if key not in self.acilan_karakterler:
                kar = KARAKTERLER[key]
                if self.para >= kar["fiyat"]:
                    self.para -= kar["fiyat"]
                    self.acilan_karakterler.append(key)
                    self.kayit["karakterler"] = self.acilan_karakterler
                    self.kaydet()
                    self.show_message("{} SATIN ALINDI!".format(kar['ad']), kar["renk"])

    def shop_sec(self):
        """Dükkan işlemleri"""
        silah_keys = list(SILAHLAR.keys())
        power_keys = list(POWER_UPLAR.keys())
        
        # İlk 8 silah veya güçlendirme
        if self.menu_secim < len(silah_keys):
            key = silah_keys[self.menu_secim]
            silah = SILAHLAR[key]
            if key not in self.acilan_silahlar:
                if self.para >= silah["fiyat"]:
                    self.para -= silah["fiyat"]
                    self.acilan_silahlar.append(key)
                    self.kayit["silahlar"] = self.acilan_silahlar
                    self.kaydet()
                    self.show_message("{} ALINDI!".format(silah['ad']), silah["renk"])
        elif self.menu_secim < len(silah_keys) + len(power_keys):
            p_key = power_keys[self.menu_secim - len(silah_keys)]
            power = POWER_UPLAR[p_key]
            if self.para >= power["fiyat"]:
                self.para -= power["fiyat"]
                self.powerup_al({"tur": p_key, "bilgi": power})
        elif self.menu_secim == len(silah_keys) + len(power_keys):
            # Devam et
            self.state = "PLAY"
            self.sonraki_oda()

    def oyun_baslat(self):
        self.state = "PLAY"
        self.seviye = 1
        self.oda_numarasi = 1
        self.oda_turu = "normal"
        oda_bilgi = ODALAR["normal"]
        self.oda_dusman_sayisi = oda_bilgi["dusman_sayisi"]
        self.oda_temizlendi = False
        self.skor = 0
        self.kill_count = 0
        self.p_zirh = 0
        self.hasar_boost = 1.0
        self.hiz_boost = 1.0
        self.savurma_boost = 1.0
        self.kritik_sans = 0.0

    def mouseMoveEvent(self, event): 
        self.mouse_pos = event.pos()

    def keyPressEvent(self, event):
        if self.state == "MENU":
            if event.key() == Qt.Key_Left:
                self.menu_sayfa = {"magaza": "karakter", "silah": "magaza", "karakter": "silah"}.get(self.menu_sayfa, "karakter")
                self.menu_secim = 0
                self.update()
            elif event.key() == Qt.Key_Right:
                self.menu_sayfa = {"karakter": "magaza", "magaza": "silah", "silah": "karakter"}.get(self.menu_sayfa, "magaza")
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
                    self.karakter_sec()
        elif event.key() == Qt.Key_Escape:
            if self.state == "PLAY":
                self.state = "PAUSE"
            elif self.state == "PAUSE":
                self.state = "PLAY"
        elif event.key() == Qt.Key_S:
            self.kaydet()
            self.show_message("OYUN KAYDEDİLDİ!", Qt.green)
        elif event.key() in [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4]:
            # Silah değiştirme
            silahlar = list(SILAHLAR.keys())
            idx = event.key() - Qt.Key_1
            if idx < len(silahlar) and silahlar[idx] in self.acilan_silahlar:
                self.silah = silahlar[idx]

    def silah_bilgi(self):
        return SILAHLAR.get(self.silah, SILAHLAR["kilic"])

    def ates_et(self):
        simdi = time.time()
        silah_bilgi = self.silah_bilgi()
        
        if simdi - self.last_shot_time < silah_bilgi["aralik"]:
            return
        
        self.last_shot_time = simdi
        self.silah_animasyon = 10
        
        dx = self.mouse_pos.x()-self.p_pos.x()
        dy = self.mouse_pos.y()-self.p_pos.y()
        dist = math.hypot(dx, dy)
        
        if dist > 0:
            vx = dx/dist * silah_bilgi["hiz"]
            vy = dy/dist * silah_bilgi["hiz"]
            
            if silah_bilgi["tur"] == "yakın":
                # Kılıç - savurma
                for e in self.enemies[:]:
                    if math.hypot(e['p'].x()-self.p_pos.x(), e['p'].y()-self.p_pos.y()) < 60:
                        hasar = silah_bilgi["hasar"] * self.hasar_boost * self.savurma_boost
                        e['hp'] -= hasar
                        e['p'] += QPointF(dx/dist * 20, dy/dist * 20)  # Geri itme
                        self.sparks.append(SparkEffect(e['p'], Qt.cyan))
                        
                        if e['hp'] <= 0:
                            self.dusman_oldu(e)
                
                self.shake_amount = 3
                self.glows.append(GlowEffect(self.p_pos, Qt.cyan, 30))
                
            elif silah_bilgi["tur"] == "ates":
                # Ateşli silahlar - çoklu mermi
                if self.silah == "pompali":
                    for _ in range(5):
                        aci = random.uniform(-0.4, 0.4)
                        self.bullets.append({
                            "p": QPointF(self.p_pos),
                            "v": QPointF(
                                vx * math.cos(aci) - vy * math.sin(aci),
                                vx * math.sin(aci) + vy * math.cos(aci)
                            ),
                            "omr": 30
                        })
                    self.shake_amount = 5
                else:
                    self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy), "omr": 60})
                
            elif silah_bilgi["tur"] == "alev":
                # Alev makinesi - kısa mesafe yayılım
                for _ in range(3):
                    aci = random.uniform(-0.5, 0.5)
                    self.bullets.append({
                        "p": QPointF(self.p_pos),
                        "v": QPointF(vx * 0.5 * math.cos(aci), vy * 0.5 * math.sin(aci)),
                        "omr": 15
                    })
                
            elif silah_bilgi["tur"] == "büyü":
                # Büyü - mermi
                self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy), "omr": 50})
                self.glows.append(GlowEffect(self.p_pos, silah_bilgi["renk"], 20))
                
            elif silah_bilgi["tur"] == "buz":
                # Buz - yavaşlatıcı
                self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy), "omr": 45})
                
            elif silah_bilgi["tur"] == "elektrik":
                # Yıldırım - zincirleme
                self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy), "omr": 40})
                
            else:
                # Normal mermi
                self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy), "omr": 60})
                
            # Elf çift ok
            if self.sel_char.get("ok") and silah_bilgi["tur"] == "uzak":
                offset = 15
                perp_x = -dy/dist * offset
                perp_y = dx/dist * offset
                self.bullets.append({"p": QPointF(self.p_pos.x()+perp_x, self.p_pos.y()+perp_y), "v": QPointF(vx, vy), "omr": 60})
                self.bullets.append({"p": QPointF(self.p_pos.x()-perp_x, self.p_pos.y()-perp_y), "v": QPointF(vx, vy), "omr": 60})

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        if self.shake_amount > 0:
            p.translate(random.randint(-self.shake_amount, self.shake_amount), 
                        random.randint(-self.shake_amount, self.shake_amount))

        # Arka plan
        if self.state == "PLAY" or self.state == "SHOP":
            self.ciz_arka_plan(p)
        else:
            p.fillRect(self.rect(), QColor(20, 10, 30))

        if self.state == "MENU":
            self.ciz_menu(p)
        elif self.state == "PLAY":
            self.ciz_oyun(p)
        elif self.state == "SHOP":
            self.ciz_shop(p)
        elif self.state == "PAUSE":
            self.ciz_oyun(p)
            self.ciz_pause(p)
        elif self.state == "OVER":
            self.ciz_game_over(p)

    def ciz_arka_plan(self, p):
        # Zemin
        grad = QLinearGradient(0, 0, 0, 800)
        
        if self.oda_turu == "boss":
            grad.setColorAt(0, QColor(80, 0, 0))
            grad.setColorAt(1, QColor(20, 0, 0))
        elif self.oda_turu == "magaza":
            grad.setColorAt(0, QColor(0, 60, 0))
            grad.setColorAt(1, QColor(0, 20, 0))
        elif self.oda_turu == "dinlenme":
            grad.setColorAt(0, QColor(0, 0, 80))
            grad.setColorAt(1, QColor(0, 0, 30))
        else:
            grad.setColorAt(0, QColor(50, 30, 60))
            grad.setColorAt(1, QColor(20, 10, 30))
        
        p.fillRect(self.rect(), grad)
        
        # Oda çerçevesi
        p.setPen(QPen(QColor(100, 80, 60), 8))
        p.setBrush(Qt.NoBrush)
        p.drawRect(30, 80, 1140, 650)
        
        # Izgara deseni
        p.setPen(QPen(QColor(255, 255, 255, 10), 1))
        for i in range(50, 1150, 50):
            p.drawLine(i, 80, i, 730)
        for i in range(100, 730, 50):
            p.drawLine(30, i, 1170, i)

    def ciz_menu(self, p):
        p.fillRect(self.rect(), QColor(15, 5, 25))
        
        # Başlık
        grad = QLinearGradient(0, 40, 0, 100)
        grad.setColorAt(0, QColor(255, 100, 50))
        grad.setColorAt(0.5, QColor(200, 50, 150))
        grad.setColorAt(1, QColor(100, 50, 255))
        
        p.setPen(Qt.white)
        p.setFont(QFont("Impact", 48))
        p.drawText(self.rect().adjusted(0, 20, 0, 0), Qt.AlignCenter, "⚔️ SOUL KNIGHT ⚔️")
        
        p.setFont(QFont("Arial", 16))
        p.setPen(QColor(255, 215, 0))
        p.drawText(QRect(0, 90, 1200, 30), Qt.AlignCenter, "💰 Para: {}".format(self.para))
        
        # Menü sekmeleri
        sekmeler = ["KARAKTER", "Silah DÜKKANI", "DÜKKAN"]
        secili_index = {"karakter": 0, "silah": 1, "magaza": 2}[self.menu_sayfa]
        
        p.setFont(QFont("Arial", 14))
        for i, sekme in enumerate(sekmeler):
            x = 250 + i * 250
            if i == secili_index:
                p.setBrush(QColor(150, 50, 0))
                p.setPen(QPen(QColor(255, 150, 50), 2))
            else:
                p.setBrush(QColor(40, 20, 20))
                p.setPen(QPen(QColor(100, 50, 30), 1))
            p.drawRoundedRect(x, 130, 220, 40, 10, 10)
            p.setPen(Qt.white)
            p.drawText(QRect(x, 130, 220, 40), Qt.AlignCenter, sekme)
        
        # İçerik
        if self.menu_sayfa == "karakter":
            self.ciz_karakter_secim(p)
        elif self.menu_sayfa == "silah":
            self.ciz_silah_secim(p)
        elif self.menu_sayfa == "magaza":
            self.ciz_magaza(p)
        
        # Alt bilgi
        p.setPen(QColor(150, 150, 150))
        p.setFont(QFont("Arial", 11))
        p.drawText(QRect(0, 720, 1200, 30), Qt.AlignCenter, "← → Sayfa | ↑↓ Seç | ENTER Oyna | S Kaydet | ESC Çıkış")

    def ciz_karakter_secim(self, p):
        karakterler = list(KARAKTERLER.items())
        kart_genislik = 170
        kart_yukseklik = 200
        baslangic_x = (1200 - len(karakterler) * kart_genislik) // 2
        
        for i, (key, kar) in enumerate(karakterler):
            x = baslangic_x + i * kart_genislik
            y = 200
            
            satin_alindi = key in self.acilan_karakterler
            
            if i == self.menu_secim:
                p.setBrush(QColor(150, 75, 0))
                p.setPen(QPen(QColor(255, 150, 0), 3))
                p.drawRoundedRect(x-5, y-5, kart_genislik+10, kart_yukseklik+10, 15, 15)
            else:
                p.setBrush(QColor(35, 20, 35))
                p.setPen(QPen(QColor(80, 40, 60), 1))
                p.drawRoundedRect(x, y, kart_genislik, kart_yukseklik, 10, 10)
            
            # Karakter ikonu
            p.setBrush(kar["renk"])
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(x + kart_genislik//2, y + 45), 35, 35)
            
            # Göz (karakter yönü)
            p.setBrush(kar["goz"])
            p.drawEllipse(QPoint(x + kart_genislik//2 - 10, y + 40), 6, 4)
            p.drawEllipse(QPoint(x + kart_genislik//2 + 10, y + 40), 6, 4)
            
            # İsim
            p.setPen(Qt.white if satin_alindi else QColor(120, 120, 120))
            p.setFont(QFont("Arial", 11, QFont.Bold))
            p.drawText(QRect(x, y + 85, kart_genislik, 20), Qt.AlignCenter, kar["ad"])
            
            # Özellik
            p.setPen(kar["goz"])
            p.setFont(QFont("Arial", 9))
            p.drawText(QRect(x, y + 105, kart_genislik, 15), Qt.AlignCenter, kar["ozel"])
            
            # HP
            p.setPen(QColor(255, 100, 100))
            p.setFont(QFont("Arial", 8))
            p.drawText(QRect(x, y + 125, kart_genislik, 15), Qt.AlignCenter, "❤️ {}".format(kar["baslangic_hp"]))
            
            # Durum
            if satin_alindi:
                p.setPen(Qt.green)
                p.setFont(QFont("Arial", 12, QFont.Bold))
                p.drawText(QRect(x, y + 160, kart_genislik, 25), Qt.AlignCenter, "SEÇ")
            else:
                p.setPen(QColor(255, 215, 0))
                p.setFont(QFont("Arial", 11))
                p.drawText(QRect(x, y + 160, kart_genislik, 25), Qt.AlignCenter, "💰 {}".format(kar['fiyat']))

    def ciz_silah_secim(self, p):
        silahlar = list(SILAHLAR.items())
        kart_genislik = 160
        kart_yukseklik = 160
        baslangic_x = (1200 - len(silahlar) * kart_genislik) // 2
        
        p.setPen(Qt.white)
        p.setFont(QFont("Arial", 14))
        p.drawText(QRect(0, 190, 1200, 30), Qt.AlignCenter, "🔫 SİLAHINI SEÇ")
        
        for i, (key, silah) in enumerate(silahlar):
            x = baslangic_x + i * kart_genislik
            y = 230
            
            satin_alindi = key in self.acilan_silahlar
            
            if i == self.menu_secim:
                p.setBrush(QColor(100, 50, 0))
                p.setPen(QPen(Qt.yellow, 2))
                p.drawRoundedRect(x-5, y-5, kart_genislik+10, kart_yukseklik+10, 12, 12)
            else:
                p.setBrush(QColor(30, 25, 35))
                p.setPen(QPen(QColor(70, 50, 60), 1))
                p.drawRoundedRect(x, y, kart_genislik, kart_yukseklik, 8, 8)
            
            # Silah ikonu
            p.setBrush(silah["renk"])
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(x + kart_genislik//2, y + 40), 25, 25)
            
            # İsim
            p.setPen(Qt.white if satin_alindi else QColor(100, 100, 100))
            p.setFont(QFont("Arial", 10, QFont.Bold))
            p.drawText(QRect(x, y + 70, kart_genislik, 18), Qt.AlignCenter, silah["ad"])
            
            # Tür
            p.setPen(silah["renk"])
            p.setFont(QFont("Arial", 8))
            p.drawText(QRect(x, y + 90, kart_genislik, 15), Qt.AlignCenter, silah["tur"].upper())
            
            # Durum
            if satin_alindi:
                p.setPen(Qt.green)
                p.setFont(QFont("Arial", 10, QFont.Bold))
                p.drawText(QRect(x, y + 130, kart_genislik, 20), Qt.AlignCenter, "✓")
            else:
                p.setPen(QColor(255, 215, 0))
                p.setFont(QFont("Arial", 10))
                p.drawText(QRect(x, y + 130, kart_genislik, 20), Qt.AlignCenter, "💰 {}".format(silah['fiyat']))

    def ciz_magaza(self, p):
        karakterler = list(KARAKTERLER.items())
        kart_genislik = 170
        kart_yukseklik = 140
        baslangic_x = (1200 - len(karakterler) * kart_genislik) // 2
        
        p.setPen(Qt.white)
        p.setFont(QFont("Arial", 14))
        p.drawText(QRect(0, 190, 1200, 30), Qt.AlignCenter, "🛒 YENİ KARAKTER AL")
        
        for i, (key, kar) in enumerate(karakterler):
            x = baslangic_x + i * kart_genislik
            y = 230
            
            satin_alindi = key in self.acilan_karakterler
            
            if i == self.menu_secim:
                p.setBrush(QColor(80, 40, 0))
                p.setPen(QPen(QColor(255, 200, 0), 2))
                p.drawRoundedRect(x-5, y-5, kart_genislik+10, kart_yukseklik+10, 12, 12)
            else:
                p.setBrush(QColor(30, 25, 30))
                p.setPen(QPen(QColor(80, 50, 30), 1))
                p.drawRoundedRect(x, y, kart_genislik, kart_yukseklik, 8, 8)
            
            # İkon
            p.setBrush(kar["renk"])
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(x + kart_genislik//2, y + 35), 25, 25)
            
            # İsim
            p.setPen(Qt.white)
            p.setFont(QFont("Arial", 10, QFont.Bold))
            p.drawText(QRect(x, y + 65, kart_genislik, 18), Qt.AlignCenter, kar["ad"])
            
            # Durum
            if satin_alindi:
                p.setPen(Qt.green)
                p.setFont(QFont("Arial", 9))
                p.drawText(QRect(x, y + 100, kart_genislik, 20), Qt.AlignCenter, "VAR")
            else:
                p.setPen(QColor(255, 215, 0))
                p.setFont(QFont("Arial", 11))
                p.drawText(QRect(x, y + 100, kart_genislik, 20), Qt.AlignCenter, "💰 {}".format(kar['fiyat']))

    def ciz_shop(self, p):
        # Dükkan arka plan
        p.fillRect(self.rect(), QColor(20, 40, 20))
        
        p.setPen(Qt.white)
        p.setFont(QFont("Impact", 36))
        p.drawText(self.rect().adjusted(0, 20, 0, 0), Qt.AlignCenter, "🏪 DÜKKAN")
        
        p.setFont(QFont("Arial", 18))
        p.setPen(QColor(255, 215, 0))
        p.drawText(QRect(0, 70, 1200, 30), Qt.AlignCenter, "💰 Para: {}".format(self.para))
        
        # Silahlar
        silahlar = list(SILAHLAR.items())
        powerups = list(POWER_UPLAR.items())
        
        p.setFont(QFont("Arial", 14))
        p.setPen(Qt.white)
        p.drawText(QRect(0, 110, 1200, 25), Qt.AlignCenter, "🔫 SILAHLAR")
        
        for i, (key, silah) in enumerate(silahlar):
            x = 50 + (i % 4) * 280
            y = 140 + (i // 4) * 70
            
            satin_alindi = key in self.acilan_silahlar
            
            if i == self.menu_secim:
                p.setBrush(QColor(100, 50, 0))
                p.setPen(QPen(Qt.yellow, 2))
                p.drawRoundedRect(x-5, y-5, 260, 55, 8, 8)
            else:
                p.setBrush(QColor(40, 30, 30))
                p.setPen(QPen(QColor(80, 50, 30), 1))
                p.drawRoundedRect(x, y, 260, 55, 5, 5)
            
            p.setBrush(silah["renk"])
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(x + 25, y + 27), 18, 18)
            
            p.setPen(Qt.white if satin_alindi else QColor(200, 200, 200))
            p.setFont(QFont("Arial", 11, QFont.Bold))
            p.drawText(QRect(x + 50, y + 10, 150, 20), Qt.AlignLeft, silah["ad"])
            
            if satin_alindi:
                p.setPen(Qt.green)
                p.setFont(QFont("Arial", 9))
                p.drawText(QRect(x + 50, y + 32, 150, 15), Qt.AlignLeft, "SAHİP")
            else:
                p.setPen(QColor(255, 215, 0))
                p.setFont(QFont("Arial", 10))
                p.drawText(QRect(x + 50, y + 32, 150, 15), Qt.AlignLeft, "💰 {}".format(silah['fiyat']))
        
        # Güçlendirmeler
        p.setFont(QFont("Arial", 14))
        p.setPen(Qt.white)
        p.drawText(QRect(0, 350, 1200, 25), Qt.AlignCenter, "⚡ GÜÇLENDİRMELER")
        
        for i, (key, power) in enumerate(powerups):
            x = 50 + (i % 4) * 280
            y = 380 + (i // 4) * 60
            
            if i + len(silahlar) == self.menu_secim:
                p.setBrush(QColor(50, 50, 100))
                p.setPen(QPen(Qt.cyan, 2))
                p.drawRoundedRect(x-5, y-5, 260, 50, 8, 8)
            else:
                p.setBrush(QColor(30, 30, 50))
                p.setPen(QPen(QColor(50, 50, 80), 1))
                p.drawRoundedRect(x, y, 260, 50, 5, 5)
            
            p.setBrush(power["renk"])
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(x + 25, y + 25), 15, 15)
            
            p.setPen(Qt.white)
            p.setFont(QFont("Arial", 10, QFont.Bold))
            p.drawText(QRect(x + 50, y + 10, 150, 15), Qt.AlignLeft, power["aciklama"])
            
            p.setPen(QColor(255, 215, 0))
            p.setFont(QFont("Arial", 9))
            p.drawText(QRect(x + 50, y + 28, 150, 15), Qt.AlignLeft, "💰 {}".format(power['fiyat']))
        
        # Devam butonu
        if len(silahlar) + len(powerups) == self.menu_secim:
            p.setBrush(QColor(0, 100, 0))
            p.setPen(QPen(Qt.green, 3))
            p.drawRoundedRect(450, 600, 300, 60, 10, 10)
            p.setPen(Qt.white)
            p.setFont(QFont("Arial", 18, QFont.Bold))
            p.drawText(QRect(450, 600, 300, 60), Qt.AlignCenter, "DEVAM ET ▶")
        else:
            p.setBrush(QColor(20, 60, 20))
            p.setPen(QPen(QColor(0, 150, 0), 2))
            p.drawRoundedRect(450, 600, 300, 60, 10, 10)
            p.setPen(QColor(100, 200, 100))
            p.setFont(QFont("Arial", 16))
            p.drawText(QRect(450, 600, 300, 60), Qt.AlignCenter, "DEVAM ET ▶")
        
        # Alt bilgi
        p.setPen(QColor(150, 150, 150))
        p.setFont(QFont("Arial", 11))
        p.drawText(QRect(0, 680, 1200, 30), Qt.AlignCenter, "↑↓ Seç | ENTER Satın Al/Devam | ESC Geri")

    def ciz_oyun(self, p):
        # Efektler
        for g in self.glows:
            g.draw(p)
        
        for s in self.sparks:
            s.draw(p)
        
        # Parçacıklar
        for part in self.particles:
            c = QColor(part.color)
            c.setAlpha(part.life)
            p.setBrush(c)
            p.drawRect(QRectF(part.pos.x()-part.size/2, part.pos.y()-part.size/2, part.size, part.size))

        # Güçlendirmeler
        for pu in self.powerups:
            bilgi = POWER_UPLAR[pu["tur"]]
            p.setBrush(bilgi["renk"])
            p.setPen(Qt.white)
            p.drawEllipse(pu["p"], 12, 12)
            p.setFont(QFont("Arial", 12, QFont.Bold))
            p.drawText(int(pu["p"].x()-4), int(pu["p"].y()+4), bilgi["sembol"])

        # Düşmanlar
        for e in self.enemies:
            tur_bilgi = DUSMAN_TURLERI[e["tur"]]
            renk = tur_bilgi["renk"]
            
            if e.get("yavas"):
                renk = QColor(150, 200, 255)
            if e.get("yaniyor", 0) > 0:
                renk = QColor(255, 100, 0)
            if e.get("asitli", 0) > 0:
                renk = QColor(0, 255, 0)
            
            self.ciz_karakter(p, e["p"], renk, tur_bilgi["boyut"], e["tur"] == "boss1" or e["tur"] == "boss2")
            
            # HP barı
            if e["hp"] < e["max_hp"]:
                hp_oran = e["hp"] / e["max_hp"]
                p.setBrush(QColor(50, 0, 0))
                p.setPen(Qt.NoPen)
                p.drawRect(e["p"].x()-20, e["p"].y()-tur_bilgi["boyut"]-10, 40, 5)
                p.setBrush(Qt.red)
                p.drawRect(e["p"].x()-20, e["p"].y()-tur_bilgi["boyut"]-10, 40*hp_oran, 5)

        # Mermiler
        silah_bilgi = self.silah_bilgi()
        for b in self.bullets:
            p.setBrush(silah_bilgi["renk"])
            p.setPen(Qt.NoPen)
            p.drawEllipse(b["p"], silah_bilgi["boyut"], silah_bilgi["boyut"])
            
            # Glow
            c = QColor(silah_bilgi["renk"])
            c.setAlpha(80)
            p.setBrush(c)
            p.drawEllipse(b["p"], silah_bilgi["boyut"]+3, silah_bilgi["boyut"]+3)

        # Oyuncu
        self.ciz_karakter(p, self.p_pos, self.sel_char["renk"], 25, False, True)
        
        # UI
        self.ciz_ui(p)

    def ciz_karakter(self, p, pos, renk, boyut, is_boss=False, is_player=False):
        p.save()
        p.translate(pos)
        
        if is_player:
            p.rotate(math.degrees(self.oyuncu_yonu) + 90)
        
        # Gövde
        p.setBrush(renk)
        p.setPen(QPen(renk.darker(150), 2))
        p.drawEllipse(-boyut//2, -boyut//2, boyut, boyut)
        
        # Gözler
        p.setBrush(Qt.white)
        if is_player:
            p.drawRect(boyut//4, -boyut//4, boyut//3, boyut//3)
        else:
            p.drawRect(-boyut//3, -boyut//4, boyut//3, boyut//3)
        
        p.restore()

    def ciz_ui(self, p):
        # Üst bar
        p.setBrush(QColor(0, 0, 0, 180))
        p.drawRect(0, 0, 1200, 50)
        
        # Sol üst - Skor ve Para
        p.setPen(Qt.white)
        p.setFont(QFont("Consolas", 14, QFont.Bold))
        p.drawText(15, 32, "🏆 {}".format(self.skor))
        
        p.setPen(QColor(255, 215, 0))
        p.setFont(QFont("Arial", 13))
        p.drawText(120, 32, "💰 {}".format(self.para))
        
        # Orta üst - Oda bilgisi
        oda_bilgi = ODALAR[self.oda_turu]
        p.setPen(oda_bilgi["renk"])
        p.setFont(QFont("Arial", 14, QFont.Bold))
        p.drawText(350, 32, "ODA {} - {}".format(self.oda_numarasi, oda_bilgi["ad"]))
        
        # Sağ üst - Silah
        silah_bilgi = self.silah_bilgi()
        p.setPen(silah_bilgi["renk"])
        p.setFont(QFont("Arial", 12, QFont.Bold))
        p.drawText(850, 32, "🔫 {}".format(silah_bilgi['ad'].upper()))
        
        # Alt bar - Can ve Zırh
        p.setPen(Qt.white)
        p.setFont(QFont("Arial", 11, QFont.Bold))
        p.drawText(15, 770, "❤️")
        
        # Can barı
        p.setBrush(QColor(40, 40, 40))
        p.setPen(Qt.NoPen)
        p.drawRect(50, 758, 200, 16)
        
        if self.p_can > 60:
            p.setBrush(Qt.green)
        elif self.p_can > 30:
            p.setBrush(Qt.yellow)
        else:
            p.setBrush(Qt.red)
        p.drawRect(52, 760, max(0, int(self.p_can * 1.96)), 12)
        
        p.setPen(Qt.white)
        p.setFont(QFont("Arial", 10))
        p.drawText(255, 770, "{}/{}".format(int(self.p_can), self.max_can))
        
        # Zırh
        if self.p_zirh > 0:
            p.setBrush(QColor(50, 50, 200))
            p.setPen(Qt.NoPen)
            p.drawRect(50, 778, int(self.p_zirh * 2), 4)
            p.setPen(QColor(150, 150, 255))
            p.setFont(QFont("Arial", 8))
            p.drawText(255, 780, "Zırh: {}".format(int(self.p_zirh)))
        
        # Güçlendirmeler
        x = 350
        if self.hasar_boost > 1.0:
            p.setPen(Qt.red)
            p.setFont(QFont("Arial", 10))
            p.drawText(x, 770, "⚔️+{}%".format(int((self.hasar_boost-1)*100)))
            x += 60
        
        if self.kritik_sans > 0:
            p.setPen(QColor(255, 165, 0))
            p.setFont(QFont("Arial", 10))
            p.drawText(x, 770, "💥{}%".format(int(self.kritik_sans*100)))
            x += 60
        
        # Düşman sayısı
        p.setPen(QColor(200, 200, 200))
        p.setFont(QFont("Arial", 11))
        if not self.oda_temizlendi and self.oda_turu not in ["magaza", "dinlenme"]:
            p.drawText(1050, 770, "Düşman: {}/{}".format(len(self.enemies), self.oda_dusman_sayisi))
        else:
            p.setPen(Qt.green)
            p.drawText(1050, 770, "✓ TEMİZ")
        
        # Mesaj
        if hasattr(self, 'aktif_mesaj') and self.aktif_mesaj:
            p.setPen(self.aktif_mesaj["renk"])
            p.setFont(QFont("Arial", 24, QFont.Bold))
            p.drawText(self.rect().adjusted(0, -100, 0, 0), Qt.AlignCenter, self.aktif_mesaj["metin"])
            self.aktif_mesaj["sure"] -= 1
            if self.aktif_mesaj["sure"] <= 0:
                del self.aktif_mesaj

    def ciz_pause(self, p):
        p.fillRect(self.rect(), QColor(0, 0, 0, 150))
        
        p.setBrush(QColor(30, 30, 50))
        p.setPen(QPen(QColor(100, 150, 255), 2))
        p.drawRoundedRect(400, 280, 400, 240, 20, 20)
        
        p.setPen(Qt.white)
        p.setFont(QFont("Impact", 36))
        p.drawText(QRect(400, 300, 400, 50), Qt.AlignCenter, "⏸️ DURAKLADI")
        
        p.setFont(QFont("Arial", 16))
        p.drawText(QRect(400, 370, 400, 30), Qt.AlignCenter, "Devam için ESC")
        p.drawText(QRect(400, 410, 400, 30), Qt.AlignCenter, "Kaydet için S")
        p.drawText(QRect(400, 450, 400, 30), Qt.AlignCenter, "Menü için M")

    def ciz_game_over(self, p):
        p.fillRect(self.rect(), QColor(0, 0, 0, 220))
        
        p.setPen(Qt.red)
        p.setFont(QFont("Impact", 60))
        p.drawText(self.rect().adjusted(0, -80, 0, 0), Qt.AlignCenter, "💀 OYUN BİTTİ 💀")
        
        p.setPen(Qt.white)
        p.setFont(QFont("Arial", 28))
        p.drawText(QRect(0, 250, 1200, 40), Qt.AlignCenter, "Skor: {}".format(self.skor))
        
        p.setPen(QColor(255, 215, 0))
        p.setFont(QFont("Arial", 22))
        p.drawText(QRect(0, 300, 1200, 35), Qt.AlignCenter, "Kazanılan Para: +{}".format(self.para))
        
        p.setPen(Qt.cyan)
        p.setFont(QFont("Arial", 18))
        p.drawText(QRect(0, 350, 1200, 30), Qt.AlignCenter, "Ulaşılan Oda: {}".format(self.oda_numarasi))
        p.drawText(QRect(0, 380, 1200, 30), Qt.AlignCenter, "Öldürülen Düşman: {}".format(self.kill_count))
        
        p.setPen(Qt.green)
        p.setFont(QFont("Arial", 22))
        p.drawText(QRect(0, 480, 1200, 50), Qt.AlignCenter, "🎮 Tekrar oynamak için tıkla 🎮")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = SoulKnight()
    w.show()
    sys.exit(app.exec_())
