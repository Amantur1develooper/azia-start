from datetime import timezone
from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import AcademicYear, Application, Grade, Student, Income, Expense, Reservation, AuditLog, Student2, Teacher, TelegramSubscriber
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
    
admin.site.register(Teacher)    
admin.site.register(Application)
from django.contrib import admin
from .models import Student

@admin.register(Student2)
class StudentAdmin2(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'level', 'is_featured', 'order')
    list_editable = ('is_featured', 'order')
    list_filter = ('is_featured', 'level')
    search_fields = ('first_name', 'last_name', 'achievements')
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'level')
        }),
        ('Дополнительно', {
            'fields': ('achievements', 'image', 'is_featured', 'order')
        }),
    )
from django.contrib import admin
from .models import News
from datetime import datetime
import pytz
from django.contrib import admin
from .models import Document

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'created_at')
    search_fields = ('title', 'category')
    list_filter = ('category', 'created_at')
admin.site.register(TelegramSubscriber)

from django.contrib import admin
from .models import GalleryEvent, GalleryImage
from django.utils.html import format_html

class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1
    fields = ('image', 'preview', 'caption', 'order')
    readonly_fields = ('preview',)
    
    def preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="100" />', obj.image.url)
        return "-"
    preview.short_description = "Превью"

@admin.register(GalleryEvent)
class GalleryEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'created_at')
    search_fields = ('title', 'description')
    list_filter = ('date',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GalleryImageInline]
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'date', 'cover_image', 'description')
        }),
    )
    
    
@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'is_published')
    list_editable = ('is_published',)
    list_filter = ('is_published', 'created_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'image')
        }),
        ('Дополнительно', {
            'fields': ('is_published', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
    
    def save_model(self, request, obj, form, change):
        if not change:
            # При создании новости автоматически устанавливаем текущую дату
            tz = pytz.timezone('Asia/Bishkek')  # Example for UTC+06:00
            obj.created_at = datetime.now(tz)
            # obj.created_at = timezone
        super().save_model(request, obj, form, change)
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