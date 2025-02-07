from django.urls import path
from .views import CreateTable, CRUDOperations, ImportCSV, DeleteTable, ListTables, GetFields
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('create_table/', CreateTable.as_view(), name='create_table'),
    path('crud/<str:table_name>/', CRUDOperations.as_view(), name='crud_operations'),
    path('import_csv/<str:table_name>/', ImportCSV.as_view(), name='import_csv'),
    path('delete_table/<str:table_name>/', DeleteTable.as_view(), name='delete_table'),
    path('list_tables/', ListTables.as_view(), name='list_tables'),
    path('get_table_fields/<str:table_name>/', GetFields.as_view(), name='get_table_fields'),
]
