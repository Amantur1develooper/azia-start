from .models import AcademicYear


def academic_years(request):
    return {
        'all_academic_years': AcademicYear.objects.order_by('-start_date'),
        'current_academic_year': AcademicYear.objects.filter(is_current=True).first(),
    }
