from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import AcademicYear, Grade, Student, Income, Expense, Reservation, AuditLog
from import_export.admin import ImportExportModelAdmin

from django.contrib import admin

admin.site.site_header = "Администрирование школы 'Азия Старт'"
admin.site.site_title = "Азия Старт"
admin.site.index_title = "Панель управления"

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(Grade)
class GradeAdmin(ImportExportModelAdmin):
    list_display = ('number', 'parallel', 'max_students')
    list_filter = ('number', 'parallel')
    search_fields = ('number', 'parallel')
    ordering = ('number', 'parallel')

admin.site.register(AcademicYear)
@admin.register(Student)
class StudentAdmin(ImportExportModelAdmin):
    list_display = ('full_name', 'grade', 'status', 'is_active')
    list_filter = ('grade', 'status', 'is_active')
    search_fields = ('full_name', 'parent_contacts')
    list_editable = ('status', 'is_active')
    ordering = ('grade', 'full_name')
    fieldsets = (
        (None, {
            'fields': ('full_name', 'birth_date', 'grade','pol')
        }),
        ('Контракт',{
            'fields':('number_contract','contract_amount','contract_date','contract_file','current_year_paid','payment_notes')
        }),
        ('Контакты', {
            'fields': ('parent_contacts',)
        }),
        ('Статус', {
            'fields': ('admission_date', 'status', 'is_active')
        }),
    )


@admin.register(Income)
class IncomeAdmin(ImportExportModelAdmin):
    list_display = ('date', 'student', 'amount', 'payment_method', 'status')
    list_filter = ('date', 'payment_method', 'status')
    search_fields = ('student__full_name', 'transaction_id')
    list_editable = ('status',)
    date_hierarchy = 'date'
    ordering = ('-date',)
    raw_id_fields = ('student',)


@admin.register(Expense)
class ExpenseAdmin(ImportExportModelAdmin):
    list_display = ('date', 'category', 'supplier', 'amount', 'payment_method')
    list_filter = ('date', 'category', 'payment_method')
    search_fields = ('supplier', 'notes')
    date_hierarchy = 'date'
    ordering = ('-date',)
    readonly_fields = ('invoice_preview',)
    
    def invoice_preview(self, obj):
        if obj.invoice:
            return f'<a href="{obj.invoice.url}" target="_blank">Просмотреть счёт</a>'
        return "Нет файла"
    invoice_preview.short_description = "Предпросмотр счёта"
    invoice_preview.allow_tags = True


@admin.register(Reservation)
class ReservationAdmin(ImportExportModelAdmin):
    list_display = ('student', 'academic_year', 'intended_grade', 'status', 'created_at')
    list_filter = ('academic_year', 'intended_grade', 'status')
    search_fields = ('student__full_name',)
    list_editable = ('status',)
    ordering = ('-created_at',)
    raw_id_fields = ('student', 'intended_grade')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model_name', 'object_id', 'timestamp')
    list_filter = ('action', 'model_name', 'timestamp')
    search_fields = ('user__username', 'model_name', 'details')
    ordering = ('-timestamp',)
    readonly_fields = ('user', 'action', 'model_name', 'object_id', 'details', 'timestamp')
    date_hierarchy = 'timestamp'


# Перерегистрируем стандартную модель User
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# сотрудники


from django.contrib import admin
from .models import Position, Employee, SalaryPayment

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'position', 'phone', 'email', 'is_active')
    list_filter = ('position', 'is_active', 'contract_type')
    search_fields = ('full_name', 'phone', 'email', 'contract_number')
    fieldsets = (
        ('Основная информация', {
            'fields': ('full_name', 'birth_date', 'gender', 'address', 'phone', 'email')
        }),
        ('Работа', {
            'fields': ('position', 'hire_date', 'is_active', 'notes')
        }),
        ('Контракт', {
            'fields': ('contract_type', 'contract_number', 'contract_start_date', 
                      'contract_end_date', 'monthly_salary', 'contract_file')
        }),
    )

@admin.register(SalaryPayment)
class SalaryPaymentAdmin(admin.ModelAdmin):
    list_display = ('employee', 'amount', 'for_month', 'payment_date', 'is_bonus')
    list_filter = ('is_bonus', 'payment_method')
    search_fields = ('employee__full_name', 'notes')
    date_hierarchy = 'payment_date'