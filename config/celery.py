import os
from celery import Celery

# Thiết lập biến môi trường cấu hình Django cho Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('ai_recruitment_portal')

# Đọc cấu hình Celery từ settings.py với tiền tố CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Tự động phát hiện tasks.py trong tất cả các installed apps
app.autodiscover_tasks()


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')

