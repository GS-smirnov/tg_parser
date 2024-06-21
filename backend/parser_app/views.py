import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.db.models import Q

from .models import TelegramMessage, TelegramPredict


@method_decorator(csrf_exempt, name='dispatch')
class TelegramMessageView(View):

    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            telegram_message = await sync_to_async(TelegramMessage.objects.create)(
                channel=data['channel'],
                text=data['text'],
                date=data['date']
            )
            return JsonResponse({"status": "Created"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    async def get(self, request, *args, **kwargs):
        try:
            channel = request.GET.get('channel')
            keywords = request.GET.get('keywords')
            limit = int(request.GET.get('limit', 10))

            query = TelegramMessage.objects.all()

            if channel:
                query = query.filter(channel=channel)

            if keywords:
                keyword_list = keywords.split(',')
                query = query.filter(
                    *[Q(text__icontains=keyword) for keyword in keyword_list]
                )

            query = query.order_by('id')[:limit]

            messages = await database_sync_to_async(list)(query.values())
            return JsonResponse({"data": messages}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class TelegramPredictView(View):

    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            telegram_predict, created = await database_sync_to_async(TelegramPredict.objects.update_or_create)(
                channel=data['channel'],
                defaults={'prediction': data['prediction']}
            )

            return JsonResponse({"status": "Created" if created else "Updated"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    async def get(self, request, *args, **kwargs):
        try:
            channel = request.GET.get('channel')

            if channel:
                predict = await database_sync_to_async(TelegramPredict.objects.get)(channel=channel)
                data = {
                    'channel': predict.channel,
                    'prediction': predict.prediction,
                    'updated_at': predict.updated_at,
                }
                return JsonResponse({"data": data}, status=status.HTTP_200_OK)
            else:
                queryset = await database_sync_to_async(list)(TelegramPredict.objects.all().values())
                return JsonResponse({"data": queryset}, status=status.HTTP_200_OK)
        except TelegramPredict.DoesNotExist:
            return JsonResponse({"error": "Predict for the given channel does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
