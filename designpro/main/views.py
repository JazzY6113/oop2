from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ApplicationForm
from .models import Application, Category, CategoryStatus
from .my_captcha import CustomCaptcha
from django.contrib.auth.decorators import user_passes_test
import logging

logger = logging.getLogger(__name__)

def captcha_view(request):
    captcha = CustomCaptcha()
    image, text = captcha.generate()
    request.session['captcha_text'] = text

    if request.method == 'POST':
        user_input = request.POST.get('captcha_input')
        if user_input == request.session.get('captcha_text'):
            return render(request, 'success.html')
        else:
            return render(request, 'captcha_template.html',
                          {'captcha_image': image, 'error': 'Неправильный ввод капчи'})

    return render(request, 'captcha_template.html', {'captcha_image': image})


def index(request):
    # Получаем заявки, у которых есть категории со статусом "Выполнено"
    completed_applications = Application.objects.filter(categorystatus__status='completed').distinct().order_by('-created_at')[:4]

    # Фильтруем категории для каждой заявки
    for application in completed_applications:
        application.completed_categories = application.categories.filter(categorystatus__status='completed')

    logger.debug(f"Completed applications: {list(completed_applications)}")

    in_progress_count = CategoryStatus.objects.filter(status='in_progress').count()
    completed_count = CategoryStatus.objects.filter(status='completed').count()
    new_count = CategoryStatus.objects.filter(status='new').count()

    return render(request, 'main/index.html', {
        'completed_applications': completed_applications,
        'in_progress_count': in_progress_count,
        'completed_count': completed_count,
        'new_count': new_count,
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
    image = None
    captcha_text = None

    if 'captcha_text' not in request.session:
        captcha = CustomCaptcha()
        image, captcha_text = captcha.generate()
        request.session['captcha_text'] = captcha_text.strip()

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        user_input = request.POST.get('captcha_input', '').strip()

        if form.is_valid():
            if user_input.lower() == request.session.get('captcha_text').lower():
                user = form.save(commit=False)
                user.set_password(form.cleaned_data['password'])
                user.save()
                login(request, user)
                del request.session['captcha_text']
                return redirect('main:index')
            else:
                form.add_error(None, "Неправильный ввод капчи")

        captcha = CustomCaptcha()
        image, captcha_text = captcha.generate()
        request.session['captcha_text'] = captcha_text.strip()

    else:
        form = UserRegistrationForm()
        captcha = CustomCaptcha()
        image, captcha_text = captcha.generate()
        request.session['captcha_text'] = captcha_text.strip()

    return render(request, 'main/register.html', {
        'form': form,
        'captcha_image': image,
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
        applications = applications.filter(categorystatus__status=status_filter).distinct()

    for application in applications:
        application.can_delete = application.categorystatus_set.filter(status='new').exists()

    return render(request, 'main/applications.html', {'applications': applications, 'status_filter': status_filter})

@login_required
def application_create_view(request):
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.user = request.user
            application.save()
            for category in form.cleaned_data['categories']:
                CategoryStatus.objects.create(application=application, category=category)
            return redirect('main:applications')
    else:
        form = ApplicationForm()

    return render(request, 'main/applications_create.html', {'form': form})

@login_required
def application_delete_view(request, id):
    application = get_object_or_404(Application, id=id, user=request.user)

    if application.status != 'new':
        return render(request, 'main/applications_confirm_delete.html', {
            'application': application,
            'error': 'Нельзя удалить заявку с таким статусом. Можно удалить только заявки со статусом "Новая".'
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
        category_id = request.POST.get('category_id')
        new_status = request.POST.get('status')

        category_status = get_object_or_404(CategoryStatus, application=application, category_id=category_id)
        category_status.status = new_status
        category_status.save()

        return redirect('main:applications')

    category_statuses = CategoryStatus.objects.filter(application=application)
    return render(request, 'main/change_application_status.html', {'application': application, 'category_statuses': category_statuses})

@login_required
@user_passes_test(is_admin)
def manage_categories(request):
    categories = Category.objects.all()

    if request.method == 'POST':
        if 'add_category' in request.POST:
            new_category_name = request.POST.get('new_category')
            if new_category_name:
                Category.objects.create(name=new_category_name)
        elif 'delete_category' in request.POST:
            category_id = request.POST.get('category_id')
            Category.objects.filter(id=category_id).delete()

        return redirect('main:manage_categories')

    return render(request, 'main/manage_categories.html', {'categories': categories})