from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'asunto', 'estado', 'creador', 'asignado_a', 'fecha_creacion')
    search_fields = ('asunto',)
