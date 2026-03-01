import sys, random, math, time
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

# ==================== FOOTBALL GAME ====================
class Ball:
    def __init__(self, x, y):
        self.pos = QPointF(x, y)
        self.vel = QPointF(0, 0)
        self.radius = 15
        
    def update(self, friction=0.98):
        self.pos += self.vel
        self.vel *= friction
        
        if self.pos.x() < self.radius:
            self.pos.setX(self.radius)
            self.vel.setX(-self.vel.x() * 0.8)
        if self.pos.x() > 1180 - self.radius:
            self.pos.setX(1180 - self.radius)
            self.vel.setX(-self.vel.x() * 0.8)
        if self.pos.y() < 60 + self.radius:
            self.pos.setY(60 + self.radius)
            self.vel.setY(-self.vel.y() * 0.8)
        if self.pos.y() > 780 - self.radius:
            self.pos.setY(780 - self.radius)
            self.vel.setY(-self.vel.y() * 0.8)

# ==================== FARM GAME ====================
class LandTile:
    def __init__(self, x, y, size=80):
        self.rect = QRect(x, y, size, size)
        self.state = "empty"
        self.plant_type = None
        self.growth_progress = 0
        self.watered = False

# ==================== MAIN GAME CLASS ====================
class MultiGame(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFixedSize(1200, 800)
        self.setWindowTitle("GAME CENTER - Football & Farm")
        self.setMouseTracking(True)
        
        self.current_game = None
        self.menu_select = 0
        
        # Football game state
        self.football_state = "MENU"
        self.ball = Ball(600, 400)
        self.team1_score = 0
        self.team2_score = 0
        self.time_left = 180
        self.timer_count = time.time()
        self.player = {"x": 200, "y": 400, "speed": 5}
        self.cpu_team = []
        self.my_team = []
        
        # Farm game state
        self.farm_state = "MENU"
        self.money = 100
        self.day = 1
        self.time_of_day = 0
        self.selected_tool = "hand"
        self.selected_seed = None
        self.tiles = []
        self.animals = []
        self.products = {"milk": 0, "egg": 0, "wool": 0, "vegetable": 0, "fruit": 0}
        
        # Initialize farm
        self.init_farm()
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update)
        self.timer.start(16)

    def init_farm(self):
        tile_size = 80
        for row in range(6):
            for col in range(8):
                x = 150 + col * tile_size
                y = 100 + row * tile_size
                self.tiles.append(LandTile(x, y, tile_size))
        
        self.animals = [
            {"type": "cow", "x": 900, "y": 150, "fed": 0},
            {"type": "chicken", "x": 950, "y": 250, "fed": 0},
            {"type": "sheep", "x": 900, "y": 350, "fed": 0}
        ]
        
        self.seeds = {
            "tomato": {"price": 5, "grow_time": 30, "color": QColor(255, 100, 100)},
            "cucumber": {"price": 8, "grow_time": 40, "color": QColor(100, 200, 100)},
            "corn": {"price": 10, "grow_time": 50, "color": QColor(255, 255, 100)},
            "strawberry": {"price": 15, "grow_time": 60, "color": QColor(255, 100, 150)},
            "grape": {"price": 20, "grow_time": 80, "color": QColor(150, 50, 200)},
        }
        
        self.prices = {"milk": 15, "egg": 8, "wool": 25, "vegetable": 10, "fruit": 20}
        self.animals_rect = QRect(850, 100, 300, 400)

    def update(self):
        if self.current_game == "FOOTBALL":
            self.update_football()
        elif self.current_game == "FARM":
            self.update_farm()
        QMainWindow.update(self)

    def update_football(self):
        if self.football_state != "PLAY": return
        
        if time.time() - self.timer_count >= 1:
            self.time_left -= 1
            self.timer_count = time.time()
            if self.time_left <= 0:
                self.football_state = "END"
        
        self.ball.update()
        
        # Player follow ball
        dx = self.ball.pos.x() - self.player["x"]
        dy = self.ball.pos.y() - self.player["y"]
        dist = math.hypot(dx, dy)
        if dist > 10:
            self.player["x"] += (dx / dist) * self.player["speed"]
            self.player["y"] += (dy / dist) * self.player["speed"]
        
        # CPU AI
        for p in self.cpu_team:
            dx = self.ball.pos.x() - p["x"]
            dy = self.ball.pos.y() - p["y"]
            dist = math.hypot(dx, dy)
            if dist > 5:
                p["x"] += (dx / dist) * p["speed"]
                p["y"] += (dy / dist) * p["speed"]
            p["x"] = max(50, min(1150, p["x"]))
            p["y"] = max(70, min(750, p["y"]))
        
        # Collision
        for p in [self.player] + self.my_team + self.cpu_team:
            dx = self.ball.pos.x() - p["x"]
            dy = self.ball.pos.y() - p["y"]
            dist = math.hypot(dx, dy)
            if dist < 30:
                power = 12
                if dist > 0:
                    self.ball.vel.setX((dx / dist) * power)
                    self.ball.vel.setY((dy / dist) * power)
        
        # Goals
        if self.ball.pos.x() < 30 and 300 < self.ball.pos.y() < 500:
            self.team2_score += 1
            self.goal_scored("RIGHT TEAM SCORES!")
        elif self.ball.pos.x() > 1170 and 300 < self.ball.pos.y() < 500:
            self.team1_score += 1
            self.goal_scored("LEFT TEAM SCORES!")

    def goal_scored(self, msg):
        self.football_state = "GOAL"
        self.goal_msg = msg
        QTimer.singleShot(2000, self.after_goal)

    def after_goal(self):
        self.ball.pos = QPointF(600, 400)
        self.ball.vel = QPointF(0, 0)
        self.player = {"x": 200, "y": 400, "speed": 5}
        self.football_state = "PLAY"

    def update_farm(self):
        if self.farm_state != "PLAY": return
        
        self.time_of_day += 0.5
        if self.time_of_day >= 100:
            self.time_of_day = 0
            self.day += 1
            self.animal_production()
        
        for tile in self.tiles:
            if tile.state == "planted" and tile.watered:
                tile.growth_progress += 1
                seed_info = self.seeds[tile.plant_type]
                if tile.growth_progress >= seed_info["grow_time"]:
                    tile.state = "ripe"
        
        for animal in self.animals:
            animal["fed"] = max(0, animal["fed"] - 0.1)

    def animal_production(self):
        for animal in self.animals:
            if animal["fed"] > 50:
                if animal["type"] == "cow":
                    self.products["milk"] += random.randint(1, 3)
                elif animal["type"] == "chicken":
                    self.products["egg"] += random.randint(1, 2)
                elif animal["type"] == "sheep":
                    if random.random() > 0.7:
                        self.products["wool"] += 1

    def mousePressEvent(self, event):
        pos = event.pos()
        
        if self.current_game is None:
            # Main menu
            if self.menu_select == 0:
                self.start_football()
            elif self.menu_select == 1:
                self.start_farm()
            elif self.menu_select == 2:
                self.current_game = None
        elif self.current_game == "FOOTBALL":
            self.football_mouse_press(pos)
        elif self.current_game == "FARM":
            self.farm_mouse_press(pos)

    def football_mouse_press(self, pos):
        if self.football_state == "MENU":
            if self.menu_select == 0:
                self.football_state = "PLAY"
            else:
                self.reset_football()
                self.football_state = "PLAY"
        elif self.football_state == "PLAY":
            dx = self.ball.pos.x() - self.player["x"]
            dy = self.ball.pos.y() - self.player["y"]
            dist = math.hypot(dx, dy)
            if dist < 40:
                mx = pos.x() - self.player["x"]
                my = pos.y() - self.player["y"]
                power = min(math.hypot(mx, my) / 10, 15)
                if power > 1:
                    self.ball.vel.setX(mx / math.hypot(mx, my) * power)
                    self.ball.vel.setY(my / math.hypot(mx, my) * power)
        elif self.football_state == "END":
            self.reset_football()
            self.football_state = "MENU"

    def farm_mouse_press(self, pos):
        if self.farm_state == "MENU":
            if self.menu_select == 0:
                self.farm_state = "PLAY"
            elif self.menu_select == 1:
                self.farm_state = "MARKET"
            else:
                self.reset_farm()
                self.farm_state = "PLAY"
        elif self.farm_state == "PLAY":
            # Tile click
            for tile in self.tiles:
                if tile.rect.contains(pos):
                    self.handle_tile_click(tile)
            
            # Animal click
            for animal in self.animals:
                if QRect(int(animal["x"]), int(animal["y"]), 60, 60).contains(pos):
                    if self.products["vegetable"] > 0:
                        self.products["vegetable"] -= 1
                        animal["fed"] = 100
            
            # Market button
            if QRect(1050, 700, 140, 80).contains(pos):
                self.farm_state = "MARKET"
        elif self.farm_state == "MARKET":
            y_pos = 200
            for seed_name, info in self.seeds.items():
                if QRect(100, y_pos, 200, 40).contains(pos):
                    if self.money >= info["price"]:
                        self.money -= info["price"]
                        self.selected_seed = seed_name
                        self.selected_tool = "seed"
                y_pos += 60
            
            y_pos = 200
            for product, count in self.products.items():
                if QRect(500, y_pos, 150, 40).contains(pos) and count > 0:
                    self.money += self.prices[product] * count
                    self.products[product] = 0
                y_pos += 50
            
            if QRect(50, 700, 100, 50).contains(pos):
                self.farm_state = "PLAY"

    def handle_tile_click(self, tile):
        if self.selected_tool == "hand":
            if tile.state == "ripe":
                self.products["vegetable"] += random.randint(1, 3)
                tile.state = "empty"
                tile.plant_type = None
                tile.growth_progress = 0
        elif self.selected_tool == "water":
            if tile.state == "planted":
                tile.watered = True
        elif self.selected_tool == "seed":
            if tile.state == "empty" and self.selected_seed:
                tile.state = "planted"
                tile.plant_type = self.selected_seed
                tile.watered = False
                tile.growth_progress = 0

    def start_football(self):
        self.current_game = "FOOTBALL"
        self.football_state = "MENU"
        self.reset_football()
        
    def start_farm(self):
        self.current_game = "FARM"
        self.farm_state = "MENU"
        self.menu_select = 0

    def reset_football(self):
        self.ball = Ball(600, 400)
        self.team1_score = 0
        self.team2_score = 0
        self.time_left = 180
        self.player = {"x": 200, "y": 400, "speed": 5}
        self.cpu_team = []
        self.my_team = []
        
        for i in range(4):
            self.cpu_team.append({
                "x": 800 + i * 80, 
                "y": 200 + i * 100, 
                "speed": 3 + random.random()
            })
        
        for i in range(3):
            self.my_team.append({
                "x": 300 + i * 100,
                "y": 200 + i * 150,
                "speed": 3
            })

    def reset_farm(self):
        self.money = 100
        self.day = 1
        self.time_of_day = 0
        self.products = {"milk": 0, "egg": 0, "wool": 0, "vegetable": 0, "fruit": 0}
        for tile in self.tiles:
            tile.state = "empty"
            tile.plant_type = None
            tile.growth_progress = 0
            tile.watered = False

    def keyPressEvent(self, event):
        if self.current_game is None:
            if event.key() == Qt.Key_Up:
                self.menu_select = (self.menu_select - 1) % 3
            elif event.key() == Qt.Key_Down:
                self.menu_select = (self.menu_select + 1) % 3
            elif event.key() == Qt.Key_Return:
                if self.menu_select == 0:
                    self.start_football()
                elif self.menu_select == 1:
                    self.start_farm()
        elif self.current_game == "FOOTBALL":
            if event.key() == Qt.Key_Escape:
                self.current_game = None
        elif self.current_game == "FARM":
            if event.key() == Qt.Key_1:
                self.selected_tool = "hand"
            elif event.key() == Qt.Key_2:
                self.selected_tool = "water"
            elif event.key() == Qt.Key_3:
                self.selected_tool = "seed"
            elif event.key() == Qt.Key_Escape:
                self.current_game = None

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        
        if self.current_game is None:
            self.draw_main_menu(p)
        elif self.current_game == "FOOTBALL":
            self.draw_football(p)
        elif self.current_game == "FARM":
            self.draw_farm(p)

    def draw_main_menu(self, p):
        # Gradient background
        grad = QLinearGradient(0, 0, 0, 800)
        grad.setColorAt(0, QColor(0, 100, 200))
        grad.setColorAt(0.5, QColor(50, 50, 150))
        grad.setColorAt(1, QColor(0, 100, 100))
        p.fillRect(self.rect(), grad)
        
        # Title
        p.setPen(Qt.white); p.setFont(QFont("Impact", 55))
        p.drawText(self.rect().adjusted(0, 80, 0, 0), Qt.AlignCenter, "GAME CENTER")
        
        p.setFont(QFont("Arial", 18))
        p.drawText(QRect(0, 170, 1200, 40), Qt.AlignCenter, "Choose your game!")
        
        # Game options
        games = [
            ("SOCCER", "Football Match - Score goals!", QColor(50, 200, 50)),
            ("FARMING", "Farm Simulator - Grow crops!", QColor(100, 150, 50)),
            ("BACK", "Return to game", Qt.gray)
        ]
        
        for i, (name, desc, color) in enumerate(games):
            if i == self.menu_select:
                p.setBrush(QColor(50, 50, 100)); p.setPen(QPen(color, 3))
            else:
                p.setBrush(QColor(30, 30, 60)); p.setPen(QPen(Qt.gray, 1))
            
            p.drawRoundedRect(350, 250 + i * 80, 500, 70, 15, 15)
            p.setFont(QFont("Arial", 22, QFont.Bold))
            p.setPen(color)
            p.drawText(QRect(350, 250 + i * 80, 500, 35), Qt.AlignCenter, name)
            p.setPen(Qt.gray); p.setFont(QFont("Arial", 12))
            p.drawText(QRect(350, 280 + i * 80, 500, 30), Qt.AlignCenter, desc)
        
        # Footer
        p.setPen(Qt.white); p.setFont(QFont("Arial", 14))
        p.drawText(QRect(0, 550, 1200, 30), Qt.AlignCenter, "UP/DOWN: Select | ENTER: Play | ESC: Back")

    def draw_football(self, p):
        # Back button
        if self.football_state == "MENU":
            p.fillRect(self.rect(), QColor(34, 139, 34))
            self.draw_football_menu(p)
        else:
            self.draw_football_field(p)
            if self.football_state == "PLAY":
                self.draw_football_game(p)
            elif self.football_state == "GOAL":
                self.draw_football_game(p)
                self.draw_goal_message(p)
            elif self.football_state == "END":
                self.draw_football_game(p)
                self.draw_football_end(p)

    def draw_football_field(self, p):
        p.fillRect(self.rect(), QColor(34, 139, 34))
        p.setPen(QPen(Qt.white, 3))
        p.drawRect(30, 60, 1140, 720)
        p.drawLine(600, 60, 600, 780)
        p.drawEllipse(QPoint(600, 420), 80, 80)
        p.drawRect(30, 220, 120, 360)
        p.drawRect(1050, 220, 120, 360)
        
        p.setBrush(QColor(200, 200, 200))
        p.drawRect(0, 300, 30, 200)
        p.drawRect(1170, 300, 30, 200)

    def draw_football_menu(self, p):
        p.setPen(Qt.white); p.setFont(QFont("Impact", 50))
        p.drawText(self.rect().adjusted(0, 50, 0, 0), Qt.AlignCenter, "SOCCER MATCH")
        
        p.setFont(QFont("Arial", 18))
        p.drawText(QRect(0, 150, 1200, 40), Qt.AlignCenter, "Score goals and win!")
        
        options = ["NEW MATCH", "QUICK START"]
        for i, opt in enumerate(options):
            if i == self.menu_select:
                p.setBrush(QColor(0, 150, 0)); p.setPen(QPen(Qt.white, 3))
            else:
                p.setBrush(QColor(50, 50, 50)); p.setPen(QPen(Qt.gray, 1))
            p.drawRoundedRect(450, 280 + i * 60, 300, 50, 10, 10)
            p.setFont(QFont("Arial", 18, QFont.Bold))
            p.drawText(QRect(450, 280 + i * 60, 300, 50), Qt.AlignCenter, opt)
        
        p.setPen(Qt.gray); p.setFont(QFont("Arial", 14))
        p.drawText(QRect(0, 500, 1200, 30), Qt.AlignCenter, "UP/DOWN: Select | ENTER: Start | ESC: Back")

    def draw_football_game(self, p):
        # Ball with shadow
        p.setBrush(QColor(50, 50, 50, 50))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPoint(int(self.ball.pos.x()), int(self.ball.pos.y()) + 20), 18, 8)
        
        p.setBrush(Qt.white); p.setPen(QPen(Qt.black, 2))
        p.drawEllipse(self.ball.pos, self.ball.radius, self.ball.radius)
        
        # Player
        p.setBrush(QColor(0, 100, 255)); p.setPen(QPen(Qt.white, 2))
        p.drawEllipse(QPoint(int(self.player["x"]), int(self.player["y"])), 20, 20)
        
        # Team mates
        p.setBrush(QColor(0, 100, 255))
        for pl in self.my_team:
            p.drawEllipse(QPoint(int(pl["x"]), int(pl["y"])), 18, 18)
        
        # CPU
        p.setBrush(QColor(255, 50, 50))
        for pl in self.cpu_team:
            p.drawEllipse(QPoint(int(pl["x"]), int(pl["y"])), 18, 18)
        
        # Scoreboard
        p.setBrush(QColor(0, 0, 0, 200))
        p.drawRect(0, 0, 1200, 50)
        p.setFont(QFont("Arial", 24, QFont.Bold))
        p.setPen(Qt.white)
        p.drawText(QRect(0, 5, 1200, 40), Qt.AlignCenter, 
                  f"TIME: {self.time_left // 60}:{self.time_left % 60:02d}  {self.team1_score} - {self.team2_score}")

    def draw_goal_message(self, p):
        p.fillRect(self.rect(), QColor(0, 0, 0, 100))
        p.setPen(QColor(255, 215, 0)); p.setFont(QFont("Impact", 60))
        p.drawText(self.rect(), Qt.AlignCenter, self.goal_msg)

    def draw_football_end(self, p):
        p.fillRect(self.rect(), QColor(0, 0, 0, 200))
        p.setPen(Qt.white); p.setFont(QFont("Impact", 50))
        p.drawText(self.rect().adjusted(0, -50, 0, 0), Qt.AlignCenter, "MATCH FINISHED!")
        
        if self.team1_score > self.team2_score:
            p.setPen(QColor(0, 255, 0)); p.setFont(QFont("Arial", 30))
            p.drawText(QRect(0, 100, 1200, 50), Qt.AlignCenter, "YOU WIN!")
        elif self.team2_score > self.team1_score:
            p.setPen(Qt.red); p.setFont(QFont("Arial", 30))
            p.drawText(QRect(0, 100, 1200, 50), Qt.AlignCenter, "YOU LOSE!")
        else:
            p.setPen(Qt.yellow); p.setFont(QFont("Arial", 30))
            p.drawText(QRect(0, 100, 1200, 50), Qt.AlignCenter, "DRAW!")
        
        p.setPen(Qt.white); p.setFont(QFont("Arial", 24))
        p.drawText(QRect(0, 200, 1200, 40), Qt.AlignCenter, f"RESULT: {self.team1_score} - {self.team2_score}")
        
        p.setPen(Qt.gray); p.setFont(QFont("Arial", 18))
        p.drawText(QRect(0, 300, 1200, 30), Qt.AlignCenter, "Click to continue")

    def draw_farm(self, p):
        if self.farm_state == "MENU":
            p.fillRect(self.rect(), QColor(34, 139, 34))
            self.draw_farm_menu(p)
        elif self.farm_state == "PLAY":
            self.draw_farm_game(p)
        elif self.farm_state == "MARKET":
            self.draw_farm_market(p)

    def draw_farm_menu(self, p):
        p.setPen(Qt.white); p.setFont(QFont("Impact", 50))
        p.drawText(self.rect().adjusted(0, 50, 0, 0), Qt.AlignCenter, "FARM SIMULATOR")
        
        p.setFont(QFont("Arial", 18))
        p.drawText(QRect(0, 150, 1200, 40), Qt.AlignCenter, "Grow crops, raise animals, make money!")
        
        options = ["NEW FARM", "MARKET", "CONTINUE"]
        for i, opt in enumerate(options):
            if i == self.menu_select:
                p.setBrush(QColor(0, 150, 0)); p.setPen(QPen(Qt.white, 3))
            else:
                p.setBrush(QColor(50, 50, 50)); p.setPen(QPen(Qt.gray, 1))
            p.drawRoundedRect(400, 250 + i * 70, 400, 60, 15, 15)
            p.setFont(QFont("Arial", 20, QFont.Bold))
            p.drawText(QRect(400, 250 + i * 70, 400, 60), Qt.AlignCenter, opt)
        
        p.setPen(Qt.gray); p.setFont(QFont("Arial", 14))
        p.drawText(QRect(0, 550, 1200, 30), Qt.AlignCenter, "UP/DOWN: Select | ENTER: Start | ESC: Back")

    def draw_farm_game(self, p):
        # Sky
        p.fillRect(self.rect(), QColor(135, 206, 235))
        
        # Sun
        p.setBrush(QColor(255, 255, 0))
        sun_x = 100 + self.time_of_day * 10
        p.drawEllipse(QPoint(int(sun_x), 80), 40, 40)
        
        # Farm land
        p.setBrush(QColor(101, 67, 33))
        p.drawRect(100, 80, 700, 550)
        
        # Tiles
        for tile in self.tiles:
            if tile.state == "empty":
                p.setBrush(QColor(80, 50, 30))
            elif tile.state == "planted":
                p.setBrush(QColor(60, 40, 20))
                if tile.watered:
                    growth = tile.growth_progress / self.seeds[tile.plant_type]["grow_time"]
                    plant_size = int(20 + growth * 30)
                    p.setBrush(self.seeds[tile.plant_type]["color"])
                    p.drawEllipse(QPoint(tile.rect.x() + 40, tile.rect.y() + 40), plant_size, plant_size)
            elif tile.state == "ripe":
                p.setBrush(QColor(60, 40, 20))
                p.setBrush(self.seeds[tile.plant_type]["color"])
                p.drawEllipse(QPoint(tile.rect.x() + 40, tile.rect.y() + 40), 35, 35)
            
            p.setPen(QPen(QColor(50, 30, 10), 2))
            p.drawRect(tile.rect)
            
            if tile.watered and tile.state == "planted":
                p.setBrush(QColor(0, 100, 255, 100))
                p.drawRect(tile.rect)
        
        # Animals
        p.setBrush(QColor(100, 180, 100))
        p.drawRect(self.animals_rect)
        
        for animal in self.animals:
            if animal["type"] == "cow":
                p.setBrush(Qt.white); p.setPen(Qt.black)
                p.drawEllipse(QPoint(int(animal["x"]), int(animal["y"])), 30, 25)
                p.setBrush(Qt.black)
                p.drawEllipse(QPoint(int(animal["x"]) - 10, int(animal["y"]) - 5), 8, 8)
            elif animal["type"] == "chicken":
                p.setBrush(Qt.white); p.setPen(Qt.black)
                p.drawEllipse(QPoint(int(animal["x"]), int(animal["y"])), 15, 15)
                p.setBrush(Qt.red)
                p.drawEllipse(QPoint(int(animal["x"]), int(animal["y"]) - 15), 5, 5)
            elif animal["type"] == "sheep":
                p.setBrush(Qt.white); p.setPen(Qt.black)
                p.drawEllipse(QPoint(int(animal["x"]), int(animal["y"])), 25, 20)
            
            if animal["fed"] < 30:
                p.setPen(Qt.red); p.setFont(QFont("Arial", 10))
                p.drawText(int(animal["x"]) - 20, int(animal["y"]) - 30, "Hungry!")
        
        # UI
        p.setBrush(QColor(0, 0, 0, 200))
        p.drawRect(0, 650, 1200, 150)
        
        p.setPen(QColor(255, 215, 0)); p.setFont(QFont("Arial", 24, QFont.Bold))
        p.drawText(50, 700, f"Money: ${self.money}")
        
        p.setPen(Qt.white); p.setFont(QFont("Arial", 18))
        p.drawText(50, 740, f"Day: {self.day}")
        
        # Tools
        tools = [("1", "Harvest", QColor(200, 150, 100)), ("2", "Water", QColor(0, 150, 255)), ("3", "Plant", QColor(0, 200, 100))]
        x = 400
        for key, name, color in tools:
            if (self.selected_tool == "hand" and key == "1") or (self.selected_tool == "water" and key == "2") or (self.selected_tool == "seed" and key == "3"):
                p.setBrush(QColor(100, 100, 100)); p.setPen(QPen(color, 3))
            else:
                p.setBrush(QColor(50, 50, 50)); p.setPen(QPen(Qt.gray, 1))
            p.drawRoundedRect(x, 690, 100, 50, 10, 10)
            p.setPen(color); p.setFont(QFont("Arial", 14, QFont.Bold))
            p.drawText(QRect(x, 690, 100, 50), Qt.AlignCenter, f"[{key}] {name}")
            x += 120
        
        if self.selected_seed:
            p.setPen(QColor(0, 255, 0)); p.setFont(QFont("Arial", 14))
            p.drawText(800, 705, f"Seed: {self.selected_seed.capitalize()}")
        
        p.setPen(Qt.white); p.setFont(QFont("Arial", 12))
        y = 730
        for product, count in self.products.items():
            p.drawText(800, y, f"{product.capitalize()}: {count}")
            y += 15
        
        p.setBrush(QColor(255, 200, 0)); p.setPen(Qt.black)
        p.drawRoundedRect(1050, 700, 140, 80, 15, 15)
        p.setFont(QFont("Arial", 16, QFont.Bold))
        p.drawText(QRect(1050, 700, 140, 80), Qt.AlignCenter, "MARKET")

    def draw_farm_market(self, p):
        p.fillRect(self.rect(), QColor(70, 130, 70))
        
        p.setPen(Qt.white); p.setFont(QFont("Impact", 40))
        p.drawText(self.rect().adjusted(0, 20, 0, 0), Qt.AlignCenter, "MARKET")
        
        p.setPen(QColor(255, 215, 0)); p.setFont(QFont("Arial", 24, QFont.Bold))
        p.drawText(50, 80, f"Your Money: ${self.money}")
        
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
            p.drawText(520, y + 28, f"{product.capitalize()}: {count} x ${self.prices[product]}")
            y += 50
        
        p.setBrush(QColor(200, 100, 100)); p.setPen(Qt.white)
        p.drawRoundedRect(50, 700, 100, 50, 10, 10)
        p.setFont(QFont("Arial", 14, QFont.Bold))
        p.drawText(QRect(50, 700, 100, 50), Qt.AlignCenter, "BACK")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    game = MultiGame()
    game.show()
    sys.exit(app.exec_())
