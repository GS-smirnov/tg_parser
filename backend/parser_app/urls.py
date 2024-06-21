from django.urls import path
from .views import TelegramMessageView, TelegramChannelMessagesView

urlpatterns = [
    path('messages/', TelegramMessageView.as_view(), name='telegram-messages'),
    path('channel_messages/', TelegramChannelMessagesView.as_view(), name='telegram-channel-messages'),
]

