from PIL import Image, ImageDraw, ImageFont
import random
import string
import io
import base64


class CustomCaptcha:
    def generate(self):
        # Генерация случайного текста капчи из кириллических символов
        characters = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789'
        text = ''.join(random.choices(characters, k=6))

        # Размер изображения
        image_width = 250  # Увеличен размер изображения
        image_height = 100  # Увеличен размер изображения
        font_size = 60  # Увеличен размер шрифта
        font = ImageFont.truetype(
            "fonts/Playfair_Display,Roboto/Roboto/Roboto-Regular.ttf",
            font_size)

        # Создание изображения
        image = Image.new('RGBA', (image_width, image_height), (255, 255, 255, 255))
        draw = ImageDraw.Draw(image)

        # Изменение фона с помощью случайных линий
        for _ in range(20):
            x1 = random.randint(0, image_width)
            y1 = random.randint(0, image_height)
            x2 = random.randint(0, image_width)
            y2 = random.randint(0, image_height)
            draw.line((x1, y1, x2, y2), fill=(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)),
                      width=2)

        # Ширина для каждого символа
        char_width = image_width // len(text)

        # Рисуем текст на изображении с искажениями
        for i, char in enumerate(text):
            # Определение позиции для каждого символа
            x = char_width * i + random.randint(-10, 10)  # Случайное смещение
            y = (image_height - font_size) // 2 + random.randint(-10, 10)  # Центрируем по вертикали

            # Создание нового изображения для каждого символа
            char_image = Image.new('RGBA', (font_size, font_size), (255, 255, 255, 0))  # Изменено на 'RGBA'
            char_draw = ImageDraw.Draw(char_image)
            char_draw.text((0, 0), char, fill=(0, 0, 0, 255), font=font)  # Добавлен альфа-канал
            char_image = char_image.rotate(random.randint(-30, 30), expand=1)  # Поворот

            # Накладываем символ на основное изображение
            image.paste(char_image, (x, y), char_image)

        # Сохранение изображения в памяти
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return img_str, text  # Возвращаем изображение и текст капчи