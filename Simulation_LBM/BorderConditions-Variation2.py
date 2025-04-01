import pygame
import numpy as np

# Simulation settings
WIDTH, HEIGHT = 128, 128
CELL_SIZE = 5
FPS = 60
TAU = 1.0
SAVE_INTERVAL = 100
STEADY_STATE_THRESHOLD = 1e-6

# Initialize Pygame
WINDOW_WIDTH = WIDTH * CELL_SIZE * 2 + 100  # Space for two windows
WINDOW_HEIGHT = HEIGHT * CELL_SIZE
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("LBM Flow Simulation - Vx | Vy")
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

w = np.array([4/9, 1/9, 1/9, 1/9, 1/9, 1/36, 1/36, 1/36, 1/36])

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

def apply_boundary_conditions(f_in, f_out):
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
        ux = 0.02 * (1-y / HEIGHT)
        uy = 0.0
        rho_left = (f_in[y, 0, 0] + f_in[y, 0, 3] + f_in[y, 0, 4] +
                   2 * (f_in[y, 0, 2] + f_in[y, 0, 6] + f_in[y, 0, 7])) / (1.0 - ux)
        f_in[y, 0, 1] = f_in[y, 0, 2] + 2/3 * ux * rho_left
        f_in[y, 0, 5] = f_in[y, 0, 7] + 1/6 * ux * rho_left
        f_in[y, 0, 8] = f_in[y, 0, 6] + 1/6 * ux * rho_left

    # Top boundary - symmetrical condition
    f_in[0, :, 3] = f_in[1, :, 3]
    f_in[0, :, 5] = f_in[1, :, 5]
    f_in[0, :, 6] = f_in[1, :, 6]

    # Bottom boundary - bounce-back
    f_in[-1, :, 4] = f_out[-1, :, 3]
    f_in[-1, :, 7] = f_out[-1, :, 5]
    f_in[-1, :, 8] = f_out[-1, :, 6]

def draw_velocity_fields(surface, ux, uy):
    # Draw horizontal velocity (left window)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            vel = np.clip(ux[y, x], -0.05, 0.05) / 0.05
            if vel >= 0:
                color = (int(255 * vel), 0, 0)  # Red for positive
            else:
                color = (0, 0, int(-255 * vel))  # Blue for negative
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, color, rect)

    # Draw vertical velocity (right window)
    for y in range(HEIGHT):
        for x in range(WIDTH):
            vel = np.clip(uy[y, x], -0.05, 0.05) / 0.05
            if vel >= 0:
                color = (int(255 * vel), 0, 0)  # Red for positive
            else:
                color = (0, 0, int(-255 * vel))  # Blue for negative
            rect = pygame.Rect((x + WIDTH) * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(surface, color, rect)

def save_screenshot(iteration):
    filename = f"screenshot_iter_{iteration}.png"
    pygame.image.save(screen, filename)
    print(f"Screenshot saved: {filename}")

def main():
    pygame.font.init()
    font = pygame.font.SysFont('Arial', 20)

    # Initialize simulation
    f_in, f_out, rho, ux, uy = initialize_simulation()
    ux_old = np.zeros_like(ux)

    running = True
    iteration = 0
    steady_state_reached = False
    screenshot_iterations = [0, 10, 50, 100, 200, 500, 1000]

    while running and not steady_state_reached:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        np.copyto(ux_old, ux)

        # Main simulation step
        rho = np.sum(f_in, axis=2)
        ux = np.sum(c[:, 0] * f_in, axis=2) / rho
        uy = np.sum(c[:, 1] * f_in, axis=2) / rho

        f_eq = calculate_equilibrium(rho, ux, uy)
        f_out = f_in + (1.0 / TAU) * (f_eq - f_in)

        for i in range(9):
            f_in[:, :, i] = np.roll(np.roll(f_out[:, :, i], c[i, 0], axis=1), c[i, 1], axis=0)

        apply_boundary_conditions(f_in, f_out)

        # Check steady state
        if iteration > 0:
            steady_state_reached = check_steady_state(ux_old, ux)

        # Save results
        if iteration % SAVE_INTERVAL == 0:
            results = {
                'ux': ux,
                'uy': uy,
                'iteration': iteration
            }
            np.save(f'results_iter_{iteration}.npy', results)

        # Drawing
        screen.fill((0, 0, 0))
        draw_velocity_fields(screen, ux, uy)

        # Separator line
        pygame.draw.line(screen, (255, 255, 255),
                        (WIDTH * CELL_SIZE, 0),
                        (WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE))

        # Text overlays
        iteration_text = font.render(f"Iteration: {iteration}", True, (255, 255, 255))
        vx_text = font.render("Vx", True, (255, 255, 255))
        vy_text = font.render("Vy", True, (255, 255, 255))

        if steady_state_reached:
            status_text = font.render("Steady state reached!", True, (0, 255, 0))
            screen.blit(status_text, (10, 40))

        screen.blit(iteration_text, (10, 10))
        screen.blit(vx_text, (10, HEIGHT * CELL_SIZE - 30))
        screen.blit(vy_text, (WIDTH * CELL_SIZE + 10, HEIGHT * CELL_SIZE - 30))

        if iteration in screenshot_iterations:
            save_screenshot(iteration)

        pygame.display.flip()
        clock.tick(FPS)
        iteration += 1

if __name__ == "__main__":
    pygame.font.init()
    main()
    pygame.quit()