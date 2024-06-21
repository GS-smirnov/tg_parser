from django.db import models
import uuid


class TelegramMessage(models.Model):
    id = models.AutoField(primary_key=True,)
    uuid = models.UUIDField(default=uuid.uuid4,
                            editable=False,)
    channel = models.CharField(max_length=255,)
    message_id = models.IntegerField(unique=True,)
    text = models.TextField()
    date = models.DateTimeField()

    def __str__(self):
        return f"{self.channel} - {self.message_id}"


class Predicts(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4,
                            editable=False,)
    channel = models.CharField(max_length=255,)
    prediction = models.TextField(null=True, blank=True,)

    def __str__(self):
        return f"{self.channel} - {self.prediction}"