import numpy as np
import csv
import matplotlib.pyplot as plt

# Funkcja do tworzenia reguły na podstawie liczby (8-bitowa)
def create_rule(rule_number):
    return [(rule_number >> i) & 1 for i in range(7, -1, -1)]

# Funkcja do symulacji automatu komórkowego
def cellular_automaton(rule, grid_size, iterations, boundary_condition, initial_state):
    # Siatka dla wyników
    grid = np.zeros((iterations, grid_size), dtype=int)
    grid[0] = initial_state

    # Iteracja przez kroki czasowe
    for i in range(1, iterations):
        for j in range(grid_size):
            # Sąsiedztwo zależne od warunku brzegowego
            if boundary_condition == "periodic":
                left = grid[i-1][(j-1) % grid_size]
                center = grid[i-1][j]
                right = grid[i-1][(j+1) % grid_size]
            elif boundary_condition == "absorbing":
                left = grid[i-1][j-1] if j > 0 else 0
                center = grid[i-1][j]
                right = grid[i-1][j+1] if j < grid_size - 1 else 0

            # Wyznaczanie nowego stanu na podstawie reguły
            pattern = (left << 2) | (center << 1) | right
            grid[i][j] = rule[pattern]

    return grid

# Funkcja zapisu wyników do pliku CSV
def save_to_csv(grid, filename="OutputAutomata\\cellular_automaton_output.csv"):
    with open(filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        for row in grid:
            writer.writerow(row)

def visualize_terminal(grid):
    for row in grid:
        line = ''.join(['█' if cell == 1 else '.' for cell in row])
        print(line)

# Wizualizacja graficzna za pomocą Matplotlib
def visualize_matplotlib(grid, rule_number):
    plt.figure(figsize=(10, 10))
    plt.imshow(grid, cmap="binary", interpolation="nearest")
    plt.title(f"Cellular Automaton - Rule {rule_number}")
    plt.xlabel("Cells")
    plt.ylabel("Time Steps")
    plt.show()

# Funkcja do zapisania obrazu w formacie PNG
def save_as_image(grid, rule_number):
    plt.figure(figsize=(10, 10))
    plt.imshow(grid, cmap="binary", interpolation="nearest")
    plt.axis("off")
    filename = f"OutputAutomata\\automaton_rule_{rule_number}.png"
    plt.savefig(filename, bbox_inches="tight")
    print(f"Wizualizacja zapisana do pliku {filename}")

def menu():
    # Wprowadzanie danych
    try:
        album_number = input("Podaj 6 cyfr: ")
        if len(album_number) != 6 or not album_number.isdigit():
            raise ValueError("Numer albumu musi mieć 6 cyfr.")

        grid_size = int(input("Podaj rozmiar siatki: "))
        iterations = int(input("Podaj liczbę iteracji: "))
        if grid_size <= 0 or iterations <= 0:
            raise ValueError("Rozmiar siatki i liczba iteracji muszą być dodatnie.")

        boundary_condition = input("Wybierz warunek brzegowy ('periodic' lub 'absorbing'): ").strip().lower()
        if boundary_condition not in ["periodic", "absorbing"]:
            raise ValueError("Nieprawidłowy warunek brzegowy.")

        # Wybór, czy dodać inną regułę
        additional_rule_choice = input("Czy chcesz dodać dodatkową regułę? (tak/nie): ").strip().lower()
        additional_rules = []
        if additional_rule_choice == 'tak':
            while True:
                rule_input = input("Podaj dodatkową regułę (0-255) lub 'koniec', aby zakończyć: ")
                if rule_input.lower() == 'koniec':
                    break
                try:
                    rule_num = int(rule_input)
                    if 0 <= rule_num <= 255:
                        additional_rules.append(rule_num)
                    else:
                        print("Reguła musi być w zakresie 0-255.")
                except ValueError:
                    print("Proszę podać poprawną liczbę.")

        # Użytkownik może wybrać, czy chce wprowadzić własny stan początkowy
        initial_state_choice = input("Czy chcesz podać statyczny stan początkowy? (tak/nie): ").strip().lower()
        if initial_state_choice == "tak":
            initial_state_input = input(f"Podaj stan początkowy jako ciąg {grid_size} cyfr '0' lub '1': ")
            if len(initial_state_input) != grid_size or not all(c in "01" for c in initial_state_input):
                raise ValueError(f"Stan początkowy musi być ciągiem dokładnie {grid_size} cyfr '0' i '1'.")
            initial_state = np.array([int(c) for c in initial_state_input], dtype=int)
        else:
            initial_state = np.random.choice([0, 1], size=grid_size)
            print(f"Wylosowany stan początkowy: {''.join(map(str, initial_state))}")

    except ValueError as e:
        print(f"Błąd: {e}")
        return

    # Tworzenie reguł na podstawie numeru albumu
    rules = [int(album_number[i:i+2]) for i in range(0, 6, 2)] + [190] + additional_rules
    print(f"Używane reguły: {rules}")


    for rule_number in rules:
        rule = create_rule(rule_number)
        result_grid = cellular_automaton(rule, grid_size, iterations, boundary_condition, initial_state)

        # Zapis do pliku CSV dla każdej reguły
        filename = f"OutputAutomata\\automaton_rule_{rule_number}.csv"
        save_to_csv(result_grid, filename)
        print(f"Wynik dla reguły {rule_number} zapisano do {filename}")

        print(f"\nWizualizacja dla reguły {rule_number} (stan początkowy w iteracji 0):")
        visualize_terminal(result_grid)  # Wizualizacja w terminalu
        visualize_matplotlib(result_grid, rule_number) # Wizualizacja
        save_as_image(result_grid, rule_number)         # Zapis do PNG

# Uruchomienie menu
menu()
