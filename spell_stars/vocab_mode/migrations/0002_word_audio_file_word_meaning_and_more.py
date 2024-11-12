# Generated by Django 4.2.16 on 2024-11-12 01:37

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("vocab_mode", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="word",
            name="audio_file",
            field=models.FileField(blank=True, null=True, upload_to="word_audios/"),
        ),
        migrations.AddField(
            model_name="word",
            name="meaning",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="word",
            name="pronunciation_guide",
            field=models.TextField(default=""),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="word",
            name="text",
            field=models.CharField(default=" ", max_length=50),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="VocabularyBook",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "json_file",
                    models.FileField(
                        blank=True, null=True, upload_to="utils/combined_words.json"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                ("words", models.ManyToManyField(to="vocab_mode.word")),
            ],
        ),
        migrations.CreateModel(
            name="PronunciationRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("score", models.FloatField()),
                ("audio_file", models.FileField(upload_to="pronunciation_records/")),
                (
                    "student",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
                (
                    "word",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="vocab_mode.word",
                    ),
                ),
            ],
        ),
    ]
