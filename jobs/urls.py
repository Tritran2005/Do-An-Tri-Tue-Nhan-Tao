from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    # Công khai (Public)
    path('', views.job_list_view, name='job_list'),
    path('<int:pk>/', views.job_detail_view, name='job_detail'),

    # Dành cho Ứng viên (Candidate Apply & Applications)
    path('<int:pk>/apply/', views.apply_job_view, name='job_apply'),
    path('applications/<int:pk>/', views.application_detail_view, name='application_detail'),
    path('my-applications/', views.my_applications_view, name='my_applications'),

    # Dành riêng cho Nhà tuyển dụng (HR Management)
    path('hr/dashboard/', views.hr_dashboard_view, name='hr_dashboard'),
    path('hr/multi-job-screening/', views.hr_multi_job_screening_view, name='hr_multi_job_screening'),
    path('hr/create/', views.job_create_view, name='job_create'),
    path('hr/<int:pk>/candidates/', views.hr_job_candidates_view, name='hr_job_candidates'),
    path('hr/<int:pk>/export-csv/', views.hr_export_candidates_csv_view, name='hr_export_candidates_csv'),
    path('hr/<int:pk>/export-xlsx/', views.hr_export_candidates_xlsx_view, name='hr_export_candidates_xlsx'),
    path('hr/<int:pk>/batch-update-status/', views.hr_batch_update_status_view, name='hr_batch_update_status'),
    path('hr/<int:pk>/batch-upload/', views.hr_batch_upload_cvs_view, name='hr_batch_upload_cvs'),
    path('hr/<int:pk>/edit/', views.job_update_view, name='job_update'),
    path('hr/<int:pk>/delete/', views.job_delete_view, name='job_delete'),
    path('applications/<int:pk>/update-status/', views.application_update_status_view, name='application_update_status'),
]
