import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import json

class ImageSelf:
    def __init__(self, image_path):
        self.image = Image.open(image_path).convert('RGB')

    #LAB 2

    def to_grayscale(self):
        return self.image.convert('L')

    def dilatation(self, radius=1):
        img_copy = self.to_grayscale()
        pixels = np.array(img_copy)
        padded = np.pad(pixels, radius, mode='reflect')  # Użycie edge mirroring
        dilated = np.zeros_like(pixels)

        for x in range(dilated.shape[0]):
            for y in range(dilated.shape[1]):
                neighborhood = padded[x:x + 2 * radius + 1, y:y + 2 * radius + 1]
                dilated[x, y] = np.max(neighborhood)

        return Image.fromarray(dilated)

    def erosion(self, radius=1):
        img_copy = self.to_grayscale()
        pixels = np.array(img_copy)
        padded = np.pad(pixels, radius, mode='reflect')  # Użycie edge mirroring
        eroded = np.zeros_like(pixels)

        for x in range(eroded.shape[0]):
            for y in range(eroded.shape[1]):
                neighborhood = padded[x:x + 2 * radius + 1, y:y + 2 * radius + 1]
                eroded[x, y] = np.min(neighborhood)

        return Image.fromarray(eroded)

    def opening(self, radius=1):
        eroded = self.erosion(radius)
        self.image = eroded
        opened = self.dilatation(radius)
        return opened

    def closing(self, radius=1):
        dilated = self.dilatation(radius)
        self.image = dilated
        closed = self.erosion(radius)
        return closed

    def apply_convolution(self, mask):
        img_copy = self.to_grayscale()
        pixels = np.array(img_copy)
        padded = np.pad(pixels, 1, mode='reflect')  # Użycie edge mirroring
        convolved = np.zeros_like(pixels)

        mask = np.array(mask)
        for x in range(convolved.shape[0]):
            for y in range(convolved.shape[1]):
                region = padded[x:x + 3, y:y + 3]
                convolved[x, y] = np.clip(np.sum(region * mask), 0, 255)

        return Image.fromarray(convolved)

    def apply_convolution_with_radius(self, mask, radius):
        img_copy = self.to_grayscale()
        pixels = np.array(img_copy)
        mask_height, mask_width = len(mask), len(mask[0])
        padded = np.pad(pixels, radius, mode='reflect')  # Użycie edge mirroring
        convolved = np.zeros_like(pixels)

        for x in range(pixels.shape[0]):
            for y in range(pixels.shape[1]):
                region = padded[x:x + mask_height, y:y + mask_width]
                convolved[x, y] = np.clip(np.sum(region * mask), 0, 255)  # Użycie maski

        return Image.fromarray(convolved)

    def load_mask(self, file_path):
        with open(file_path, 'r') as f:
            data = json.load(f)
            return data['masks']

    #KONIEC LAB 2

    #LAB1
    def przyciemnij(self, procent_sciemnienia):
        if not (1 <= procent_sciemnienia <= 99):
            raise ValueError('Procent przyciemniania musi być w zakresie  od 1 do 99')
        factor = (1 - (procent_sciemnienia / 100))

        img_copy = self.image.copy()
        pixels = img_copy.load()

        width, height = img_copy.size

        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]

                r = int(r * factor)
                g = int(g * factor)
                b = int(b * factor)

                pixels[x, y] = (r, g, b)

        return img_copy

    def rozjasnij(self, procent_rozjasniania):
        if not (1 <= procent_rozjasniania <= 99):
            raise ValueError('Procent rozjaśnienia musi być w zakresie od 1 do 99.')

        factor = (1 + (procent_rozjasniania / 100))

        img_copy = self.image.copy()
        pixels = img_copy.load()

        width, height = img_copy.size

        for x in range(width):
            for y in range(height):
                r, g, b = pixels[x, y]

                r = min(int(r * factor), 255)
                g = min(int(g * factor), 255)
                b = min(int(b * factor), 255)

                pixels[x, y] = (r, g, b)

        return img_copy

    def binaryzacja(self, prog=128):
        if not (0 <= prog <= 255):
            raise ValueError("Próg binaryzacji musi być w zakresie od 0 do 255.")
        img_copy = self.image.convert('L')
        pixels = img_copy.load()
        width, height = img_copy.size

        for x in range(width):
            for y in range(height):
                pixel_value = pixels[x, y]
                pixels[x, y] = 255 if pixel_value > prog else 0

        return img_copy

    def histogram(self):
        gray = self.image.convert('L')
        img_tmp = np.array(gray)

        plt.hist(img_tmp.ravel(), bins=256, range=(0, 256), density=True, color='gray', alpha=0.7)
        plt.title('Histogram obrazu')
        plt.xlabel('Wartość pikseli')
        plt.ylabel('Częstość występowania')
        plt.grid(True)
        plt.show()

    #KONIEC LAB1
