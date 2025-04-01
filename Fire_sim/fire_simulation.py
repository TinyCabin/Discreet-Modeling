import pygame
import numpy as np
from PIL import Image
import random
from collections import Counter

# Wczytaj obraz
image_path = "UTILITY\\urban.png"
image = Image.open(image_path).convert("RGB")

# Pobranie pikseli
pixels = np.array(image).reshape(-1, 3)
colors = [tuple(p) for p in pixels]

# Policz najczęstsze kolory
color_counts = Counter(colors).most_common(10)
print("Najczęstsze kolory w obrazie:", color_counts)


#Czas odradzania
MIN_REGROWTH_TIME = 200
BASE_REGROWTH_PROBABILITY = 0.001
NEIGHBOR_INFLUENCE = 0.02

# Dodajemy mapowanie bazowych szans zapalenia dla typów terenu
BURN_PROBABILITY = {
    "forest": 0.8,      # 80% szansy na zapalenie
    "grassland": 0.5,   # 50% szansy na zapalenie
    "urban": 0.1,       # 10% szansy na zapalenie
    "water": 0.0,       # Woda się nie pali
    "burning": 1.0,     # Już płonie
    "burnt": 0.0,       # Spalone
    "unknown": 0.0      # Nieznane
}

# Współczynniki wpływu wiatru na rozprzestrzenianie się ognia
WIND_MODIFIER = {
    "none": 1.0,       # Brak wiatru
    "north": (1.5, 0.8, 1.0, 1.0),  # (północ, południe, wschód, zachód)
    "south": (0.8, 1.5, 1.0, 1.0),
    "east": (1.0, 1.0, 1.5, 0.8),
    "west": (1.0, 1.0, 0.8, 1.5)
}

# Konfiguracja okna
WINDOW_SIZE = 800
GRID_SIZE = 200  # Liczba komórek w siatce (GRID_SIZE x GRID_SIZE)
CELL_SIZE = WINDOW_SIZE // GRID_SIZE

# Kolory dla różnych typów terenu
COLORS = {
    "water": (0, 0, 255),       # Niebieski (poprawiony)
    "forest": (0, 128, 0),      # Ciemnozielony
    "grassland": (0, 255, 0),   # Jasnozielony
    "urban": (128, 128, 128),   # Szary
    "burning": (255, 0, 0),     # Czerwony
    "burnt": (50, 25, 0),       # Ciemny brąz/czarny
}


BUTTON_HEIGHT = 40
BUTTON_WIDTH = 100
PANEL_HEIGHT = BUTTON_HEIGHT + 10
FONT_SIZE = 20

# Funkcja do przypisania cech terenu na podstawie koloru
def classify_terrain(pixel):
    r, g, b = pixel

    if r > 150 and g > 150 and b > 150:
        return "urban"  # Drogi i budynki
    elif r < 100 and g < 100 and b < 100:
        return "urban"  # Budynki
    elif g > 120 and r < 100:
        return "forest"  # Lasy
    elif r > 120 and g > 80 and b < 50:
        return "grassland"  # Trawa
    elif b > 150 and g < 100 and r < 100:
        return "water"  # Woda -> Nowa klasyfikacja!
    else:
        return "grassland"  # Domyślnie przypisujemy tereny zielone



# Funkcja do wczytania obrazu i konwersji na siatkę
def load_image_to_grid(image_path, grid_size):
    image = Image.open(image_path).convert("RGB")
    image = image.resize((grid_size, grid_size), Image.LANCZOS)  # Skalowanie do rozmiaru siatki
    grid = np.empty((grid_size, grid_size), dtype=object)

    for y in range(grid_size):
        for x in range(grid_size):
            pixel = image.getpixel((x, y))
            grid[y, x] = classify_terrain(pixel)

    return grid




# Funkcja do rysowania siatki w Pygame
def draw_grid(screen, grid):
    for y in range(grid.shape[0]):
        for x in range(grid.shape[1]):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            terrain = grid[y, x]
            color = COLORS.get(terrain, (255, 0, 255))  # Różowy dla nieznanych kategorii
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (50, 50, 50), rect, 1)  # Linie siatki


def regrow_greenery(grid, time_since_burn):
    new_grid = grid.copy()
    for y in range(grid.shape[0]):
        for x in range(grid.shape[1]):
            # Regeneracja tylko dla spalonych komórek
            if grid[y, x] == "burnt" and time_since_burn[y, x] >= MIN_REGROWTH_TIME:
                neighbors = [
                    (y - 1, x),  # Północ
                    (y + 1, x),  # Południe
                    (y, x + 1),  # Wschód
                    (y, x - 1),  # Zachód
                ]
                green_neighbors = sum(
                    1 for ny, nx in neighbors
                    if 0 <= ny < grid.shape[0] and 0 <= nx < grid.shape[1] and grid[ny, nx] in ["forest", "grassland"]
                )

                # Zwiększ szansę odrastania dla testów
                regrowth_prob = BASE_REGROWTH_PROBABILITY + green_neighbors * NEIGHBOR_INFLUENCE
                if random.random() < regrowth_prob:
                    new_grid[y, x] = "grassland"  # Odradza się jako las

    return new_grid

# Funkcja do aktualizacji stanu automatu z uwzględnieniem wiatru i prawdopodobieństwa
def update_fire(grid, time_since_burn, wind="none"):
    # Jeżeli wiatr jest 'none', przypisujemy domyślne wartości dla wiatru
    if wind == "none":
        wind_factors = (1.0, 1.0, 1.0, 1.0)  # Brak wiatru, wszystkie kierunki mają współczynnik 1.0
    else:
        wind_factors = WIND_MODIFIER.get(wind, (1.0, 1.0, 1.0, 1.0))  # Domyślnie brak wiatru

    new_grid = grid.copy()
    new_time_since_burn = time_since_burn.copy()

    for y in range(grid.shape[0]):
        for x in range(grid.shape[1]):
            cell = grid[y, x]

            # Jeśli komórka płonie
            if cell == "burning":
                new_grid[y, x] = "burnt"
                new_time_since_burn[y, x] = 0  # Ustaw czas od spalenia

                # Rozprzestrzenianie ognia na sąsiadów
                neighbors = [
                    (y - 1, x, wind_factors[0]),  # Północ
                    (y + 1, x, wind_factors[1]),  # Południe
                    (y, x + 1, wind_factors[2]),  # Wschód
                    (y, x - 1, wind_factors[3])  # Zachód
                ]
                for ny, nx, wind_factor in neighbors:
                    if 0 <= ny < grid.shape[0] and 0 <= nx < grid.shape[1]:
                        neighbor_cell = grid[ny, nx]
                        if neighbor_cell in ["forest", "grassland"]:
                            base_prob = BURN_PROBABILITY[neighbor_cell]
                            adjusted_prob = base_prob * wind_factor
                            if random.random() < adjusted_prob:
                                new_grid[ny, nx] = "burning"

            # Aktualizacja czasu od spalenia dla spalonych komórek
            elif cell == "burnt":
                new_time_since_burn[y, x] += 1

    # Dodaj odradzanie terenów zielonych
    new_grid = regrow_greenery(new_grid, new_time_since_burn)
    return new_grid, new_time_since_burn

def extinguish_fire(grid, start, end):
    """Gasi pożar na trasie między `start` a `end` (symulacja helikoptera)."""
    start_x, start_y = start
    end_x, end_y = end
    # Używamy interpolacji liniowej do narysowania linii
    steps = max(abs(end_x - start_x), abs(end_y - start_y))
    for step in range(steps + 1):
        x = int(start_x + (end_x - start_x) * step / steps)
        y = int(start_y + (end_y - start_y) * step / steps)
        if 0 <= y < grid.shape[0] and 0 <= x < grid.shape[1]:
            grid[y, x] = "water"  # Gasi pożar

def draw_buttons(screen, wind_direction):
    """Rysowanie panelu z przyciskami"""
    font = pygame.font.Font(None, FONT_SIZE)
    panel_rect = pygame.Rect(0, WINDOW_SIZE, WINDOW_SIZE, PANEL_HEIGHT)
    pygame.draw.rect(screen, (200, 200, 200), panel_rect)

    # Przycisk do zmiany kierunku wiatru
    directions = ["North", "South", "East", "West"]
    for i, direction in enumerate(directions):
        btn_rect = pygame.Rect(i * BUTTON_WIDTH, WINDOW_SIZE, BUTTON_WIDTH, BUTTON_HEIGHT)
        color = (100, 200, 100) if wind_direction.lower() == direction.lower() else (200, 100, 100)
        pygame.draw.rect(screen, color, btn_rect)
        text = font.render(direction, True, (0, 0, 0))
        text_rect = text.get_rect(center=btn_rect.center)
        screen.blit(text, text_rect)

    # Wyświetlenie aktualnego kierunku wiatru
    wind_text = f"Current Wind: {wind_direction}"
    wind_label = font.render(wind_text, True, (0, 0, 0))
    screen.blit(wind_label, (WINDOW_SIZE - 200, WINDOW_SIZE + 5))

def check_button_click(pos, wind):
    """Sprawdzanie, czy kliknięto przycisk zmiany wiatru"""
    directions = ["north", "south", "east", "west"]
    for i, direction in enumerate(directions):
        btn_rect = pygame.Rect(i * BUTTON_WIDTH, WINDOW_SIZE, BUTTON_WIDTH, BUTTON_HEIGHT)
        if btn_rect.collidepoint(pos):
            return direction
    return wind  # Jeśli nie kliknięto przycisku, zwracamy obecny wiatr

# Główna funkcja symulacji z uwzględnieniem zasad
def run_simulation(image_path):
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE + PANEL_HEIGHT))
    pygame.display.set_caption("Symulacja Pożaru Lasu z GUI")
    clock = pygame.time.Clock()

    # Wczytanie siatki z obrazu
    grid = load_image_to_grid(image_path, GRID_SIZE)
    time_since_burn = np.zeros_like(grid, dtype=int)  # Śledzenie czasu od spalenia

    wind = "none"  # Wiatr domyślnie brak
    extinguishing = False
    extinguish_start = None

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # Kliknięcie myszą - dodaj ogień
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
                if mouse_y < WINDOW_SIZE:  # W obszarze siatki
                    if pygame.key.get_pressed()[pygame.K_LSHIFT]:  # Gaszenie
                        extinguishing = True
                        extinguish_start = (grid_x, grid_y)
                    else:  # Podpalanie
                        if grid[grid_y, grid_x] in ["forest", "grassland"]:
                            grid[grid_y, grid_x] = "burning"
                else:  # Kliknięcie w panelu
                    wind = check_button_click((mouse_x, mouse_y), wind)

            # Zwolnienie przycisku myszy
            if event.type == pygame.MOUSEBUTTONUP and extinguishing:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x, grid_y = mouse_x // CELL_SIZE, mouse_y // CELL_SIZE
                if extinguish_start:
                    extinguish_fire(grid, extinguish_start, (grid_x, grid_y))
                extinguishing = False
                extinguish_start = None

        # Aktualizacja automatu
        grid, time_since_burn = update_fire(grid, time_since_burn, wind)

        # Rysowanie siatki i panelu
        screen.fill((0, 0, 0))  # Tło
        draw_grid(screen, grid)
        draw_buttons(screen, wind)
        pygame.display.flip()
        clock.tick(30)  # 30 klatek na sekundę

    pygame.quit()

# Uruchomienie symulacji z pliku obrazu
run_simulation("UTILITY\\urban.png")

