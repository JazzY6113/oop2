from django import forms
from django.contrib.auth.models import User
from .models import Application, Category
from django.core.validators import RegexValidator, EmailValidator
from django.core.exceptions import ValidationError

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput)
    consent = forms.BooleanField(required=True, label="Согласие на обработку персональных данных")
    fio = forms.CharField(
        label="ФИО",
        validators=[RegexValidator(r'^[А-Яа-яЁё\s-]+$', "ФИО должно содержать только кириллические буквы, дефисы и пробелы.")]
    )

    class Meta:
        model = User
        fields = ['fio', 'username', 'email', 'password', 'password_confirm', 'consent']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        validator = RegexValidator(r'^[a-zA-Z0-9-]+$', "Логин должен содержать только латиницу, цифры и дефисы.")
        validator(username)

        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Этот логин уже занят.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        EmailValidator()(email)
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот email уже занят.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password != password_confirm:
            raise forms.ValidationError("Пароли не совпадают")

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['title', 'description', 'categories', 'image']  # Измените 'category' на 'categories'

    categories = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Используйте чекбоксы для выбора нескольких категорий
        required=False
    )

    def clean_categories(self):
        categories = self.cleaned_data.get('categories')
        if categories and len(categories) > 3:
            raise ValidationError('Вы можете выбрать не более 3-х категорий.')
        return categories