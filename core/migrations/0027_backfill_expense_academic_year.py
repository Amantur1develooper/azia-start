from django.db import migrations


def backfill_expense_academic_year(apps, schema_editor):
    Expense = apps.get_model('core', 'Expense')
    AcademicYear = apps.get_model('core', 'AcademicYear')

    years = list(AcademicYear.objects.order_by('start_date'))
    if not years:
        return

    for expense in Expense.objects.filter(academic_year__isnull=True):
        matched = None
        # 1. Exact range match
        for y in years:
            if y.start_date and y.end_date and y.start_date <= expense.date <= y.end_date:
                matched = y
                break
        # 2. Closest year by start_date
        if not matched:
            matched = min(years, key=lambda y: abs((y.start_date - expense.date).days))
        expense.academic_year = matched
        expense.save()


def reverse_backfill(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_expense_academic_year'),
    ]

    operations = [
        migrations.RunPython(backfill_expense_academic_year, reverse_backfill),
    ]
