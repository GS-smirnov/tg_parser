from django.urls import path
from .views import MessagesView, PredictsView, CompanyMessagesView, ParseTelegramChannelsView, GeneratePredictionView

urlpatterns = [
    path('message/', MessagesView.as_view(), name='telegram-message'),
    path('predict/', PredictsView.as_view(), name='telegram-predict'),
    path('filtered_messages/', CompanyMessagesView.as_view(), name='filtered-messages'),
    path('parse_channels/', ParseTelegramChannelsView.as_view(), name='parse-channels'),
    path('generate_predict/', GeneratePredictionView.as_view(), name='parse-channels'),
]

