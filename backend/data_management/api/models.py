from django.db import models

class TableSchema(models.Model):
    name = models.CharField(max_length=255, unique=True)

class FieldSchema(models.Model):
    table = models.ForeignKey(TableSchema, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=255)
    is_unique = models.BooleanField(default=False) 