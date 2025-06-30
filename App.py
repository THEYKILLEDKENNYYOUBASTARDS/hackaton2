import pygame
import random
from pygame.sprite import Sprite

# Инициализация Pygame
pygame.init()

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)       # Камень (побеждает Ножницы)
GREEN = (0, 255, 0)     # Ножницы (побеждают Бумагу)
BLUE = (0, 0, 255)      # Бумага (побеждает Камень)
YELLOW = (255, 255, 0)  # Еда (может быть съедена всеми)
GRAY = (200, 200, 200)  # Сетка
ORANGE = (255, 165, 0)  # Ядерка
PURPLE = (160, 90, 180) # Нажатие кнопок

# Параметры поля
GRID_SIZE = 48
CELL_SIZE = 10
GAME_WIDTH = GRID_SIZE * CELL_SIZE
GAME_HEIGHT = GRID_SIZE * CELL_SIZE
PANEL_WIDTH = 200
WIDTH = GAME_WIDTH + PANEL_WIDTH
HEIGHT = GAME_HEIGHT
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Экосистема 'Камень-Ножницы-Бумага'")

food_chance = 0
max_food = 30

class Object(Sprite):
    def __init__(self, x, y, color):
        super().__init__()
        self.image = pygame.Surface((CELL_SIZE, CELL_SIZE))
        self.image.fill(color)
        self.rect = self.image.get_rect()
        self.rect.x = x * CELL_SIZE
        self.rect.y = y * CELL_SIZE
        self.x = x
        self.y = y
        self.color = color

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Animal(Object):
    def __init__(self, x, y, color, animal_type):
        super().__init__(x, y, color)
        self.type = animal_type  # 'rock', 'scissors', 'paper'
        self.energy = 100
        self.speed = 1
        self.target = None
        self.cooldown = 0
        self.reproduction_threshold = 150  # Порог энергии для размножения
        self.reproduction_cost = 50  # Стоимость размножения
    
    def find_path(self, targets, grid_size, occupied_cells):
        if not targets:
            return None
        
        queue = []
        queue.append(((self.x, self.y), [(self.x, self.y)]))
        visited = set()
        visited.add((self.x, self.y))
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        
        while queue:
            (x, y), path = queue.pop(0)
            
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                if (0 <= nx < grid_size and 0 <= ny < grid_size and 
                    (nx, ny) not in visited and 
                    (nx, ny) not in occupied_cells):
                    new_path = path + [(nx, ny)]
                    if (nx, ny) in targets:
                        return new_path
                    visited.add((nx, ny))
                    queue.append(((nx, ny), new_path))
        return None
    
    def move(self, path, animals):
        if path and len(path) > 1:
            steps = min(self.speed, len(path)-1)
            new_x, new_y = path[steps]
            
            # Проверяем, не занята ли клетка другим животным
            cell_occupied = any(a.x == new_x and a.y == new_y for a in animals if a != self)
            
            if not cell_occupied:
                self.x, self.y = new_x, new_y
                self.rect.x = self.x * CELL_SIZE
                self.rect.y = self.y * CELL_SIZE
                self.energy -= 1
                return path[steps:]
            else:
                # Если клетка занята, проверяем, можем ли мы атаковать
                for other in animals:
                    if other.x == new_x and other.y == new_y and other != self:
                        if self.can_attack(other):
                            if self.cooldown <= 0:
                                self.attack(other)
                                self.cooldown = 5
                            return path[steps:]
        return path
    
    def can_attack(self, other):
        return RULES[self.type] == other.type
    
    def attack(self, other):
        other.energy = 0
        self.energy += 50
    
    def try_reproduce(self, animals):
        if self.energy >= self.reproduction_threshold:
            directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
            random.shuffle(directions)
            
            for dx, dy in directions:
                new_x, new_y = self.x + dx, self.y + dy
                if (0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE and
                    not any(a.x == new_x and a.y == new_y for a in animals)):
                    
                    if self.type == 'rock':
                        new_animal = Rock(new_x, new_y)
                    elif self.type == 'scissors':
                        new_animal = Scissors(new_x, new_y)
                    else:
                        new_animal = Paper(new_x, new_y)
                    
                    animals.append(new_animal)
                    self.energy -= self.reproduction_cost
                    break

class Rock(Animal):
    def __init__(self, x, y):
        super().__init__(x, y, RED, 'rock')
        self.speed = random.randint(1, 2)

class Scissors(Animal):
    def __init__(self, x, y):
        super().__init__(x, y, GREEN, 'scissors')
        self.energy = 200  # Ножницы имеют в два раза больше энергии
        self.reproduction_threshold = 250
        self.reproduction_cost = 30

class Paper(Animal):
    def __init__(self, x, y):
        super().__init__(x, y, BLUE, 'paper')
        self.speed = random.randint(1, 2)
    
    def can_attack(self, other):
        # Бумага воспринимает всех как еду
        return True
    
    def try_reproduce(self, animals):
        # Бумага не размножается
        pass

class Food(Object):
    def __init__(self, x, y):
        super().__init__(x, y, YELLOW)

# Создание объектов
animals = []
foods = []

# Правила "Камень-Ножницы-Бумага"
RULES = {
    'rock': 'scissors',    # Камень побеждает Ножницы
    'scissors': 'paper',   # Ножницы побеждают Бумагу
    'paper': 'rock'        # Бумага побеждает Камень
}

# Генерация случайных животных
for _ in range(1):
    x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
    animals.append(Rock(x, y))

for _ in range(10):
    x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
    animals.append(Scissors(x, y))

for _ in range(8):
    x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
    animals.append(Paper(x, y))

# Генерация случайной еды (20 штук)
for _ in range(20):
    x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
    foods.append(Food(x, y))

# Кнопки для панели управления
buttons = [
    (pygame.Rect(GAME_WIDTH + 10, 245, 50, 50), RED, "Добавить камень"),
    (pygame.Rect(GAME_WIDTH + 10, 305, 50, 50), GREEN, "Добавить ножницы"),
    (pygame.Rect(GAME_WIDTH + 10, 365, 50, 50), BLUE, "Добавить бумагу"),
    (pygame.Rect(GAME_WIDTH + 10, 425, 50, 50), YELLOW, "Добавить еду"),
    (pygame.Rect(GAME_WIDTH + 10, 485, 50, 50), ORANGE, "ЯДЕРКА!")
]

# Увеличиваем высоту окна для кнопки
HEIGHT = max(HEIGHT, 550)
SCREEN = pygame.display.set_mode((WIDTH, HEIGHT))

def nuclear_blast():
    """Очищает всё поле"""
    global animals, foods
    animals = []
    foods = []

# Основной цикл
running = True
clock = pygame.time.Clock()

# Создаем кнопки для изменения вероятности появления еды
minus_button = pygame.Rect(20, 510, 30, 30)  # Кнопка "-"
plus_button = pygame.Rect(180, 510, 30, 30)  # Кнопка "+"

max_food_minus_button = pygame.Rect(305, 510, 30, 30)  # Кнопка "-"
max_food_plus_button = pygame.Rect(420, 510, 30, 30)  # Кнопка "+"

while running:
    # Получаем позицию мыши для подсветки кнопок
    mouse_pos = pygame.mouse.get_pos()
    minus_hovered = minus_button.collidepoint(mouse_pos)
    plus_hovered = plus_button.collidepoint(mouse_pos)
    max_food_minus_hovered = max_food_minus_button.collidepoint(mouse_pos)
    max_food_plus_hovered = max_food_plus_button.collidepoint(mouse_pos)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()
            
            # Проверяем нажатие кнопок управления вероятностью еды
            if minus_button.collidepoint(mouse_pos):
                food_chance = max(0, round(food_chance - 0.1, 2))  # Уменьшаем вероятность, но не ниже 0
            elif plus_button.collidepoint(mouse_pos):
                food_chance = min(1, round(food_chance + 0.1, 2))  # Увеличиваем вероятность, но не выше 1
            
            if max_food_minus_button.collidepoint(mouse_pos):
                max_food = max(0, round(max_food - 5, 2))
            elif max_food_plus_button.collidepoint(mouse_pos):
                max_food = min(100, round(max_food + 5, 2))

            # Проверяем нажатие кнопок панели управления
            for i, (rect, _, _) in enumerate(buttons):
                if rect.collidepoint(mouse_pos):
                    if i == 4:  # Ядерка
                        nuclear_blast()
                    else:
                        # Находим пустую клетку
                        occupied_cells = {(a.x, a.y) for a in animals} | {(f.x, f.y) for f in foods}
                        empty_cells = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)
                                     if (x, y) not in occupied_cells]
                        
                        if empty_cells:
                            x, y = random.choice(empty_cells)
                            if i == 0:  # Камень
                                animals.append(Rock(x, y))
                            elif i == 1:  # Ножницы
                                animals.append(Scissors(x, y))
                            elif i == 2:  # Бумага
                                animals.append(Paper(x, y))
                            elif i == 3:  # Еда
                                foods.append(Food(x, y))

    
    # Получаем список занятых клеток
    occupied_cells = {(a.x, a.y) for a in animals}
    
    # Обновление животных
    for animal in animals[:]:
        if animal.energy <= 0:
            animals.remove(animal)
            continue
        
        if animal.cooldown > 0:
            animal.cooldown -= 1
        
        # Определяем цели в зависимости от типа животного
        if isinstance(animal, Paper):
            # Для бумаги все - еда (включая других животных)
            all_targets = [(a.x, a.y) for a in animals if a != animal] + [(f.x, f.y) for f in foods]
            path = animal.find_path(all_targets, GRID_SIZE, occupied_cells)
        else:
            # Для камня и ножниц сначала ищем еду
            food_targets = [(food.x, food.y) for food in foods]
            path = animal.find_path(food_targets, GRID_SIZE, occupied_cells)
            
            if not path and animal.type != 'paper':
                # Если еды нет, ищем жертву
                prey_types = [RULES[animal.type]]
                prey_targets = [(a.x, a.y) for a in animals if a.type in prey_types and a != animal]
                path = animal.find_path(prey_targets, GRID_SIZE, occupied_cells)
        
        if path:
            new_path = animal.move(path, animals)
            if path and new_path and len(new_path) < len(path):
                target_x, target_y = path[-1]
                if animal.x == target_x and animal.y == target_y:
                    # Проверяем, съели ли мы еду
                    for food in foods[:]:
                        if animal.x == food.x and animal.y == food.y:
                            foods.remove(food)
                            animal.energy += 30
                            animal.try_reproduce(animals)
                            break
                    # Проверяем, съели ли мы другое животное (для бумаги)
                    for other in animals[:]:
                        if other.x == target_x and other.y == target_y and other != animal:
                            if animal.can_attack(other):
                                animal.attack(other)
                                animal.try_reproduce(animals)
                                break
    
    # Периодическое добавление новой еды
    if random.random() < food_chance and len(foods) < max_food:
        empty_cells = [(x, y) for x in range(GRID_SIZE) for y in range(GRID_SIZE)
                    if (x, y) not in occupied_cells and 
                    not any(f.x == x and f.y == y for f in foods)]
        if empty_cells:
            x, y = random.choice(empty_cells)
            foods.append(Food(x, y))
    
    # Отрисовка
    SCREEN.fill(WHITE)
    
    # Отрисовка игрового поля
    game_surface = pygame.Surface((GAME_WIDTH, GAME_HEIGHT))
    game_surface.fill(WHITE)
    
    # Сетка
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(game_surface, GRAY, rect, 1)
    
    # Еда
    for food in foods:
        food.draw(game_surface)
    
    # Животные
    for animal in animals:
        animal.draw(game_surface)
    
    # Отображаем игровое поле
    SCREEN.blit(game_surface, (0, 0))
    
    # Отрисовка панели управления
    pygame.draw.line(SCREEN, BLACK, (GAME_WIDTH, 0), (GAME_WIDTH, HEIGHT), 5)
    
    # Шрифты
    font = pygame.font.Font(None, 30)
    count_font = pygame.font.Font(None, 50)
    button_font = pygame.font.Font(None, 20)
    small_font = pygame.font.Font(None, 24)  # Добавлен шрифт для текста внизу
    
    # Статистика
    rock_count = sum(1 for a in animals if a.type == 'rock')
    scissors_count = sum(1 for a in animals if a.type == 'scissors')
    paper_count = sum(1 for a in animals if a.type == 'paper')
    
    # Надписи животных
    labels = [
        ("Камень:", GAME_WIDTH + 10, 10),
        ("Ножницы:", GAME_WIDTH + 10, 70),
        ("Бумага:", GAME_WIDTH + 10, 130),
        ("Еда:", GAME_WIDTH + 10, 190)
    ]
    
    for text, x, y in labels:
        surface = font.render(text, True, BLACK)
        SCREEN.blit(surface, (x, y))
    
    # Значения счетчиков
    count_positions = [
        (str(rock_count), GAME_WIDTH + 10, 35),
        (str(scissors_count), GAME_WIDTH + 10, 95),
        (str(paper_count), GAME_WIDTH + 10, 155),
        (str(len(foods)), GAME_WIDTH + 10, 215)
    ]
    
    for text, x, y in count_positions:
        surface = count_font.render(text, True, BLACK)
        SCREEN.blit(surface, (x, y))
    
    # Рисуем кнопки и их подписи
    button_labels = []
    for i, (rect, color, text) in enumerate(buttons):
        pygame.draw.rect(SCREEN, color, rect)
        label_pos = (GAME_WIDTH + 64, 250 + i * 60)
        button_labels.append((text, *label_pos))
    
    for text, x, y in button_labels:
        # Для кнопки "ЯДЕРКА!" используем меньший шрифт
        font_size = 18 if text == "ЯДЕРКА!" else 20
        button_font = pygame.font.Font(None, font_size)
        surface = button_font.render(text, True, BLACK)
        SCREEN.blit(surface, (x, y))
    
    # Добавляем текст "Вероятность появления еды" внизу игрового поля
    food_chance_text = small_font.render("Вероятность появления еды:", True, BLACK)
    SCREEN.blit(food_chance_text, (10, 490))

    # Отображаем текущее значение вероятности (с округлением до 2 знаков)
    food_chance_num = count_font.render(str(food_chance * 100) + "%", True, BLACK)
    SCREEN.blit(food_chance_num, (60, 510))

    # Рисуем кнопку "-" с подсветкой при наведении
    minus_color = PURPLE if minus_hovered else BLACK
    pygame.draw.circle(SCREEN, minus_color, (35, 525), 15)
    food_chance_minus = count_font.render("-", True, WHITE)
    SCREEN.blit(food_chance_minus, (30, 505))

    # Рисуем кнопку "+" с подсветкой при наведении
    plus_color = PURPLE if plus_hovered else BLACK
    pygame.draw.circle(SCREEN, plus_color, (180, 525), 15)
    food_chance_plus = count_font.render("+", True, WHITE)
    SCREEN.blit(food_chance_plus, (170, 505))

    # Добавляем текст "Макс. число еды" внизу игрового поля
    max_food_text = small_font.render("Макс. число еды:", True, BLACK)
    SCREEN.blit(max_food_text, (280, 490))

    # Отображаем текущее значение
    max_food_num = count_font.render(str(max_food), True, BLACK)
    SCREEN.blit(max_food_num, (330, 510))

    # Рисуем кнопку "-" с подсветкой при наведении
    max_food_minus_color = PURPLE if max_food_minus_hovered else BLACK
    pygame.draw.circle(SCREEN, max_food_minus_color, (305, 525), 15)
    food_chance_minus = count_font.render("-", True, WHITE)
    SCREEN.blit(food_chance_minus, (300, 505))

    # Рисуем кнопку "+" с подсветкой при наведении
    max_food_plus_color = PURPLE if max_food_plus_hovered else BLACK
    pygame.draw.circle(SCREEN, max_food_plus_color, (420, 525), 15)
    food_chance_plus = count_font.render("+", True, WHITE)
    SCREEN.blit(food_chance_plus, (410, 505))

    # Рисуем линию над текстом
    pygame.draw.line(SCREEN, BLACK, (0, HEIGHT - 70), (GAME_WIDTH, HEIGHT - 70), 5)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
