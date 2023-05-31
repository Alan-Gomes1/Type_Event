from django.contrib import admin

from .models import Evento

admin.site.register(Evento)


class EventoAdmin(admin.ModelAdmin):
    pass
