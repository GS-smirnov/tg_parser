from django.db import models
import uuid


class Companies(models.Model):
    id = models.AutoField(primary_key=True,)
    uuid = models.UUIDField(default=uuid.uuid4,
                            editable=False,)
    company = models.CharField(max_length=255,)

    class Meta:
        db_table = 'companies'

    def __str__(self):
        return f"{self.company}"


class Keywords(models.Model):
    id = models.AutoField(primary_key=True,)
    uuid = models.UUIDField(default=uuid.uuid4,
                            editable=False,)
    keywords = models.TextField()

    class Meta:
        db_table = 'keywords'

    def __str__(self):
        return f"{self.keywords}"


class Channels(models.Model):
    id = models.AutoField(primary_key=True,)
    uuid = models.UUIDField(default=uuid.uuid4,
                            editable=False,)
    channel = models.TextField()

    class Meta:
        db_table = 'channels'

    def __str__(self):
        return f"{self.channel}"


class Messages(models.Model):
    id = models.AutoField(primary_key=True,)
    uuid = models.UUIDField(default=uuid.uuid4,
                            editable=False,)
    channel = models.CharField(max_length=255,)
    text = models.TextField()
    date = models.DateTimeField()

    class Meta:
        db_table = 'messages'

    def __str__(self):
        return f"{self.channel} - {self.text}"


class Predicts(models.Model):
    id = models.AutoField(primary_key=True)
    uuid = models.UUIDField(default=uuid.uuid4,
                            editable=False,)
    company = models.CharField(max_length=255,)
    prediction = models.TextField(null=True, blank=True,)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'predicts'

    def __str__(self):
        return f"{self.company} - {self.prediction}"
