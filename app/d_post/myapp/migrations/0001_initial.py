# Generated by Django 3.1.2 on 2021-02-18 09:49

import django.contrib.auth.models
import django.contrib.auth.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
from django.utils import timezone
# from django.conf import settings


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        # migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Registers2',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reg_number', models.PositiveBigIntegerField()),
                ('reg_date', models.DateField(default=timezone.now)),
                ('reg_real_datetime', models.DateTimeField(default=timezone.now)),
                ('fns_id', models.CharField(max_length=2, 
                                            choices=[('OK', 'ИФНС России по Октябрьскому району г. Пензы'),
                                                     ('ZD', 'ИФНС России по Железнодорожному району г. Пензы'),
                                                     ('LN', 'ИФНС России по Ленинскому району г. Пензы'),
                                                     ('ZR', 'ИФНС России по г. Заречному Пензенской области'),
                                                     ('PM', 'ИФНС России по Первомайскому району г. Пензы'),
                                                     ('PO', 'УФНС России по Пензенской области'),
                                                    ])),
                ('notification_id', models.CharField(max_length=2, choices=[(None, ''), ('OR', 'простое'), ('NU', 'заказное'), ('WU', 'заказное с уведомлением'), ('AU', 'административное заказное с уведомлением')])),
                ('printed', models.BooleanField(default=False)),

            ],
            options={
                'ordering': ['id'],
            },
        ),
        migrations.CreateModel(
            name='OrdinaryMails',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('record_creation_date', models.DateField(default=timezone.now)),
                ('fns_id', models.CharField(max_length=2, 
                                            choices=[('OK', 'ИФНС России по Октябрьскому району г. Пензы'),
                                                     ('ZD', 'ИФНС России по Железнодорожному району г. Пензы'),
                                                     ('LN', 'ИФНС России по Ленинскому району г. Пензы'),
                                                     ('ZR', 'ИФНС России по г. Заречному Пензенской области'),
                                                     ('PM', 'ИФНС России по Первомайскому району г. Пензы'),
                                                     ('PO', 'УФНС России по Пензенской области'),
                                                    ])),
                ('address', models.CharField(max_length=255, default='')),
                ('fio', models.CharField(max_length=255, default='')),
                ('made_date', models.CharField(max_length=128, blank=True, null=True)),
                ('doc_number', models.CharField(max_length=255, default='')),
                ('inspector', models.CharField(max_length=30, default='')),
                ('reg_id', models.ForeignKey(to='myapp.registers2', to_field='id', on_delete=models.CASCADE, default=1)),
            ],
            options={
                'ordering': ['record_creation_date'],
            },
        ),
        migrations.CreateModel(
            name='Abonents',
            fields=[
                ('shpi', models.CharField(max_length=14, unique=True)),
                ('abon_id', models.CharField(max_length=40)),
                ('fio', models.CharField(max_length=255)),
                ('doc_number', models.CharField(max_length=255)),
                ('made_date', models.CharField(blank=True, max_length=128, null=True)),
                ('address', models.CharField(max_length=255, default='')),
                ('telephone', models.CharField(max_length=12)),
                ('inspector', models.CharField(default='', max_length=30)),
                ('notification_id', models.CharField(choices=[(None, ''), ('OR', 'простое'), ('NU', 'заказное'), ('WU', 'заказное с уведомлением'), ('AU', 'административное заказное с уведомлением')], max_length=2)),
                ('reg_id', models.ForeignKey(to='myapp.registers2', to_field='id', on_delete=models.CASCADE)),
                ('idd', models.AutoField(unique=True, primary_key=True)),
                ('record_creation_date', models.DateField(default=django.utils.timezone.now)),
                ('fns_id', models.CharField(max_length=2, default='',
                                            choices=[('OK', 'ИФНС России по Октябрьскому району г. Пензы'),
                                                     ('ZD', 'ИФНС России по Железнодорожному району г. Пензы'),
                                                     ('LN', 'ИФНС России по Ленинскому району г. Пензы'),
                                                     ('ZR', 'ИФНС России по г. Заречному Пензенской области'),
                                                     ('PM', 'ИФНС России по Первомайскому району г. Пензы'),
                                                     ('PO', 'УФНС России по Пензенской области'),
                                                    ])),
            ],
            options={
            },
        ),
        migrations.CreateModel(
            name='Generated_shpi',
            fields=[
                ('shpi', models.IntegerField(primary_key=True, unique=True)),
                ('generated_date', models.DateField(default=django.utils.timezone.now)),
                ('fns_id', models.CharField(choices=[('OK', 'ИФНС России по Октябрьскому району г. Пензы'), ('ZD', 'ИФНС России по Железнодорожному району г. Пензы'), ('LN', 'ИФНС России по Ленинскому району г. Пензы'), ('ZR', 'ИФНС России по г. Заречному Пензенской области'), ('PM', 'ИФНС России по Первомайскому району г. Пензы'), ('PO', 'УФНС России по Пензенской области')], max_length=2)),
            ],
        ),
        migrations.CreateModel(
            name='Status_history',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('shpi', models.ForeignKey(to='myapp.abonents', to_field='shpi', on_delete=django.db.models.deletion.CASCADE)),
                ('status_date', models.DateField()),
                ('status_id', models.CharField(choices=[('VR', 'вручено'), ('OB', 'в обработке'), ('PR', 'принят в отделении связи'), ('DO', 'доставка'), ('HR', 'хранение'), ('VZ', 'возврат')], max_length=2, default='VZ')),
            ],
            options={
                'ordering': ['status_date'],
            },
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('fns_id', models.CharField(default='LN', max_length=2)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
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
    ]
