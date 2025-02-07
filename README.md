# Data_Management

# Prerequisites
•	Python 3.12 installed
•	Django 5 installed
•	PostgreSQL 16 installed and running

# Steps

1.	Clone the repository:
    - git clone <repository_url>
    - cd data-management-system
  
2.	Create and activate a virtual environment:
    - python -m venv venv
    - source venv/bin/activate  # On Windows use `venv\Scripts\activate`
      
3.	Install dependencies:
    - pip install -r requirements.txt
      
4.	Configure PostgreSQL database settings in settings.py
   
5.	Run migrations: python manage.py migrate
   
6.	Start the server: python manage.py runserver
    
7.	Create a superuser: python manage.py createsuperuser
8.	Start the frontend server: npm start
    
# API Endpoints
# Schema Management

•	POST /api/schema/ - Create a new table
•	PUT /api/schema/<table_name>/ - Modify table schema
•	DELETE /api/schema/<table_name>/ - Delete a table
CRUD Operations
•	POST /api/crud/<table_name>/ - Create a record
•	GET /api/crud/<table_name>/ - Read records (supports filtering & pagination)
•	PUT /api/crud/<table_name>/<record_id>/ - Update a record
•	DELETE /api/crud/<table_name>/<record_id>/ - Delete a record
CSV Import
•	POST /api/import/ - Upload CSV file for bulk import
