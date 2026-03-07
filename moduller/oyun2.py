import sys, random, math, time, json
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ==================== SOUL KNIGHT - BİREBİR KOPYASINA ÇEVİRME ====================

# --- KARAKTERLER (Resmi Soul Knight Karakterleri) ---
KARAKTERLER = {
    "1": {
        "ad": "Şövalye", 
        "hiz": 4.5, 
        "goz": Qt.cyan, 
        "hasar": 1.0,
        "silah": "kilic",
        "ozel": "Kalkan",
        "renk": QColor(70, 130, 180),  # Steel Blue
        "aciklama": "Dengeli savaşçı - Kalkan ile hasar azaltma",
        "fiyat": 0,
        "baslangic_hp": 100,
        "ozellik": {"zirh_bonus": 0.3}
    },
    "2": {
        "ad": "Büyücü", 
        "hiz": 5, 
        "goz": Qt.magenta, 
        "hasar": 2.0,
        "silah": "buz_deynek",
        "ozel": "Büyü Ustası",
        "renk": QColor(148, 0, 211),  # Dark Violet
        "aciklama": "Güçlü büyü saldırıları - Mana kullanımı",
        "fiyat": 500,
        "baslangic_hp": 70,
        "ozellik": {"buyu_bonus": 1.5}
    },
    "3": {
        "ad": "Suikastçı", 
        "hiz": 9, 
        "goz": Qt.yellow, 
        "hasar": 1.5,
        "silah": "yay",
        "ozel": "Gölge",
        "renk": QColor(50, 205, 50),  # Lime Green
        "aciklama": "En hızlı - Kritik vuruş şansı",
        "fiyat": 750,
        "baslangic_hp": 65,
        "ozellik": {"kritik": 0.25}
    },
    "4": {
        "ad": "Mühendis", 
        "hiz": 4, 
        "goz": QColor(255, 165, 0),  # Orange
        "hasar": 1.2,
        "silah": "makinali",
        "ozel": "Tamirci",
        "renk": QColor(255, 140, 0),  # Dark Orange
        "aciklama": "İstasyon kurar - Düşmanlarısilah düşürür",
        "fiyat": 1000,
        "baslangic_hp": 90,
        "ozellik": {"silah_dusurme": 0.3}
    },
    "5": {
        "ad": "Rahip", 
        "hiz": 5, 
        "goz": QColor(255, 255, 240),  # Ivory
        "hasar": 0.8,
        "silah": "buz_deynek",
        "ozel": "İyileştirme",
        "renk": QColor(255, 215, 0),  # Gold
        "aciklama": "Otomatik iyileşme - Her vuruşta can",
        "fiyat": 1500,
        "baslangic_hp": 85,
        "ozellik": "iyilestirme": 0.02
    },
    "6": {
        "ad": "Elf", 
        "hiz": 7, 
        "goz": QColor(0, 255, 127),  # Spring Green
        "hasar": 1.3,
        "silah": "yay",
        "ok": True,
        "ozel": "Avcı",
        "renk": QColor(34, 139, 34),  # Forest Green
        "aciklama": "Çift ok atar - Düşmanları yavaşlatır",
        "fiyat": 2000,
        "baslangic_hp": 75,
        "ozellik": "yavaslatma": True
    },
    "7": {
        "ad": "Paladin", 
        "hiz": 3.5, 
        "goz": QColor(255, 215, 0),  # Gold
        "hasar": 1.8,
        "silah": "kilic",
        "ozel": "Kutsal",
        "renk": QColor(255, 250, 205),  # Lemon Chiffon
        "aciklama": "Yüksek hasar + Zırh - Boss hasarı azaltma",
        "fiyat": 2500,
        "baslangic_hp": 130,
        "ozellik": "boss_zirh": 0.5
    },
    "8": {
        "ad": "Vampir", 
        "hiz": 6, 
        "goz": Qt.red, 
        "hasar": 1.4,
        "silah": "kilic",
        "ozel": "Kan Emici",
        "renk": QColor(139, 0, 0),  # Dark Red
        "aciklama": "Vuruşta can kazanır - Ölümsüzlük şansı",
        "fiyat": 3000,
        "baslangic_hp": 80,
        "ozellik": "can_emme": 0.15
    },
    "9": {
        "ad": "Ninja", 
        "hiz": 8, 
        "goz": QColor(200, 0, 200),  # Purple
        "hasar": 1.6,
        "silah": "ninjya_bıcağı",
        "ozel": "Shuriken",
        "renk": QColor(75, 0, 130),  # Indigo
        "aciklama": "Hızlı - Bıçak fırlatma",
        "fiyat": 3500,
        "baslangic_hp": 72,
        "ozellik": "suresiz_silah": True
    },
    "10": {
        "ad": "Baba Yaga", 
        "hiz": 4, 
        "goz": QColor(255, 100, 100),  # Light Red
        "hasar": 2.2,
        "silah": "ases_deynek",
        "ozel": "Ateş Topu",
        "renk": QColor(128, 0, 0),  # Maroon
        "aciklama": "En güçlü - Patlama hasarı",
        "fiyat": 4000,
        "baslangic_hp": 75,
        "ozellik": "patlama": True
    },
}

# --- SİLAHLAR (Soul Knight Silahları) ---
SILAHLAR = {
    "kilic": {
        "renk": QColor(192, 192, 192),  # Silver
        "boyut": 10, "hiz": 0, "aralik": 0.5, "hasar": 3, 
        "ad": "Kılıç", "fiyat": 0, "tur": "yakın",
        "aciklama": "Yakın dövüş silahı"
    },
    "yay": {
        "renk": QColor(139, 90, 43),  # Brown
        "boyut": 4, "hiz": 18, "aralik": 0.4, "hasar": 1.5, 
        "ad": " Yay", "fiyat": 500, "tur": "uzak",
        "aciklama": "Hızlı ok atışı"
    },
    "makinali": {
        "renk": QColor(100, 100, 100),  # Gray
        "boyut": 3, "hiz": 25, "aralik": 0.08, "hasar": 0.4, 
        "ad": "Makinalı", "fiyat": 750, "tur": "ates",
        "aciklama": "Sürekli ateş"
    },
    "pompa": {
        "renk": QColor(205, 92, 92),  # Indian Red
        "boyut": 14, "hiz": 10, "aralik": 0.7, "hasar": 4, 
        "ad": "Pompalı Tüfek", "fiyat": 1000, "tur": "ates",
        "aciklama": "Geniş alan hasarı"
    },
    "buz_deynek": {
        "renk": QColor(135, 206, 250),  # Light Blue
        "boyut": 5, "hiz": 15, "aralik": 0.5, "hasar": 2, 
        "ad": "Buz Asası", "fiyat": 1250, "tur": "buz",
        "aciklama": "Düşmanları yavaşlatır"
    },
    "ates_deynek": {
        "renk": QColor(255, 69, 0),  # Orange Red
        "boyut": 6, "hiz": 12, "aralik": 0.6, "hasar": 2.5, 
        "ad": "Ateş Asası", "fiyat": 1500, "tur": "ates",
        "aciklama": "Yanma hasarı"
    },
    "elektrik_deynek": {
        "renk": QColor(255, 255, 0),  # Yellow
        "boyut": 4, "hiz": 20, "aralik": 0.3, "hasar": 1.5, 
        "ad": "Yıldırım Asası", "fiyat": 1750, "tur": "elektrik",
        "aciklama": "Zincirleme hasar"
    },
    "lazer_tufek": {
        "renk": Qt.red,
        "boyut": 3, "hiz": 30, "aralik": 0.15, "hasar": 0.8, 
        "ad": "Lazer Tüfeği", "fiyat": 2000, "tur": "lazer",
        "aciklama": "İsabet oranı yüksek"
    },
    "ninjya_bıcağı": {
        "renk": QColor(128, 128, 128),  # Gray
        "boyut": 4, "hiz": 22, "aralik": 0.25, "hasar": 1.2, 
        "ad": "Ninja Bıçağı", "fiyat": 1500, "tur": "firlatilan",
        "aciklama": "Hızlı fırlatma"
    },
    "tesbih": {
        "renk": QColor(255, 215, 0),  # Gold
        "boyut": 5, "hiz": 14, "aralik": 0.45, "hasar": 1.8, 
        "ad": "Kutsal Tesbih", "fiyat": 2500, "tur": "kutsal",
        "aciklama": "Şifa verir"
    },
    "kask": {
        "renk": QColor(0, 255, 127),  # Spring Green
        "boyut": 6, "hiz": 16, "aralik": 0.35, "hasar": 1.3, 
        "ad": "Nebula", "fiyat": 3000, "tur": "nebula",
        "aciklama": "Yıldız fırlatır"
    },
    "kılıç_2": {
        "renk": QColor(255, 0, 255),  # Magenta
        "boyut": 12, "hiz": 0, "aralik": 0.4, "hasar": 4, 
        "ad": "Kutsal Kılıç", "fiyat": 3500, "tur": "kutsal_kilic",
        "aciklama": "Döner kılıç"
    },
}

# --- DÜŞMAN TÜRLERİ (Soul Knight Düşmanları) ---
DUSMAN_TURLERI = {
    "toplanan": {"hp": 1, "hiz": 2, "renk": QColor(0, 255, 0), "boyut": 18, "puan": 5, "ad": "Yeşil Top", "efekt": "yavas", "desc": "Yavaşlar"},
    "mavi_top": {"hp": 1, "hiz": 3, "renk": QColor(0, 100, 255), "boyut": 16, "puan": 8, "ad": "Mavi Top", "efekt": None, "desc": "Hızlı"},
    "kırmızı_top": {"hp": 2, "hiz": 2.5, "renk": QColor(255, 50, 50), "boyut": 20, "puan": 12, "ad": "Kırmızı Top", "efekt": "carpma", "desc": "Patlar"},
    "mor_top": {"hp": 1.5, "hiz": 2.8, "renk": QColor(180, 0, 255), "boyut": 17, "puan": 10, "ad": "Mor Top", "efekt": "buyulu", "desc": "Büyülü"},
    "iskelet": {"hp": 3, "hiz": 2, "renk": QColor(240, 240, 240), "boyut": 22, "puan": 20, "ad": "İskelet", "efekt": None, "desc": "Savaşçı"},
    "iskelet_okcu": {"hp": 2, "hiz": 1.5, "renk": QColor(200, 200, 200), "boyut": 18, "puan": 25, "ad": "İskelet Okçu", "efekt": "ok", "desc": "Uzaktan"},
    "golem": {"hp": 12, "hiz": 1, "renk": QColor(105, 105, 105), "boyut": 45, "puan": 80, "ad": "Golem", "efekt": "darbe", "desc": "Zırhlı"},
    "orc": {"hp": 5, "hiz": 2.5, "renk": QColor(139, 69, 19), "boyut": 30, "puan": 35, "ad": "Ork", "efekt": "carpma", "desc": "Güçlü"},
    "hayalet": {"hp": 1, "hiz": 3.5, "renk": QColor(200, 200, 255), "boyut": 15, "puan": 30, "ad": "Hayalet", "efekt": "gecirgen", "desc": "Geçirgen"},
    "bos_kral": {"hp": 40, "hiz": 1.2, "renk": QColor(139, 0, 0), "boyut": 55, "puan": 500, "ad": "Ölümsüz Wollow", "efekt": "boss", "desc": "BOSS"},
    "canavar": {"hp": 60, "hiz": 1.5, "renk": QColor(75, 0, 130), "boyut": 65, "puan": 1000, "ad": "Kara Canavar", "efekt": "boss", "desc": "BOSS"},
}

# --- ODALAR ---
ODALAR = {
    "savas": {"ad": "Savaş Odası", "dusman_sayisi": 5, "zorluk": 1, "renk": QColor(80, 80, 80), "icon": "⚔️"},
    "zorlu": {"ad": "Zorlu Oda", "dusman_sayisi": 8, "zorluk": 2, "renk": QColor(139, 69, 19), "icon": "💀"},
    "boss": {"ad": "Boss Odası", "dusman_sayisi": 1, "zorluk": 3, "renk": QColor(139, 0, 0), "icon": "👹"},
    "dukkan": {"ad": "Dükkan", "dusman_sayisi": 0, "zorluk": 0, "renk": QColor(0, 100, 0), "icon": "🏪"},
    "sandik": {"ad": "Hazine", "dusman_sayisi": 3, "zorluk": 1.5, "renk": QColor(218, 165, 32), "icon": "📦"},
    "istirahat": {"ad": "İstirahat", "dusman_sayisi": 0, "zorluk": 0, "renk": QColor(0, 0, 139), "icon": "⛺"},
}

# --- GÜÇLENDİRMELER ---
POWER_UPLAR = {
    "can": {"renk": Qt.green, "sembol": "+", "aciklama": "Maks. Can +30%", "fiyat": 200, "deger": 30},
    "zirh": {"renk": Qt.blue, "sembol": "Z", "aciklama": "Zırh +20", "fiyat": 250, "deger": 20},
    "hasar": {"renk": Qt.red, "sembol": "⚔️", "aciklama": "Hasar +20%", "fiyat": 300, "deger": 0.2},
    "hiz": {"renk": Qt.yellow, "sembol": "⚡", "aciklama": "Ateş Hızı +15%", "fiyat": 250, "deger": 0.15},
    "kritik": {"renk": QColor(255, 165, 0), "sembol": "💥", "aciklama": "Kritik +10%", "fiyat": 400, "deger": 0.1},
    "ok": {"renk": QColor(139, 90, 43), "sembol": "🏹", "aciklama": "Ok Sayısı +1", "fiyat": 350, "deger": 1},
}

# --- EFEKT SINIFLARI ---
class Particle:
    def __init__(self, pos, color, size=None):
        self.pos = QPointF(pos)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 10)
        self.vel = QPointF(math.cos(angle) * speed, math.sin(angle) * speed)
        self.life = 255
        self.color = color
        self.size = size if size else random.randint(3, 10)

    def update(self):
        self.pos += self.vel
        self.vel *= 0.92
        self.life -= 12
        return self.life > 0

class SparkEffect:
    def __init__(self, pos, color):
        self.particles = []
        for _ in range(15):
            p = Particle(pos, color, random.randint(2, 6))
            p.vel *= 2.5
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
        self.life -= 10
        self.size += 0.5
        return self.life > 0
    
    def draw(self, p):
        c = QColor(self.color)
        c.setAlpha(self.life // 3)
        p.setPen(QPen(c, 3))
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(self.pos, self.size, self.size)

class Trail:
    def __init__(self, pos, color):
        self.pos = QPointF(pos)
        self.color = color
        self.life = 180
        self.size = 12
    
    def update(self):
        self.life -= 6
        self.size *= 0.97
        return self.life > 0
    
    def draw(self, p):
        c = QColor(self.color)
        c.setAlpha(self.life // 3)
        p.setBrush(c)
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
class SoulKnightGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1200, 800)
        self.setWindowTitle("SOUL KNIGHT - Resmi Tarzı")
        self.setMouseTracking(True)
        
        self.shake_amount = 0
        self.last_shot_time = 0
        self.init_game()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(16)
        
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
        
        self.menu_sayfa = "karakter"

    def init_game(self):
        self.state = "MENU"
        self.p_pos = QPointF(600, 450)
        self.mouse_pos = QPoint(600, 450)
        
        self.enemies = []
        self.bullets = []
        self.particles = []
        self.sparks = []
        self.glows = []
        self.powerups = []
        self.trails = []
        self.sandiklar = []
        
        self.para = 0
        self.skor = 0
        self.seviye = 1
        self.oda_numarasi = 1
        self.kill_count = 0
        
        self.p_can = 100
        self.p_zirh = 0
        self.max_can = 100
        self.sel_char = KARAKTERLER["1"]
        self.silah = "kilic"
        
        self.hasar_boost = 1.0
        self.hiz_boost = 1.0
        self.kritik_sans = 0.0
        self.ok_sayisi = 1
        
        self.oda_turu = "savas"
        self.oda_temizlendi = False
        self.oda_dusman_sayisi = 5
        self.oda_dusman_olen = 0
        
        self.menu_secim = 0
        self.oyuncu_yonu = 0
        self.silah_animasyon = 0
        
        self.odul_kazanildi = False
        self.para_miktari = 0

    def update_game(self):
        if self.state != "PLAY": 
            self.update()
            return
        
        if self.shake_amount > 0: 
            self.shake_amount -= 1
        
        if self.silah_animasyon > 0:
            self.silah_animasyon -= 1
        
        # Karakter özellikleri
        if self.sel_char.get("ozellik", {}).get("iyilestirme") and self.p_can < self.max_can:
            if random.random() < self.sel_char["ozellik"]["iyilestirme"]:
                self.p_can = min(self.max_can, self.p_can + 0.3)
                self.glows.append(GlowEffect(self.p_pos, QColor(0, 255, 0), 10))
        
        # Karakter hareketi
        target = QPointF(self.mouse_pos)
        d = math.hypot(target.x()-self.p_pos.x(), target.y()-self.p_pos.y())
        if d > 5:
            hiz = self.sel_char["hiz"] * self.hiz_boost
            move = QPointF((target.x()-self.p_pos.x())/d * hiz, 
                           (target.y()-self.p_pos.y())/d * hiz)
            self.p_pos += move
            
            self.oyuncu_yonu = math.atan2(target.y()-self.p_pos.y(), target.x()-self.p_pos.x())
            
            # İz efekti
            if random.random() > 0.5:
                self.trails.append(Trail(self.p_pos, self.silah_bilgi()["renk"]))
        
        # İz güncelleme
        self.trails = [t for t in self.trails if t.update()]
        
        # Oda temiz mi?
        if not self.oda_temizlendi and len(self.enemies) == 0 and self.oda_dusman_sayisi > 0 and not self.odul_kazanildi:
            self.oda_temizlendi = True
            self.odul_kazanildi = True
            self.para_miktari = 30 + self.seviye * 15 + random.randint(10, 50)
            self.para += self.para_miktari
            
            # Sandık spawn
            if random.random() < 0.3:
                self.spawn_sandik()
            
            self.show_message("ODA TEMİZLENDİ! +{} Para".format(self.para_miktari), Qt.green)
            
            if self.oda_turu != "boss":
                QTimer.singleShot(2500, self.oda_secimi_goster)
        
        # Düşman spawn
        if not self.oda_temizlendi and len(self.enemies) < self.oda_dusman_sayisi:
            if random.random() < 0.04:
                self.spawn_dusman()
        
        # Düşman hareketi
        for e in self.enemies[:]:
            tur_bilgi = DUSMAN_TURLERI[e["tur"]]
            hiz = tur_bilgi["hiz"] * (1 + self.seviye * 0.1)
            
            if e.get("yavas"):
                hiz *= 0.25
            
            dist = math.hypot(self.p_pos.x()-e["p"].x(), self.p_pos.y()-e["p"].y())
            if dist > 0:
                e["p"] += QPointF(
                    (self.p_pos.x()-e["p"].x())/dist * hiz, 
                    (self.p_pos.y()-e["p"].y())/dist * hiz
                )
            
            if dist < 30:
                boss_zarar = 1 if self.oda_turu != "boss" else 3
                if self.sel_char.get("ozellik", {}).get("boss_zirh"):
                    boss_zarar *= (1 - self.sel_char["ozellik"]["boss_zirh"])
                self.al_hasar(boss_zarar * 0.5)
                self.shake_amount = 5
        
        # Mermi kontrolü
        for b in self.bullets[:]:
            b['p'] += b['v']
            b['omr'] -= 1
            
            if b['omr'] <= 0:
                self.bullets.remove(b)
                continue
            
            for e in self.enemies[:]:
                tur_bilgi = DUSMAN_TURLERI[e["tur"]]
                if math.hypot(b['p'].x()-e['p'].x(), b['p'].y()-e['p'].y()) < tur_bilgi["boyut"]:
                    silah_bilgi = self.silah_bilgi()
                    
                    kritik = random.random() < (self.kritik_sans + self.sel_char.get("ozellik", {}).get("kritik", 0))
                    hasar = silah_bilgi["hasar"] * self.hasar_boost
                    
                    if kritik:
                        hasar *= 2
                        self.sparks.append(SparkEffect(e['p'], Qt.yellow))
                    
                    e['hp'] -= hasar
                    
                    self.sparks.append(SparkEffect(e['p'], tur_bilgi["renk"]))
                    
                    if self.silah == "buz_deynek":
                        e["yavas"] = True
                    elif self.silah == "ates_deynek":
                        e["yaniyor"] = 40
                    
                    if b in self.bullets:
                        self.bullets.remove(b)
                    
                    # Can emme
                    if self.sel_char.get("ozellik", {}).get("can_emme"):
                        self.p_can = min(self.max_can, self.p_can + hasar * self.sel_char["ozellik"]["can_emme"])
                    
                    if e['hp'] <= 0:
                        self.dusman_oldu(e)
            
            if not self.rect().contains(b['p'].toPoint()): 
                if b in self.bullets: 
                    self.bullets.remove(b)

        # Yanma efekti
        for e in self.enemies[:]:
            if e.get("yaniyor", 0) > 0:
                e["hp"] -= 0.04
                e["yaniyor"] -= 1
                if random.random() > 0.6:
                    self.particles.append(Particle(e["p"], QColor(255, 100, 0), 3))
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
        
        # Sandık toplama
        for s in self.sandiklar[:]:
            dist = math.hypot(self.p_pos.x()-s["p"].x(), self.p_pos.y()-s["p"].y())
            if dist < 30:
                sandik_para = random.randint(20, 100) * self.seviye
                self.para += sandik_para
                self.show_message("SANDIK! +{} Para".format(sandik_para), QColor(255, 215, 0))
                for _ in range(10):
                    self.particles.append(Particle(s["p"], QColor(255, 215, 0), 5))
                self.sandiklar.remove(s)

        # Can yenileme
        if self.p_can < self.max_can and random.random() < 0.002:
            self.p_can = min(self.max_can, self.p_can + 0.5)

        if self.p_can <= 0: 
            self.oyun_bitti()
        
        self.update()

    def spawn_dusman(self):
        side = random.choice(['T', 'B', 'L', 'R'])
        if side == 'T':
            px = random.randint(100, 1100)
            py = random.randint(50, 120)
        elif side == 'B':
            px = random.randint(100, 1100)
            py = random.randint(680, 750)
        elif side == 'L':
            px = random.randint(50, 120)
            py = random.randint(150, 650)
        else:
            px = random.randint(1080, 1150)
            py = random.randint(150, 650)
        
        if self.oda_turu == "boss":
            tur = random.choice(["bos_kral", "canavar"])
        elif self.oda_turu == "zorlu":
            tur = random.choice(["iskelet", "orc", "golem"])
        elif self.oda_turu == "sandik":
            tur = random.choice(["toplanan", "mavi_top"])
        else:
            tur = random.choices(["toplanan", "mavi_top", "kırmızı_top", "mor_top"], weights=[35, 30, 20, 15])[0]
        
        hp_carpani = 1 + (self.seviye - 1) * 0.25
        
        self.enemies.append({
            "p": QPointF(px, py), 
            "hp": DUSMAN_TURLERI[tur]["hp"] * hp_carpani,
            "max_hp": DUSMAN_TURLERI[tur]["hp"] * hp_carpani,
            "tur": tur,
            "yavas": False,
            "yaniyor": 0
        })

    def spawn_sandik(self):
        self.sandiklar.append({
            "p": QPointF(random.randint(200, 1000), random.randint(200, 600))
        })

    def dusman_oldu(self, e):
        tur_bilgi = DUSMAN_TURLERI[e["tur"]]
        
        for _ in range(20):
            self.particles.append(Particle(e["p"], tur_bilgi["renk"], random.randint(4, 10)))
        
        para_kazanci = tur_bilgi["puan"] + random.randint(5, 15)
        self.para += para_kazanci
        self.skor += tur_bilgi["puan"]
        self.kill_count += 1
        
        # Mühendis - silah düşürme şansı
        if self.sel_char.get("ozellik", {}).get("silah_dusurme") and random.random() < 0.15:
            self.spawn_powerup(e["p"])
        
        if e["tur"] in ["bos_kral", "canavar"]:
            self.para += 300 * self.seviye
            self.skor += 1000 * self.seviye
            self.show_message("BOSS ÖLDÜ! +{} Para".format(300 * self.seviye), Qt.yellow)
            self.glows.append(GlowEffect(QPointF(600, 400), Qt.yellow, 150))
            self.seviye += 1
            self.oda_temizlendi = True
            QTimer.singleShot(3000, self.oda_secimi_goster)
        
        if e in self.enemies:
            self.enemies.remove(e)
        
        self.oda_dusman_olen += 1

    def spawn_powerup(self, pos):
        tur = random.choice(list(POWER_UPLAR.keys()))
        self.powerups.append({
            "p": QPointF(pos),
            "tur": tur,
            "bilgi": POWER_UPLAR[tur]
        })

    def powerup_al(self, powerup):
        tur = powerup["tur"]
        bilgi = POWER_UPLAR[tur]
        
        if tur == "can":
            self.max_can += int(self.max_can * bilgi["deger"] / 100)
            self.p_can = min(self.max_can, self.p_can + self.max_can * 0.5)
        elif tur == "zirh":
            self.p_zirh = min(100, self.p_zirh + bilgi["deger"])
        elif tur == "hasar":
            self.hasar_boost += bilgi["deger"]
        elif tur == "hiz":
            self.hiz_boost += bilgi["deger"]
        elif tur == "kritik":
            self.kritik_sans += bilgi["deger"]
        elif tur == "ok":
            self.ok_sayisi += bilgi["deger"]
        
        self.show_message(bilgi["aciklama"], bilgi["renk"])
        self.glows.append(GlowEffect(self.p_pos, bilgi["renk"], 25))

    def oda_secimi_goster(self):
        self.state = "ODA_SECIM"

    def al_hasar(self, miktar):
        if self.p_zirh > 0:
            self.p_zirh -= miktar * 0.7
            miktar *= 0.3
            if self.p_zirh < 0:
                miktar -= self.p_zirh
                self.p_zirh = 0
        
        if miktar > 0:
            self.p_can -= miktar
        
        self.shake_amount = 8
        if random.random() > 0.4:
            self.particles.append(Particle(self.p_pos, Qt.red))
            self.sparks.append(SparkEffect(self.p_pos, Qt.red))

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
            elif self.menu_sayfa == "dukkan":
                self.dukkan_sec()
        elif self.state == "ODA_SECIM":
            self.oda_sec()
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
                self.p_zirh = 0
                self.oyun_baslat()

    def oyun_baslat(self):
        self.state = "PLAY"
        self.seviye = 1
        self.oda_numarasi = 1
        self.oda_turu = "savas"
        self.oda_dusman_sayisi = ODALAR["savas"]["dusman_sayisi"]
        self.oda_temizlendi = False
        self.odul_kazanildi = False
        self.skor = 0
        self.kill_count = 0
        self.hasar_boost = 1.0
        self.hiz_boost = 1.0
        self.kritik_sans = 0.0
        self.ok_sayisi = 1

    def oda_sec(self):
        # Sonraki odayı belirle
        if self.oda_turu == "boss":
            self.seviye += 1
        
        self.oda_numarasi += 1
        
        # Oda seçimi - Soul Knight tarzı
        if self.menu_secim == 0:
            self.oda_turu = "savas"
        elif self.menu_secim == 1:
            self.oda_turu = "zorlu"
        elif self.menu_secim == 2:
            self.oda_turu = "sandik"
        elif self.menu_secim == 3:
            self.oda_turu = "dukkan"
        elif self.menu_secim == 4:
            self.oda_turu = "istirahat"
        elif self.menu_secim == 5:
            self.oda_turu = "boss"
        
        oda_bilgi = ODALAR[self.oda_turu]
        
        if self.oda_turu == "dukkan":
            self.state = "SHOP"
            self.show_message("DÜKKAN", Qt.cyan)
        elif self.oda_turu == "istirahat":
            self.p_can = min(self.max_can, self.p_can + self.max_can * 0.5)
            self.show_message("İSTİRAAT! Can +50%", Qt.green)
            self.state = "PLAY"
            self.oda_temizlendi = False
            self.odul_kazanildi = False
            QTimer.singleShot(2000, self.oda_secimi_goster)
        else:
            self.oda_dusman_sayisi = oda_bilgi["dusman_sayisi"]
            self.oda_temizlendi = False
            self.odul_kazanildi = False
            self.state = "PLAY"
        
        self.enemies = []
        self.bullets = []
        self.powerups = []
        self.sandiklar = []
        self.p_pos = QPointF(600, 450)
        
        self.show_message("ODA {} - {}".format(self.oda_numarasi, oda_bilgi["ad"]), oda_bilgi["renk"])

    def dukkan_sec(self):
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
                    self.show_message("{} ALINDI!".format(kar['ad']), kar["renk"])

    def shop_sec(self):
        silah_keys = list(SILAHLAR.keys())
        power_keys = list(POWER_UPLAR.keys())
        
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
            self.oda_sec()

    def mouseMoveEvent(self, event): 
        self.mouse_pos = event.pos()

    def keyPressEvent(self, event):
        if self.state == "MENU":
            if event.key() == Qt.Key_Left:
                self.menu_sayfa = {"dukkan": "karakter", "karakter": "dukkan"}.get(self.menu_sayfa, "karakter")
                self.menu_secim = 0
                self.update()
            elif event.key() == Qt.Key_Right:
                self.menu_sayfa = {"karakter": "dukkan", "dukkan": "karakter"}.get(self.menu_sayfa, "dukkan")
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
        elif self.state == "ODA_SECIM":
            if event.key() == Qt.Key_Up:
                self.menu_secim = max(0, self.menu_secim - 1)
                self.update()
            elif event.key() == Qt.Key_Down:
                self.menu_secim = min(5, self.menu_secim + 1)
                self.update()
            elif event.key() == Qt.Key_Return:
                self.oda_sec()
        elif self.state == "SHOP":
            if event.key() == Qt.Key_Up:
                self.menu_secim = max(0, self.menu_secim - 1)
                self.update()
            elif event.key() == Qt.Key_Down:
                max_idx = len(SILAHLAR) + len(POWER_UPLAR)
                self.menu_secim = min(max_idx, self.menu_secim + 1)
                self.update()
            elif event.key() == Qt.Key_Return:
                self.shop_sec()
            elif event.key() == Qt.Key_Escape:
                self.state = "PLAY"
                self.oda_sec()
        elif event.key() == Qt.Key_Escape:
            if self.state == "PLAY":
                self.state = "PAUSE"
            elif self.state == "PAUSE":
                self.state = "PLAY"
        elif event.key() == Qt.Key_S:
            self.kaydet()
            self.show_message("KAYDEDİLDİ!", Qt.green)
        elif event.key() in [Qt.Key_1, Qt.Key_2, Qt.Key_3, Qt.Key_4, Qt.Key_5]:
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
                # Kılıç saldırısı
                for e in self.enemies[:]:
                    if math.hypot(e['p'].x()-self.p_pos.x(), e['p'].y()-self.p_pos.y()) < 70:
                        hasar = silah_bilgi["hasar"] * self.hasar_boost
                        e['hp'] -= hasar
                        e['p'] += QPointF(dx/dist * 30, dy/dist * 30)
                        self.sparks.append(SparkEffect(e['p'], Qt.cyan))
                        
                        if e['hp'] <= 0:
                            self.dusman_oldu(e)
                
                self.shake_amount = 4
                self.glows.append(GlowEffect(self.p_pos, Qt.cyan, 35))
                
            elif silah_bilgi["tur"] in ["ates", "buz", "elektrik", "lazer"]:
                # Ateşli silahlar
                if self.silah == "pompa":
                    for _ in range(6):
                        aci = random.uniform(-0.5, 0.5)
                        self.bullets.append({
                            "p": QPointF(self.p_pos),
                            "v": QPointF(
                                vx * math.cos(aci) - vy * math.sin(aci),
                                vx * math.sin(aci) + vy * math.cos(aci)
                            ),
                            "omr": 25
                        })
                    self.shake_amount = 6
                else:
                    self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy), "omr": 50})
                
                if silah_bilgi["tur"] in ["ates", "buz", "elektrik"]:
                    self.glows.append(GlowEffect(self.p_pos, silah_bilgi["renk"], 15))
                
            elif silah_bilgi["tur"] == "uzak":
                # Yay - çoklu ok
                for i in range(self.ok_sayisi):
                    if i == 0:
                        self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy), "omr": 60})
                    else:
                        aci = random.uniform(-0.2, 0.2)
                        self.bullets.append({
                            "p": QPointF(self.p_pos),
                            "v": QPointF(
                                vx * math.cos(aci) - vy * math.sin(aci),
                                vx * math.sin(aci) + vy * math.cos(aci)
                            ),
                            "omr": 55
                        })
                
            elif silah_bilgi["tur"] == "firlatilan":
                # Bıçak
                self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy), "omr": 35})
            
            elif silah_bilgi["tur"] in ["kutsal", "nebula", "kutsal_kilic"]:
                # Özel silahlar
                self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy), "omr": 45})
                self.glows.append(GlowEffect(self.p_pos, silah_bilgi["renk"], 20))
                
            else:
                self.bullets.append({"p": QPointF(self.p_pos), "v": QPointF(vx, vy), "omr": 50})
            
            # Elf çift ok
            if self.sel_char.get("ok") and silah_bilgi["tur"] == "uzak":
                offset = 18
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
        if self.state in ["PLAY", "SHOP", "ODA_SECIM"]:
            self.ciz_arka_plan(p)
        else:
            p.fillRect(self.rect(), QColor(15, 10, 25))

        if self.state == "MENU":
            self.ciz_menu(p)
        elif self.state == "PLAY":
            self.ciz_oyun(p)
        elif self.state == "SHOP":
            self.ciz_shop(p)
        elif self.state == "ODA_SECIM":
            self.ciz_oda_secim(p)
        elif self.state == "PAUSE":
            self.ciz_oyun(p)
            self.ciz_pause(p)
        elif self.state == "OVER":
            self.ciz_game_over(p)

    def ciz_arka_plan(self, p):
        grad = QLinearGradient(0, 0, 0, 800)
        
        if self.oda_turu == "boss":
            grad.setColorAt(0, QColor(60, 0, 0))
            grad.setColorAt(1, QColor(15, 0, 0))
        elif self.oda_turu == "dukkan":
            grad.setColorAt(0, QColor(0, 50, 0))
            grad.setColorAt(1, QColor(0, 15, 0))
        elif self.oda_turu == "istirahat":
            grad.setColorAt(0, QColor(0, 0, 60))
            grad.setColorAt(1, QColor(0, 0, 20))
        elif self.oda_turu == "sandik":
            grad.setColorAt(0, QColor(60, 50, 0))
            grad.setColorAt(1, QColor(20, 15, 0))
        else:
            grad.setColorAt(0, QColor(40, 25, 50))
            grad.setColorAt(1, QColor(15, 8, 25))
        
        p.fillRect(self.rect(), grad)
        
        # Zemin deseni
        p.setPen(QPen(QColor(255, 255, 255, 8), 1))
        for i in range(40, 1160, 40):
            p.drawLine(i, 60, i, 740)
        for i in range(80, 740, 40):
            p.drawLine(40, i, 1160, i)
        
        # Oda çerçevesi
        p.setPen(QPen(QColor(80, 60, 40), 10))
        p.setBrush(Qt.NoBrush)
        p.drawRect(25, 55, 1150, 690)

    def ciz_menu(self, p):
        p.fillRect(self.rect(), QColor(10, 5, 20))
        
        # Başlık - Soul Knight tarzı
        grad = QLinearGradient(0, 30, 0, 90)
        grad.setColorAt(0, QColor(255, 150, 50))
        grad.setColorAt(0.5, QColor(255, 50, 150))
        grad.setColorAt(1, QColor(150, 50, 255))
        
        p.setPen(Qt.white)
        p.setFont(QFont("Impact", 52))
        p.drawText(self.rect().adjusted(0, 10, 0, 0), Qt.AlignCenter, "⚔️ SOUL KNIGHT ⚔️")
        
        p.setFont(QFont("Arial", 16))
        p.setPen(QColor(255, 215, 0))
        p.drawText(QRect(0, 85, 1200, 30), Qt.AlignCenter, "💰 Para: {}".format(self.para))
        
        # Menü sekmeleri
        sekmeler = ["KARAKTER SEÇ", "DÜKKAN"]
        secili_index = {"karakter": 0, "dukkan": 1}[self.menu_sayfa]
        
        p.setFont(QFont("Arial", 14))
        for i, sekme in enumerate(sekmeler):
            x = 350 + i * 350
            if i == secili_index:
                p.setBrush(QColor(180, 60, 0))
                p.setPen(QPen(QColor(255, 150, 50), 2))
            else:
                p.setBrush(QColor(35, 20, 30))
                p.setPen(QPen(QColor(80, 40, 50), 1))
            p.drawRoundedRect(x, 125, 250, 40, 10, 10)
            p.setPen(Qt.white)
            p.drawText(QRect(x, 125, 250, 40), Qt.AlignCenter, sekme)
        
        if self.menu_sayfa == "karakter":
            self.ciz_karakter_secim(p)
        elif self.menu_sayfa == "dukkan":
            self.ciz_dukkan(p)
        
        p.setPen(QColor(150, 150, 150))
        p.setFont(QFont("Arial", 11))
        p.drawText(QRect(0, 730, 1200, 30), Qt.AlignCenter, "← → Sayfa | ↑↓ Seç | ENTER Oyna | S Kaydet | ESC Çıkış")

    def ciz_karakter_secim(self, p):
        karakterler = list(KARAKTERLER.items())
        cols = 5
        kart_genislik = 200
        kart_yukseklik = 180
        baslangic_x = (1200 - cols * kart_genislik) // 2
        baslangic_y = 180
        
        for i, (key, kar) in enumerate(karakterler):
            col = i % cols
            row = i // cols
            x = baslangic_x + col * kart_genislik
            y = baslangic_y + row * kart_yukseklik
            
            satin_alindi = key in self.acilan_karakterler
            
            if i == self.menu_secim:
                p.setBrush(QColor(180, 90, 0))
                p.setPen(QPen(QColor(255, 180, 0), 3))
                p.drawRoundedRect(x-5, y-5, kart_genislik+10, kart_yukseklik+10, 15, 15)
            else:
                p.setBrush(QColor(30, 20, 35))
                p.setPen(QPen(QColor(70, 40, 60), 1))
                p.drawRoundedRect(x, y, kart_genislik, kart_yukseklik, 10, 10)
            
            # Karakter ikonu
            p.setBrush(kar["renk"])
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(x + kart_genislik//2, y + 45), 35, 35)
            
            # Göz
            p.setBrush(kar["goz"])
            p.drawEllipse(QPoint(x + kart_genislik//2 - 12, y + 40), 6, 4)
            p.drawEllipse(QPoint(x + kart_genislik//2 + 12, y + 40), 6, 4)
            
            # İsim
            p.setPen(Qt.white if satin_alindi else QColor(100, 100, 100))
            p.setFont(QFont("Arial", 12, QFont.Bold))
            p.drawText(QRect(x, y + 85, kart_genislik, 20), Qt.AlignCenter, kar["ad"])
            
            # Özellik
            p.setPen(kar["goz"])
            p.setFont(QFont("Arial", 9))
            p.drawText(QRect(x, y + 105, kart_genislik, 15), Qt.AlignCenter, kar["ozel"])
            
            # HP
            p.setPen(QColor(255, 100, 100))
            p.setFont(QFont("Arial", 8))
            p.drawText(QRect(x, y + 122, kart_genislik, 15), Qt.AlignCenter, "❤️ {}".format(kar["baslangic_hp"]))
            
            if satin_alindi:
                p.setPen(Qt.green)
                p.setFont(QFont("Arial", 13, QFont.Bold))
                p.drawText(QRect(x, y + 150, kart_genislik, 25), Qt.AlignCenter, "SEÇ")
            else:
                p.setPen(QColor(255, 215, 0))
                p.setFont(QFont("Arial", 11))
                p.drawText(QRect(x, y + 150, kart_genislik, 25), Qt.AlignCenter, "💰 {}".format(kar['fiyat']))

    def ciz_dukkan(self, p):
        karakterler = list(KARAKTERLER.items())
        cols = 5
        kart_genislik = 200
        kart_yukseklik = 150
        baslangic_x = (1200 - cols * kart_genislik) // 2
        baslangic_y = 180
        
        p.setPen(Qt.white)
        p.setFont(QFont("Arial", 14))
        p.drawText(QRect(0, 170, 1200, 30), Qt.AlignCenter, "🛒 YENİ KARAKTER AL")
        
        for i, (key, kar) in enumerate(karakterler):
            col = i % cols
            row = i // cols
            x = baslangic_x + col * kart_genislik
            y = baslangic_y + row * kart_yukseklik
            
            satin_alindi = key in self.acilan_karakterler
            
            if i == self.menu_secim:
                p.setBrush(QColor(100, 50, 0))
                p.setPen(QPen(QColor(255, 200, 0), 2))
                p.drawRoundedRect(x-5, y-5, kart_genislik+10, kart_yukseklik+10, 12, 12)
            else:
                p.setBrush(QColor(30, 25, 25))
                p.setPen(QPen(QColor(80, 50, 30), 1))
                p.drawRoundedRect(x, y, kart_genislik, kart_yukseklik, 8, 8)
            
            p.setBrush(kar["renk"])
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(x + kart_genislik//2, y + 35), 25, 25)
            
            p.setPen(Qt.white)
            p.setFont(QFont("Arial", 11, QFont.Bold))
            p.drawText(QRect(x, y + 65, kart_genislik, 18), Qt.AlignCenter, kar["ad"])
            
            if satin_alindi:
                p.setPen(Qt.green)
                p.setFont(QFont("Arial", 10))
                p.drawText(QRect(x, y + 110, kart_genislik, 20), Qt.AlignCenter, "VAR")
            else:
                p.setPen(QColor(255, 215, 0))
                p.setFont(QFont("Arial", 11))
                p.drawText(QRect(x, y + 110, kart_genislik, 20), Qt.AlignCenter, "💰 {}".format(kar['fiyat']))

    def ciz_oda_secim(self, p):
        p.fillRect(self.rect(), QColor(10, 5, 20))
        
        p.setPen(Qt.white)
        p.setFont(QFont("Impact", 40))
        p.drawText(self.rect().adjusted(0, 30, 0, 0), Qt.AlignCenter, "🗺️ SONRAKİ ODAYI SEÇ")
        
        p.setFont(QFont("Arial", 18))
        p.setPen(QColor(255, 215, 0))
        p.drawText(QRect(0, 90, 1200, 30), Qt.AlignCenter, "💰 Para: {}".format(self.para))
        
        # Oda seçenekleri
        oda_secenekleri = [
            ("savas", "Savaş Odası", "⚔️", "Normal düşmanlar"),
            ("zorlu", "Zorlu Oda", "💀", "Güçlü düşmanlar"),
            ("sandik", "Hazine Odası", "📦", "Sandık + az düşman"),
            ("dukkan", "Dükkan", "🏪", "Silah ve güçlendirme al"),
            ("istirahat", "İstirahat", "⛺", "Can yenileme"),
            ("boss", "Boss Odası", "👹", "BOSS SAVAŞI"),
        ]
        
        p.setFont(QFont("Arial", 14))
        for i, (tur, ad, icon, desc) in enumerate(oda_secenekleri):
            y = 160 + i * 90
            
            if i == self.menu_secim:
                p.setBrush(QColor(150, 75, 0))
                p.setPen(QPen(QColor(255, 200, 0), 3))
                p.drawRoundedRect(250, y-5, 700, 80, 15, 15)
            else:
                p.setBrush(QColor(40, 25, 35))
                p.setPen(QPen(QColor(80, 50, 60), 1))
                p.drawRoundedRect(250, y, 700, 70, 10, 10)
            
            p.setPen(Qt.white if i == self.menu_secim else QColor(180, 180, 180))
            p.setFont(QFont("Arial", 16, QFont.Bold))
            p.drawText(QRect(280, y + 10, 300, 30), Qt.AlignLeft, "{} {}".format(icon, ad))
            
            p.setPen(QColor(150, 150, 150))
            p.setFont(QFont("Arial", 12))
            p.drawText(QRect(280, y + 40, 500, 20), Qt.AlignLeft, desc)
        
        p.setPen(QColor(150, 150, 150))
        p.setFont(QFont("Arial", 11))
        p.drawText(QRect(0, 730, 1200, 30), Qt.AlignCenter, "↑↓ Oda Seç | ENTER Devam Et")

    def ciz_shop(self, p):
        p.fillRect(self.rect(), QColor(15, 35, 15))
        
        p.setPen(Qt.white)
        p.setFont(QFont("Impact", 36))
        p.drawText(self.rect().adjusted(0, 20, 0, 0), Qt.AlignCenter, "🏪 DÜKKAN")
        
        p.setFont(QFont("Arial", 18))
        p.setPen(QColor(255, 215, 0))
        p.drawText(QRect(0, 70, 1200, 30), Qt.AlignCenter, "💰 Para: {}".format(self.para))
        
        silahlar = list(SILAHLAR.items())
        powerups = list(POWER_UPLAR.items())
        
        p.setFont(QFont("Arial", 14))
        p.setPen(Qt.white)
        p.drawText(QRect(0, 110, 1200, 25), Qt.AlignCenter, "🔫 SİLAHLAR")
        
        for i, (key, silah) in enumerate(silahlar):
            x = 50 + (i % 4) * 285
            y = 140 + (i // 4) * 70
            
            satin_alindi = key in self.acilan_silahlar
            
            if i == self.menu_secim:
                p.setBrush(QColor(120, 60, 0))
                p.setPen(QPen(Qt.yellow, 2))
                p.drawRoundedRect(x-5, y-5, 270, 55, 8, 8)
            else:
                p.setBrush(QColor(40, 30, 30))
                p.setPen(QPen(QColor(80, 50, 30), 1))
                p.drawRoundedRect(x, y, 270, 55, 5, 5)
            
            p.setBrush(silah["renk"])
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(x + 25, y + 27), 18, 18)
            
            p.setPen(Qt.white if satin_alindi else QColor(200, 200, 200))
            p.setFont(QFont("Arial", 11, QFont.Bold))
            p.drawText(QRect(x + 50, y + 8, 150, 18), Qt.AlignLeft, silah["ad"])
            
            if satin_alindi:
                p.setPen(Qt.green)
                p.setFont(QFont("Arial", 9))
                p.drawText(QRect(x + 50, y + 28, 150, 15), Qt.AlignLeft, "SAHİP")
            else:
                p.setPen(QColor(255, 215, 0))
                p.setFont(QFont("Arial", 10))
                p.drawText(QRect(x + 50, y + 28, 150, 15), Qt.AlignLeft, "💰 {}".format(silah['fiyat']))
        
        # Güçlendirmeler
        p.setFont(QFont("Arial", 14))
        p.setPen(Qt.white)
        p.drawText(QRect(0, 360, 1200, 25), Qt.AlignCenter, "⚡ GÜÇLENDİRMELER")
        
        for i, (key, power) in enumerate(powerups):
            x = 50 + (i % 4) * 285
            y = 390 + (i // 4) * 60
            
            if i + len(silahlar) == self.menu_secim:
                p.setBrush(QColor(0, 80, 0))
                p.setPen(QPen(Qt.green, 2)) 
                p.drawRoundedRect(x-5, y-5, 270, 50, 8, 8)
                
