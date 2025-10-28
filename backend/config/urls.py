from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/tickets/', include('apps.tickets.urls')),
    path('api/chat/', include('apps.chatbot.urls')),
]
