# Generated by Django 3.0.7 on 2020-07-05 20:27

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pronym_api', '0010_auto'),
    ]

    operations = [
        migrations.CreateModel(
            name='SshKey',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('content', models.TextField()),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Repository',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('url', models.URLField(unique=True)),
                ('python_version', models.CharField(choices=[('PYTHON_3_8', '3.8')], max_length=255)),
                ('deployment_repo', models.CharField(blank=True, max_length=255, null=True)),
                ('deployment_branch', models.CharField(default='master', max_length=255)),
                ('run_unittests', models.BooleanField()),
                ('run_api_integration_tests', models.BooleanField()),
                ('run_integration_tests', models.BooleanField()),
                ('run_wdio_tests', models.BooleanField()),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='repositories', to='pronym_api.ApiAccount')),
                ('ssh_key', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='+', to='core.SshKey')),
            ],
        ),
        migrations.CreateModel(
            name='PullRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('pr_number', models.PositiveIntegerField()),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('FAILED', 'Failed'), ('ERROR', 'Error'), ('SUCCESS', 'Success')], default='PENDING', max_length=255)),
                ('repository', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pull_requests', to='core.Repository')),
            ],
        ),
        migrations.CreateModel(
            name='Build',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('datetime_created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('PENDING', 'Pending'), ('FAILED', 'Failed'), ('ERROR', 'Error'), ('SUCCESS', 'Success')], default='PENDING', max_length=255)),
                ('stdout', models.TextField()),
                ('stderr', models.TextField()),
                ('pull_request', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='builds', to='core.PullRequest')),
            ],
        ),
    ]
