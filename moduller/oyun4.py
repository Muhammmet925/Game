import sys, random, math, time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# --- FARMING GAME ---
class LandTile:
    """Farm land tile"""
    def __init__(self, x, y, size=80):
        self.rect = QRect(x, y, size, size)
        self.state = "bos"  # bos, dikili, olgun, hasat
        self.plant_type = None
        self.plant_time = 0
        self.watered = False
        self.growth_progress = 0

class FarmingGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1200, 800)
        self.setWindowTitle("FARM SIMULATOR")
        self.setMouseTracking(True)
        
        self.init_game()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_game)
        self.timer.start(50)

    def init_game(self):
        self.state = "MENU"
        self.money = 100
        self.day = 1
        self.time_of_day = 0  # 0-100
        self.selected_tool = "el"
        self.selected_seed = None
        self.menu_select = 0
        
        # Land tiles
        self.tiles = []
        tile_size = 80
        for row in range(6):
            for col in range(8):
                x = 150 + col * tile_size
                y = 100 + row * tile_size
                self.tiles.append(LandTile(x, y, tile_size))
        
        # Animals
        self.animals = []
        self.animals.append({"type": "inek", "x": 900, "y": 150, "fed": 0})
        self.animals.append({"type": "tavuk", "x": 950, "y": 250, "fed": 0})
        self.animals.append({"type": "koyun", "x": 900, "y": 350, "fed": 0})
        
        # Products
        self.products = {"sut": 0, "yumurta": 0, "yün": 0, "sebze": 0, "meyve": 0}
        
        # Animals area
        self.animals_rect = QRect(850, 100, 300, 400)
        
        # Market prices
        self.prices = {
            "sut": 15,
            "yumurta": 8,
            "yün": 25,
            "sebze": 10,
            "meyve": 20
        }
        
        # Seeds
        self.seeds = {
            "domates": {"price": 5, "grow_time": 30, "sell": 15, "color": QColor(255, 100, 100)},
            "salatalik": {"price": 8, "grow_time": 40, "sell": 20, "color": QColor(100, 200, 100)},
            "misir": {"price": 10, "grow_time": 50, "sell": 30, "color": QColor(255, 255, 100)},
            "cilek": {"price": 15, "grow_time": 60, "sell": 45, "color": QColor(255, 100, 150)},
            "uzum": {"price": 20, "grow_time": 80, "sell": 60, "color": QColor(150, 50, 200)},
        }

    def update_game(self):
        if self.state == "PLAY":
            # Time passes
            self.time_of_day += 0.5
            if self.time_of_day >= 100:
                self.time_of_day = 0
                self.day += 1
                self.animal_production()
            
            # Plant growth
            for tile in self.tiles:
                if tile.state == "dikili" and tile.watered:
                    tile.growth_progress += 1
                    seed_info = self.seeds[tile.plant_type]
                    if tile.growth_progress >= seed_info["grow_time"]:
                        tile.state = "olgun"
            
            # Animal mood
            for animal in self.animals:
                animal["fed"] = max(0, animal["fed"] - 0.1)
        
        self.update()

    def animal_production(self):
        """Animals produce when fed"""
        for animal in self.animals:
            if animal["fed"] > 50:
                if animal["type"] == "inek":
                    self.products["sut"] += random.randint(1, 3)
                elif animal["type"] == "tavuk":
                    self.products["yumurta"] += random.randint(1, 2)
                elif animal["type"] == "koyun":
                    if random.random() > 0.7:
                        self.products["yün"] += 1

    def get_tile_at(self, pos):
        for tile in self.tiles:
            if tile.rect.contains(pos):
                return tile
        return None

    def get_animal_at(self, pos):
        for animal in self.animals:
            animal_rect = QRect(int(animal["x"]), int(animal["y"]), 60, 60)
            if animal_rect.contains(pos):
                return animal
        return None

    def mousePressEvent(self, event):
        pos = event.pos()
        
        if self.state == "MENU":
            if self.menu_select == 0:
                self.state = "PLAY"
            elif self.menu_select == 1:
                self.state = "MARKET"
            elif self.menu_select == 2:
                self.init_game()
                self.state = "PLAY"
        elif self.state == "PLAY":
            # Check if clicked on a tile
            tile = self.get_tile_at(pos)
            if tile:
                self.handle_tile_click(tile)
            
            # Check if clicked on animal
            animal = self.get_animal_at(pos)
            if animal:
                self.handle_animal_click(animal)
            
            # Market button
            if QRect(1050, 700, 140, 80).contains(pos):
                self.state = "MARKET"
        elif self.state == "MARKET":
            # Buy seeds
            y_pos = 200
            for seed_name, info in self.seeds.items():
                if QRect(100, y_pos, 200, 40).contains(pos):
                    if self.money >= info["price"]:
                        self.money -= info["price"]
                        self.selected_seed = seed_name
                        self.selected_tool = "tohum"
                y_pos += 60
            
            # Sell products
            y_pos = 200
            for product, count in self.products.items():
                if QRect(500, y_pos, 150, 40).contains(pos) and count > 0:
                    self.money += self.prices[product] * count
                    self.products[product] = 0
                y_pos += 50
            
            # Back button
            if QRect(50, 700, 100, 50).contains(pos):
                self.state = "PLAY"

    def handle_tile_click(self, tile):
        if self.selected_tool == "el":
            # Harvest
            if tile.state == "olgun":
                seed_info = self.seeds[tile.plant_type]
                self.products["sebze"] += random.randint(1, 3)
                tile.state = "bos"
                tile.plant_type = None
                tile.growth_progress = 0
        elif self.selected_tool == "sucu":
            # Water
            if tile.state == "dikili":
                tile.watered = True
        elif self.selected_tool == "tohum":
            # Plant
            if tile.state == "bos" and self.selected_seed:
                tile.state = "dikili"
                tile.plant_type = self.selected_seed
                tile.watered = False
                tile.growth_progress = 0

    def handle_animal_click(self, animal):
        # Feed animal
        if self.products["sebze"] > 0:
            self.products["sebze"] -= 1
            animal["fed"] = 100

    def keyPressEvent(self, event):
        if self.state == "MENU":
            if event.key() == Qt.Key_Up:
                self.menu_select = (self.menu_select - 1) % 3
            elif event.key() == Qt.Key_Down:
                self.menu_select = (self.menu_select + 1) % 3
            elif event.key() == Qt.Key_Return:
                if self.menu_select == 0:
                    self.state = "PLAY"
                elif self.menu_select == 1:
                    self.state = "MARKET"
                elif self.menu_select == 2:
                    self.init_game()
                    self.state = "PLAY"
        elif self.state == "PLAY":
            if event.key() == Qt.Key_1:
                self.selected_tool = "el"
                self.selected_seed = None
            elif event.key() == Qt.Key_2:
                self.selected_tool = "sucu"
            elif event.key() == Qt.Key_3:
                self.selected_tool = "tohum"
            elif event.key() == Qt.Key_Escape:
                self.state = "MENU"
        elif self.state == "MARKET":
            if event.key() == Qt.Key_Escape:
                self.state = "PLAY"

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        if self.state == "MENU":
            self.draw_menu(p)
        elif self.state == "PLAY":
            self.draw_game(p)
        elif self.state == "MARKET":
            self.draw_market(p)

    def draw_menu(self, p):
        # Background
        p.fillRect(self.rect(), QColor(34, 139, 34))
        
        # Title
        p.setPen(Qt.white); p.setFont(QFont("Impact", 50))
        p.drawText(self.rect().adjusted(0, 50, 0, 0), Qt.AlignCenter, "FARM SIMULATOR")
        
        p.setFont(QFont("Arial", 18))
        p.drawText(QRect(0, 150, 1200, 40), Qt.AlignCenter, "Grow crops, raise animals, make money!")
        
        # Menu options
        options = ["NEW FARM", "MARKET", "CONTINUE"]
        
        for i, opt in enumerate(options):
            if i == self.menu_select:
                p.setBrush(QColor(0, 150, 0)); p.setPen(QPen(Qt.white, 3))
            else:
                p.setBrush(QColor(50, 50, 50)); p.setPen(QPen(Qt.gray, 1))
            
            p.drawRoundedRect(400, 250 + i * 70, 400, 60, 15, 15)
            p.setFont(QFont("Arial", 20, QFont.Bold))
            p.drawText(QRect(400, 250 + i * 70, 400, 60), Qt.AlignCenter, opt)
        
        # Controls
        p.setPen(Qt.gray); p.setFont(QFont("Arial", 14))
        p.drawText(QRect(0, 550, 1200, 30), Qt.AlignCenter, "UP/DOWN: Select | ENTER: Start")

    def draw_game(self, p):
        # Sky
        p.fillRect(self.rect(), QColor(135, 206, 235))
        
        # Sun
        p.setBrush(QColor(255, 255, 0))
        p.setPen(Qt.NoPen)
        sun_x = 100 + self.time_of_day * 10
        p.drawEllipse(QPoint(int(sun_x), 80), 40, 40)
        
        # Farm background
        p.setBrush(QColor(101, 67, 33))
        p.drawRect(100, 80, 700, 550)
        
        # Land tiles
        for tile in self.tiles:
            # Soil
            if tile.state == "bos":
                p.setBrush(QColor(80, 50, 30))
            elif tile.state == "dikili":
                p.setBrush(QColor(60, 40, 20))
                # Growing plant
                if tile.watered:
                    growth = tile.growth_progress / self.seeds[tile.plant_type]["grow_time"]
                    plant_size = int(20 + growth * 30)
                    p.setBrush(self.seeds[tile.plant_type]["color"])
                    p.drawEllipse(QPoint(tile.rect.x() + 40, tile.rect.y() + 40), plant_size, plant_size)
            elif tile.state == "olgun":
                p.setBrush(QColor(60, 40, 20))
                p.setBrush(self.seeds[tile.plant_type]["color"])
                p.drawEllipse(QPoint(tile.rect.x() + 40, tile.rect.y() + 40), 35, 35)
            
            p.setPen(QPen(QColor(50, 30, 10), 2))
            p.drawRect(tile.rect)
            
            # Water indicator
            if tile.watered and tile.state == "dikili":
                p.setBrush(QColor(0, 100, 255, 100))
                p.drawRect(tile.rect)
        
        # Animals area
        p.setBrush(QColor(100, 180, 100))
        p.drawRect(self.animals_rect)
        
        for animal in self.animals:
            if animal["type"] == "inek":
                p.setBrush(Qt.white)
                p.setPen(Qt.black)
                p.drawEllipse(QPoint(int(animal["x"]), int(animal["y"])), 30, 25)
                # Spots
                p.setBrush(Qt.black)
                p.drawEllipse(QPoint(int(animal["x"]) - 10, int(animal["y"]) - 5), 8, 8)
            elif animal["type"] == "tavuk":
                p.setBrush(Qt.white)
                p.setPen(Qt.black)
                p.drawEllipse(QPoint(int(animal["x"]), int(animal["y"])), 15, 15)
                p.setBrush(Qt.red)
                p.drawEllipse(QPoint(int(animal["x"]), int(animal["y"]) - 15), 5, 5)
            elif animal["type"] == "koyun":
                p.setBrush(Qt.white)
                p.setPen(Qt.black)
                p.drawEllipse(QPoint(int(animal["x"]), int(animal["y"])), 25, 20)
            
            # Fed indicator
            if animal["fed"] < 30:
                p.setPen(Qt.red)
                p.setFont(QFont("Arial", 10))
                p.drawText(int(animal["x"]) - 20, int(animal["y"]) - 30, "Hungry!")
        
        # UI Panel
        p.setBrush(QColor(0, 0, 0, 200))
        p.drawRect(0, 650, 1200, 150)
        
        # Money
        p.setPen(QColor(255, 215, 0)); p.setFont(QFont("Arial", 24, QFont.Bold))
        p.drawText(50, 700, f"Money: ${self.money}")
        
        # Day/Time
        p.setPen(Qt.white); p.setFont(QFont("Arial", 18))
        p.drawText(50, 740, f"Day: {self.day}")
        
        # Tools
        tools = [
            ("1", "Harvest", QColor(200, 150, 100)),
            ("2", "Water", QColor(0, 150, 255)),
            ("3", "Plant", QColor(0, 200, 100))
        ]
        
        x = 400
        for key, name, color in tools:
            if self.selected_tool == "el" and key == "1" or self.selected_tool == "sucu" and key == "2" or self.selected_tool == "tohum" and key == "3":
                p.setBrush(QColor(100, 100, 100)); p.setPen(QPen(color, 3))
            else:
                p.setBrush(QColor(50, 50, 50)); p.setPen(QPen(Qt.gray, 1))
            p.drawRoundedRect(x, 690, 100, 50, 10, 10)
            p.setPen(color); p.setFont(QFont("Arial", 14, QFont.Bold))
            p.drawText(QRect(x, 690, 100, 50), Qt.AlignCenter, f"[{key}] {name}")
            x += 120
        
        # Selected seed
        if self.selected_seed:
            p.setPen(QColor(0, 255, 0)); p.setFont(QFont("Arial", 14))
            p.drawText(800, 705, f"Seed: {self.selected_seed.capitalize()}")
        
        # Products
        p.setPen(Qt.white); p.setFont(QFont("Arial", 12))
        y = 730
        for product, count in self.products.items():
            p.drawText(800, y, f"{product.capitalize()}: {count}")
            y += 15
        
        # Market button
        p.setBrush(QColor(255, 200, 0)); p.setPen(Qt.black)
        p.drawRoundedRect(1050, 700, 140, 80, 15, 15)
        p.setFont(QFont("Arial", 16, QFont.Bold))
        p.drawText(QRect(1050, 700, 140, 80), Qt.AlignCenter, "MARKET")

    def draw_market(self, p):
        p.fillRect(self.rect(), QColor(70, 130, 70))
        
        # Title
        p.setPen(Qt.white); p.setFont(QFont("Impact", 40))
        p.drawText(self.rect().adjusted(0, 20, 0, 0), Qt.AlignCenter, "MARKET")
        
        # Money display
        p.setPen(QColor(255, 215, 0)); p.setFont(QFont("Arial", 24, QFont.Bold))
        p.drawText(50, 80, f"Your Money: ${self.money}")
        
        # Seeds section
        p.setPen(Qt.white); p.setFont(QFont("Arial", 20, QFont.Bold))
        p.drawText(100, 150, "BUY SEEDS:")
        
        y = 200
        for seed_name, info in self.seeds.items():
            p.setBrush(QColor(50, 50, 50)); p.setPen(Qt.white)
            p.drawRoundedRect(100, y, 250, 40, 10, 10)
            p.setBrush(info["color"]); p.setPen(Qt.NoPen)
            p.drawEllipse(QPoint(130, y + 20), 15, 15)
            p.setPen(Qt.white); p.setFont(QFont("Arial", 14))
            p.drawText(160, y + 28, f"{seed_name.capitalize()} - ${info['price']}")
            y += 60
        
        # Products section
        p.setPen(Qt.white); p.setFont(QFont("Arial", 20, QFont.Bold))
        p.drawText(500, 150, "SELL PRODUCTS:")
        
        y = 200
        for product, count in self.products.items():
            if count > 0:
                p.setBrush(QColor(50, 150, 50)); p.setPen(Qt.white)
            else:
                p.setBrush(QColor(50, 50, 50)); p.setPen(Qt.gray)
            p.drawRoundedRect(500, y, 300, 40, 10, 10)
            p.setFont(QFont("Arial", 14))
            p.drawText(520, y + 28, f"{product.capitalize()}: {count} x ${self.prices[product]} = ${count * self.prices[product]}")
            y += 50
        
        # Back button
        p.setBrush(QColor(200, 100, 100)); p.setPen(Qt.white)
        p.drawRoundedRect(50, 700, 100, 50, 10, 10)
        p.setFont(QFont("Arial", 14, QFont.Bold))
        p.drawText(QRect(50, 700, 100, 50), Qt.AlignCenter, "BACK")
        
        # Instructions
        p.setPen(Qt.gray); p.setFont(QFont("Arial", 12))
        p.drawText(QRect(0, 760, 1200, 30), Qt.AlignCenter, "Click on seeds to buy | Click on products to sell | ESC to go back")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = FarmingGame()
    game.show()
    sys.exit(app.exec_())
