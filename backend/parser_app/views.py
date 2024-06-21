import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from .models import TelegramMessage


@method_decorator(csrf_exempt, name='dispatch')
class TelegramMessageView(View):

    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            telegram_message = await sync_to_async(TelegramMessage.objects.create)(
                channel=data['channel'],
                message_id=data['message_id'],
                text=data['text'],
                date=data['date']
            )
            return JsonResponse({"status": "Created"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    async def get(self, request, *args, **kwargs):
        try:
            queryset = await database_sync_to_async(list)(TelegramMessage.objects.all().values())
            return JsonResponse({"data": queryset}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramChannelMessagesView(View):

    async def get(self, request, *args, **kwargs):
        try:
            channel = request.GET.get('channel')
            if not channel:
                return JsonResponse({"error": "Channel is required"}, status=status.HTTP_400_BAD_REQUEST)

            messages = await database_sync_to_async(list)(
                TelegramMessage.objects.filter(channel=channel).order_by('id').values()
            )
            return JsonResponse({"data": messages}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)