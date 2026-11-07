# Generated migration for contact info extraction
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('jobs', '0004_alter_application_options_application_match_score'),
    ]

    operations = [
        migrations.AddField(
            model_name='application',
            name='extracted_email',
            field=models.CharField(blank=True, default='', max_length=255, verbose_name='Email bóc tách từ CV (AI Extractor)'),
        ),
        migrations.AddField(
            model_name='application',
            name='extracted_phone',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='Số điện thoại bóc tách từ CV (AI Extractor)'),
        ),
    ]

