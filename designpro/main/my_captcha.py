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

        # Создание изображения
        font_size = 50
        font = ImageFont.truetype("C:/Users/Exz00/PycharmProjects/designpro/designpro/fonts/Playfair_Display,Roboto/Roboto/Roboto-Regular.ttf", font_size)
        image = Image.new('RGB', (200, 80), (255, 255, 255))
        draw = ImageDraw.Draw(image)

        # Получение размеров текста
        bbox = draw.textbbox((0, 0), text, font=font)  # Используем textbbox вместо textsize
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # Вычисление позиции текста
        x = (image.width - text_width) / 2
        y = (image.height - text_height) / 2

        # Рисуем текст на изображении
        draw.text((x, y), text, fill=(0, 0, 0), font=font)

        # Сохранение изображения в памяти
        buffered = io.BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')

        return img_str, text  # Возвращаем изображение и текст капчи