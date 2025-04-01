import pygame
import numpy as np

# Ustawienia symulacji
WIDTH, HEIGHT = 100, 100
CELL_SIZE = 5
FPS = 60
TAU = 1.0

# Parametry obszaru i ściany
WALL_X = WIDTH // 4
HOLE_START = HEIGHT // 3
HOLE_END = 2 * HEIGHT // 3

# Inicjalizacja Pygame
pygame.init()
pygame.font.init()
WINDOW_WIDTH = WIDTH * CELL_SIZE * 3
WINDOW_HEIGHT = HEIGHT * CELL_SIZE
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("LBM Flow Simulation - Density | Velocity X | Velocity Y")
clock = pygame.time.Clock()

# Model D2Q9
c = np.array([
    [0, 0],  # środek
    [1, 0],  # E
    [-1, 0],  # W
    [0, 1],  # N
    [0, -1],  # S
    [1, 1],  # NE
    [-1, 1],  # NW
    [-1, -1],  # SW
    [1, -1]  # SE
])

# Przeciwne kierunki dla odbić
OPPOSITE = np.array([0, 2, 1, 4, 3, 7, 8, 5, 6])

w = np.array([4 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 36, 1 / 36, 1 / 36, 1 / 36])

# Inicjalizacja zmiennych
f_in = np.zeros((HEIGHT, WIDTH, 9))
f_out = np.zeros_like(f_in)
rho = np.ones((HEIGHT, WIDTH)) * 1.5  # Zwiększona gęstość w lewej komorze
ux = np.zeros((HEIGHT, WIDTH))
uy = np.zeros((HEIGHT, WIDTH))

# Stan otworu
hole_open = True

# Warunki początkowe - różnica gęstości
rho[:, WALL_X:] = 0.7  # Zmniejszona gęstość w prawej komorze
for i in range(9):
    f_in[:, :, i] = w[i] * rho

# Inicjalizacja maski ściany
wall_mask = np.zeros((HEIGHT, WIDTH), dtype=bool)
wall_mask[:, WALL_X] = True

def calculate_equilibrium(rho, ux, uy):
    f_eq = np.zeros((HEIGHT, WIDTH, 9))
    u_sq = ux ** 2 + uy ** 2

    for i in range(9):
        cu = c[i, 0] * ux + c[i, 1] * uy
        f_eq[:, :, i] = w[i] * rho * (1.0 + 3.0 * cu + 4.5 * cu ** 2 - 1.5 * u_sq)

    return f_eq

def apply_wall_boundary():
    global wall_mask
    # Aktualizacja maski ściany
    wall_mask[:, WALL_X] = True
    if hole_open:
        wall_mask[HOLE_START:HOLE_END + 1, WALL_X] = False

    # Odbicie dla węzłów ściany
    for i in range(9):
        if i != 0:  # Pomijamy kierunek centralny
            opp = OPPOSITE[i]
            f_in[wall_mask, i] = f_out[wall_mask, opp]

    # Zerowanie prędkości na ścianie
    ux[wall_mask] = 0
    uy[wall_mask] = 0

    # Blokowanie przepływu przez górną i dolną część bariery
    for y in range(HEIGHT):
        if y < HOLE_START or y > HOLE_END:
            if WALL_X > 0:
                rho[y, WALL_X - 1] = 1.5
                for i in range(9):
                    f_in[y, WALL_X - 1, i] = w[i] * 1.5
            if WALL_X < WIDTH - 1:
                rho[y, WALL_X + 1] = 0.7
                for i in range(9):
                    f_in[y, WALL_X + 1, i] = w[i] * 0.7

def draw():
    # Wizualizacja gęstości
    min_rho, max_rho = 0.7, 1.5
    for y in range(HEIGHT):
        for x in range(WIDTH):
            ratio = np.clip((rho[y, x] - min_rho) / (max_rho - min_rho), 0, 1)
            r = int(255 * ratio)
            b = int(255 * (1 - ratio))
            color = (r, 0, b)
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)

    # Wizualizacja prędkości poziomej (zmodyfikowana czułość)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            vel = np.clip(ux[y, x], -0.07, 0.07) / 0.07  # Dostosowany zakres prędkości
            if vel >= 0:
                color = (int(np.clip(200 * vel, 0, 200)), 0, 0)  # Zmniejszona intensywność czerwieni
            else:
                color = (0, 0, int(np.clip(-200 * vel, 0, 200)))  # Zmniejszona intensywność niebieskiego
            rect = pygame.Rect((x + WIDTH) * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)

    # Wizualizacja prędkości pionowej (zmodyfikowana czułość)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            vel = np.clip(uy[y, x], -0.07, 0.07) / 0.07  # Dostosowany zakres prędkości
            if vel >= 0:
                color = (int(np.clip(200 * vel, 0, 200)), 0, 0)  # Zmniejszona intensywność czerwieni
            else:
                color = (0, 0, int(np.clip(-200 * vel, 0, 200)))  # Zmniejszona intensywność niebieskiego
            rect = pygame.Rect((x + 2 * WIDTH) * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)

    # Rysowanie ścian
    for y in range(HEIGHT):
        if wall_mask[y, WALL_X]:
            color = (255, 255, 255)
            for offset in range(3):
                rect = pygame.Rect((WALL_X + offset * WIDTH) * CELL_SIZE,
                                   y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, color, rect)

    # Napisy
    font = pygame.font.Font(None, 36)
    labels = ["Density", "Velocity X", "Velocity Y"]
    for i, label in enumerate(labels):
        text = font.render(label, True, (255, 255, 255))
        screen.blit(text, (i * WIDTH * CELL_SIZE + 10, 10))

# Główna pętla symulacji
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                hole_open = not hole_open

    # Obliczanie wielkości makroskopowych
    rho = np.sum(f_in, axis=2)

    ux = np.zeros_like(rho)
    uy = np.zeros_like(rho)
    for i in range(9):
        ux += c[i, 0] * f_in[:, :, i]
        uy += c[i, 1] * f_in[:, :, i]
    ux = np.divide(ux, rho, where=rho != 0)
    uy = np.divide(uy, rho, where=rho != 0)

    # Obliczanie funkcji równowagowej
    f_eq = calculate_equilibrium(rho, ux, uy)

    # Kolizja
    f_out = f_in + (1.0 / TAU) * (f_eq - f_in)

    # Streaming
    for i in range(9):
        f_in[:, :, i] = np.roll(np.roll(f_out[:, :, i], c[i, 0], axis=1), c[i, 1], axis=0)

    # Aplikacja warunków brzegowych
    apply_wall_boundary()

    # Warunki brzegowe na granicach obszaru
    f_in[:, 0, [1, 5, 8]] = f_out[:, 0, [2, 7, 6]]
    f_in[:, -1, [2, 7, 6]] = f_out[:, -1, [1, 5, 8]]
    f_in[0, :, [3, 5, 6]] = f_out[0, :, [4, 8, 7]]
    f_in[-1, :, [4, 8, 7]] = f_out[-1, :, [3, 5, 6]]

    # Wizualizacja
    screen.fill((0, 0, 0))
    draw()
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()

