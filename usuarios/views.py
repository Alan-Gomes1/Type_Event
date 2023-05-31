from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import auth
import re


def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'Senhas diferentes')
            return redirect(reverse('cadastro'))

        regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*[0-9]).{8,}$')
        if not regex.match(senha):
            messages.add_message(request, constants.ERROR, 'Senha inválida')

        user = User.objects.filter(username=username)
        if user.exists():
            messages.add_message(
                request, constants.ERROR, 'Usuário já cadastrado'
            )
            return redirect(reverse('cadastro'))

        user = User.objects.create_user(
            username=username, email=email, password=senha
        )
        messages.add_message(request, constants.SUCCESS, 'Usuário cadastrado')

    return redirect(reverse('login'))


def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = auth.authenticate(username=username, password=senha)
        if not user:
            messages.add_message(
                request, constants.ERROR, 'Usuário ou senha inválidos'
            )
            return redirect(reverse('login'))

        auth.login(request, user)
        return redirect(reverse('novo_evento'))
