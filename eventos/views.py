import csv
import os
import sys
from io import BytesIO
from secrets import token_urlsafe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from PIL import Image, ImageDraw, ImageFont

from .models import Certificado, Evento


@login_required(login_url='/usuarios/login')
def novo_evento(request):
    if request.method == "GET":
        return render(request, 'novo_evento.html')
    elif request.method == "POST":
        nome = request.POST.get('nome')
        descricao = request.POST.get('descricao')
        data_inicio = request.POST.get('data_inicio')
        data_termino = request.POST.get('data_termino')
        carga_horaria = request.POST.get('carga_horaria')

        cor_primaria = request.POST.get('cor_primaria')
        cor_secundaria = request.POST.get('cor_secundaria')
        cor_fundo = request.POST.get('cor_fundo')

        logo = request.FILES.get('logo')

        evento = Evento(
            criador=request.user,
            nome=nome,
            descricao=descricao,
            data_inicio=data_inicio,
            data_termino=data_termino,
            carga_horaria=carga_horaria,
            cor_primaria=cor_primaria,
            cor_secundaria=cor_secundaria,
            cor_fundo=cor_fundo,
            logo=logo,
        )

        evento.save()

        messages.add_message(
            request, constants.SUCCESS, 'Evento cadastrado com sucesso'
        )
        return redirect(reverse('novo_evento'))


@login_required(login_url='/usuarios/login')
def gerenciar_evento(request):
    if request.method == "GET":
        nome = request.GET.get('nome')
        eventos = Evento.objects.filter(criador=request.user)

        if nome:
            eventos = Evento.objects.filter(nome__icontains=nome)

        return render(request, 'gerenciar_evento.html', {'eventos': eventos})


@login_required(login_url='/usuarios/login')
def inscrever_evento(request, id):
    evento = get_object_or_404(Evento, id=id)
    if request.method == 'GET':
        return render(request, 'inscrever_evento.html', {'evento': evento})
    elif request.method == 'POST':
        user = request.user
        evento.participantes.add(user)
        evento.save()

        messages.add_message(
            request, constants.SUCCESS, 'Inscrição realizada com sucesso'
        )
        return redirect(reverse('inscrever_evento', kwargs={'id': id}))


@login_required(login_url='/usuarios/login')
def participantes_evento(request, id):
    evento = get_object_or_404(Evento, id=id)

    if request.user not in evento.participantes.all():
        raise Http404('Não autorizado')

    if request.method == 'GET':
        participantes = evento.participantes.all()[:10]
        return render(
            request, 'participantes_evento.html',
            {'evento': evento, 'participantes': participantes}
        )


@login_required(login_url='/usuarios/login')
def gerar_csv(request, id):
    evento = get_object_or_404(Evento, id=id)

    if not evento.criador == request.user:
        raise Http404('Não autorizado')

    participantes = evento.participantes.all()
    token = f'{token_urlsafe(6)}.csv'
    path = os.path.join(settings.MEDIA_ROOT, token)

    with open(path, 'w') as arq:
        writer = csv.writer(arq, delimiter=',')
        for participante in participantes:
            x = (participante.username, participante.email)
            writer.writerow(x)

    return redirect(f'/media/csv/{token}.csv')


@login_required(login_url='/usuarios/login')
def certificados_evento(request, id):
    evento = get_object_or_404(Evento, id=id)
    participantes = evento.participantes.all()

    if request.user not in participantes:
        raise Http404('Não autorizado')

    if request.method == 'GET':
        certificados = Certificado.objects.filter(evento=evento).count()
        qtd_certificados = participantes.count() - certificados
        qtd_certificados = 0 if qtd_certificados < 0 else qtd_certificados
        return render(
            request, 'certificados_evento.html',
            {'evento': evento, 'qtd_certificados': qtd_certificados}
        )


@login_required(login_url='/usuarios/login')
def gerar_certificado(request, id):
    evento = get_object_or_404(Evento, id=id)
    participantes = evento.participantes.all()

    if request.user not in participantes:
        raise Http404('Não autorizado')

    path_template = os.path.join(
        settings.BASE_DIR,
        'templates/static/evento/img/template_certificado.png'
    )
    path_fonte = os.path.join(
        settings.BASE_DIR, 'templates/static/fontes/arimo.ttf'
    )

    for participante in participantes:
        img = Image.open(path_template)
        draw = ImageDraw.Draw(img)

        fonte_nome = ImageFont.truetype(path_fonte, 80)
        fonte_info = ImageFont.truetype(path_fonte, 40)

        draw.text(
            (230, 630),
            f"{participante.username}", font=fonte_nome, fill=(0, 0, 0)
        )
        draw.text((761, 774), f"{evento.nome}",
                  font=fonte_info, fill=(0, 0, 0))
        draw.text((816, 841), f"{evento.carga_horaria} horas",
                  font=fonte_info, fill=(0, 0, 0))

        output = BytesIO()
        img.save(output, format='PNG')
        output.seek(0)

        img_final = InMemoryUploadedFile(
            output,
            'ImageField',
            f'{token_urlsafe(8)}.png',
            'image/jpeg',
            sys.getsizeof(output),
            None
        )

        certificado_gerado = Certificado(
            certificado=img_final,
            participante=participante,
            evento=evento
        )
        certificado_gerado.save()

    messages.add_message(
        request, constants.SUCCESS, 'Certificado gerado com sucesso!'
    )
    return redirect(reverse('certificados_evento', kwargs={'id': id}))


@login_required(login_url='/usuarios/login')
def procurar_certificado(request, id):
    evento = get_object_or_404(Evento, id=id)
    participantes = evento.participantes.all()

    if request.user not in participantes:
        raise Http404('Não autorizado')

    email = request.POST.get('email')
    certificado = Certificado.objects.filter(
        participante__email=email, evento=evento
    ).first()

    if not certificado:
        messages.add_message(
            request, constants.ERROR, 'O certificado não foi gerado!'
        )
        return redirect(reverse('certificados_evento', kwargs={'id': id}))

    return redirect(certificado.certificado.url)
