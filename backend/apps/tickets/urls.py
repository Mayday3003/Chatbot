from django.urls import path
from .views import TicketListCreateView, TicketRetrieveUpdateView

urlpatterns = [
    path('', TicketListCreateView.as_view(), name='tickets_list_create'),
    path('<uuid:pk>/', TicketRetrieveUpdateView.as_view(), name='ticket_detail'),
]
