from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegistrationForm, ApplicationForm
from .models import Application

def index(request):
    completed_applications = Application.objects.filter(status='completed').order_by('-created_at')[:5]
    in_progress_count = Application.objects.filter(status='in_progress').count()

    return render(request, 'main/index.html', {
        'completed_applications': completed_applications,
        'in_progress_count': in_progress_count,
    })

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('main:index')
    else:
        form = UserRegistrationForm()
    return render(request, 'main/register.html', {'form': form})

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

@login_required
def logout_view(request):
    logout(request)
    return redirect('main:index')

# @login_required
# def application_create_view(request):
#     if request.method == 'POST':
#         form = ApplicationForm(request.POST, request.FILES)
#         if form.is_valid():
#             application = form.save(commit=False)
#             application.user = request.user
#             application.save()
#             return redirect('main:applications')
#     else:
#         form = ApplicationForm()
#     return render(request, 'main/application_create.html', {'form': form})

@login_required
def applications_view(request):
    applications = Application.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'main/applications.html', {'applications': applications})

# def application_delete_view(request, id):
#     application = get_object_or_404(Application, id=id)
#     if request.method == 'POST':
#         application.delete()
#         return redirect('main:applications')  # Перенаправление на страницу заявок после удаления
#     return render(request, 'main/application_confirm_delete.html', {'application': application})