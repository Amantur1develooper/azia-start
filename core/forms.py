from django import forms
from .models import SalaryPayment, Student, Income, Expense, Reservation, News, Teacher, Student2, Graduate, GalleryEvent, GalleryImage, Discount, AcademicYear
from django.utils import timezone 
from django.core.exceptions import ValidationError
import random
import string
from .models import Employee


class StudentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        # Финансовые поля (кроме суммы контракта) скрыты для обычных пользователей
        if user and not (user.is_staff or user.is_superuser):
            for f in ['contract_date', 'contract_file', 'payment_notes']:
                if f in self.fields:
                    del self.fields[f]
        # Сумму контракта видят все, но редактирует только суперпользователь
        if user and not user.is_superuser:
            if 'contract_amount' in self.fields:
                self.fields['contract_amount'].disabled = True
                self.fields['contract_amount'].help_text = 'Только суперпользователь может изменять сумму контракта.'
        # Добавляем классы и placeholder для полей
        for field in self.fields:
            if field not in ['is_active', 'is_graduated', 'pol']:
                self.fields[field].widget.attrs.update({
                    'class': 'form-control'
                })
            if field in ['full_name', 'number_contract']:
                self.fields[field].widget.attrs['placeholder'] = 'Введите значение...'

    class Meta:
        model = Student
        fields = [
            'full_name', 'birth_date', 'pol', 'parent_contacts',
            'admission_date', 'enrollment_year', 'number_contract', 'grade', 'status',
            'is_active', 'is_graduated', 'contract_amount', 'contract_date', 'contract_file',
            'payment_notes'
        ]
        widgets = {
            'birth_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'admission_date': forms.DateInput(
                format='%Y-%m-%d',
                attrs={'type': 'date', 'class': 'form-control'}
            ),
            'contract_date': forms.DateInput(
                format='%Y-%m-%d',
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
            'enrollment_year': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'full_name': 'ФИО ученика',
            'birth_date': 'Дата рождения',
            'pol': 'Пол',
            'parent_contacts': 'Контакты родителей',
            'admission_date': 'Дата поступления',
            'enrollment_year': 'Год зачисления (с какого учебного года учится)',
            'number_contract': 'Номер контракта',
            'grade': 'Класс',
            'status': 'Статус',
            'is_active': 'Активный (учится)',
            'is_graduated': 'Выпустился',
            'contract_amount': 'Сумма контракта (сом)',
            'contract_date': 'Дата подписания контракта',
            'contract_file': 'Файл контракта',
            'payment_notes': 'Примечания по оплате',
        }



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
        self.fields['date'].initial = timezone.now().date()
        self.fields['date'].widget = forms.DateInput(
            format='%Y-%m-%d',
            attrs={'type': 'date', 'class': 'form-control'}
        )

        
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
            'birth_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'contract_start_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'contract_end_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'hire_date': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
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


# ── CMS формы ────────────────────────────────────────────────────

class NewsForm(forms.ModelForm):
    class Meta:
        model = News
        fields = ['title', 'content', 'image', 'is_published']
        widgets = {
            'title':   forms.TextInput(attrs={'class': 'form-control'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 6}),
            'image':   forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Заголовок', 'content': 'Содержание',
            'image': 'Изображение', 'is_published': 'Опубликовать',
        }


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['first_name', 'last_name', 'subject', 'description',
                  'image', 'is_main', 'is_publish', 'order']
        widgets = {
            'first_name':   forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':    forms.TextInput(attrs={'class': 'form-control'}),
            'subject':      forms.TextInput(attrs={'class': 'form-control'}),
            'description':  forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image':        forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'order':        forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Имя', 'last_name': 'Фамилия',
            'subject': 'Предмет', 'description': 'Описание',
            'image': 'Фото', 'is_main': 'Главный учитель',
            'is_publish': 'Показывать на сайте', 'order': 'Порядок',
        }


class BestStudentForm(forms.ModelForm):
    class Meta:
        model = Student2
        fields = ['first_name', 'last_name', 'level', 'achievements',
                  'image', 'is_featured', 'order']
        widgets = {
            'first_name':   forms.TextInput(attrs={'class': 'form-control'}),
            'last_name':    forms.TextInput(attrs={'class': 'form-control'}),
            'level':        forms.TextInput(attrs={'class': 'form-control'}),
            'achievements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image':        forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'order':        forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Имя', 'last_name': 'Фамилия',
            'level': 'Класс', 'achievements': 'Достижения',
            'image': 'Фото', 'is_featured': 'Показывать на главной',
            'order': 'Порядок',
        }


class GraduateForm(forms.ModelForm):
    class Meta:
        model = Graduate
        fields = ['username', 'graduation_year', 'achievements', 'image', 'order']
        widgets = {
            'username':        forms.TextInput(attrs={'class': 'form-control'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control'}),
            'achievements':    forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'image':           forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'order':           forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': 'ФИО выпускника', 'graduation_year': 'Год выпуска',
            'achievements': 'Достижения после школы', 'image': 'Фото', 'order': 'Порядок',
        }


class GalleryEventForm(forms.ModelForm):
    class Meta:
        model = GalleryEvent
        fields = ['title', 'description', 'date', 'cover_image']
        widgets = {
            'title':       forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date':        forms.DateInput(format='%Y-%m-%d', attrs={'class': 'form-control', 'type': 'date'}),
            'cover_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'title': 'Название события', 'description': 'Описание',
            'date': 'Дата', 'cover_image': 'Обложка',
        }


class GalleryImageForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['image', 'caption', 'order']
        widgets = {
            'image':   forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'caption': forms.TextInput(attrs={'class': 'form-control'}),
            'order':   forms.NumberInput(attrs={'class': 'form-control'}),
        }
        labels = {'image': 'Фото', 'caption': 'Подпись', 'order': 'Порядок'}


GalleryImageFormSet = forms.inlineformset_factory(
    GalleryEvent, GalleryImage,
    form=GalleryImageForm,
    extra=3, can_delete=True,
)


class DiscountForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['academic_year'].queryset = AcademicYear.objects.order_by('-start_date')

    class Meta:
        model = Discount
        fields = ['academic_year', 'amount', 'reason']
        widgets = {
            'academic_year': forms.Select(attrs={'class': 'form-select'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '0', 'min': '1'}),
            'reason': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Причина скидки...'}),
        }
        labels = {
            'academic_year': 'Учебный год',
            'amount': 'Сумма скидки (сом)',
            'reason': 'Причина',
        }