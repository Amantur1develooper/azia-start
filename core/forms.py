from django import forms
from .models import SalaryPayment, Student, Income, Expense, Reservation
from django.utils import timezone 

class StudentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем классы и placeholder для полей
        for field in self.fields:
            if field not in ['is_active', 'pol']:
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })
            if field in ['full_name', 'number_contract']:
                self.fields[field].widget.attrs['placeholder'] = 'Введите значение...'
    
    class Meta:
        model = Student
        fields = [
            'full_name', 'birth_date', 'pol', 'parent_contacts',
            'admission_date', 'number_contract', 'grade', 'status',
            'is_active', 'contract_amount', 'contract_date', 'contract_file',
            'payment_notes'
        ]
        widgets = {
            'birth_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'admission_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'contract_date': forms.DateInput(
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'parent_contacts': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Телефоны, email и другие контакты...'}
            ),
            'payment_notes': forms.Textarea(
                attrs={'rows': 3, 'class': 'form-control', 'placeholder': 'Дополнительная информация по оплате...'}
            ),
            'grade': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'pol': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'full_name': 'ФИО ученика',
            'birth_date': 'Дата рождения',
            'pol': 'Пол',
            'parent_contacts': 'Контакты родителей',
            'admission_date': 'Дата поступления',
            'number_contract': 'Номер контракта',
            'grade': 'Класс',
            'status': 'Статус',
            'is_active': 'Активный',
            'contract_amount': 'Сумма контракта (сом)',
            'contract_date': 'Дата подписания контракта',
            'contract_file': 'Файл контракта',
            'payment_notes': 'Примечания по оплате',
        }
# class StudentForm(forms.ModelForm):
#     class Meta:
#         model = Student
#         fields = [
#             'full_name', 'birth_date', 'pol', 'parent_contacts',
#             'admission_date', 'number_contract', 'grade', 'status',
#             'is_active', 'contract_amount', 'contract_date', 'contract_file',
#             'payment_notes'
#         ]
#         widgets = {
#             'birth_date': forms.DateInput(attrs={'type': 'date'}),
#             'admission_date': forms.DateInput(attrs={'type': 'date'}),
#             'contract_date': forms.DateInput(attrs={'type': 'date'}),
#             'parent_contacts': forms.Textarea(attrs={'rows': 3}),
#             'payment_notes': forms.Textarea(attrs={'rows': 3}),
#         }
#         labels = {
#             'contract_amount': 'Сумма контракта (сом)',
#             'contract_date': 'Дата подписания контракта',
#         }
# class StudentForm(forms.ModelForm):
#     class Meta:
#         model = Student
#         fields = [
#             'full_name', 'birth_date', 'pol', 'parent_contacts',
#             'admission_date', 'number_contract', 'grade', 'status',
#             'is_active', 'contract_amount', 'contract_date', 'contract_file',
#             'payment_notes'
#         ]
#         widgets = {
#             'birth_date': forms.DateInput(attrs={'type': 'date'}),
#             'admission_date': forms.DateInput(attrs={'type': 'date'}),
#             'contract_date': forms.DateInput(attrs={'type': 'date'}),
#             'contract_amount': forms.NumberInput(attrs={'step': '0.01'}),
#             'parent_contacts': forms.Textarea(attrs={'rows': 3}),
#             'payment_notes': forms.Textarea(attrs={'rows': 3}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self.instance and self.instance.grade:
#             self.fields['contract_amount'].initial = self.instance.grade.annual_tuition
# class StudentForm(forms.ModelForm):
#     class Meta:
#         model = Student
#         fields = [
#             'full_name', 'birth_date', 'parent_contacts', 'admission_date',
#             'number_contract', 'grade', 'status', 'is_active'
#         ]
#         widgets = {
#             'birth_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'admission_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'parent_contacts': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#             'full_name': forms.TextInput(attrs={'class': 'form-control'}),
#             'number_contract': forms.NumberInput(attrs={'class': 'form-control'}),
#             'grade': forms.Select(attrs={'class': 'form-select'}),
#             'status': forms.Select(attrs={'class': 'form-select'}),
#             'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
#         }

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Устанавливаем текущую дату для admission_date, если она не передана
#         if not self.initial.get('admission_date'):
#             self.initial['admission_date'] = timezone.now().date()
        # Можно также отфильтровать queryset для 'grade', если нужно,
        # например, показывать только классы с доступными местами (но это сложнее для CreateView)
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Income, Student
import random
import string

class ExpenseForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем классы и placeholder для полей
        for field in self.fields:
            if field != 'is_active':
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })
            if field in ['supplier', 'invoice_number']:
                self.fields[field].widget.attrs['placeholder'] = 'Введите значение...'
    
    class Meta:
        model = Expense
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'payment_method': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'amount': 'Сумма расхода (сом)',
            'invoice': 'Счет/фактура',
        }
class IncomeForm(forms.ModelForm):
    months = forms.MultipleChoiceField(
        choices=Income.MONTH_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Оплатить месяцы"
    )
    full_year = forms.BooleanField(
        required=False,
        label="Оплатить весь учебный год"
    )
    
    class Meta:
        model = Income
        fields = ['date','student','amount','payment_method','income_type','status','notes','paid_months']
    
    def __init__(self, *args, **kwargs):
        student_id = kwargs.pop('student_id', None)
        super().__init__(*args, **kwargs)
        
        if student_id:
            self.fields['student'].initial = student_id
            self.fields['student'].widget = forms.HiddenInput()
    
    def clean(self):
        cleaned_data = super().clean()
        months = cleaned_data.get('months')
        full_year = cleaned_data.get('full_year')
        
        if full_year and months:
            raise forms.ValidationError("Выберите либо оплату за весь год, либо отдельные месяцы")
        
        return cleaned_data
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        months = self.cleaned_data.get('months', [])
        full_year = self.cleaned_data.get('full_year', False)
        
        instance.paid_months = months
        instance.is_full_year_payment = full_year
        
        if commit:
            instance.save()
        
        return instance
# class IncomeForm(forms.ModelForm):
#     def __init__(self, *args, student_id=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.student_id = student_id
#         if not self.instance.pk:
#             self.initial['transaction_id'] = self.generate_transaction_id()
#             self.initial['status'] = 'paid'
    
#     class Meta:
#         model = Income
#         fields = ['date', 'amount', 'payment_method', 'income_type', 'status', 'transaction_id', 'notes']
#         widgets = {
#             'date': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'form-control',
#                 'value': timezone.now().strftime('%Y-%m-%d')
#             }),
#             'amount': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'step': '0.01'
#             }),
#             'payment_method': forms.Select(attrs={
#                 'class': 'form-select'
#             }),
#             'income_type': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'readonly': 'readonly'
#             }),
#             'status': forms.Select(attrs={
#                 'class': 'form-select'
#             }),
#             'transaction_id': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'readonly': 'readonly'
#             }),
#             'notes': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 3
#             }),
#         }
    
#     def save(self, commit=True):
#         instance = super().save(commit=False)
#         instance.student_id = self.student_id
#         if commit:
#             instance.save()
#         return instance
    
#     def generate_transaction_id(self):
#         date_part = timezone.now().strftime('%Y%m%d')
#         rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
#         return f"INV-{date_part}-{rand_part}"
# class IncomeForm(forms.ModelForm):
#     class Meta:
#         model = Income
#         fields = ['date', 'amount', 'payment_method', 'income_type', 'status', 'transaction_id', 'notes']
#         widgets = {
#             'date': forms.DateInput(
#                 attrs={
#                     'type': 'date',
#                     'class': 'form-control',
#                     'value': timezone.now().strftime('%Y-%m-%d')
#                 }
#             ),
#             'amount': forms.NumberInput(
#                 attrs={
#                     'class': 'form-control',
#                     'step': '0.01',
#                     'placeholder': 'Введите сумму'
#                 }
#             ),
#             'payment_method': forms.Select(
#                 attrs={'class': 'form-select'}
#             ),
#             'income_type': forms.TextInput(
#                 attrs={
#                     'class': 'form-control',
#                     'readonly': 'readonly'
#                 }
#             ),
#             'status': forms.Select(
#                 attrs={'class': 'form-select'}
#             ),
#             'transaction_id': forms.TextInput(
#                 attrs={
#                     'class': 'form-control',
#                     'readonly': 'readonly'
#                 }
#             ),
#             'notes': forms.Textarea(
#                 attrs={
#                     'class': 'form-control',
#                     'rows': 3,
#                     'placeholder': 'Дополнительная информация'
#                 }
#             ),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if not self.instance.pk:
#             self.initial['transaction_id'] = self.generate_transaction_id()
#             self.initial['status'] = 'paid'
    
#     def generate_transaction_id(self):
#         date_part = timezone.now().strftime('%Y%m%d')
#         rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
#         return f"INV-{date_part}-{rand_part}"
# class IncomeForm(forms.ModelForm):
#     student_search = forms.CharField(
#         label='Поиск ученика',
#         required=False,
#         widget=forms.TextInput(attrs={
#             'class': 'form-control',
#             'placeholder': 'Введите ФИО ученика',
#             'hx-get': '/students/search/',
#             'hx-trigger': 'keyup changed delay:500ms',
#             'hx-target': '#student-results',
#             'hx-swap': 'innerHTML'
#         })
#     )
    
#     class Meta:
#         model = Income
#         fields = '__all__'
#         widgets = {
#             'date': forms.DateInput(attrs={
#                 'type': 'date',
#                 'class': 'form-control',
#                 'value': timezone.now().strftime('%Y-%m-%d')
#             }),
#             'student': forms.HiddenInput(),
#             'amount': forms.NumberInput(attrs={
#                 'class': 'form-control',
#                 'step': '0.01'
#             }),
#             'payment_method': forms.Select(attrs={
#                 'class': 'form-select'
#             }),
#             'income_type': forms.TextInput(attrs={
#                 'class': 'form-control'
#             }),
#             'status': forms.Select(attrs={
#                 'class': 'form-select'
#             }),
#             'transaction_id': forms.TextInput(attrs={
#                 'class': 'form-control',
#                 'readonly': 'readonly'
#             }),
#             'notes': forms.Textarea(attrs={
#                 'class': 'form-control',
#                 'rows': 3
#             }),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.fields['date'].initial = timezone.now().date()
#         if not self.instance.pk and not self.data.get('transaction_id'):
#             self.initial['transaction_id'] = self.generate_transaction_id()
    
#     def generate_transaction_id(self):
#         date_part = timezone.now().strftime('%Y%m%d')
#         rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
#         return f"INV-{date_part}-{rand_part}"
# from django.core.exceptions import ValidationError
# from .models import Income
# import random
# import string

# class IncomeForm(forms.ModelForm):
#     class Meta:
#         model = Income
#         fields = '__all__'
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'student': forms.Select(attrs={'class': 'form-select'}),
#             'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
#             'payment_method': forms.Select(attrs={'class': 'form-select'}),
#             'income_type': forms.TextInput(attrs={'class': 'form-control'}),
#             'status': forms.Select(attrs={'class': 'form-select'}),
#             'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
#             'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
#         }
    
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         # Генерация номера транзакции, если поле пустое
#         if not self.instance.pk and not self.data.get('transaction_id'):
#             self.initial['transaction_id'] = self.generate_transaction_id()
    
#     def generate_transaction_id(self):
#         """Генерация уникального номера транзакции"""
#         date_part = timezone.now().strftime('%Y%m%d')
#         rand_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
#         return f"INV-{date_part}-{rand_part}"
# class IncomeForm(forms.ModelForm):
#     class Meta:
#         model = Income
#         fields = '__all__'
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date'}),
#         }

class ExpenseForm(forms.ModelForm):
    class Meta:
        model = Expense
        exclude = ['created_by', 'created_at'] 
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = '__all__'
        
        
from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'full_name', 'birth_date', 'gender', 'address', 'phone', 'email',
            'position', 'contract_type', 'contract_number', 'contract_start_date',
            'contract_end_date', 'monthly_salary', 'contract_file', 'hire_date', 
            'is_active', 'notes'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'contract_start_date': forms.DateInput(attrs={'type': 'date'}),
            'contract_end_date': forms.DateInput(attrs={'type': 'date'}),
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'address': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Делаем поле contract_end_date необязательным
        self.fields['contract_end_date'].required = False
        self.fields['contract_file'].required = False
        self.fields['email'].required = False
        self.fields['notes'].required = False
        
        
class SalaryPaymentForm(forms.ModelForm):
    class Meta:
        model = SalaryPayment
        fields = ['employee', 'amount', 'payment_date', 'for_month', 
                 'payment_method', 'is_bonus', 'notes']
        widgets = {
            'payment_date': forms.DateInput(attrs={'type': 'date'}),
            'for_month': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Устанавливаем текущую дату по умолчанию
        self.fields['payment_date'].initial = timezone.now().date()
        # Устанавливаем первый день текущего месяца по умолчанию
        today = timezone.now().date()
        self.fields['for_month'].initial = today.replace(day=1)