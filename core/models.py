import os
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

  
    def is_fully_paid_for_year(self, year):
        """Проверка полной оплаты за учебный год"""
        return self.get_total_paid_for_year(year) >= self.contract_amount
    
    def update_payment_status(self, year):
        """Обновляет статус оплаты для указанного учебного года"""
        self.current_year_paid = self.is_fully_paid_for_year(year)
        self.save()
        
        

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

from django.db import models

class Teacher(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    subject = models.CharField(max_length=100, verbose_name="Предмет")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='teachers/', verbose_name="Фото")
    is_main = models.BooleanField(default=False, verbose_name="Главный учитель?")
    is_publish = models.BooleanField(default=False, blank=True, null=True, verbose_name='На лицевую часть публиковать?')
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    class Meta:
        verbose_name = "Учитель"
        verbose_name_plural = "Учителя"
        ordering = ['order', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.subject}"
    
    
from django.db import models

class Student2(models.Model):
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    level = models.CharField(max_length=20, verbose_name="Класс")
    achievements = models.TextField(verbose_name="Достижения")
    image = models.ImageField(upload_to='students/', verbose_name="Фото")
    is_featured = models.BooleanField(default=False, verbose_name="Показывать на главной?")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок отображения")

    class Meta:
        verbose_name = "Лучший ученик"
        verbose_name_plural = "Лучшие ученики"
        ordering = ['order', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.level} класс"
    
    
from django.db import models
from django.utils import timezone

class News(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    content = models.TextField(verbose_name="Содержание")
    image = models.ImageField(upload_to='news/', verbose_name="Изображение")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="Дата публикации")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")
    
    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title
    
from django.db import models

class Document(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название документа")
    file = models.FileField(upload_to='documents/', verbose_name="Файл")
    category = models.CharField(max_length=100, verbose_name="Категория", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
# models.py
class TelegramSubscriber(models.Model):
    name = models.CharField(max_length=100, blank=True)
    chat_id = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name or self.chat_id}"


class Application(models.Model):
    child_name = models.CharField(max_length=100)
    child_surname = models.CharField(max_length=100)
    child_class = models.CharField(max_length=20)
    parent_phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        verbose_name = "Заявка на обучение"
        verbose_name_plural = "Заявки на обучение"
       
class Expense(models.Model):
    CATEGORIES = [
        ('salary', 'Зарплата'),
        ('materials', 'Учебные материалы'),
        ('events', 'Мероприятия'),
        ('utilities', 'Коммунальные услуги'),
        ('other', 'Другие расходы'),
        ('arenda','Аренда'),
        ('kichin','Кухня'),
    ]
    
    PAYMENT_METHODS = [
        ('cash', 'Наличные'),
        ('card', 'Безналичный'),
        ('bank_transfer', 'Банковский перевод'),
        ('online', 'Онлайн платеж'),
    ]
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name="Номер квитанции"
    )
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
    
    
    def save(self, *args, **kwargs):
        # Генерируем уникальный номер квитанции при создании
        if not self.receipt_number:
            current_year = timezone.now().strftime('%Y')
            last_receipt = Expense.objects.filter(
                receipt_number__startswith=f'RK-{current_year}-'
            ).order_by('-receipt_number').first()
            
            if last_receipt:
                last_num = int(last_receipt.receipt_number.split('-')[-1])
                new_num = last_num + 1
            else:
                new_num = 1
                
            self.receipt_number = f'RK-{current_year}-{str(new_num).zfill(4)}'
        super().save(*args, **kwargs)

 

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
    
#сотрудники
class Position(models.Model):
    """Должности сотрудников"""
    name = models.CharField(max_length=100, verbose_name="Название должности")
    description = models.TextField(blank=True, verbose_name="Описание")
    
    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"
    
    def __str__(self):
        return self.name
    
    

class Employee(models.Model):
    """Сотрудники школы"""
    GENDER_CHOICES = [
        ('male', 'Мужской'),
        ('female', 'Женский'),
    ]
    
    CONTRACT_TYPES = [
        ('permanent', 'Бессрочный'),
        ('fixed_term', 'Срочный'),
        ('temporary', 'Временный'),
    ]
    
    full_name = models.CharField(max_length=200, verbose_name="ФИО сотрудника")
    birth_date = models.DateField(verbose_name="Дата рождения")
    gender = models.CharField(
        max_length=10, 
        choices=GENDER_CHOICES, 
        verbose_name="Пол"
    )
    address = models.TextField(verbose_name="Адрес")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(blank=True, verbose_name="Email")
    position = models.ForeignKey(
        Position,
        on_delete=models.PROTECT,
        verbose_name="Должность"
    )
    
    # Поля контракта
    contract_type = models.CharField(
        max_length=20,
        choices=CONTRACT_TYPES,
        verbose_name="Тип контракта"
    )
    contract_number = models.CharField(
        max_length=50, 
        verbose_name="Номер контракта",
        blank=True,
        null=True
    )
    contract_start_date = models.DateField(
        verbose_name="Дата начала контракта"
    )
    contract_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="Дата окончания контракта"
    )
    monthly_salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Месячная зарплата (сом)"
    )
    contract_file = models.FileField(
        upload_to='employee_contracts/',
        blank=True,
        null=True,
        verbose_name="Файл контракта"
    )
    
    hire_date = models.DateField(verbose_name="Дата приема на работу")
    is_active = models.BooleanField(default=True, verbose_name="Активный сотрудник")
    notes = models.TextField(blank=True, verbose_name="Примечания")
    
    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"
        ordering = ['full_name']
    
    def __str__(self):
        return f"{self.full_name} ({self.position})"
    
    @property
    def contract_status(self):
        """Статус контракта"""
        if not self.is_active:
            return "Неактивен"
        if self.contract_type == 'permanent':
            return "Бессрочный"
        if self.contract_end_date and timezone.now().date() > self.contract_end_date:
            return "Истек"
        return "Действует"

class SalaryPayment(models.Model):
    """Зарплатные выплаты (как расходы)"""
    employee = models.ForeignKey(
        Employee,
        on_delete=models.PROTECT,
        verbose_name="Сотрудник"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Сумма выплаты"
    )
    payment_date = models.DateField(verbose_name="Дата выплаты")
    for_month = models.DateField(verbose_name="За месяц")  # Хранит первый день месяца
    payment_method = models.CharField(
        max_length=15,
        choices=Expense.PAYMENT_METHODS,
        verbose_name="Способ оплаты"
    )
    is_bonus = models.BooleanField(
        default=False,
        verbose_name="Премиальная выплата"
    )
    notes = models.TextField(blank=True, verbose_name="Примечания")
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
        verbose_name = "Зарплатная выплата"
        verbose_name_plural = "Зарплатные выплаты"
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"Выплата {self.employee} - {self.amount} за {self.for_month.strftime('%B %Y')}"
    
    def save(self, *args, **kwargs):
        # Автоматически создаем связанный расход при создании выплаты
        if not self.pk:
            Expense.objects.create(
                date=self.payment_date,
                category='salary',
                supplier=f"Зарплата {self.employee.full_name}",
                amount=self.amount,
                payment_method=self.payment_method,
                notes=f"Зарплатная выплата за {self.for_month.strftime('%B %Y')}. {self.notes}",
                created_by=self.created_by
            )
        super().save(*args, **kwargs)
        
from django.db import models
from django.utils.text import slugify

class GalleryEvent(models.Model):
    title = models.CharField(max_length=200, verbose_name="Название события")
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField(verbose_name="Описание", blank=True)
    date = models.DateField(verbose_name="Дата события")
    cover_image = models.ImageField(upload_to='gallery/covers/', verbose_name="Обложка")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Событие галереи"
        verbose_name_plural = "События галереи"
        ordering = ['-date']
    
    
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    @property
    def image_count(self):
        return self.images.count()
    def __str__(self):
        return self.title

class GalleryImage(models.Model):
    event = models.ForeignKey(GalleryEvent, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='gallery/images/', verbose_name="Изображение")
    caption = models.CharField(max_length=255, blank=True, verbose_name="Подпись")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок")
    
    class Meta:
        verbose_name = "Изображение галереи"
        verbose_name_plural = "Изображения галереи"
        ordering = ['order']
    
    def __str__(self):
        return f"Изображение {self.id} для {self.event.title}"