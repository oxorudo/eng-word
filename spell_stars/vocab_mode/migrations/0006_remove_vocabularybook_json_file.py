# Generated by Django 4.2.16 on 2024-11-12 05:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('vocab_mode', '0005_remove_word_audio_file_remove_word_meaning_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='vocabularybook',
            name='json_file',
        ),
    ]
