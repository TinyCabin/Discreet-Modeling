import random
import pygame

pygame.init()

BLACK = (0, 0, 0)
GREEN = (0, 255, 50)
RED = (255, 0, 0)
WHITE = (255, 255, 255)

WIDTH, HEIGHT = 1500, 750
TILE_SIZE = 3
GRID_WIDTH = WIDTH // TILE_SIZE  # 500
GRID_HEIGHT = HEIGHT // TILE_SIZE  # 250
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT))

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 16)

DIRECTIONS = {
    "N": (0, -1),
    "S": (0, 1),
    "E": (1, 0),
    "W": (-1, 0),
}

def create_initial_board():
    positions = {}

    # Obramowanie - górna i dolna krawędź
    for col in range(GRID_WIDTH):
        positions[(col, 0)] = {"boundary": True}
        positions[(col, GRID_HEIGHT - 1)] = {"boundary": True}

    # Obramowanie - lewa i prawa krawędź
    for row in range(GRID_HEIGHT):
        positions[(0, row)] = {"boundary": True}
        positions[(GRID_WIDTH - 1, row)] = {"boundary": True}

    # Pionowa ściana z przerwą
    wall_col = GRID_WIDTH // 5
    for row in range(GRID_HEIGHT):
        if not (100 < row < 150):
            positions[(wall_col, row)] = {"boundary": True}

    return positions


def gen(num, positions):
    for _ in range(num):
        col = random.randint(1, GRID_WIDTH // 5 - 2)
        row = random.randint(1, GRID_HEIGHT - 2)
        position = (col, row)

        if position not in positions:
            positions[position] = {}

        # Dodaj cząstkę z losowym kierunkiem
        direction = random.choice(list(DIRECTIONS.keys()))
        positions[position][direction] = True


def drawGrid(positions):
    for position, states in positions.items():
        col, row = position
        if "boundary" in states:
            color = WHITE
        elif any(states.values()):
            color = RED
        else:
            continue

        pygame.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))


def adjust_grid(positions):
    new_positions = {}

    for position, states in positions.items():
        if "boundary" in states:
            new_positions[position] = {"boundary": True}
            continue

        for direction, active in states.items():
            if not active:
                continue

            dx, dy = DIRECTIONS[direction]
            new_position = (position[0] + dx, position[1] + dy)

            # Odbicie od ściany
            if new_position in positions and "boundary" in positions[new_position]:
                if direction == "N":
                    direction = "S"
                elif direction == "S":
                    direction = "N"
                elif direction == "E":
                    direction = "W"
                elif direction == "W":
                    direction = "E"

                dx, dy = DIRECTIONS[direction]
                new_position = (position[0] + dx, position[1] + dy)

            # Przenoszenie cząstki do nowej pozycji
            if new_position not in new_positions:
                new_positions[new_position] = {}
            new_positions[new_position][direction] = True

    handle_collisions(new_positions)
    return new_positions



def handle_collisions(positions):
    for position, states in positions.items():
        active_directions = [dir for dir, active in states.items() if active]

        # Obsługa kolizji dwóch cząstek z przeciwnych stron
        if len(active_directions) == 2:
            if "N" in active_directions and "S" in active_directions:
                states["N"], states["S"] = False, False
                states["E"], states["W"] = True, True
            elif "E" in active_directions and "W" in active_directions:
                states["E"], states["W"] = False, False
                states["N"], states["S"] = True, True

        # Obsługa bardziej złożonych kolizji
        elif len(active_directions) > 2:
            pass



def get_neighbors(position):
    pass


def main():
    global FPS
    running = True
    playing = False
    f = 10

    positions = create_initial_board()
    gen(1000, positions)  # Generuj 10 cząstek

    while running:
        clock.tick(FPS)

        if playing:
            positions = adjust_grid(positions)

        pygame.display.set_caption("Playing" if playing else "Paused")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                if event.key == pygame.K_SPACE:
                    playing = not playing

                if event.key == pygame.K_g:
                    gen(1000, positions)

                if event.key == pygame.K_UP:
                    FPS = min(FPS + 1, 60)

                if event.key == pygame.K_DOWN:
                    FPS = max(FPS - 1, 1)

                if event.key == pygame.K_EQUALS:
                    FPS = 60

                if event.key == pygame.K_MINUS:
                    FPS = 1

        screen.fill(BLACK)
        drawGrid(positions)

        txtsurf = font.render(f"{FPS} FPS", True, WHITE)
        screen.blit(txtsurf, (3, 3))

        pygame.display.update()

    pygame.quit()


if __name__ == '__main__':
    main()