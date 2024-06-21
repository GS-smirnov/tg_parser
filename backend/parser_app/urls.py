from django.urls import path
from .views import TelegramMessageView, TelegramPredictView

urlpatterns = [
    path('message/', TelegramMessageView.as_view(), name='telegram-message'),
    path('predict/', TelegramPredictView.as_view(), name='telegram-predict'),
]

