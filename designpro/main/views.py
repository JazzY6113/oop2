from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ApplicationForm
from .models import Application, Category
from .my_captcha import CustomCaptcha
from django.contrib.auth.decorators import user_passes_test

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
    completed_applications = Application.objects.filter(status='completed')
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
    if request.user.is_superuser:
        applications = Application.objects.all().order_by('-created_at')
    else:
        applications = Application.objects.filter(user=request.user).order_by('-created_at')

    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)

    return render(request, 'main/applications.html', {'applications': applications, 'status_filter': status_filter})

@login_required
def application_create_view(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user  # Устанавливаем текущего пользователя
            application.save()
            form.save_m2m()  # Сохраняем связь ManyToMany
            return redirect('main:applications')
    else:
        form = ApplicationForm()

    return render(request, 'main/applications_create.html', {'form': form})

@login_required
def application_delete_view(request, id):
    application = get_object_or_404(Application, id=id, user=request.user)

    if application.status in ['in_progress', 'completed']:
        return render(request, 'main/applications_confirm_delete.html', {
            'application': application,
            'error': 'Нельзя удалить заявку с таким статусом.'
        })

    if request.method == 'POST':
        application.delete()
        return redirect('main:applications')

    return render(request, 'main/applications_confirm_delete.html', {'application': application})

def is_admin(user):
    return user.is_superuser

@login_required
def change_application_status(request, id):
    application = get_object_or_404(Application, id=id)

    if request.method == 'POST':
        if application.status == 'new':
            new_status = request.POST.get('status')
            comment = request.POST.get('comment')

            if not comment:
                return render(request, 'main/change_application_status.html', {
                    'application': application,
                    'error': 'Необходимо указать комментарий.'
                })

            application.comment = comment  # Сохраняем комментарий
            if new_status == 'in_progress':
                application.status = new_status
            elif new_status == 'completed':
                # Проверка на наличие изображения
                if 'image' not in request.FILES or not request.FILES['image']:
                    return render(request, 'main/change_application_status.html', {
                        'application': application,
                        'error': 'Необходимо прикрепить изображение дизайна.'
                    })
                application.image = request.FILES['image']  # Сохраняем загруженное изображение
                application.status = new_status

            application.save()
            return redirect('main:applications')

    return render(request, 'main/change_application_status.html', {'application': application})

@login_required
@user_passes_test(is_admin)
def manage_categories(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        # Обработка добавления категории
        if 'add_category' in request.POST:
            new_category_name = request.POST.get('new_category')
            if new_category_name:
                Category.objects.create(name=new_category_name)

        # Обработка удаления категории
        elif 'delete_category' in request.POST:
            category_id = request.POST.get('category_id')
            Category.objects.filter(id=category_id).delete()

        return redirect('main:manage_categories')

    return render(request, 'main/manage_categories.html', {'categories': categories})