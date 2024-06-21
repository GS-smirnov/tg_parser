import json

from asgiref.sync import sync_to_async
from channels.db import database_sync_to_async
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from django.db.models import Q
from django.db.models.functions import Lower
from .parser import parse_telegram_channel

from .models import Messages, Predicts, Companies, Keywords, Channels


@method_decorator(csrf_exempt, name='dispatch')
class ChannelView(View):

    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            telegram_predict, created = await database_sync_to_async(Predicts.objects.update_or_create)(
                channel=data['channel'],
                keywords={'prediction': data['prediction']}
            )

            return JsonResponse({"status": "Created" if created else "Updated"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    async def get(self, request, *args, **kwargs):
        try:
            channel = request.GET.get('channel')

            if channel:
                predict = await database_sync_to_async(Predicts.objects.get)(channel=channel)
                data = {
                    'channel': predict.channel,
                    'prediction': predict.prediction,
                    'updated_at': predict.updated_at,
                }
                return JsonResponse({"data": data}, status=status.HTTP_200_OK)
            else:
                queryset = await database_sync_to_async(list)(Predicts.objects.all().values())
                return JsonResponse({"data": queryset}, status=status.HTTP_200_OK)
        except Predicts.DoesNotExist:
            return JsonResponse({"error": "Predict for the given channel does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class MessagesView(View):

    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            telegram_message = await sync_to_async(Messages.objects.create)(
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

            query = Messages.objects.all()

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
class PredictsView(View):

    async def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            telegram_predict, created = await database_sync_to_async(Predicts.objects.update_or_create)(
                company=data['company'],
                defaults={'prediction': data['prediction']}
            )

            return JsonResponse({"status": "Created" if created else "Updated"}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    async def get(self, request, *args, **kwargs):
        try:
            channel = request.GET.get('channel')

            if channel:
                predict = await database_sync_to_async(Predicts.objects.get)(channel=channel)
                data = {
                    'company': predict.company,
                    'prediction': predict.prediction,
                    'updated_at': predict.updated_at,
                }
                return JsonResponse({"data": data}, status=status.HTTP_200_OK)
            else:
                queryset = await database_sync_to_async(list)(Predicts.objects.all().values())
                return JsonResponse({"data": queryset}, status=status.HTTP_200_OK)
        except Predicts.DoesNotExist:
            return JsonResponse({"error": "Predict for the given channel does not exist"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class CompanyMessagesView(View):

    async def get(self, request, *args, **kwargs):
        try:
            company_name = request.GET.get('company')
            limit = int(request.GET.get('limit', 10))

            if not company_name:
                return JsonResponse({"error": "Company name is required"}, status=status.HTTP_400_BAD_REQUEST)

            company_exists = await database_sync_to_async(Companies.objects.filter(company__iexact=company_name).exists)()
            if not company_exists:
                return JsonResponse({"error": "Company not found"}, status=status.HTTP_404_NOT_FOUND)

            keywords_obj = await database_sync_to_async(Keywords.objects.first)()
            if not keywords_obj:
                return JsonResponse({"error": "Keywords not found"}, status=status.HTTP_404_NOT_FOUND)

            keywords = keywords_obj.keywords.split(':')

            messages = Messages.objects.annotate(lower_text=Lower('text')).filter(lower_text__icontains=company_name.lower()).order_by('date')

            query = Q()
            for keyword_group in keywords:
                group_query = Q()
                for keyword in keyword_group.split(','):
                    group_query |= Q(lower_text__icontains=keyword.lower())
                query &= group_query

            filtered_messages = messages.filter(query).values('id', 'uuid', 'channel', 'text', 'date')[:limit]

            results = await database_sync_to_async(list)(filtered_messages)
            return JsonResponse({"data": results}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class ParseTelegramChannelsView(View):

    def post(self, request, *args, **kwargs):
        try:
            channels = Channels.objects.all()
            if not channels:
                return JsonResponse({"error": "No channels found"}, status=status.HTTP_404_NOT_FOUND)

            for channel in channels:
                parse_telegram_channel(channel.channel)

            return JsonResponse({"status": "Parsing started for all channels"}, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
