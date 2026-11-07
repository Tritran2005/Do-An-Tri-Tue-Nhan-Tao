from django import forms
from .models import JobPosting, Application

class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = [
            'title',
            'required_skills',
            'min_experience',
            'salary_range',
            'location',
            'job_type',
            'description',
            'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm transition',
                'placeholder': 'Ví dụ: Senior AI/NLP Engineer, Django Fullstack Developer...'
            }),
            'required_skills': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm font-mono transition',
                'placeholder': 'Python, Django, MySQL, PyTorch, Sentence-BERT, Docker'
            }),
            'min_experience': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm transition',
                'min': '0',
                'placeholder': '0'
            }),
            'salary_range': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm transition',
                'placeholder': '15 - 25 triệu, $1,500 - $2,500, Thỏa thuận...'
            }),
            'location': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm transition',
                'placeholder': 'Hà Nội, TP. Hồ Chí Minh, Đà Nẵng, Remote...'
            }),
            'job_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2.5 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm transition bg-white'
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 rounded-xl border border-slate-300 focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 outline-none text-sm font-sans transition',
                'rows': 8,
                'placeholder': 'Nhập mô tả công việc (JD) chi tiết: Trách nhiệm chính, yêu cầu chuyên môn, quyền lợi ứng viên...\n(Nội dung này sẽ được Sentence-BERT sử dụng để đối chiếu ngữ nghĩa với CV ứng viên).'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-indigo-600 border-slate-300 rounded focus:ring-indigo-500 transition'
            }),
        }
        labels = {
            'title': 'Tiêu đề vị trí tuyển dụng',
            'required_skills': 'Kỹ năng trọng tâm (Skills Taxonomy)',
            'min_experience': 'Kinh nghiệm tối thiểu (Số năm)',
            'salary_range': 'Mức lương dự kiến',
            'location': 'Địa điểm làm việc',
            'job_type': 'Hình thức làm việc',
            'description': 'Mô tả chi tiết công việc (JD)',
            'is_active': 'Kích hoạt đăng tuyển công khai',
        }


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cv_file']
        widgets = {
            'cv_file': forms.FileInput(attrs={
                'class': 'block w-full text-xs text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100 cursor-pointer border border-slate-200 rounded-xl p-2 bg-white',
                'accept': '.pdf,.docx'
            })
        }
        labels = {
            'cv_file': 'Tải lên CV của bạn (Hỗ trợ PDF hoặc DOCX)'
        }

    def clean_cv_file(self):
        cv = self.cleaned_data.get('cv_file')
        if cv:
            import os
            ext = os.path.splitext(cv.name)[1].lower()
            if ext not in ['.pdf', '.docx']:
                raise forms.ValidationError("Hệ thống chỉ chấp nhận tệp định dạng .PDF hoặc .DOCX")
            if cv.size > 10 * 1024 * 1024:
                raise forms.ValidationError("Dung lượng file CV không được vượt quá 10MB.")
        return cv

