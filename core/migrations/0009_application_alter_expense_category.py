# Generated by Django 5.2.1 on 2025-07-16 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_position_alter_expense_category_employee_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('child_name', models.CharField(max_length=100)),
                ('child_surname', models.CharField(max_length=100)),
                ('child_class', models.CharField(max_length=20)),
                ('parent_phone', models.CharField(max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Заявка на обучение',
                'verbose_name_plural': 'Заявки на обучение',
            },
        ),
        migrations.AlterField(
            model_name='expense',
            name='category',
            field=models.CharField(choices=[('salary', 'Зарплата'), ('materials', 'Учебные материалы'), ('events', 'Мероприятия'), ('utilities', 'Коммунальные услуги'), ('other', 'Другие расходы'), ('arenda', 'Аренда'), ('kichin', 'Кухня')], max_length=20, verbose_name='Категория расхода'),
        ),
    ]
