from django.db import models
import uuid
from django.conf import settings

class Ticket(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    estado = models.CharField(max_length=50, default='open')
    creador = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='created_tickets', on_delete=models.SET_NULL, null=True)
    asunto = models.CharField(max_length=255)
    prioridad = models.FloatField(default=1.0)
    mensajes = models.JSONField(default=list, blank=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    adjuntos = models.JSONField(default=list, blank=True)
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='assigned_tickets', on_delete=models.SET_NULL, null=True, blank=True)

    def actualizar_estado(self, nuevo_estado: str):
        self.estado = nuevo_estado
        self.save()
        return self

    def recibir_mensaje(self, mensaje: dict):
        self.mensajes.append(mensaje)
        self.save()
        return self

    def asignar_agente(self, agente):
        self.asignado_a = agente
        self.save()
        return self

    def __str__(self):
        return f"Ticket {self.id} - {self.asunto}"
