from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User


# Tailwind input class tái sử dụng
_TW_INPUT = (
    'w-full px-4 py-2.5 rounded-lg border border-slate-300 '
    'focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 '
    'outline-none transition duration-150 placeholder-slate-400 text-sm'
)


class UserRegistrationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=50,
        required=True,
        label="Họ và tên đệm",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition duration-150 placeholder-slate-400 text-sm',
            'placeholder': 'Ví dụ: Nguyễn Văn'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        required=True,
        label="Tên",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition duration-150 placeholder-slate-400 text-sm',
            'placeholder': 'Ví dụ: An'
        })
    )
    email = forms.EmailField(
        required=True,
        label="Địa chỉ Email",
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition duration-150 placeholder-slate-400 text-sm',
            'placeholder': 'example@domain.com'
        })
    )
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'hidden peer'}),
        label="Bạn đăng ký với vai trò gì?",
        initial=User.ROLE_CANDIDATE
    )
    company_name = forms.CharField(
        max_length=255,
        required=False,
        label="Tên doanh nghiệp / Công ty",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition duration-150 placeholder-slate-400 text-sm',
            'placeholder': 'Tập đoàn Công nghệ ABC (nếu là HR)'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label="Số điện thoại liên hệ",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition duration-150 placeholder-slate-400 text-sm',
            'placeholder': '0912 345 678'
        })
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'company_name',
            'phone_number',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Apply Tailwind classes to username, password fields inherited from UserCreationForm
        if 'username' in self.fields:
            self.fields['username'].widget.attrs.update({
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition duration-150 placeholder-slate-400 text-sm',
                'placeholder': 'Tên đăng nhập (viết liền không dấu)'
            })
        if 'password' in self.fields:
            self.fields['password'].widget.attrs.update({
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition duration-150 placeholder-slate-400 text-sm',
                'placeholder': '••••••••'
            })
        if 'password2' in self.fields:
            self.fields['password2'].widget.attrs.update({
                'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition duration-150 placeholder-slate-400 text-sm',
                'placeholder': '••••••••'
            })

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Địa chỉ Email này đã được sử dụng. Vui lòng chọn Email khác.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        role = cleaned_data.get('role')
        company_name = cleaned_data.get('company_name')

        if role == User.ROLE_HR and not company_name:
            self.add_error('company_name', 'Nhà tuyển dụng vui lòng nhập Tên công ty / tổ chức.')
        return cleaned_data


class UserLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Tên đăng nhập",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition duration-150 placeholder-slate-400 text-sm',
            'placeholder': 'Nhập tên đăng nhập của bạn',
            'autocomplete': 'username'
        })
    )
    password = forms.CharField(
        label="Mật khẩu",
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2.5 rounded-lg border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none transition duration-150 placeholder-slate-400 text-sm',
            'placeholder': '••••••••',
            'autocomplete': 'current-password'
        })
    )


# ==============================================================================
# P2 – FORM CHỈNH SỬA HỒ SƠ NGƯỜI DÙNG (UserProfileForm)
# ==============================================================================
class UserProfileForm(forms.ModelForm):
    """
    Form chỉnh sửa thông tin hồ sơ cá nhân cho cả Ứng viên, HR và Admin.
    Cho phép cập nhật: Họ tên, Email, Số điện thoại, Tên công ty (HR).
    """
    first_name = forms.CharField(
        max_length=50,
        required=False,
        label="Họ và tên đệm",
        widget=forms.TextInput(attrs={
            'class': _TW_INPUT,
            'placeholder': 'Nguyễn Văn'
        })
    )
    last_name = forms.CharField(
        max_length=50,
        required=False,
        label="Tên",
        widget=forms.TextInput(attrs={
            'class': _TW_INPUT,
            'placeholder': 'An'
        })
    )
    email = forms.EmailField(
        required=False,
        label="Địa chỉ Email",
        widget=forms.EmailInput(attrs={
            'class': _TW_INPUT,
            'placeholder': 'example@domain.com'
        })
    )
    phone_number = forms.CharField(
        max_length=20,
        required=False,
        label="Số điện thoại",
        widget=forms.TextInput(attrs={
            'class': _TW_INPUT,
            'placeholder': '0912 345 678'
        })
    )
    company_name = forms.CharField(
        max_length=255,
        required=False,
        label="Tên công ty / Tổ chức (Dành cho HR)",
        widget=forms.TextInput(attrs={
            'class': _TW_INPUT,
            'placeholder': 'Tập đoàn Công nghệ ABC'
        })
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'phone_number', 'company_name')

    def clean_email(self):
        """Đảm bảo Email không trùng với tài khoản khác (trừ chính mình)."""
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError("Địa chỉ Email này đã được sử dụng bởi tài khoản khác.")
        return email
