# Generated by Django 4.2.16 on 2024-11-27 01:49

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_student_unique_code'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='unique_code',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name='학생 코드'),
        ),
    ]
