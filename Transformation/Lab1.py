from ImageSelf import *
import sys

image = ImageSelf("images\\krzyk.jpg")

def zad1(procent_sciemnienia):
    image_wynik = image.przyciemnij(procent_sciemnienia)
    image_wynik.show()
    image_wynik.save(r'images\przyciemniony_obraz.bmp')
    print("Obraz został przyciemniony i zapisany jako 'przyciemniony_obraz.bmp'.")

def zad2(procent_rozjasniania):
    if not (10 <= procent_rozjasniania <= 20):
        raise ValueError("Procent rozjaśnienia musi być w zakresie od 10 do 20.")
    for i in range(3):
        image_wynik = image.rozjasnij(procent_rozjasniania * (i + 1))
        image_wynik.show()
        image_wynik.save(f'images\\rozjasniony_obraz{i}.bmp')
        print(f"Obraz rozjaśniony o {procent_rozjasniania * (i + 1)}% zapisany jako 'rozjasniony_obraz{i}.bmp'.")

def zad3(prog=128):
    image_wynik = image.binaryzacja(prog)
    image_wynik.show()
    image_wynik.save(r'images\zbinaryzowany_obraz.bmp')
    print("Obraz został zbinaryzowany i zapisany jako 'zbinaryzowany_obraz.bmp'.")

def zad4():
    while True:
        try:
            prog = int(input("Wprowadź próg binaryzacji (0-255): "))
            if not (0 <= prog <= 255):
                raise ValueError("Próg binaryzacji musi być w zakresie od 0 do 255.")
            break  # Jeśli próg jest poprawny, wychodzimy z pętli
        except ValueError as e:
            print(e)  # Wyświetlenie błędu

    # Przeprowadzenie binaryzacji
    image_wynik = image.binaryzacja(prog)
    image_wynik.show()
    image_wynik.save(r'images\zbinaryzowany_obraz_z_progiem_uzytkownika.bmp')
    print("Obraz został zbinaryzowany z użyciem podanego progu i zapisany jako 'zbinaryzowany_obraz_z_progiem_uzytkownika.bmp'.")

def menu():
    while True:
        print("\n--- Menu ---")
        print("1. Przyciemnij obraz")
        print("2. Rozjaśnij obraz w sukcesji")
        print("3. Binaryzacja z domyślnym progiem")
        print("4. Binaryzacja z użytkownikowym progiem")
        print("5. Wyjście")

        choice = input("Wybierz opcję (1-5): ")

        if choice == '1':
            procent = int(input("Wprowadź procent przyciemnienia (0-100): "))
            zad1(procent)
        elif choice == '2':
            procent = int(input("Wprowadź procent rozjaśnienia (10-20): "))
            try:
                zad2(procent)
            except ValueError as e:
                print(e)
        elif choice == '3':
            zad3(128)  # Domyślny próg
        elif choice == '4':
            zad4()
        elif choice == '5':
            print("Zamykam program...")
            sys.exit()
        else:
            print("Nieprawidłowy wybór, spróbuj ponownie.")

menu()