from django.db import models
import uuid


class TelegramMessage(models.Model):
    id = models.AutoField(primary_key=True,)
    uuid = models.UUIDField(default=uuid.uuid4,
                            editable=False,)
    channel = models.CharField(max_length=255,)
    text = models.TextField()
    date = models.DateTimeField()

    class Meta:
        db_table = 'telegram_message'

    def __str__(self):
        return f"{self.channel} - {self.text}"


class TelegramPredict(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4,
                            editable=False,)
    channel = models.CharField(max_length=255,)
    prediction = models.TextField(null=True, blank=True,)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'telegram_predict'

    def __str__(self):
        return f"{self.channel} - {self.prediction}"
