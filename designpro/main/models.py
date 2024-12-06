from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

def validate_image(image):
    # Ограничение по размеру (2 Мб)
    max_size = 2 * 1024 * 1024  # 2 MB
    if image.size > max_size:
        raise ValidationError("Размер изображения не должен превышать 2 Мб.")

    # Ограничение по типу файла
    valid_extensions = ['jpg', 'jpeg', 'png', 'bmp']
    ext = image.name.split('.')[-1].lower()
    if ext not in valid_extensions:
        raise ValidationError("Допустимые форматы: jpg, jpeg, png, bmp.")

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Application(models.Model):

    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'Принято в работу'),
        ('completed', 'Выполнено'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    description = models.TextField()
    categories = models.ManyToManyField(Category)
    image = models.ImageField(upload_to='applications/', validators=[validate_image], blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title