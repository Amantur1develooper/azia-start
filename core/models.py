import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.db.models import Sum
class AcademicYear(models.Model):
    year = models.CharField(max_length=9, verbose_name="Учебный год (например: 2024-2025)")
    start_date = models.DateField(verbose_name="Дата начала учебного года")
    end_date = models.DateField(verbose_name="Дата окончания учебного года")
    is_current = models.BooleanField(default=False, verbose_name="Текущий учебный год")
    
    class Meta:
        verbose_name = "Учебный год"
        verbose_name_plural = "Учебные годы"
        
    def __str__(self):
        return self.year
    
    def save(self, *args, **kwargs):
        if self.is_current:
            # Сбрасываем флаг is_current у всех других годов
            AcademicYear.objects.filter(is_current=True).update(is_current=False)
        super().save(*args, **kwargs)
        
        
class Grade(models.Model):
    GRADE_CHOICES = [(i, str(i)) for i in range(1, 12)]
    PARALLEL_CHOICES = [('А', 'А'), ('Б', 'Б'), ('В', 'В'), ('Г', 'Г')]
    
    number = models.IntegerField(
        choices=GRADE_CHOICES,
        verbose_name="Номер класса"
    )
    parallel = models.CharField(
        max_length=1,
        choices=PARALLEL_CHOICES,
        verbose_name="Параллель"
    )
    max_students = models.IntegerField(
        default=25,
        verbose_name="Максимальное количество учеников"
    )
    
    class Meta:
        verbose_name = "Класс"
        verbose_name_plural = "Классы"
        unique_together = ('number', 'parallel')
    
    def __str__(self):
        return f"{self.number}{self.parallel}"
from decimal import Decimal, InvalidOperation


class Student(models.Model):
    STATUS_CHOICES = [
        ('studying', 'Обучается'),
        ('reserve', 'Резерв'),
        ('expelled', 'Отчислен'),
    ]
    pol_choices = [
        ('male', 'муж'),
        ('female', 'жен'),
    ]
    
    full_name = models.CharField(max_length=200, verbose_name="ФИО ученика")
    birth_date = models.DateField(verbose_name="Дата рождения")
    pol = models.CharField(max_length=10, choices=pol_choices, default='male', verbose_name="Пол", blank=True, null=True)
    parent_contacts = models.TextField(verbose_name="Контакты родителей")
    admission_date = models.DateField(verbose_name="Дата поступления")
    number_contract = models.CharField(max_length=50, verbose_name="Номер контракта", blank=True, null=True)
    grade = models.ForeignKey(Grade, on_delete=models.PROTECT, verbose_name="Класс")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='studying', verbose_name="Статус")
    is_active = models.BooleanField(default=True, verbose_name="Активный")
    
    # Новые поля для индивидуального контракта
    contract_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма контракта (сом)",
        null=True,
        blank=True
    )
    contract_date = models.DateField(
        verbose_name="Дата контракта",
        null=True,
        blank=True
    )
    contract_file = models.FileField(
        upload_to='contracts/',
        verbose_name="Файл контракта",
        null=True,
        blank=True
    )
    
    # Платежи и учет оплаты
    current_year_paid = models.BooleanField(default=False, verbose_name="Оплачен текущий учебный год")
    payment_notes = models.TextField(blank=True, verbose_name="Примечания по оплате")
    
    class Meta:
        verbose_name = "Ученик"
        verbose_name_plural = "Ученики"
        ordering = ['grade', 'full_name']
    
    def __str__(self):
        return self.full_name
    
    def save(self, *args, **kwargs):
        # Если сумма контракта не указана, используем стандартную для класса
        if self.contract_amount is None:
            self.contract_amount = self.grade.annual_tuition
        super().save(*args, **kwargs)
        
    # def get_total_paid_for_year(self, year):
    #     """Общая сумма оплат за учебный год"""
    #     payments = self.income_set.filter(
    #         academic_year=year,
    #         status='paid'
    #     )
    #     return payments.aggregate(models.Sum('amount'))['amount__sum'] or 0
    def get_payment_percent(self):
        """Возвращает процент оплаты контракта"""
        if not self.contract_amount or self.contract_amount <= 0:
            return 0

        current_year = AcademicYear.objects.filter(is_current=True).first()
        if not current_year:
            return 0

        try:
            total_paid = self.get_total_paid_for_year(current_year) or 0
            percent = (Decimal(total_paid) / Decimal(self.contract_amount)) * 100
            return min(round(percent), 100)
        except (InvalidOperation, ZeroDivisionError):
            return 0
    # def get_payment_percent(self):
    #     """Возвращает процент оплаты контракта"""
    #     if not self.contract_amount or self.contract_amount <= 0:
    #         return 0
            
    #     current_year = AcademicYear.objects.filter(is_current=True).first()
    #     if not current_year:
    #         return 0
            
    #     total_paid = self.get_total_paid_for_year(current_year)
    #     return min(round((total_paid / self.contract_amount) * 100, 100))
    
    def get_total_paid_for_year(self, academic_year):
        """Общая сумма оплат за учебный год"""
        payments = self.income_set.filter(
            academic_year=academic_year,
            status='paid'
        ).aggregate(total=Sum('amount'))['total'] or 0
        return payments
    
    def get_remaining_payment(self):
        """Остаток к оплате за текущий учебный год"""
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if not current_year or not self.contract_amount:
            return 0
            
        total_paid = self.get_total_paid_for_year(current_year)
        return max(self.contract_amount - total_paid, 0)

    # def get_total_paid_for_year(self, year):
    #     """Сумма оплат за указанный учебный год"""
    #     total = self.income_set.filter(
    #         date__gte=year.start_date,
    #         date__lte=year.end_date,
    #         status='paid'
    #     ).aggregate(models.Sum('amount'))['amount__sum'] or 0
    #     return total
    # def get_remaining_payment(self, academic_year):
    #     """Возвращает остаток к оплате за указанный учебный год"""
    #     if not academic_year:
    #         return 0
            
    #     total_paid = self.income_set.filter(
    #         academic_year=academic_year,
    #         status='paid'
    #     ).aggregate(total=Sum('amount'))['total'] or 0
        
    #     contract_amount = self.contract_amount or 0
    #     remaining = contract_amount - total_paid
    #     return max(remaining, 0)  # Не возвращаем отрицательные значения
    
    
    # def get_remaining_payment(self, year):
    #     """Остаток к оплате за учебный год"""
    #     return self.contract_amount - self.get_total_paid_for_year(year)
    
    def is_fully_paid_for_year(self, year):
        """Проверка полной оплаты за учебный год"""
        return self.get_total_paid_for_year(year) >= self.contract_amount
    
    def update_payment_status(self, year):
        """Обновляет статус оплаты для указанного учебного года"""
        self.current_year_paid = self.is_fully_paid_for_year(year)
        self.save()
# class Student(models.Model):
#     STATUS_CHOICES = [
#         ('studying', 'Обучается'),
#         ('reserve', 'Резерв'),
#         ('expelled', 'Отчислен'),
#     ]
#     pol_choices = [
#         ('male', 'муж'),
#         ('famale', 'жен'),
       
#     ]
#     full_name = models.CharField(
#         max_length=200,
#         verbose_name="ФИО ученика"
#     )
#     birth_date = models.DateField(
#         verbose_name="Дата рождения"
#     )
#     pol = models.CharField(
#         max_length=10,
#         choices=pol_choices,
#         default='male',
#         verbose_name="Пол", blank=True, null=True,
#     )
#     parent_contacts = models.TextField(
#         verbose_name="Контакты родителей"
#     )
#     admission_date = models.DateField(
#         verbose_name="Дата поступления"
#     )
#     number_contract = models.IntegerField(verbose_name="Номер контракта", blank=True, null=True)
#     grade = models.ForeignKey(
#         Grade,
#         on_delete=models.PROTECT,
#         verbose_name="Класс"
#     )
#     status = models.CharField(
#         max_length=10,
#         choices=STATUS_CHOICES,
#         default='studying',
#         verbose_name="Статус"
#     )
#     is_active = models.BooleanField(
#         default=True,
#         verbose_name="Активный"
#     )
    
#     class Meta:
#         verbose_name = "Ученик"
#         verbose_name_plural = "Ученики"
#         ordering = ['grade', 'full_name']
    
#     def __str__(self):
#         return self.full_name


class Income(models.Model):
    MONTH_CHOICES = [
        (9, 'Сентябрь'),
        (10, 'Октябрь'),
        (11, 'Ноябрь'),
        (12, 'Декабрь'),
        (1, 'Январь'),
        (2, 'Февраль'),
        (3, 'Март'),
        (4, 'Апрель'),
        (5, 'Май'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('card', 'Безналичный'),
        ('online', 'Онлайн платеж'),
    ]
    STATUS_CHOICES = [
        ('paid', 'Оплачено'),
        ('partial', 'Частично'),
        ('refund', 'Возврат'),
    ]
    
    date = models.DateField(verbose_name="Дата платежа", default=timezone.now)
    student = models.ForeignKey(Student, on_delete=models.PROTECT, verbose_name="Ученик")
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Сумма"
    )
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHODS, verbose_name="Способ оплаты")
    income_type = models.CharField(max_length=100, default="Оплата обучения", verbose_name="Статья дохода")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='paid', verbose_name="Статус оплаты")
    transaction_id = models.CharField(max_length=50, unique=True,  verbose_name="Номер транзакции")
    notes = models.TextField(blank=True, verbose_name="Примечания")
    academic_year = models.ForeignKey(AcademicYear,blank=True, null=True, on_delete=models.PROTECT, verbose_name="Учебный год")
    receipt_pdf = models.FileField(upload_to='receipts/', null=True, blank=True, verbose_name="Квитанция PDF")
    paid_months = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Оплаченные месяцы (номера)"
    )
    is_full_year_payment = models.BooleanField(
        default=False,
        verbose_name="Оплата за весь учебный год"
    )
    class Meta:
        verbose_name = "Приход"
        verbose_name_plural = "Приходы"
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.student} - {self.amount} ({self.academic_year})"
    def get_paid_months_display(self):
        """Возвращает список названий оплаченных месяцев"""
        if self.is_full_year_payment:
            return "Весь учебный год"
        elif self.paid_months:
            month_names = dict(self.MONTH_CHOICES)
            return ", ".join([month_names[int(m)] for m in self.paid_months])
        return "Разовый платеж"
    def save(self, *args, **kwargs):
        # Генерируем уникальный номер транзакции если он не задан
        if not self.transaction_id:
            self.transaction_id = str(uuid.uuid4())[:13].upper()
            
        # Автоматически устанавливаем текущий учебный год, если не указан
        if not self.academic_year_id:
            self.academic_year = AcademicYear.objects.filter(is_current=True).first()
        
        super().save(*args, **kwargs)
        
        # Обновляем статус оплаты студента
        if self.status == 'paid':
            self.student.update_payment_status(self.academic_year)
    # def save(self, *args, **kwargs):
    #     # Автоматически устанавливаем текущий учебный год, если не указан
    #     if not self.academic_year_id:
    #         self.academic_year = AcademicYear.objects.filter(is_current=True).first()
        
    #     super().save(*args, **kwargs)
        
    #     # Обновляем статус оплаты студента
    #     if self.status == 'paid':
    #         self.student.update_payment_status(self.academic_year)
# class Income(models.Model):
#     PAYMENT_METHODS = [
#         ('cash', 'Наличные'),
#         ('card', 'Безналичный'),
#         ('online', 'Онлайн платеж'),
#     ]
#     receipt_pdf = models.FileField(
#         upload_to='receipts/',
#         null=True,
#         blank=True,
#         verbose_name="Квитанция PDF"
#     )
#     STATUS_CHOICES = [
#         ('paid', 'Оплачено'),
#         ('partial', 'Частично'),
#         ('refund', 'Возврат'),
#     ]
    
#     date = models.DateField(
#         verbose_name="Дата платежа"
#     )
#     student = models.ForeignKey(
#         Student,
#         on_delete=models.PROTECT,
#         verbose_name="Ученик"
#     )
#     amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         validators=[MinValueValidator(0)],
#         verbose_name="Сумма"
#     )
#     payment_method = models.CharField(
#         max_length=10,
#         choices=PAYMENT_METHODS,
#         verbose_name="Способ оплаты"
#     )
#     income_type = models.CharField(
#         max_length=100,
#         verbose_name="Статья дохода"
#     )
#     status = models.CharField(
#         max_length=10,
#         choices=STATUS_CHOICES,
#         default='paid',
#         verbose_name="Статус оплаты"
#     )
#     transaction_id = models.CharField(
#         max_length=50,
#         unique=True,
#         verbose_name="Номер транзакции"
#     )
#     notes = models.TextField(
#         blank=True,
#         verbose_name="Примечания"
#     )
#     def get_receipt_url(self):
#         if self.receipt_pdf:
#             return self.receipt_pdf.url
#         return None
#     class Meta:
#         verbose_name = "Приход"
#         verbose_name_plural = "Приходы"
#         ordering = ['-date']
    
#     def __str__(self):
#         return f"{self.student} - {self.amount}"

class Expense(models.Model):
    CATEGORIES = [
        ('salary', 'Зарплата'),
        ('materials', 'Учебные материалы'),
        ('events', 'Мероприятия'),
        ('utilities', 'Коммунальные услуги'),
        ('other', 'Другие расходы'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('card', 'Безналичный'),
        ('bank_transfer', 'Банковский перевод'),
        ('online', 'Онлайн платеж'),
    ]
    
    date = models.DateField(verbose_name="Дата расхода")
    category = models.CharField(
        max_length=20,
        choices=CATEGORIES,
        verbose_name="Категория расхода"
    )
    supplier = models.CharField(
        max_length=200,
        verbose_name="Поставщик/контрагент"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Сумма"
    )
    payment_method = models.CharField(
        max_length=15,
        choices=PAYMENT_METHODS,
        verbose_name="Способ оплаты"
    )
    invoice_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Номер счета"
    )
    invoice = models.FileField(
        upload_to='expenses/invoices/',
        blank=True,
        null=True,
        verbose_name="Счет/фактура"
    )
    notes = models.TextField(
        blank=True,
        verbose_name="Комментарий"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Кто создал"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )

    class Meta:
        verbose_name = "Расход"
        verbose_name_plural = "Расходы"
        ordering = ['-date']

    def __str__(self):
        return f"{self.category} - {self.amount} - {self.date}"
    
    
# class Expense(models.Model):
#     CATEGORIES = [
#         ('salary', 'Зарплата'),
#         ('materials', 'Учебные материалы'),
#         ('events', 'Мероприятия'),
#         ('utilities', 'Коммунальные услуги'),
#     ]
    
#     date = models.DateField(
#         verbose_name="Дата расхода"
#     )
#     category = models.CharField(
#         max_length=20,
#         choices=CATEGORIES,
#         verbose_name="Категория расхода"
#     )
#     supplier = models.CharField(
#         max_length=200,
#         verbose_name="Поставщик/контрагент"
#     )
#     amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         validators=[MinValueValidator(0)],
#         verbose_name="Сумма"
#     )
#     payment_method = models.CharField(
#         max_length=10,
#         choices=Income.PAYMENT_METHODS,
#         verbose_name="Способ оплаты"
#     )
#     invoice = models.FileField(
#         upload_to='expenses/invoices/',
#         blank=True,
#         null=True,
#         verbose_name="Счет/фактура"
#     )
#     notes = models.TextField(
#         blank=True,
#         verbose_name="Комментарий"
#     )
    
#     class Meta:
#         verbose_name = "Расход"
#         verbose_name_plural = "Расходы"
#         ordering = ['-date']
    
#     def __str__(self):
#         return f"{self.category} - {self.amount}"


class Reservation(models.Model):
    RESERVATION_STATUS = [
        ('confirmed', 'Подтверждена'),
        ('pending', 'Ожидает оплаты'),
        ('cancelled', 'Отменена'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        verbose_name="Ученик"
    )
    academic_year = models.CharField(
        max_length=9,
        verbose_name="Учебный год"
    )
    intended_grade = models.ForeignKey(
        Grade,
        on_delete=models.PROTECT,
        verbose_name="Предполагаемый класс"
    )
    status = models.CharField(
        max_length=10,
        choices=RESERVATION_STATUS,
        verbose_name="Статус брони"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата создания"
    )
    
    class Meta:
        verbose_name = "Бронирование"
        verbose_name_plural = "Бронирования"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.student} - {self.academic_year}"


class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Создание'),
        ('update', 'Обновление'),
        ('delete', 'Удаление'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        verbose_name="Пользователь"
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        verbose_name="Действие"
    )
    model_name = models.CharField(
        max_length=50,
        verbose_name="Модель"
    )
    object_id = models.IntegerField(
        verbose_name="ID объекта"
    )
    details = models.TextField(
        blank=True,
        verbose_name="Детали"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Временная метка"
    )
    
    class Meta:
        verbose_name = "Журнал аудита"
        verbose_name_plural = "Журналы аудита"
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user} - {self.action} - {self.model_name}"