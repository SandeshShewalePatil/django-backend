# Generated by Django 5.0.8 on 2024-11-27 09:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_adminlogin'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomerModel',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('customerName', models.CharField(max_length=200)),
                ('product', models.CharField(max_length=200)),
                ('price', models.CharField(max_length=200)),
            ],
        ),
        migrations.DeleteModel(
            name='adminLogin',
        ),
        migrations.DeleteModel(
            name='exploreModel',
        ),
        migrations.DeleteModel(
            name='videoModel',
        ),
    ]
