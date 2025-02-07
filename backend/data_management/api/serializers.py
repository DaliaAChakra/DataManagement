from rest_framework import serializers
from .models import TableSchema, FieldSchema

class FieldSchemaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldSchema
        fields = '__all__'

class TableSchemaSerializer(serializers.ModelSerializer):
    fields = FieldSchemaSerializer(many=True)

    class Meta:
        model = TableSchema
        fields = '__all__'
