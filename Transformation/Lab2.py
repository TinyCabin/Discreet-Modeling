from ImageSelf import *
import sys

# Ładowanie obrazu
image = ImageSelf("images\\krzyk.jpg")
#image = ImageSelf("images\\sans.bmp")

def gaussian_mask(radius, sigma=1):
    size = 2 * radius + 1
    kernel = np.zeros((size, size))
    mean = radius  # Środek maski

    for x in range(size):
        for y in range(size):
            # Obliczanie wartości Gaussa
            kernel[x, y] = (1 / (2 * np.pi * sigma ** 2)) * np.exp(-(((x - mean) ** 2 + (y - mean) ** 2) / (2 * sigma ** 2)))

    # Normalizacja maski
    kernel /= np.sum(kernel)
    return kernel

def user_defined_mask():
    radius = int(input("Podaj promień maski (np. 1, 2, 3, ...): "))

    # Obliczanie rozmiaru maski
    size = 2 * radius + 1
    mask = []

    print(f"Wprowadź wartości maski {size}x{size}, używając spacji jako separatora (np. '0 1 0'):")

    for i in range(size):
        row = input(f"Wiersz {i + 1}: ")
        # Przekształcenie wprowadzonego tekstu na listę liczb
        mask.append(list(map(float, row.split())))

    mask = np.array(mask)

    # Zastosuj maskę do obrazu
    image_wynik = image.apply_convolution_with_radius(mask, radius)
    image_wynik.show()
    image_wynik.save(r'images\splot_z_uzytkownika_maska.bmp')

# Zadanie 1: Dylatacja obrazu
def zad1(radius=1):
    image_wynik = image.dilatation(radius)
    image_wynik.show()
    image_wynik.save(r'images\dylatacja.bmp')

# Zadanie 2: Erozja obrazu
def zad2(radius=1):
    image_wynik = image.erosion(radius)
    image_wynik.show()
    image_wynik.save(r'images\erozja.bmp')

# Zadanie 3: Otwarcie morfologiczne
def zad3(radius=1):
    image_wynik = image.opening(radius)
    image_wynik.show()
    image_wynik.save(r'images\otwarcie.bmp')

# Zadanie 4: Domknięcie morfologiczne
def zad4(radius=1):
    image_wynik = image.closing(radius)
    image_wynik.show()
    image_wynik.save(r'images\domkniecie.bmp')

# Zadanie 5: Splot z wybrana maską
def zad5():
    masks = image.load_mask("Data\\path_to_mask.json")  # Wczytanie masek z pliku JSON

    print("Dostępne maski:")
    for name in masks.keys():
        print(f"- {name}")

    mask_name = input("Wybierz maskę z listy: ")  # Użytkownik wybiera maskę
    if mask_name not in masks:
        raise ValueError("Wybrana maska nie istnieje.")

    custom_mask = np.array(masks[mask_name])  # Wybór maski
    image_wynik = image.apply_convolution(custom_mask)
    image_wynik.show()
    image_wynik.save(r'images\splot_z_wybrana_maska.bmp')

# Zadanie 6: Splot z maską o promieniu r
def zad6():
    # Poproś użytkownika o podanie promienia
    radius = int(input("Podaj promień dla maski Gaussa (np. 1, 2, 3, ...): "))

    # Generuj maskę Gaussa
    gaussian_mask_array = gaussian_mask(radius)

    # Wyświetl maskę
    print("Generowana maska Gaussa:")
    print(gaussian_mask_array)

    # Zastosuj maskę do obrazu
    image_wynik = image.apply_convolution_with_radius(gaussian_mask_array, radius)
    image_wynik.show()
    image_wynik.save(r'images\splot_z_maska_gaussa.bmp')


# Zadanie 7: Własny filtr dolnoprzepustowy
def zad7():
    low_pass_filter = [[1/9] * 3] * 3  # filtr dolnoprzepustowy 3x3
    image_wynik = image.apply_convolution(low_pass_filter)
    image_wynik.show()
    image_wynik.save(r'images\dolnoprzepustowy.bmp')

# Zadanie 8: Własny filtr górnoprzepustowy
def zad8():
    high_pass_filter = [[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]]  # filtr górnoprzepustowy 3x3
    image_wynik = image.apply_convolution(high_pass_filter)
    image_wynik.show()
    image_wynik.save(r'images\gornoprzepustowy.bmp')

# Menu
def menu():
    while True:
        print("\n--- Menu ---")
        print("1. Dylatacja obrazu")
        print("2. Erozja obrazu")
        print("3. Otwarcie morfologiczne")
        print("4. Domknięcie morfologiczne")
        print("5. Splot z wybraną maską")
        print("6. Splot z maską o promieniu r")
        print("7. Filtr dolnoprzepustowy")
        print("8. Filtr górnoprzepustowy")
        print("9. Wprowadź własną maskę")
        print("10. Wyjście")

        choice = input("Wybierz opcję (1-9): ")

        if choice == '1':
            radius = int(input("Podaj promień sąsiedztwa dla dylatacji: "))
            zad1(radius)
        elif choice == '2':
            radius = int(input("Podaj promień sąsiedztwa dla erozji: "))
            zad2(radius)
        elif choice == '3':
            radius = int(input("Podaj promień sąsiedztwa dla otwarcia morfologicznego: "))
            zad3(radius)
        elif choice == '4':
            radius = int(input("Podaj promień sąsiedztwa dla domknięcia morfologicznego: "))
            zad4(radius)
        elif choice == '5':
            zad5()
        elif choice == '6':
            zad6()
        elif choice == '7':
            zad7()
        elif choice == '8':
            zad8()
        elif choice == '9':
            user_defined_mask()
        elif choice == '10':
            print("Zamykam program...")
            sys.exit()
        else:
            print("Nieprawidłowy wybór, spróbuj ponownie.")

menu()