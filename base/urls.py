from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('register/', user_register, name='user_register'),
    path('login/', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    path('upload/', upload_file, name='upload_file'),
    path('user_data_list/', access_user_data, name='access_user_data'),
    path('files/', view_files, name='user_data_list'),
    path('files/<int:file_id>/', view_each_file, name='view_each_file'),
    path('schedule_appointment/', schedule_appointment, name='schedule_appointment'),
    path('view_appointments/', view_appointments, name='view_appointments'),
    path('manage_appointments/', manage_appointments, name='manage_appointments'),
    path('schedule_conference/', schedule_conference, name='schedule_conference'),
    path('view_conferences/', view_conferences, name='view_conferences'),
    path('join_conference/<uuid:meeting_id>/', join_conference, name='join_conference'),
]

