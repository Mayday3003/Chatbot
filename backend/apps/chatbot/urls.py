from django.urls import path
from . import views

urlpatterns = [
    path('session/', views.CreateSessionView.as_view(), name='create_session'),
    path('message/', views.SendMessageView.as_view(), name='send_message'),
    path('conversations/<str:session_id>/', views.ConversationDetailView.as_view(), name='conversation_detail'),
    path('feedback/', views.FeedbackView.as_view(), name='feedback'),
    path('kb/', views.KBListCreateView.as_view(), name='kb_list_create'),
    path('kb/reindex/', views.ReindexView.as_view(), name='kb_reindex'),
]
