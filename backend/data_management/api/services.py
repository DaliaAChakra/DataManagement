from django.db import connection
import csv

ALLOWED_COLUMN_TYPES = {"TEXT", "INTEGER", "BOOLEAN", "DATE", "TIMESTAMP"}

def is_valid_table(table_name):
    """Ensure table exists in the TableSchema model."""
    from .models import TableSchema
    return TableSchema.objects.filter(name=table_name).exists()

def validate_fields(fields):
    """Check that field names are valid and types are allowed."""
    return all(field["name"].isidentifier() and field["type"].upper() in ALLOWED_COLUMN_TYPES for field in fields)

def create_table(table_name, fields):
    """Dynamically create a table with validated fields."""
    field_definitions = ', '.join([f'"{f["name"]}" {f["type"]}' for f in fields])
    query = f'CREATE TABLE IF NOT EXISTS "{table_name}" (id SERIAL PRIMARY KEY, {field_definitions}, created_at TIMESTAMP DEFAULT NOW())'
    with connection.cursor() as cursor:
        cursor.execute(query)

def bulk_insert_csv(file_path, table_name):
    """Fast CSV import using PostgreSQL COPY."""
    with connection.cursor() as cursor:
        with open(file_path, 'r', encoding='utf-8') as f:
            cursor.copy_expert(f"COPY {table_name} FROM STDIN WITH CSV HEADER", f)
