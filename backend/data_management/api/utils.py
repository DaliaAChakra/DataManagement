from django.core.mail import send_mail
from django.http import JsonResponse
from django.core.files.storage import default_storage
import csv

def send_notification(email, message):
    send_mail(
        'Import Completed',
        message,
        'dalia2000w@gmail.com', 
        [email], 
        fail_silently=False,
    )

def handle_csv_upload(request):
    if request.method == 'POST' and request.FILES.get('file'):
        try:
            user_email = request.user.email if request.user.is_authenticated else 'user@example.com'
            csv_file = request.FILES['file']

            path = default_storage.save('temp.csv', csv_file)

            with default_storage.open(path) as f:
                reader = csv.reader(f)
                for row in reader:
                    print(row)
            
            send_notification(user_email, "The CSV file was successfully imported.")
            return JsonResponse({'status': 'success', 'message': 'Import completed successfully'})
        
        except Exception as e:
            print(f"Error during CSV import: {e}")

            send_notification(user_email, f"Something went wrong during the CSV import: {str(e)}")
            
            return JsonResponse({'status': 'error', 'message': 'An error occurred during the import'}, status=500)
    
    return JsonResponse({'status': 'error', 'message': 'No file uploaded'}, status=400)
