import pygame
import numpy as np

# Ustawienia symulacji
WIDTH, HEIGHT = 100, 100  # Wymiary siatki (kwadratowe)
CELL_SIZE = 5            # Rozmiar komórki w pikselach
FPS = 60                 # Liczba klatek na sekundę
TAU = 1.0                # Czas relaksacji

# Parametry obszaru i ściany
WALL_X = WIDTH // 4      # Pozycja pionowej ściany
HOLE_START = HEIGHT // 3 # Początek otworu w ścianie
HOLE_END = 2 * HEIGHT // 3 # Koniec otworu w ścianie

# Inicjalizacja Pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH * CELL_SIZE * 2, HEIGHT * CELL_SIZE))  # Szerokie okno
pygame.display.set_caption("LBM Diffusion")
clock = pygame.time.Clock()

# Model prędkości D2Q4
c = np.array([[1, 0], [-1, 0], [0, 1], [0, -1]])  # Kierunki [prawo, lewo, dół, góra]
w = np.array([0.25, 0.25, 0.25, 0.25])           # Współczynniki wagowe

# Inicjalizacja zmiennych
f_in = np.zeros((HEIGHT, WIDTH, 4))  # Funkcje wejściowe
f_out = np.zeros_like(f_in)          # Funkcje wyjściowe
concentration = np.zeros((HEIGHT, WIDTH))

# Warunki początkowe
concentration[:, :WALL_X-1] = 1.0  # Lewa strona pełna, prawa pusta
for i in range(4):
    f_in[:, :, i] = w[i] * concentration

# Funkcja pomocnicza do wizualizacji
def draw(concentration):
    for y in range(HEIGHT):
        for x in range(WIDTH):
            intensity = int(min(max(concentration[y, x], 0), 1.0) * 255)  # Clamp concentration
            color = (intensity, 0, 0)  # Red color
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)

    # Rysowanie ściany z otworem
    for y in range(HEIGHT):
        if y < HOLE_START or y > HOLE_END:
            rect = pygame.Rect(WALL_X * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, (0, 0, 255), rect)  # Blue wall

# Główna pętla symulacji
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Obliczanie stężenia
    concentration = np.sum(f_in, axis=2)

    # Wyznaczenie równowagi
    f_eq = np.zeros_like(f_in)
    for i in range(4):
        f_eq[:, :, i] = w[i] * concentration

    # Operacja kolizji
    f_out = f_in + (1.0 / TAU) * (f_eq - f_in)

    # Operacja streaming
    for i in range(4):
        f_in[:, :, i] = np.roll(f_out[:, :, i], shift=c[i], axis=(1, 0))

    # Warunki brzegowe (bounce-back)
    for y in range(HEIGHT):
        if y < HOLE_START or y > HOLE_END:
            f_in[y, WALL_X, 1] = f_out[y, WALL_X, 0]  # Odbicie w lewo
            f_in[y, WALL_X, 0] = f_out[y, WALL_X, 1]  # Odbicie w prawo

    # Granice obszaru
    f_in[:, 0, 0] = f_out[:, 0, 1]  # Odbicie na lewej krawędzi
    f_in[:, -1, 1] = f_out[:, -1, 0]  # Odbicie na prawej krawędzi
    f_in[0, :, 2] = f_out[0, :, 3]  # Odbicie na górnej krawędzi
    f_in[-1, :, 3] = f_out[-1, :, 2]  # Odbicie na dolnej krawędzi

    # Ustawienie nieskończonej ilości cząsteczek po lewej stronie ściany
    concentration[:, :WALL_X-1] = 1.0
    for i in range(4):
        f_in[:, :WALL_X-1, i] = w[i] * concentration[:, :WALL_X-1]

    # Wizualizacja
    screen.fill((0, 0, 0))
    draw(concentration)
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
