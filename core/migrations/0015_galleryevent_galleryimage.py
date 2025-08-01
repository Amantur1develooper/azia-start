# Generated by Django 5.2.1 on 2025-07-30 09:46

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_document'),
    ]

    operations = [
        migrations.CreateModel(
            name='GalleryEvent',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200, verbose_name='Название события')),
                ('slug', models.SlugField(blank=True, max_length=200, unique=True)),
                ('description', models.TextField(blank=True, verbose_name='Описание')),
                ('date', models.DateField(verbose_name='Дата события')),
                ('cover_image', models.ImageField(upload_to='gallery/covers/', verbose_name='Обложка')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Событие галереи',
                'verbose_name_plural': 'События галереи',
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='GalleryImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', models.ImageField(upload_to='gallery/images/', verbose_name='Изображение')),
                ('caption', models.CharField(blank=True, max_length=255, verbose_name='Подпись')),
                ('order', models.PositiveIntegerField(default=0, verbose_name='Порядок')),
                ('event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='core.galleryevent')),
            ],
            options={
                'verbose_name': 'Изображение галереи',
                'verbose_name_plural': 'Изображения галереи',
                'ordering': ['order'],
            },
        ),
    ]
