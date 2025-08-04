# users/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Успешная регистрация!")
            return redirect('posts:post_list')
        else:
            messages.error(request, "Ошибка регистрации. Пожалуйста, исправьте ошибки.")
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})