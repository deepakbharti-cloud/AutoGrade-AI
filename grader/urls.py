from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # Home page
    path('',               views.home,                  name='home'),
    
    # Dashboard
    path('dashboard/',     views.dashboard,             name='dashboard'),

    # Auth
    path('login/',         auth_views.LoginView.as_view(template_name='grader/login.html'), name='login'),
    path('logout/',        auth_views.LogoutView.as_view(), name='logout'),
    path('register/', views.register, name='register'),
    
    # Papers
    path('papers/',        views.paper_list,            name='paper_list'),
    path('papers/create/', views.paper_create,          name='paper_create'),
    path('papers/<int:pk>/questions/', views.paper_questions, name='paper_questions'),

    # Students
    path('students/',      views.student_list,          name='student_list'),
    path('students/add/',  views.student_create,        name='student_create'),

    # Copy processing
    path('upload/',        views.upload_copy,           name='upload_copy'),
    path('process/',       views.process_copy,          name='process_copy'),

    # Results
    path('result/<int:pk>/',          views.result_view,     name='result_view'),
    path('result/<int:pk>/pdf/',      views.download_pdf,    name='download_pdf'),
    path('result/<int:pk>/whatsapp/', views.send_whatsapp,   name='send_whatsapp'),
    path('results/',                  views.all_results,     name='all_results'),

    # Extra features
    path('analytics/',       views.class_analytics,     name='class_analytics'),
    path('export/excel/',    views.export_excel,         name='export_excel'),
    path('export/bulk-pdf/', views.bulk_pdf_download,   name='bulk_pdf_download'),
    path('student-portal/',  views.student_result_portal, name='student_portal'),
]
