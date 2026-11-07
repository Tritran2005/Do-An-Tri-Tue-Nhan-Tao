from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.http import url_has_allowed_host_and_scheme
from django.db.models import Q, Count
from django.core.paginator import Paginator
from functools import wraps
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm
from .models import User

# ==========================================
# CUSTOM ROLE-BASED ACCESS DECORATORS
# ==========================================
def admin_required(view_func):
    """Decorator đảm bảo chỉ Admin mới có quyền truy cập."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Vui lòng đăng nhập với tài khoản Quản trị viên (Admin).")
            return redirect('accounts:login')
        if not request.user.is_admin:
            messages.error(request, "Truy cập bị từ chối: Trang này chỉ dành cho Quản trị viên (Admin).")
            return redirect('jobs:job_list')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def candidate_required(view_func):
    """Decorator đảm bảo chỉ Ứng viên (Candidate) mới có quyền truy cập."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Vui lòng đăng nhập để tiếp tục.")
            return redirect('accounts:login')
        if not request.user.is_candidate and not request.user.is_admin:
            messages.error(request, "Truy cập bị từ chối: Trang này chỉ dành cho Ứng viên.")
            return redirect('jobs:hr_dashboard')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def hr_required(view_func):
    """Decorator đảm bảo chỉ Nhà tuyển dụng (HR) hoặc Admin mới có quyền truy cập."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Vui lòng đăng nhập tài khoản Nhà tuyển dụng.")
            return redirect('accounts:login')
        if not request.user.is_hr and not request.user.is_admin:
            messages.error(request, "Truy cập bị từ chối: Trang này chỉ dành cho Nhà tuyển dụng (HR).")
            return redirect('jobs:job_list')
        return view_func(request, *args, **kwargs)
    return _wrapped_view

# ==========================================
# HELPER: REDIRECT BY ROLE
# ==========================================
def get_redirect_url_for_user(user, next_url=None):
    """Hàm định tuyến thông minh theo Role của người dùng."""
    if next_url and url_has_allowed_host_and_scheme(next_url, allowed_hosts=None):
        return next_url
    if user.is_admin:
        return 'accounts:admin_users'
    if user.is_hr:
        return 'jobs:hr_dashboard'
    return 'jobs:job_list'

# ==========================================
# AUTHENTICATION VIEWS
# ==========================================
def register_view(request):
    """View đăng ký tài khoản với lựa chọn Vai trò (Candidate / HR)."""
    if request.user.is_authenticated:
        return redirect(get_redirect_url_for_user(request.user))

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Tự động đăng nhập sau khi đăng ký thành công
            login(request, user)
            role_label = user.get_role_display()
            messages.success(
                request,
                f"Đăng ký thành công! Chào mừng {user.get_full_name() or user.username} tham gia hệ thống với vai trò {role_label}."
            )
            return redirect(get_redirect_url_for_user(user))
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin nhập trong biểu mẫu.")
    else:
        form = UserRegistrationForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """View đăng nhập và tự động phân luồng theo Role."""
    if request.user.is_authenticated:
        return redirect(get_redirect_url_for_user(request.user))

    next_url = request.GET.get('next', '')

    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f"Đăng nhập thành công! Chào mừng trở lại, {user.get_full_name() or user.username}.")
            
            # Kiểm tra chuyển hướng an toàn
            redirect_to = request.POST.get('next') or request.GET.get('next')
            return redirect(get_redirect_url_for_user(user, redirect_to))
        else:
            messages.error(request, "Tên đăng nhập hoặc mật khẩu không chính xác.")
    else:
        form = UserLoginForm()

    return render(request, 'accounts/login.html', {
        'form': form,
        'next': next_url
    })


def logout_view(request):
    """View đăng xuất và dọn sạch session."""
    if request.user.is_authenticated:
        username = request.user.username
        logout(request)
        messages.info(request, f"Tài khoản {username} đã được đăng xuất an toàn.")
    return redirect('accounts:login')


# ==========================================
# ROLE LANDING PAGES (DEMO & TEST REDIRECT)
# ==========================================
@candidate_required
def candidate_job_board_view(request):
    """Trang Sàn Tuyển Dụng (Job Board) dành cho Candidate."""
    return render(request, 'candidate/job_board.html', {
        'title': 'Sàn Việc Làm AI - Khám Phá Cơ Hội Phù Hợp',
        'active_tab': 'job_board'
    })


@hr_required
def hr_dashboard_view(request):
    """Trang Bảng Điều Khiển Quản Lý Tuyển Dụng (HR Dashboard)."""
    return render(request, 'hr/dashboard.html', {
        'title': 'Bảng Điều Khiển Nhà Tuyển Dụng - AI Recruiter Hub',
        'active_tab': 'hr_dashboard'
    })


# ==========================================
# SYSTEM ADMIN: USER & RBAC MANAGEMENT
# ==========================================
@admin_required
def admin_users_view(request):
    """
    Giao diện Quản Lý Người Dùng & Phân Quyền 3 Tầng (3-Tier RBAC) dành riêng cho System Admin:
    - Thống kê KPI: Tổng người dùng, Admin, HR, Ứng viên.
    - Tìm kiếm đa năng: Username, Email, Họ tên, Tên công ty.
    - Bộ lọc theo vai trò (Admin / HR / Candidate).
    - Phân trang & Thao tác chuyển đổi vai trò nhanh.
    """
    query = request.GET.get('q', '').strip()
    role_filter = request.GET.get('role', '').strip()

    users_qs = User.objects.all().order_by('-date_joined')

    # KPI counts
    total_users = users_qs.count()
    admin_count = users_qs.filter(Q(role=User.ROLE_ADMIN) | Q(is_superuser=True)).count()
    hr_count = users_qs.filter(role=User.ROLE_HR).count()
    candidate_count = users_qs.filter(role=User.ROLE_CANDIDATE).count()
    active_count = users_qs.filter(is_active=True).count()

    if query:
        users_qs = users_qs.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(company_name__icontains=query) |
            Q(phone_number__icontains=query)
        )

    if role_filter:
        if role_filter == 'admin':
            users_qs = users_qs.filter(Q(role=User.ROLE_ADMIN) | Q(is_superuser=True))
        elif role_filter in [User.ROLE_HR, User.ROLE_CANDIDATE]:
            users_qs = users_qs.filter(role=role_filter)

    paginator = Paginator(users_qs, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'accounts/admin_users.html', {
        'page_obj': page_obj,
        'query': query,
        'role_filter': role_filter,
        'total_users': total_users,
        'admin_count': admin_count,
        'hr_count': hr_count,
        'candidate_count': candidate_count,
        'active_count': active_count,
        'roles': User.ROLE_CHOICES,
    })


@admin_required
def update_user_role_view(request, user_id):
    """
    Cập nhật nhanh vai trò và quyền hạn (RBAC) của người dùng:
    - Chuyển đổi giữa System Admin, HR, hoặc Candidate.
    - Cập nhật Tên công ty (nếu là HR).
    - Cập nhật trạng thái Hoạt động (is_active).
    """
    target_user = get_object_or_404(User, pk=user_id)

    if request.method == 'POST':
        new_role = request.POST.get('role', '').strip()
        company_name = request.POST.get('company_name', '').strip()
        is_active = request.POST.get('is_active') == '1'

        valid_roles = [User.ROLE_ADMIN, User.ROLE_HR, User.ROLE_CANDIDATE]
        if new_role in valid_roles:
            target_user.role = new_role
            if new_role == User.ROLE_ADMIN:
                target_user.is_staff = True
            elif new_role == User.ROLE_HR:
                target_user.is_staff = True
                target_user.company_name = company_name or target_user.company_name or 'TechCorp Vietnam'
            elif new_role == User.ROLE_CANDIDATE:
                if not target_user.is_superuser:
                    target_user.is_staff = False

            target_user.is_active = is_active
            target_user.save()

            role_label = target_user.get_role_display()
            messages.success(
                request,
                f"✅ Đã cập nhật thành công vai trò cho '{target_user.username}' thành: {role_label}!"
            )
        else:
            messages.error(request, "Vai trò lựa chọn không hợp lệ.")

    return redirect('accounts:admin_users')


# ==============================================================================
# P2 – TRANG CHỈNH SỬA HỒ SƠ CÁ NHÂN (Profile Edit)
# ==============================================================================
@login_required
def profile_view(request):
    """
    Trang xem và chỉnh sửa thông tin hồ sơ cá nhân cho mọi vai trò (Candidate, HR, Admin).
    - GET: Hiển thị form được điền sẵn thông tin hiện tại.
    - POST: Lưu thay đổi và điều hướng về lại trang profile với thông báo thành công.
    """
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Hồ sơ của bạn đã được cập nhật thành công!")
            return redirect('accounts:profile')
        else:
            messages.error(request, "Vui lòng kiểm tra lại thông tin nhập.")
    else:
        form = UserProfileForm(instance=request.user)

    # Thống kê nhanh cho ứng viên
    applications_count = 0
    if request.user.is_candidate:
        applications_count = request.user.applications.count()

    # Thống kê nhanh cho HR
    jobs_count = 0
    total_applicants = 0
    if request.user.is_hr:
        jobs_count = request.user.job_postings.filter(is_active=True).count()
        total_applicants = sum(j.applications.count() for j in request.user.job_postings.all())

    return render(request, 'accounts/profile.html', {
        'form': form,
        'applications_count': applications_count,
        'jobs_count': jobs_count,
        'total_applicants': total_applicants,
    })

