from django.shortcuts import get_object_or_404
from django.db import connection
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import TableSchema, FieldSchema
from .serializers import TableSchemaSerializer
from .tasks import import_csv_task
import json
import traceback
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.apps import apps

from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied


class CreateTable(APIView):
    def post(self, request):

        table_name = request.data.get('name')
        fields = request.data.get('fields')  
        print(f"Received request to create table. Table name: {table_name}, Fields: {json.dumps(fields, indent=4)}")

        if not table_name:
            return Response({'error': 'Table name is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not fields:
            return Response({'error': 'Fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        query = f"""
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables 
            WHERE table_name = '{table_name}'
        );
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            table_exists = cursor.fetchone()[0]
        
        if table_exists:
            return Response({'error': f'Table "{table_name}" already exists'}, status=status.HTTP_400_BAD_REQUEST)

        columns = 'id SERIAL PRIMARY KEY, created_at TIMESTAMP DEFAULT NOW()'

        for field in fields:
            field_name = field.get("name")
            field_type = field.get("type")
            is_unique = field.get("is_unique", False) 
            
            if not field_name or not field_type:
                return Response({'error': 'Each field must have a name and type'}, status=status.HTTP_400_BAD_REQUEST)
            
            unique_constraint = " UNIQUE" if is_unique else "" 
            columns += f', "{field_name}" {field_type}{unique_constraint}'

        query = f"""
        CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)

            table_schema = TableSchema.objects.create(name=table_name)
            for field in fields:
                FieldSchema.objects.create(
                    table=table_schema,
                    name=field["name"],
                    field_type=field["type"],
                    is_unique=field.get("is_unique", False) 
                )

            return Response({'message': f'Table "{table_name}" created successfully with fields'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            print(f"Error creating table: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request):
        table_name = request.data.get('name')
        fields = request.data.get('fields')

        print(f"Received request to create table. Table name: {table_name}, Fields: {json.dumps(fields, indent=4)}")

        if not table_name:
            return Response({'error': 'Table name is required'}, status=status.HTTP_400_BAD_REQUEST)
        if not fields:
            return Response({'error': 'Fields are required'}, status=status.HTTP_400_BAD_REQUEST)

        query = f"""
        SELECT EXISTS (
            SELECT 1 FROM information_schema.tables WHERE table_name = '{table_name}'
        );
        """
        with connection.cursor() as cursor:
            cursor.execute(query)
            table_exists = cursor.fetchone()[0]
        
        if table_exists:
            return Response({'error': f'Table "{table_name}" already exists'}, status=status.HTTP_400_BAD_REQUEST)

        columns = 'id SERIAL PRIMARY KEY, created_at TIMESTAMP DEFAULT NOW()'
        for field in fields:
            field_name = field.get("name")
            field_type = field.get("type")

            if not field_name or not field_type:
                return Response({'error': 'Each field must have a name and type'}, status=status.HTTP_400_BAD_REQUEST)

            if field_type.upper() == "VARCHAR":
                field_type = "VARCHAR(255)"

            columns += f', "{field_name}" {field_type}'

        query = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns});'

        try:
            with connection.cursor() as cursor:
                cursor.execute(query)

            table_schema = TableSchema.objects.create(name=table_name)

            for field in fields:
                FieldSchema.objects.create(
                    table=table_schema,
                    name=field["name"],
                    field_type=field["type"] 
                )

            return Response({'message': f'Table "{table_name}" created successfully'}, status=status.HTTP_201_CREATED)

        except Exception as e:
            print(f"Error creating table: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DeleteTable(APIView):
    def delete(self, request, table_name):
        try:
            print(f"Attempting to delete table: {table_name}")  

            query = f'DROP TABLE IF EXISTS "{table_name}" CASCADE;'
            print(f"Executing query: {query}")

            with connection.cursor() as cursor:
                cursor.execute(query)

            deleted_count, _ = TableSchema.objects.filter(name=table_name).delete()
            if deleted_count == 0:
                print(f"Warning: Table schema '{table_name}' was not found in TableSchema model.")

            return Response({'message': f'Table "{table_name}" deleted successfully'}, status=status.HTTP_200_OK)

        except Exception as e:
            error_message = traceback.format_exc() 
            print(f"Error deleting table: {error_message}") 
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
class TableInfo(APIView):
    def get(self, request, table_name):
        """Retrieve table creation date"""
        try:
            table = get_object_or_404(TableSchema, name=table_name)
            return Response({"created_at": table.created_at}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class CRUDOperations(APIView):
    
    def get(self, request, table_name):
        """Retrieve all records from a table"""
        query = f'SELECT * FROM "{table_name}"'
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
                rows = cursor.fetchall()
            return Response(rows, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def post(self, request, table_name):
        """Insert a new record into the table"""
        fields = request.data
        columns = ', '.join(fields.keys())
        values = ', '.join(['%s'] * len(fields))
        
        query = f'INSERT INTO "{table_name}" ({columns}) VALUES ({values})'
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(fields.values()))
            return Response({'message': 'Record added successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, table_name):
        """Update an existing record in the table"""
        record_id = request.data.get("id")
        if not record_id:
            return Response({'error': 'ID is required for update'}, status=status.HTTP_400_BAD_REQUEST)
        
        fields = {k: v for k, v in request.data.items() if k != "id"}
        update_query = ", ".join([f'"{key}" = %s' for key in fields.keys()])
        query = f"UPDATE \"{table_name}\" SET {update_query} WHERE id = %s"
        
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, tuple(fields.values()) + (record_id,))
            return Response({'message': 'Record updated successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, table_name):
        """Delete a record from the table"""
        record_id = request.data.get("id")
        if not record_id:
            return Response({'error': 'ID is required for deletion'}, status=status.HTTP_400_BAD_REQUEST)
        
        query = f"DELETE FROM \"{table_name}\" WHERE id = %s"
        try:
            with connection.cursor() as cursor:
                cursor.execute(query, (record_id,))
            return Response({'message': 'Record deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    def delete_table(self, request, table_name):
        """Delete an entire table"""
        query = f'DROP TABLE IF EXISTS "{table_name}"'
        try:
            with connection.cursor() as cursor:
                cursor.execute(query)
            return Response({'message': f'Table "{table_name}" deleted successfully'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ImportCSV(APIView):
    """API to import CSV data into a table"""

    def post(self, request, table_name):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'CSV file is required'}, status=status.HTTP_400_BAD_REQUEST)

        file_path = default_storage.save(file.name, ContentFile(file.read()))
        import_csv_task.delay(file_path, table_name)

        return Response({"message": "Import started"}, status=status.HTTP_200_OK)
    
class ListTables(APIView):
    def get(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resource.")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
                tables = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
        return JsonResponse({"tables": tables})

    def list_tables(request):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resource.")
        
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
                tables = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
        
        return JsonResponse({"tables": tables})
    

class GetFields(APIView):
    permission_classes = [IsAuthenticated]  # Ensures only authenticated users can access this view

    def get(self, request, table_name):
        if not request.user.is_superuser:
            raise PermissionDenied("You do not have permission to access this resource.")
        
        try:
            # Dynamically get the model class based on the table name
            model = apps.get_model('your_app_name', table_name)
            
            # Fetching the fields dynamically
            fields = [field.name for field in model._meta.fields]
            return JsonResponse({"fields": fields})

        except LookupError:
            return JsonResponse({"error": "Table not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)
