from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ApplicationForm
from .models import Application
from .my_captcha import CustomCaptcha

def captcha_view(request):
    captcha = CustomCaptcha()
    image, text = captcha.generate()

    # Сохраните текст капчи в сессии, чтобы проверить его позже
    request.session['captcha_text'] = text

    if request.method == 'POST':
        user_input = request.POST.get('captcha_input')
        if user_input == request.session.get('captcha_text'):
            # Капча введена правильно
            return render(request, 'success.html')
        else:
            # Капча введена неправильно
            return render(request, 'captcha_template.html',
                          {'captcha_image': image, 'error': 'Неправильный ввод капчи'})

    return render(request, 'captcha_template.html', {'captcha_image': image})

def index(request):
    completed_applications = Application.objects.filter(status='completed').order_by('-created_at')[:5]
    in_progress_count = Application.objects.filter(status='in_progress').count()

    return render(request, 'main/index.html', {
        'completed_applications': completed_applications,
        'in_progress_count': in_progress_count,
    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('main:index')
        else:
            return render(request, 'main/login.html', {'error': 'Неверные логин или пароль'})
    return render(request, 'main/login.html')

def register_view(request):
    # Инициализация переменных
    image = None
    captcha_text = None

    # Проверяем, есть ли капча в сессии
    if 'captcha_text' not in request.session:
        captcha = CustomCaptcha()
        image, captcha_text = captcha.generate()
        request.session['captcha_text'] = captcha_text.strip()  # Сохраняем текст капчи в сессии без пробелов

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        user_input = request.POST.get('captcha_input', '').strip()  # Удаляем пробелы

        # Сравниваем введённый текст капчи с сохранённым
        if form.is_valid():
            if user_input.lower() == request.session.get('captcha_text').lower():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                login(request, user)
                # Удаляем капчу из сессии после успешной регистрации
                del request.session['captcha_text']
                return redirect('main:index')
            else:
                form.add_error(None, "Неправильный ввод капчи")

        # Генерируем новую капчу при ошибке
        captcha = CustomCaptcha()
        image, captcha_text = captcha.generate()
        request.session['captcha_text'] = captcha_text.strip()  # Обновляем текст капчи

    else:
        form = UserRegistrationForm()
        # Генерируем капчу только для GET-запроса
        captcha = CustomCaptcha()
        image, captcha_text = captcha.generate()
        request.session['captcha_text'] = captcha_text.strip()  # Сохраняем текст капчи в сессии

    # Передаем текст капчи в шаблон
    return render(request, 'main/register.html', {
        'form': form,
        'captcha_image': image,
        'captcha_text': request.session['captcha_text']  # Передаём текст капчи в шаблон
    })

@login_required
def logout_view(request):
    logout(request)
    return redirect('main:index')

@login_required
def applications_view(request):
    applications = Application.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/applications.html', {'applications': applications})

@login_required
def application_create_view(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user  # Устанавливаем текущего пользователя
            application.save()
            form.save_m2m()  # Сохраняем связь ManyToMany
            return redirect('main:applications')  # Перенаправление на страницу с заявками
    else:
        form = ApplicationForm()

    return render(request, 'main/applications_create.html', {'form': form})

@login_required
def application_delete_view(request, id):
    application = get_object_or_404(Application, id=id,
                                    user=request.user)  # Получаем заявку, принадлежащую текущему пользователю
    if request.method == 'POST':
        application.delete()
        return redirect('main:applications')  # Перенаправление на страницу с заявками

    return render(request, 'main/applications_confirm_delete.html', {'application': application})