# Generated by Django 5.2.4 on 2025-07-31 15:37

import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='InternetPlan',
            fields=[
                ('plan_id', models.AutoField(primary_key=True, serialize=False)),
                ('plan_name', models.CharField(max_length=100)),
                ('plan_price', models.DecimalField(decimal_places=0, max_digits=10)),
                ('plan_type', models.CharField(choices=[('monthly', 'Monthly'), ('temporary', 'Temporary')], default='monthly', max_length=10)),
                ('Num_Devices', models.IntegerField()),
                ('planstatus', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(max_length=100)),
                ('last_name', models.CharField(max_length=100)),
                ('is_active', models.BooleanField(default=False)),
                ('is_staff', models.BooleanField(default=False)),
                ('is_verified', models.BooleanField(default=False)),
                ('otp', models.CharField(blank=True, max_length=10, null=True)),
                ('role', models.CharField(blank=True, default='client', max_length=100, null=True)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
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
            name='Building',
            fields=[
                ('building_id', models.AutoField(primary_key=True, serialize=False)),
                ('building_name', models.CharField(max_length=2)),
                ('floors', models.CharField(max_length=10)),
                ('rooms', models.IntegerField()),
                ('Agent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='buildings_managed', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.AutoField(primary_key=True, serialize=False)),
                ('payment_date', models.DateField(auto_now_add=True)),
                ('payment_amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('payment_method', models.CharField(max_length=50)),
                ('payment_status', models.CharField(max_length=20)),
                ('payment_plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paymentsplan', to='common.internetplan')),
                ('payment_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paymentsusr', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='BillingPlan',
            fields=[
                ('billingid', models.AutoField(primary_key=True, serialize=False)),
                ('billstartdate', models.DateField(blank=True, null=True)),
                ('billendate', models.DateField(blank=True, null=True)),
                ('PlanStatus', models.CharField(default='Upcoming', max_length=20)),
                ('billingusr', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billingusr', to=settings.AUTH_USER_MODEL)),
                ('billingplan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billingplan', to='common.internetplan')),
                ('paymentid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='paymentid', to='common.payment')),
            ],
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bulding', models.CharField()),
                ('floor', models.CharField()),
                ('room', models.CharField()),
                ('phone', models.CharField(max_length=20)),
                ('profpic', models.ImageField(blank=True, default='profile_pics/default_profile.webp', null=True, upload_to='profile_pics')),
                ('is_billable', models.BooleanField(default=True)),
                ('profile_comp', models.BooleanField(default=False)),
                ('plan_start_date', models.DateField(blank=True, null=True)),
                ('next_billdate', models.DateField(blank=True, null=True)),
                ('planenddate', models.DateField(blank=True, null=True)),
                ('builing_id', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='building', to='common.building')),
                ('plan', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='plan', to='common.internetplan')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profileuser', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Ticketing',
            fields=[
                ('ticketid', models.AutoField(primary_key=True, serialize=False)),
                ('ticketdate', models.DateTimeField(auto_now_add=True)),
                ('ticketstatus', models.CharField(default='Open', max_length=20)),
                ('ticketdesc', models.TextField(blank=True, null=True)),
                ('ticketsubj', models.CharField(blank=True, max_length=255, null=True)),
                ('ticketpriority', models.CharField(blank=True, choices=[('low', 'Low'), ('medium', 'Medium'), ('high', 'High'), ('urgent', 'Urgent')], default='medium', max_length=10, null=True)),
                ('ticketfile', models.FileField(blank=True, null=True, upload_to='tickets')),
                ('ticketraised', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets_created_by_user', to=settings.AUTH_USER_MODEL)),
                ('ticketto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tickets_assigned_to_agent', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-ticketdate'],
            },
        ),
        migrations.CreateModel(
            name='TicketUpdates',
            fields=[
                ('updateid', models.AutoField(primary_key=True, serialize=False)),
                ('ticketupdate', models.DateTimeField(auto_now_add=True)),
                ('ticketupdatefile', models.FileField(blank=True, null=True, upload_to='tickets')),
                ('ticketupdatedesc', models.TextField(blank=True, null=True)),
                ('ticketid', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updates', to='common.ticketing')),
                ('ticketupdateby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='updates_made_by_user', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name_plural': 'Ticket Updates',
                'ordering': ['ticketupdate'],
            },
        ),
        migrations.CreateModel(
            name='WifiCodeUpload',
            fields=[
                ('codeupid', models.AutoField(primary_key=True, serialize=False)),
                ('uploadeddate', models.DateTimeField(auto_now_add=True)),
                ('uploadstatus', models.CharField(default='Initiated', max_length=20)),
                ('uploadedto', models.FileField(upload_to='wifi_codes')),
                ('remarks', models.CharField(blank=True, max_length=100, null=True)),
                ('uploadedby', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='uploaded_wifi_codes', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CodePoool',
            fields=[
                ('codeid', models.AutoField(primary_key=True, serialize=False)),
                ('code', models.CharField(max_length=20)),
                ('is_used', models.BooleanField(default=False)),
                ('assigneddate', models.DateTimeField(blank=True, null=True)),
                ('exiprydate', models.DateField(blank=True, null=True)),
                ('deactivated', models.DateField(blank=True, null=True)),
                ('is_deactivated', models.BooleanField(default=False)),
                ('assignedto', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assigned_codes', to=settings.AUTH_USER_MODEL)),
                ('sourcepdf', models.ForeignKey(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='Source', to='common.wificodeupload')),
            ],
        ),
    ]
