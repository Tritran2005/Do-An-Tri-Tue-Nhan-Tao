from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # URL chuyển hướng theo vai trò (Role-based views)
    path('jobs/', views.candidate_job_board_view, name='job_board'),
    path('hr/dashboard/', views.hr_dashboard_view, name='hr_dashboard'),

    # Quản trị người dùng & phân quyền 3-Tier RBAC (Dành riêng cho Admin)
    path('admin-users/', views.admin_users_view, name='admin_users'),
    path('admin-users/<int:user_id>/update-role/', views.update_user_role_view, name='update_user_role'),

    # P2 – Trang hồ sơ cá nhân (Profile)
    path('profile/', views.profile_view, name='profile'),
]
