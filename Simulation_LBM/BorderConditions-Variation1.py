import pygame
import numpy as np

# Simulation settings
WIDTH, HEIGHT = 128, 128
CELL_SIZE = 5
FPS = 60
TAU = 1.0
SAVE_INTERVAL = 100  # Co ile iteracji zapisywać wyniki
STEADY_STATE_THRESHOLD = 1e-6  # Próg zbieżności dla stanu stacjonarnego

# Initialize Pygame
WINDOW_WIDTH = WIDTH * CELL_SIZE * 2 + 100  # Additional space for color bar
WINDOW_HEIGHT = HEIGHT * CELL_SIZE
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("LBM Flow Simulation - Variant 1 | Variant 2")
clock = pygame.time.Clock()

# D2Q9 Model
c = np.array([
    [0, 0],  # center
    [1, 0],  # E
    [-1, 0],  # W
    [0, 1],  # N
    [0, -1],  # S
    [1, 1],  # NE
    [-1, 1],  # NW
    [-1, -1],  # SW
    [1, -1]  # SE
])

# Opposite directions for reflections
OPPOSITE = np.array([0, 2, 1, 4, 3, 7, 8, 5, 6])
w = np.array([4 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 9, 1 / 36, 1 / 36, 1 / 36, 1 / 36])

def check_steady_state(ux_old, ux_new, threshold=STEADY_STATE_THRESHOLD):

    return np.max(np.abs(ux_new - ux_old)) < threshold

def initialize_simulation():
    f_in = np.zeros((HEIGHT, WIDTH, 9))
    f_out = np.zeros_like(f_in)
    rho = np.ones((HEIGHT, WIDTH))
    ux = np.zeros((HEIGHT, WIDTH))
    uy = np.zeros((HEIGHT, WIDTH))

    # Initial conditions
    for i in range(9):
        f_in[:, :, i] = w[i] * rho

    return f_in, f_out, rho, ux, uy


def calculate_equilibrium(rho, ux, uy):
    f_eq = np.zeros((HEIGHT, WIDTH, 9))
    u_sq = ux ** 2 + uy ** 2
    for i in range(9):
        cu = c[i, 0] * ux + c[i, 1] * uy
        f_eq[:, :, i] = w[i] * rho * (1.0 + 3.0 * cu + 4.5 * cu ** 2 - 1.5 * u_sq)
    return f_eq


def apply_boundary_conditions_variant1(f_in, f_out):
    # Top boundary: ux = 0.02, uy = 0
    f_in[0, :, 3] = f_in[0, :, 4]  # N = S
    f_in[0, :, 5] = f_in[0, :, 7]  # NE = SW
    f_in[0, :, 6] = f_in[0, :, 8]  # NW = SE
    rho_top = f_in[0, :, 0] + f_in[0, :, 1] + f_in[0, :, 2] + 2 * f_in[0, :, 4] + 2 * f_in[0, :, 7] + 2 * f_in[0, :, 8]
    f_in[0, :, 3] += 2/3 * 0.02 * rho_top
    f_in[0, :, 5] += 1/6 * 0.02 * rho_top
    f_in[0, :, 6] += 1/6 * 0.02 * rho_top

    # Bottom boundary: ux = 0, uy = 0 (bounce-back)
    f_in[-1, :, 4] = f_out[-1, :, 3]
    f_in[-1, :, 7] = f_out[-1, :, 5]
    f_in[-1, :, 8] = f_out[-1, :, 6]

    # Linear velocity on sides (corrected to decrease from top to bottom)
    for y in range(HEIGHT):
        vel = 0.02 * (1 - y / HEIGHT)  # Zmienione na malejącą prędkość
        # Left boundary
        rho_left = f_in[y, 0, 0] + f_in[y, 0, 3] + f_in[y, 0, 4] + 2 * (f_in[y, 0, 2] + f_in[y, 0, 6] + f_in[y, 0, 7])
        f_in[y, 0, 1] = f_in[y, 0, 2] + 2/3 * vel * rho_left
        f_in[y, 0, 5] = f_in[y, 0, 7] + 1/6 * vel * rho_left
        f_in[y, 0, 8] = f_in[y, 0, 6] + 1/6 * vel * rho_left

        # Right boundary (similar but mirrored)
        rho_right = f_in[y, -1, 0] + f_in[y, -1, 3] + f_in[y, -1, 4] + 2 * (f_in[y, -1, 1] + f_in[y, -1, 5] + f_in[y, -1, 8])
        f_in[y, -1, 2] = f_in[y, -1, 1] + 2/3 * vel * rho_right
        f_in[y, -1, 6] = f_in[y, -1, 8] + 1/6 * vel * rho_right
        f_in[y, -1, 7] = f_in[y, -1, 5] + 1/6 * vel * rho_right


def apply_boundary_conditions_variant2(f_in, f_out):
    # Right boundary (open with rho = 1.0)
    rho_right = np.ones(HEIGHT)
    for y in range(HEIGHT):
        f_sum = f_in[y, -1, 0] + f_in[y, -1, 3] + f_in[y, -1, 4] + 2 * (f_in[y, -1, 1] + f_in[y, -1, 5] + f_in[y, -1, 8])
        ux = 1.0 - f_sum / rho_right[y]
        uy = 0.0
        f_in[y, -1, 2] = f_in[y, -1, 1] + 2/3 * ux * rho_right[y]
        f_in[y, -1, 6] = f_in[y, -1, 8] + 1/6 * ux * rho_right[y]
        f_in[y, -1, 7] = f_in[y, -1, 5] + 1/6 * ux * rho_right[y]

    # Left boundary (velocity boundary with linear profile)
    for y in range(HEIGHT):
        ux = 0.02 * y / HEIGHT
        uy = 0.0
        rho_left = (f_in[y, 0, 0] + f_in[y, 0, 3] + f_in[y, 0, 4] +
                   2 * (f_in[y, 0, 2] + f_in[y, 0, 6] + f_in[y, 0, 7])) / (1.0 - ux)
        f_in[y, 0, 1] = f_in[y, 0, 2] + 2/3 * ux * rho_left
        f_in[y, 0, 5] = f_in[y, 0, 7] + 1/6 * ux * rho_left
        f_in[y, 0, 8] = f_in[y, 0, 6] + 1/6 * ux * rho_left

    # Top boundary - symmetrical condition (NOWA IMPLEMENTACJA)
    f_in[0, :, 3] = f_in[1, :, 3]  # N = sąsiedni węzeł
    f_in[0, :, 5] = f_in[1, :, 5]  # NE = sąsiedni węzeł
    f_in[0, :, 6] = f_in[1, :, 6]  # NW = sąsiedni węzeł

    # Bottom boundary - bounce-back (NOWA IMPLEMENTACJA)
    f_in[-1, :, 4] = f_out[-1, :, 3]  # S = N
    f_in[-1, :, 7] = f_out[-1, :, 5]  # SW = NE
    f_in[-1, :, 8] = f_out[-1, :, 6]  # SE = NW

def draw_velocity_field(surface, ux, uy, show_both=False):
    if show_both:
        # Rysuj prędkość poziomą w lewym oknie
        for y in range(HEIGHT):
            for x in range(WIDTH):
                vel = np.clip(ux[y, x], -0.05, 0.05) / 0.05
                if vel >= 0:
                    color = (int(255 * vel), 0, 0)
                else:
                    color = (0, 0, int(-255 * vel))
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, color, rect)

        # Rysuj prędkość pionową w prawym oknie
        for y in range(HEIGHT):
            for x in range(WIDTH):
                vel = np.clip(uy[y, x], -0.05, 0.05) / 0.05
                if vel >= 0:
                    color = (int(255 * vel), 0, 0)
                else:
                    color = (0, 0, int(-255 * vel))
                rect = pygame.Rect((x + WIDTH) * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, color, rect)
    else:
        # Rysuj tylko prędkość poziomą
        for y in range(HEIGHT):
            for x in range(WIDTH):
                vel = np.clip(ux[y, x], -0.05, 0.05) / 0.05
                if vel >= 0:
                    color = (int(255 * vel), 0, 0)
                else:
                    color = (0, 0, int(-255 * vel))
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(surface, color, rect)


def save_screenshot(iteration):
    filename = f"screenshot_iter_{iteration}.png"
    pygame.image.save(screen, filename)
    print(f"Screenshot saved: {filename}")


def main():
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 20)

    # Initialize simulations
    f_in1, f_out1, rho1, ux1, uy1 = initialize_simulation()
    f_in2, f_out2, rho2, ux2, uy2 = initialize_simulation()

    # Do przechowywania poprzednich wartości prędkości
    ux1_old = np.zeros_like(ux1)
    ux2_old = np.zeros_like(ux2)

    running = True
    iteration = 0
    steady_state_reached = False
    screenshot_iterations = [0, 10, 50, 100, 200, 500, 1000]

    while running and not steady_state_reached:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Zachowanie poprzednich wartości prędkości
        np.copyto(ux1_old, ux1)
        np.copyto(ux2_old, ux2)

        # Variant 1
        rho1 = np.sum(f_in1, axis=2)
        ux1 = np.sum(c[:, 0] * f_in1, axis=2) / rho1
        uy1 = np.sum(c[:, 1] * f_in1, axis=2) / rho1

        f_eq1 = calculate_equilibrium(rho1, ux1, uy1)
        f_out1 = f_in1 + (1.0 / TAU) * (f_eq1 - f_in1)

        for i in range(9):
            f_in1[:, :, i] = np.roll(np.roll(f_out1[:, :, i], c[i, 0], axis=1), c[i, 1], axis=0)

        apply_boundary_conditions_variant1(f_in1, f_out1)

        # Variant 2
        rho2 = np.sum(f_in2, axis=2)
        ux2 = np.sum(c[:, 0] * f_in2, axis=2) / rho2
        uy2 = np.sum(c[:, 1] * f_in2, axis=2) / rho2

        f_eq2 = calculate_equilibrium(rho2, ux2, uy2)
        f_out2 = f_in2 + (1.0 / TAU) * (f_eq2 - f_in2)

        for i in range(9):
            f_in2[:, :, i] = np.roll(np.roll(f_out2[:, :, i], c[i, 0], axis=1), c[i, 1], axis=0)

        apply_boundary_conditions_variant2(f_in2, f_out2)

        # Sprawdzenie stanu stacjonarnego
        if iteration > 0:
            steady_state1 = check_steady_state(ux1_old, ux1)
            steady_state2 = check_steady_state(ux2_old, ux2)
            steady_state_reached = steady_state1 and steady_state2

        # Zapisywanie wyników
        if iteration % SAVE_INTERVAL == 0:
            results = {
                'ux1': ux1, 'uy1': uy1,
                'ux2': ux2, 'uy2': uy2,
                'iteration': iteration
            }
            np.save(f'results_iter_{iteration}.npy', results)

        # Drawing
        screen.fill((0, 0, 0))
        draw_velocity_field(screen, ux1, uy1, show_both=True)

        pygame.draw.line(screen, (255, 255, 255),
                         (WIDTH * CELL_SIZE, 0),
                         (WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE))

        iteration_text = font.render(f"Iteration: {iteration}", True, (255, 255, 255))
        variant1_text = font.render("Variant 1", True, (255, 255, 255))
        variant2_text = font.render("Variant 2", True, (255, 255, 255))

        if steady_state_reached:
            status_text = font.render("Steady state reached!", True, (0, 255, 0))
            screen.blit(status_text, (10, 40))

        screen.blit(iteration_text, (10, 10))
        screen.blit(variant1_text, (10, HEIGHT * CELL_SIZE - 30))
        screen.blit(variant2_text, (WIDTH * CELL_SIZE + 10, HEIGHT * CELL_SIZE - 30))

        if iteration in screenshot_iterations:
            save_screenshot(iteration)

        pygame.display.flip()
        clock.tick(FPS)
        iteration += 1


# if __name__ == "__main__":
#     pygame.font.init()
#     main()
#     pygame.quit()

main()