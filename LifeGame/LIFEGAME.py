import tkinter as tk
from tkinter import ttk
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.animation import FuncAnimation
import matplotlib.colors as mcolors

# Ustawienia podstawowe
size = 200  # Rozmiar planszy
steps = 50  #

# Definicje kolorów
cmap = mcolors.ListedColormap(['black', '#00FF00'])  # Czarny i zielony

# Funkcja do generowania stanu początkowego
def initial_state(size, pattern="random"):
    state = np.zeros((size, size), dtype=int)
    if pattern == "glider":
        state[1, 2] = state[2, 3] = state[3, 1] = state[3, 2] = state[3, 3] = 1
    elif pattern == "oscillator":
        state[size // 2, size // 2 - 1:size // 2 + 2] = 1
    elif pattern == "random":
        state = np.random.choice([0, 1], size=(size, size))
    elif pattern == "stable":
        state[size // 2:size // 2 + 2, size // 2:size // 2 + 2] = 1
    elif pattern == "gunner":
        x, y = size // 4, size // 4

        # Lewy kwadrat
        state[y + 5][x + 1] = state[y + 5][x + 2] = 1
        state[y + 6][x + 1] = state[y + 6][x + 2] = 1

        # Prawa strona
        state[y + 3][x + 13] = state[y + 3][x + 14] = 1
        state[y + 4][x + 12] = state[y + 4][x + 16] = 1
        state[y + 5][x + 11] = state[y + 5][x + 17] = 1
        state[y + 6][x + 11] = state[y + 6][x + 15] = state[y + 6][x + 17] = state[y + 6][x + 18] = 1
        state[y + 7][x + 11] = state[y + 7][x + 17] = 1
        state[y + 8][x + 12] = state[y + 8][x + 16] = 1
        state[y + 9][x + 13] = state[y + 9][x + 14] = 1

        # Lewa strona
        state[y + 1][x + 25] = 1
        state[y + 2][x + 23] = state[y + 2][x + 25] = 1
        state[y + 3][x + 21] = state[y + 3][x + 22] = 1
        state[y + 4][x + 21] = state[y + 4][x + 22] = 1
        state[y + 5][x + 21] = state[y + 5][x + 22] = 1
        state[y + 6][x + 23] = state[y + 6][x + 25] = 1
        state[y + 7][x + 25] = 1

        # Dodatkowy element
        state[y + 3][x + 35] = state[y + 3][x + 36] = 1
        state[y + 4][x + 35] = state[y + 4][x + 36] = 1
    return state

# Funkcja zliczająca sąsiadów
def count_neighbors(state, boundary="periodic"):
    padded_state = np.pad(state, pad_width=1, mode='wrap' if boundary == "periodic" else 'constant')
    neighbors_count = sum(np.roll(np.roll(padded_state, i, 0), j, 1)
                          for i in (-1, 0, 1) for j in (-1, 0, 1) if (i != 0 or j != 0))
    return neighbors_count[1:-1, 1:-1]

# Funkcja symulacji kroku
def game_step(state, boundary="periodic"):
    neighbors = count_neighbors(state, boundary)
    new_state = np.where((state == 1) & ((neighbors == 2) | (neighbors == 3)), 1, 0)
    new_state += np.where((state == 0) & (neighbors == 3), 1, 0)
    return new_state, neighbors

# Klasa GUI dla gry w życie
class GameOfLifeApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gra w życie - Symulacja")

        # Zmienne dla wybranych opcji
        self.pattern = tk.StringVar(value="random")
        self.boundary = tk.StringVar(value="periodic")
        self.animation_running = False  # Dodana flaga stanu animacji


        # Panel z opcjami
        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)

        tk.Label(control_frame, text="Wzorzec początkowy:").pack(anchor='w')
        ttk.Radiobutton(control_frame, text="Glider", variable=self.pattern, value="glider").pack(anchor='w')
        ttk.Radiobutton(control_frame, text="Oscylator", variable=self.pattern, value="oscillator").pack(anchor='w')
        ttk.Radiobutton(control_frame, text="Losowy", variable=self.pattern, value="random").pack(anchor='w')
        ttk.Radiobutton(control_frame, text="Niezmienny", variable=self.pattern, value="stable").pack(anchor='w')
        ttk.Radiobutton(control_frame, text="Gunner", variable=self.pattern, value="gunner").pack(anchor='w')
        # ttk.Radiobutton(control_frame, text="Zabcia Oscylator", variable=self.pattern, value="zabcia").pack(anchor='w')

        tk.Label(control_frame, text="\nWarunki brzegowe:").pack(anchor='w')
        ttk.Radiobutton(control_frame, text="Periodyczne", variable=self.boundary, value="periodic").pack(anchor='w')
        ttk.Radiobutton(control_frame, text="Odbijające", variable=self.boundary, value="reflective").pack(anchor='w')

        # Przyciski start, stop, kontynuuj i zapisz wzorzec
        self.start_button = ttk.Button(control_frame, text="Start", command=self.start_animation)
        self.start_button.pack(fill='x', pady=5)

        self.stop_button = ttk.Button(control_frame, text="Stop", command=self.stop_animation)
        self.stop_button.pack(fill='x', pady=5)

        self.continue_button = ttk.Button(control_frame, text="Kontynuuj symulację",
                                          command=self.continue_simulation)
        self.continue_button.pack(fill='x', pady=5)

        # self.save_button = ttk.Button(control_frame, text="Zapisz wzorzec", command=self.save_pattern)
        # self.save_button.pack(fill='x', pady=5)

        # Panel dla animacji
        self.fig, self.ax = plt.subplots()
        self.canvas = FigureCanvasTkAgg(self.fig, root)
        self.canvas.get_tk_widget().pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Ustawienia początkowe
        self.state = initial_state(size, self.pattern.get())
        self.mat = self.ax.matshow(self.state, cmap=cmap)
        self.ani = None  # Animacja ustawiana w `start_animation`

        self.drawing_mode = True

        self.canvas.get_tk_widget().bind("<Button-1>", self.toggle_cell)
        self.fig.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.1)
        self.ax.set_aspect('equal')  # Wymusza kwadratowe komórki

    # Aktualizacja wizualizacji
    def update_visualization(self, _):
             if self.animation_running:
                 self.state, neighbors = game_step(self.state, self.boundary.get())
                 colored_state = np.where(self.state == 1, neighbors, 0)
                 self.mat.set_data(colored_state)
             return [self.mat]

    def start_animation(self):
        if self.ani is not None:
            self.stop_animation()

        #resetuj
        self.state = initial_state(size, self.pattern.get())
        self.animation_running = True
        self.ani = FuncAnimation(self.fig, self.update_visualization,
                                 frames=None, interval=100, blit=True)
        self.canvas.draw()

    # Stop animacji
    def stop_animation(self):
        if self.ani:
            self.ani.event_source.stop()
            self.ani = None

    def clear_board(self):
        self.stop_animation()
        self.state = np.zeros((size, size), dtype=int)
        self.mat.set_data(self.state)
        self.canvas.draw()

    def save_pattern(self):
        self.saved_pattern = self.state.copy()
        print("Wzorzec zapisany!")

    def continue_simulation(self):
        if self.animation_running:
            self.stop_animation()
        self.animation_running = True
        self.ani = FuncAnimation(self.fig, self.update_visualization,
                                 frames=None, interval=100, blit=True)
        self.canvas.draw()

    # Zmienianie stanu komórek na planszy
    def toggle_cell(self, event):
        if self.animation_running:
            self.stop_animation()
        # Pobieranie informacji o faktycznym obszarze wyświetlania
        bbox = self.ax.get_position()
        canvas_width = self.canvas.get_tk_widget().winfo_width()
        canvas_height = self.canvas.get_tk_widget().winfo_height()

        # Konwersja współrzędnych kliknięcia na względne pozycje (0-1)
        click_x_rel = event.x / canvas_width
        click_y_rel = event.y / canvas_height

        # Sprawdzenie czy kliknięcie jest w obszarze wykresu
        if (bbox.x0 <= click_x_rel <= bbox.x1 and
                bbox.y0 <= (1 - click_y_rel) <= bbox.y1):  # Odwrócenie Y, bo matplotlib ma inny układ współrzędnych

            # Przeliczenie na współrzędne planszy
            x = int((click_x_rel - bbox.x0) / (bbox.x1 - bbox.x0) * size)
            y = int((click_y_rel - (1 - bbox.y1)) / (bbox.y1 - bbox.y0) * size)

            # Upewnienie się, że współrzędne są w granicach planszy
            if 0 <= x < size and 0 <= y < size:
                # Zmienianie stanu komórki
                self.state[y, x] = 1 - self.state[y, x]

                # Zaktualizowanie wizualizacji
                self.mat.set_data(self.state)
                self.canvas.draw()


# Uruchomienie aplikacji
root = tk.Tk()
app = GameOfLifeApp(root)
root.mainloop()
