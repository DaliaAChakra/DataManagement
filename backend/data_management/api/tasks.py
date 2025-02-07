from celery import shared_task
from django.db import connection
import csv
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from .models import TableSchema

@shared_task
def import_csv_task(file_path, table_name, user_email):
    table = get_object_or_404(TableSchema, name=table_name)

    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            errors = []
            successful_imports = 0

            for row in reader:
                for field in table.required_fields:
                    if not row.get(field):
                        errors.append(f"Missing required field: {field}")
                        continue

                if 'email' in row:
                    if TableSchema.objects.filter(email=row['email']).exists():
                        errors.append(f"Duplicate email found: {row['email']}")
                        continue

                columns = ', '.join([f'"{key}"' for key in row.keys()])
                values = ', '.join(['%s'] * len(row))
                query = f"INSERT INTO \"{table_name}\" ({columns}) VALUES ({values})"

                with connection.cursor() as cursor:
                    cursor.execute(query, tuple(row.values()))
                    successful_imports += 1

        # Success Email
        subject = "CSV Import Successful"
        message = f"Your CSV file has been successfully imported into the '{table_name}' table.\n\nTotal Records Imported: {successful_imports}"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])

        return {"message": f"Successfully imported {successful_imports} records", "errors": errors}

    except Exception as e:
        # Failure Email
        subject = "CSV Import Failed"
        message = f"An error occurred while importing your CSV into the '{table_name}' table.\n\nError: {str(e)}"
        send_mail(subject, message, settings.EMAIL_HOST_USER, [user_email])

        return {"error": str(e)}
