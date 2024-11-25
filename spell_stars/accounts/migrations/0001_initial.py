# Generated by Django 4.2.16 on 2024-11-25 01:59

from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('name', models.CharField(default='이름 없음', max_length=50, verbose_name='이름')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='생년월일')),
                ('role', models.CharField(choices=[('student', '학생'), ('parent', '학부모')], default='student', max_length=10, verbose_name='역할')),
                ('grade', models.IntegerField(blank=True, choices=[(1, '1학년'), (2, '2학년'), (3, '3학년'), (4, '4학년'), (5, '5학년'), (6, '6학년')], null=True, verbose_name='학년')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('unique_code', models.CharField(blank=True, max_length=12, unique=True, verbose_name='학생 코드')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL, verbose_name='사용자')),
            ],
        ),
        migrations.CreateModel(
            name='StudentLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('login_time', models.DateTimeField(verbose_name='로그인 시간')),
                ('logout_time', models.DateTimeField(blank=True, null=True, verbose_name='로그아웃 시간')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='login_logs', to='accounts.student', verbose_name='학생')),
            ],
        ),
        migrations.CreateModel(
            name='StudentLearningLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('learning_mode', models.IntegerField(choices=[(1, '사전 학습'), (2, '시험'), (3, '발음 연습')], verbose_name='학습 모드')),
                ('start_time', models.DateTimeField(verbose_name='시작 시간')),
                ('end_time', models.DateTimeField(blank=True, null=True, verbose_name='종료 시간')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='learning_logs', to='accounts.student', verbose_name='학생')),
            ],
        ),
        migrations.CreateModel(
            name='ParentStudentRelation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('parent_relation', models.CharField(choices=[('아버지', '아버지'), ('어머니', '어머니'), ('할아버지', '할아버지'), ('할머니', '할머니'), ('삼촌', '삼촌'), ('이모', '이모'), ('고모', '고모')], default='아버지', max_length=50, verbose_name='학부모 관점 관계')),
                ('student_relation', models.CharField(blank=True, max_length=50, verbose_name='학생 관점 관계')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일')),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.parent', verbose_name='학부모')),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='accounts.student', verbose_name='학생')),
            ],
            options={
                'unique_together': {('parent', 'student')},
            },
        ),
        migrations.AddField(
            model_name='parent',
            name='children',
            field=models.ManyToManyField(related_name='parents', through='accounts.ParentStudentRelation', to='accounts.student', verbose_name='자녀'),
        ),
        migrations.AddField(
            model_name='parent',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='parent_profile', to=settings.AUTH_USER_MODEL, verbose_name='사용자'),
        ),
    ]
