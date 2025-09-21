from django.shortcuts import render
from django.db.models import Sum
from django.core.mail import EmailMessage
from django.conf import settings
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import requests
from core.pdf_utils import generate_receipt
from .receipts import generate_receipt_pdf
from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib import messages
import os
from django.views import View
from django.template.loader import get_template  # Добавьте этот импорт
from django.utils.timezone import now
from io import BytesIO
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.db.models import Sum
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse, reverse_lazy
from .models import AcademicYear, Employee, News, SalaryPayment, Student, Grade, Income, Expense, Reservation, AuditLog, Student2, Teacher
from .forms import EmployeeForm, SalaryPaymentForm, StudentForm, IncomeForm, ExpenseForm, ReservationForm
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter
from django.contrib.auth import logout
# views.py
from django.shortcuts import render, redirect
from .models import Application
from django.views.generic import ListView, DetailView
from .models import News
from .models import TelegramSubscriber
# Главная страница
from django.shortcuts import render
from .models import Student, AcademicYear
from django.db.models import Count, Sum, Q
from django.http import HttpResponse
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment, PatternFill
from openpyxl.utils import get_column_letter  
from django.utils import timezone
from django.contrib import messages
from django.shortcuts import get_object_or_404
from django.views.generic import View
class NewsListView(ListView):
    model = News
    template_name = 'news_list.html'
    context_object_name = 'news_list'
    paginate_by = 6  # Показывать по 6 новостей на странице
    
    def get_queryset(self):
        return News.objects.all().order_by('-created_at')

class NewsDetailView(DetailView):
    model = News
    template_name = 'news_detail.html'
    context_object_name = 'news'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Добавляем последние новости для боковой колонки
        context['recent_news'] = News.objects.exclude(id=self.object.id).order_by('-created_at')[:3]
        return context
    
TELEGRAM_BOT_TOKEN = "7392373379:AAFmvBHQE6uCWJ817i9H3M9fKEYgUwaNoaE"

def best_student(request):
    students = Student2.objects.all()
    return render(request, 'best_student.html',{'students':students})

def application_view(request):
    if request.method == 'POST':
        child_name = request.POST.get('child_name')
        child_surname = request.POST.get('child_surname')
        child_class = request.POST.get('child_class')
        parent_phone = request.POST.get('parent_phone')
        
        Application.objects.create(
            child_name=child_name,
            child_surname=child_surname,
            child_class=child_class,
            parent_phone=parent_phone
        )
         # Формируем сообщение
        message = (
            f"📥 Новая заявка:\n"
            f"👶 Ребёнок: {child_name} {child_surname}\n"
            f"📚 Класс: {child_class}\n"
            f"📞 Телефон родителя: {parent_phone}"
        )

        # Отправка всем активным подписчикам
        subscribers = TelegramSubscriber.objects.filter(is_active=True)
        for subscriber in subscribers:
            try:
                requests.post(
                    f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage',
                    data={'chat_id': subscriber.chat_id, 'text': message}
                )
            except Exception as e:
                print(f"Ошибка при отправке для {subscriber.chat_id}: {e}")

    teachers = Teacher.objects.filter(is_publish=True)
     # Проверяем, есть ли главный учитель для отображения по умолчанию
    main_teacher = teachers.filter(is_main=True).first()
    if not main_teacher and teachers.exists():
        main_teacher = teachers.first()
    best_students = Student2.objects.filter(is_featured=True).order_by('order')[:5]  # Ограничив
    news_list = News.objects.filter(is_published=True).order_by('-created_at')[:3]
    return render(request, 'index.html',{'main_teacher':main_teacher, 
                                         'teachers':teachers,
                                         'best_students': best_students,
                                          'news_list': news_list,})
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

def get_teacher(request, teacher_id):
    teacher = get_object_or_404(Teacher, id=teacher_id)
    
    data = {
        'success': True,
        'teacher': {
            'id': teacher.id,
            'first_name': teacher.first_name,
            'last_name': teacher.last_name,
            'subject': teacher.subject,
            'description': teacher.description,
            'image': teacher.image.url,
        }
    }
    return JsonResponse(data)

class ClassDebtsReportView(LoginRequiredMixin, View):
    def test_func(self):
        return is_admin(self.request.user) or is_accountant(self.request.user)
    
    def get(self, request):
        # Получаем текущий учебный год
        current_year = AcademicYear.objects.filter(is_current=True).first()
        if not current_year:
            return HttpResponse("Текущий учебный год не установлен", status=400)

        # Создаем Excel-файл
        wb = Workbook()
        ws = wb.active
        ws.title = "Задолженности по классам"
        
        # Стили
        header_fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")
        header_font = Font(bold=True)
        center_aligned = Alignment(horizontal='center')
        right_aligned = Alignment(horizontal='right')
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Заголовки
        headers = [
            'Класс', 'Ученик', 'Сумма контракта', 
            'Оплачено', 'Остаток', 'Статус'
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_aligned
            cell.border = border

        # Получаем данные по классам
        grades = Grade.objects.all().order_by('number', 'parallel')
        row_num = 2
        
        for grade in grades:
            students = grade.student_set.filter(is_active=True)
            
            for student in students:
                # Рассчитываем оплаты за текущий год
                payments = Income.objects.filter(
                    student=student,
                    academic_year=current_year,
                    status='paid'
                ).aggregate(total=Sum('amount'))['total'] or 0
                
                contract_amount = student.contract_amount or 0
                remaining = max(contract_amount - payments, 0)
                
                # Добавляем данные в таблицу
                ws.cell(row=row_num, column=1, 
                       value=f"{grade.number}{grade.parallel}").border = border
                ws.cell(row=row_num, column=2, 
                       value=student.full_name).border = border
                ws.cell(row=row_num, column=3, 
                       value=contract_amount).border = border
                ws.cell(row=row_num, column=4, 
                       value=payments).border = border
                ws.cell(row=row_num, column=5, 
                       value=remaining).border = border
                ws.cell(row=row_num, column=6, 
                       value=student.get_status_display()).border = border
                
                # Форматируем числовые ячейки
                for col in [3,4,5]:
                    ws.cell(row=row_num, column=col).number_format = '#,##0.00'
                    ws.cell(row=row_num, column=col).alignment = right_aligned
                
                # Подсветка должников
                if remaining > 0:
                    for col in range(1,7):
                        ws.cell(row=row_num, column=col).fill = PatternFill(
                            start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")
                
                row_num += 1
        
        # Добавляем итоги по классам
        ws.cell(row=row_num, column=1, value="ИТОГО:").font = header_font
        for col, formula in [
            (3, f"SUM(C2:C{row_num-1})"),
            (4, f"SUM(D2:D{row_num-1})"),
            (5, f"SUM(E2:E{row_num-1})")
        ]:
            ws.cell(row=row_num, column=col, value=formula)
            ws.cell(row=row_num, column=col).number_format = '#,##0.00'
            ws.cell(row=row_num, column=col).font = header_font
            ws.cell(row=row_num, column=col).alignment = right_aligned
            ws.cell(row=row_num, column=col).border = border

        # Настраиваем ширину столбцов
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column].width = adjusted_width

        # Формируем ответ
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename="class_debts_report_{current_year.year}.xlsx"'},
        )
        wb.save(response)
        return response
   


def logout_view(request):
    logout(request)
    return redirect('home') 

def is_admin(user):
    return user.is_superuser

def is_accountant(user):
    return user.groups.filter(name='Бухгалтер').exists()



@login_required()
def home(request):
    current_year = AcademicYear.objects.filter(is_current=True).first()

    students = Student.objects.all()
    studying = students.filter(status='studying')
    reserve = students.filter(status='reserve')
    expelled = students.filter(status='expelled')

    male_count = studying.filter(pol='male').count()
    female_count = studying.filter(pol='female').count()

    fully_paid = studying.filter(current_year_paid=True).count()
    not_paid = studying.filter(current_year_paid=False).count()

    total_students = studying.count()
    total_reserve = reserve.count()
    total_expelled = expelled.count()

    total_contract_amount = studying.aggregate(total=Sum('contract_amount'))['total'] or 0
    total_paid_amount = sum([s.get_total_paid_for_year(current_year) for s in studying])
    total_remaining = max(total_contract_amount - total_paid_amount, 0)

    context = {
        'total_students': total_students,
        'male_count': male_count,
        'female_count': female_count,
        'fully_paid': fully_paid,
        'not_paid': not_paid,
        'total_reserve': total_reserve,
        'total_expelled': total_expelled,
        'total_contract_amount': total_contract_amount,
        'total_paid_amount': total_paid_amount,
        'total_remaining': total_remaining,
    }

    return render(request, 'school/home.html', context)



from django.shortcuts import render
from django.views.generic import ListView
from .models import Student, Grade
# Студенты
class StudentListView(ListView):
    model = Student
    template_name = 'school/students/list.html'
    context_object_name = 'students'
    paginate_by = 20

    def get_queryset(self):
        queryset = super().get_queryset().select_related('grade')
        grade_filter = self.request.GET.get('grade')
        
        if grade_filter:
            if '-' in grade_filter:
                number, parallel = grade_filter.split('-')
                queryset = queryset.filter(grade__number=number, grade__parallel=parallel)
        
        return queryset.order_by('grade__number', 'grade__parallel', 'full_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['grades'] = Grade.objects.all().order_by('number', 'parallel')
        context['selected_grade'] = self.request.GET.get('grade', '')
        return context


class StudentDetailView(LoginRequiredMixin, DetailView):
    model = Student
    template_name = 'school/students/detail.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object
    
    # Получаем текущий учебный год
        current_year = AcademicYear.objects.filter(is_current=True).first()
    
    # Фильтруем платежи по текущему учебному году
        payments = Income.objects.filter(
            student=student,
            academic_year=current_year
        ).order_by('-date')
    
    # Сумма платежей за текущий учебный год
        total_payments = payments.aggregate(Sum('amount'))['amount__sum'] or 0
    
    # Остаток к оплате
        remaining_payment = student.contract_amount - total_payments if student.contract_amount else 0
    
        context.update({
        'student': student,
        'payments': payments,
        'total_payments': total_payments,
        'remaining_payment': remaining_payment,
        'current_year': current_year,
    })
        return context
  
class StudentCreateView(LoginRequiredMixin, CreateView):  # Убрали UserPassesTestMixin
    model = Student
    form_class = StudentForm
    template_name = 'school/students/form.html'
    success_url = reverse_lazy('student-list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление нового ученика'
        context['submit_text'] = 'Создать ученика'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(
            self.request,
            f"Ученик {form.instance.full_name} успешно добавлен!"
        )
        return super().form_valid(form)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')  # укажи куда перенаправить после входа
        else:
            messages.error(request, 'Неверное имя пользователя или пароль.')

    return render(request, 'login.html')

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'  # путь к твоему шаблону
    redirect_authenticated_user = True  # если пользователь уже вошёл, перекинуть

    def get_success_url(self):
        return self.get_redirect_url() or '/'  # куда перекидывать после входа (например, на главную)



class StudentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Student
    form_class = StudentForm
    template_name = 'school/students/form.html'
    success_url = reverse_lazy('student-list')
    
    def test_func(self):
        return is_admin(self.request.user)
from django.http import HttpResponse, JsonResponse
from django.db.models import Q

def student_search(request):
    query = request.GET.get('q', '')
    if query:
        students = Student.objects.filter(
            Q(full_name__icontains=query) |
            Q(parent_contacts__icontains=query)
        )[:10]
        results = [
            {
                'id': student.id,
                'text': f"{student.full_name} ({student.grade.number}{student.grade.parallel})"
            } for student in students
        ]
    else:
        results = []
    return JsonResponse({'results': results})
# Доходы
from django.db.models import Q
# from datetime import datetime
from django.http import HttpResponse
import csv
from django.db.models import Q, Sum
# from datetime import datetime
from django.http import HttpResponse
import csv

class IncomeListView(LoginRequiredMixin, ListView):
    model = Income
    template_name = 'school/incomes/list.html'
    context_object_name = 'incomes'
    paginate_by = 20
    
    def test_func(self):
        return is_admin(self.request.user) or is_accountant(self.request.user)
    def generate_transfer_act_pdf(self, queryset):
        total_amount = queryset.aggregate(total=Sum('amount'))['total'] or 0
        date_from = self.request.GET.get('date_from', 'не указана')
        date_to = self.request.GET.get('date_to', 'не указана')
    
        context = {
        'incomes': queryset,
        'total_amount': total_amount,
        'date_from': date_from,
        'date_to': date_to,
        'generated_date': now().strftime('%d.%m.%Y %H:%M'),
        'user': self.request.user.get_full_name() or self.request.user.username,
        }
    
        template = get_template('school/incomes/transfer_act_html.html')
        html = template.render(context)
    
        return HttpResponse(html)
       

    def render_to_response(self, context, **response_kwargs):
        # Обработка экспорта в Excel
        if self.request.GET.get('export') == 'xlsx':
            return self.export_to_excel()
        # Обработка генерации акта передачи
        elif self.request.GET.get('export') == 'pdf':
            queryset = self.get_queryset()
            return self.generate_transfer_act_pdf(queryset)
            
        return super().render_to_response(context, **response_kwargs)
    def export_to_excel(self):
        queryset = self.get_queryset()
        total_amount = queryset.aggregate(Sum('amount'))['amount__sum'] or 0

        # Создаем Excel-файл
        wb = Workbook()
        ws = wb.active
        ws.title = "Приходы"

        # Стили для заголовков
        header_font = Font(bold=True)
        header_alignment = Alignment(horizontal='center')
        border = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )

        # Заголовки
        headers = [
            'Дата', 'Ученик', 'Класс', 'Сумма (сом)', 
            'Способ оплаты', 'Статус', 'Номер транзакции', 'Период оплаты'
        ]
        
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num, value=header)
            cell.font = header_font
            cell.alignment = header_alignment
            cell.border = border

        # Данные
        for row_num, income in enumerate(queryset, 2):
            ws.cell(row=row_num, column=1, value=income.date.strftime('%d.%m.%Y')).border = border
            ws.cell(row=row_num, column=2, value=income.student.full_name).border = border
            ws.cell(row=row_num, column=3, value=f"{income.student.grade.number}{income.student.grade.parallel}").border = border
            ws.cell(row=row_num, column=4, value=float(income.amount)).border = border
            ws.cell(row=row_num, column=5, value=income.get_payment_method_display()).border = border
            ws.cell(row=row_num, column=6, value=income.get_status_display()).border = border
            ws.cell(row=row_num, column=7, value=income.transaction_id).border = border
            ws.cell(row=row_num, column=8, value=income.get_paid_months_display()).border = border

        # Добавляем строку с итогами
        last_row = len(queryset) + 2
        ws.cell(row=last_row, column=1, value="ИТОГО:").font = header_font
        ws.cell(row=last_row, column=4, value=float(total_amount)).font = header_font
        ws.cell(row=last_row, column=4).number_format = '#,##0.00'

        # Настраиваем ширину столбцов
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column].width = adjusted_width

        # Формируем ответ
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            headers={'Content-Disposition': f'attachment; filename="income_report_{datetime.now().strftime("%Y-%m-%d")}.xlsx"'},
        )
        wb.save(response)
        return response

   

    def get_queryset(self):
        queryset = super().get_queryset().select_related('student', 'academic_year')
        
        # Фильтрация по дате
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
            
        # Фильтрация по статусу
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
            
        # Фильтрация по способу оплаты
        payment_method = self.request.GET.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
            
        # Фильтрация по ученику (через поиск)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(student__full_name__icontains=search) |
                Q(transaction_id__icontains=search)
            )
            
        return queryset.order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем параметры фильтрации в контекст
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['status'] = self.request.GET.get('status', '')
        context['payment_method'] = self.request.GET.get('payment_method', '')
        context['search'] = self.request.GET.get('search', '')
        
        # Добавляем choices для фильтров
        context['status_choices'] = Income.STATUS_CHOICES
        context['payment_method_choices'] = Income.PAYMENT_METHODS
        
        # Суммарная информация
        queryset = self.get_queryset()
        context['total_amount'] = queryset.aggregate(Sum('amount'))['amount__sum'] or 0
        context['total_count'] = queryset.count()
        
        return context
    
  
    
    def export_to_csv(self):
        queryset = self.get_queryset()
        
        response = HttpResponse(
            content_type='text/csv',
            headers={'Content-Disposition': f'attachment; filename="income_report_{datetime.now().strftime("%Y-%m-%d")}.csv"'},
        )
        
        writer = csv.writer(response)
        
        # Заголовки CSV
        writer.writerow([
            'Дата',
            'Ученик',
            'Класс',
            'Сумма (сом)',
            'Способ оплаты',
            'Статус',
            'Номер транзакции',
            'Период оплаты',
            'Учебный год'
        ])
        
        # Данные
        for income in queryset:
            writer.writerow([
                income.date.strftime('%d.%m.%Y'),
                income.student.full_name,
                f"{income.student.grade.number}{income.student.grade.parallel}",
                income.amount,
                income.get_payment_method_display(),
                income.get_status_display(),
                income.transaction_id,
                income.get_paid_months_display(),
                income.academic_year.year if income.academic_year else ''
            ])
        
        return response



class DownloadReceiptView(View):
    def get(self, request, pk):
        from .models import Income
        income = Income.objects.get(pk=pk)
        pdf_buffer = generate_receipt_pdf(income)
        response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{income.transaction_id}.pdf"'
        return response

      
class IncomeCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Income
    form_class = IncomeForm
    template_name = 'school/incomes/form.html'
    
    def get_success_url(self):
        return reverse_lazy('student-detail', kwargs={'pk': self.kwargs['student_id']})
    def test_func(self):
        return True 
    
    def get_initial(self):
        initial = super().get_initial()
        student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        initial.update({
            'student': student,
            'income_type': 'Оплата контракта',
            'date': timezone.now().date()
        })
        return initial
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['student_id'] = self.kwargs['student_id']
        return kwargs
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        self.object = form.save()
        # Добавляем сообщение об успехе
        messages.success(
            self.request,
            f"Платеж успешно сохранен. Номер транзакции: {self.object.transaction_id}"
        )
      
        return super().form_valid(form)
    
    def get_success_url(self):
        # После скачивания перенаправляем на страницу ученика
        return reverse('student-detail', kwargs={'pk': self.kwargs['student_id']})
    def send_receipt_email(self, income):
        # Получаем email из контактов родителя (нужно адаптировать под вашу структуру)
        email = self.extract_email_from_contacts(income.student.parent_contacts)
        
        if email:
            try:
                subject = f"Квитанция об оплате #{income.transaction_id}"
                message = f"Уважаемые родители!\n\nПрикрепляем квитанцию об оплате для {income.student.full_name}."
                
                # Генерация HTML квитанции и конвертация в PDF
                # html_receipt = generate_html_receipt(income)
                # pdf_content = generate_pdf_from_html(html_receipt)
                
                email = EmailMessage(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email]
                )
                email.attach(
                    f"receipt_{income.transaction_id}.pdf",
                    # pdf_content,
                    'application/pdf'
                )
                email.send()
            except Exception as e:
                print(f"Ошибка отправки email: {e}")
    
    def extract_email_from_contacts(self, contacts):
        # Простая реализация - нужно адаптировать под ваш формат хранения контактов
        import re
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', contacts)
        return email_match.group(0) if email_match else None
    
    def download_receipt(self, pdf_buffer):
        response = HttpResponse(pdf_buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{self.object.transaction_id}.pdf"'
        return response

from django.shortcuts import get_object_or_404
from num2words import num2words

class ReceiptPrintView(LoginRequiredMixin, DetailView):
    template_name = 'school/receipt_print.html'
    
    def get_object(self):
        student = get_object_or_404(Student, pk=self.kwargs['student_id'])
        payment = get_object_or_404(Income, pk=self.kwargs['payment_id'])
        return {'student': student, 'payment': payment}
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.object['student']
        payment = self.object['payment']
        context['student'] = student
        context['payment'] = payment

        # Сумма прописью
        som_int = int(payment.amount)
        tiyin = int(round((payment.amount - som_int) * 100))
        context['amount_words'] = f"{num2words(som_int, lang='ru').capitalize()} сом {tiyin:02d} тыйын"

        # Текущий учебный год
        current_year = AcademicYear.objects.filter(is_current=True).first()
        
        
        if current_year:
            
            payments = Income.objects.filter(
                student=student,
                academic_year=current_year,
                status='paid'
            ).aggregate(total=Sum('amount'))['total'] or 0
    
            
            
            
            contract_amount = student.contract_amount or 0
            remaining = contract_amount - payments
            context['remaining_payment'] = max(remaining, 0)
        else:
            context['remaining_payment'] = "Не установлен текущий учебный год"
        
        # Оплаченные месяцы
        if payment.paid_months:
            month_names = dict(Income.MONTH_CHOICES)
            paid_months = [month_names[int(m)] for m in payment.paid_months]
            context['paid_months'] = ", ".join(paid_months)
        else:
            context['paid_months'] = None
            
        return context


# class ReceiptPrintView(LoginRequiredMixin, DetailView):
#     template_name = 'school/receipt_print.html'
    
#     def get_object(self):
#         student = get_object_or_404(Student, pk=self.kwargs['student_id'])
#         payment = get_object_or_404(Income, pk=self.kwargs['payment_id'])
#         return {'student': student, 'payment': payment}
    
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         student = self.object['student']
#         payment = self.object['payment']
#         context['student'] = student
#         context['payment'] = payment
        
#         # Получаем текущий учебный год
#         current_year = AcademicYear.objects.filter(is_current=True).first()
        
#         if current_year:
#             # Получаем ВСЕ оплаты за текущий учебный год (включая текущую)
#             payments = Income.objects.filter(
#                 student=student,
#                 academic_year=current_year,
#                 status='paid'
#             ).aggregate(total=Sum('amount'))['total'] or 0
            
#             # Сумма контракта
#             contract_amount = student.contract_amount or 0
            
#             # Остаток к оплате
#             remaining = contract_amount - payments
#             context['remaining_payment'] = max(remaining, 0)  # Не показываем отрицательные значения
#         else:
#             context['remaining_payment'] = "Не установлен текущий учебный год"
        
#         # Форматируем оплаченные месяцы
#         if payment.paid_months:
#             month_names = dict(Income.MONTH_CHOICES)
#             paid_months = [month_names[int(m)] for m in payment.paid_months]
#             context['paid_months'] = ", ".join(paid_months)
#         else:
#             context['paid_months'] = None
            
#         return context


from django.db.models import Sum, Q
from datetime import datetime, timedelta
class ExpenseListView(LoginRequiredMixin, ListView):
    model = Expense
    template_name = 'school/expenses/list.html'
    context_object_name = 'expenses'
    paginate_by = 20
    
    def test_func(self):
        return is_admin(self.request.user) or is_accountant(self.request.user)
    
    def get_queryset(self):
        queryset = super().get_queryset().select_related('created_by')
        
        # Фильтрация по дате
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        
        if date_from:
            queryset = queryset.filter(date__gte=date_from)
        if date_to:
            queryset = queryset.filter(date__lte=date_to)
            
        # Фильтрация по категории
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
            
        # Фильтрация по способу оплаты
        payment_method = self.request.GET.get('payment_method')
        if payment_method:
            queryset = queryset.filter(payment_method=payment_method)
            
        # Фильтрация по поставщику (поиск)
        search = self.request.GET.get('search')
        if search:
            queryset = queryset.filter(
                Q(supplier__icontains=search) |
                Q(notes__icontains=search) |
                Q(invoice_number__icontains=search)
            )
            
        # Сортировка
        sort = self.request.GET.get('sort', '-date')
        queryset = queryset.order_by(sort)
        
        return queryset
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('export') == 'excel':
            return self.export_to_excel()
        return super().render_to_response(context, **response_kwargs)
    def export_to_excel(self):
        queryset = self.get_queryset()
        date_from = self.request.GET.get('date_from', 'не указана')
        date_to = self.request.GET.get('date_to', 'не указана')
    
    # Создаем Excel-файл
        wb = Workbook()
        ws = wb.active
        ws.title = "Отчет по расходам"
    
    # Стили
        header_fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")
        header_font = Font(bold=True)
        center_aligned = Alignment(horizontal='center')
        right_aligned = Alignment(horizontal='right')
        border = Border(
        left=Side(style='thin'),
        right=Side(style='thin'),
        top=Side(style='thin'),
        bottom=Side(style='thin')
        )

    # Заголовок отчета
        ws.append(["Отчет по расходам"])
        ws.merge_cells('A1:G1')
        ws['A1'].font = Font(bold=True, size=14)
        ws['A1'].alignment = center_aligned
    
        ws.append([f"Период: с {date_from} по {date_to}"])
        ws.merge_cells('A2:G2')
        ws['A2'].alignment = center_aligned
    
        ws.append([])  # Пустая строка

    # Заголовки таблицы
        headers = [
        'Дата', 'Категория', 'Поставщик', 
        'Сумма (сом)', 'Способ оплаты', 
        'Номер счета', 'Примечания'
    ]
    
        for col_num, header in enumerate(headers, 1):
            cell = ws.cell(row=4, column=col_num, value=header)
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = center_aligned
            cell.border = border

    # Данные
        for row_num, expense in enumerate(queryset, 5):
            ws.cell(row=row_num, column=1, value=expense.date).border = border
            ws.cell(row=row_num, column=2, value=expense.get_category_display()).border = border
            ws.cell(row=row_num, column=3, value=expense.supplier).border = border
            ws.cell(row=row_num, column=4, value=float(expense.amount)).border = border
            ws.cell(row=row_num, column=5, value=expense.get_payment_method_display()).border = border
            ws.cell(row=row_num, column=6, value=expense.invoice_number or '').border = border
            ws.cell(row=row_num, column=7, value=expense.notes or '').border = border

        # Форматируем числовые ячейки
            ws.cell(row=row_num, column=4).number_format = '#,##0.00'
            ws.cell(row=row_num, column=4).alignment = right_aligned

    # Итоговая строка
        last_row = len(queryset) + 5
        ws.cell(row=last_row, column=3, value="ИТОГО:").font = header_font
        ws.cell(row=last_row, column=4, 
           value=f"=SUM(D5:D{last_row-1})").font = header_font
        ws.cell(row=last_row, column=4).number_format = '#,##0.00'
        ws.cell(row=last_row, column=4).alignment = right_aligned

    # Настраиваем ширину столбцов (только для столбцов с данными, пропуская объединенные ячейки)
        for col in ws.iter_cols(min_row=4, max_row=ws.max_row, min_col=1, max_col=7):
            max_length = 0
            column_letter = get_column_letter(col[0].column)
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column_letter].width = adjusted_width

    # Формируем ответ
        response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename="expense_report.xlsx"'},
    )
        wb.save(response)
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Параметры фильтрации
        context['date_from'] = self.request.GET.get('date_from', '')
        context['date_to'] = self.request.GET.get('date_to', '')
        context['category'] = self.request.GET.get('category', '')
        context['payment_method'] = self.request.GET.get('payment_method', '')
        context['search'] = self.request.GET.get('search', '')
        context['sort'] = self.request.GET.get('sort', '-date')
        
        # Варианты для фильтров
        context['category_choices'] = Expense.CATEGORIES
        context['payment_method_choices'] = Expense.PAYMENT_METHODS
        
        # Статистика
        queryset = self.get_queryset()
        context['total_amount'] = queryset.aggregate(Sum('amount'))['amount__sum'] or 0
        context['expenses_count'] = queryset.count()
        
        # Даты по умолчанию (последние 30 дней)
        today = datetime.datetime.now().date()
        context['default_date_from'] = (today - timedelta(days=30)).strftime('%Y-%m-%d')
        context['default_date_to'] = today.strftime('%Y-%m-%d')
        
        return context
 
    
class ExpenseCreateView(LoginRequiredMixin, CreateView):
    model = Expense
    form_class = ExpenseForm
    template_name = 'school/expenses/form.html'
    success_url = reverse_lazy('expense-list')
    
    def test_func(self):
        return is_admin(self.request.user) or is_accountant(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Добавление расхода'
        context['submit_text'] = 'Добавить расход'
        return context
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(
            self.request,
            f"Расход на сумму {form.instance.amount} сом успешно добавлен!"
        )
        return super().form_valid(form)


# Отчеты
@login_required
@user_passes_test(lambda u: is_admin(u) or is_accountant(u))
def reports(request):
    return render(request, 'school/reports/index.html')

# сотрудники
class EmployeeCreateView(LoginRequiredMixin, CreateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'school/employees/form.html'
    success_url = reverse_lazy('employee-list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Сотрудник успешно добавлен")
        return super().form_valid(form)  # Это вернет HttpResponseRedirect
    
    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))  # Вернет HttpResponse


class EmployeeUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Employee
    form_class = EmployeeForm
    template_name = 'school/employees/form.html'
    success_url = reverse_lazy('employee-list')
    
    def test_func(self):
        return is_admin(self.request.user)
    
    def form_valid(self, form):
        messages.success(self.request, "Данные сотрудника обновлены")
        return super().form_valid(form)

class EmployeeListView(LoginRequiredMixin, ListView):
    model = Employee
    template_name = 'school/employees/list.html'
    context_object_name = 'employees'
    
    def test_func(self):
        return is_admin(self.request.user) or is_accountant(self.request.user)
    
    def get_queryset(self):
        return Employee.objects.filter(is_active=True).select_related('position')
    
    
class SalaryPaymentCreateView(LoginRequiredMixin, CreateView):
    model = SalaryPayment
    form_class = SalaryPaymentForm
    template_name = 'school/employees/salary_payment_form.html'
    
    def test_func(self):
        return is_admin(self.request.user) or is_accountant(self.request.user)
    
    def get_initial(self):
        initial = super().get_initial()
        employee_id = self.request.GET.get('employee')
        if employee_id:
            try:
                employee = Employee.objects.get(pk=employee_id)
                initial['employee'] = employee
                initial['amount'] = employee.monthly_salary
            except Employee.DoesNotExist:
                pass
        return initial
    
    def get_success_url(self):
        employee_id = self.request.GET.get('employee')
        if employee_id:
            return reverse('employee-detail', kwargs={'pk': employee_id})
        return reverse('employee-list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(
            self.request,
            f"Зарплатная выплата для {form.instance.employee} успешно добавлена!"
        )
        return super().form_valid(form)

class SalaryReportView(LoginRequiredMixin, ListView):
    template_name = 'school/employees/salary_report.html'
    context_object_name = 'payments'
    
    def test_func(self):
        return is_admin(self.request.user) or is_accountant(self.request.user)
    
    def get_queryset(self):
        queryset = SalaryPayment.objects.select_related('employee', 'employee__position', 'created_by')
        
        year = self.request.GET.get('year')
        month = self.request.GET.get('month')
        
        if year:
            queryset = queryset.filter(for_month__year=year)
        if month:
            queryset = queryset.filter(for_month__month=month)
            
        return queryset.order_by('-for_month', 'employee__full_name')
    
    def render_to_response(self, context, **response_kwargs):
        if self.request.GET.get('export') == 'xlsx':
            return self.export_to_excel()
        return super().render_to_response(context, **response_kwargs)

    def export_to_excel(self):
        queryset = self.get_queryset()
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=salary_report.xlsx'
    
        wb = Workbook()
        ws = wb.active
        ws.title = "Зарплатные выплаты"
    
    # Заголовки
        headers = ['Сотрудник', 'Должность', 'Месяц', 'Сумма', 'Дата выплаты', 'Способ оплаты', 'Тип']
        for col_num, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_num, value=header).font = Font(bold=True)
    
    # Данные
        for row_num, payment in enumerate(queryset, 2):
            ws.cell(row=row_num, column=1, value=payment.employee.full_name)
            ws.cell(row=row_num, column=2, value=str(payment.employee.position))
            ws.cell(row=row_num, column=3, value=payment.for_month.strftime('%B %Y'))
            ws.cell(row=row_num, column=4, value=float(payment.amount))
            ws.cell(row=row_num, column=5, value=payment.payment_date.strftime('%d.%m.%Y'))
            ws.cell(row=row_num, column=6, value=payment.get_payment_method_display())
            ws.cell(row=row_num, column=7, value='Премия' if payment.is_bonus else 'Зарплата')
    
    # Автоширина столбцов
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2) * 1.2
            ws.column_dimensions[column].width = adjusted_width
    
        wb.save(response)
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Добавляем доступные годы для фильтра
        years = SalaryPayment.objects.dates('for_month', 'year').order_by('-for_month')
        unique_years = sorted(set([year.year for year in years]), reverse=True)
        context['years'] = unique_years
        context['selected_year'] = self.request.GET.get('year')

        
        # Добавляем месяцы для фильтра
        context['months'] = [
            (1, 'Январь'), (2, 'Февраль'), (3, 'Март'), 
            (4, 'Апрель'), (5, 'Май'), (6, 'Июнь'),
            (7, 'Июль'), (8, 'Август'), (9, 'Сентябрь'),
            (10, 'Октябрь'), (11, 'Ноябрь'), (12, 'Декабрь')
        ]
        context['selected_month'] = self.request.GET.get('month')
        
        # Суммарная информация
        queryset = self.get_queryset()
        context['total_amount'] = queryset.aggregate(
            Sum('amount')
        )['amount__sum'] or 0
        
        return context      
    
    
class EmployeeDetailView(LoginRequiredMixin, DetailView):
    model = Employee
    template_name = 'school/employees/detail.html'
    
    def test_func(self):
        return is_admin(self.request.user) or is_accountant(self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['salary_payments'] = SalaryPayment.objects.filter(
            employee=self.object
        ).order_by('-for_month')
        return context


from django.views.generic import ListView
from .models import Document

class DocumentListView(ListView):
    model = Document
    template_name = 'documents.html'
    context_object_name = 'documents'
    
    def get_queryset(self):
        # Группируем документы по категориям
        documents = super().get_queryset()
        categories = {}
        for doc in documents:
            if doc.category not in categories:
                categories[doc.category] = []
            categories[doc.category].append(doc)
        return categories
    
from django.views.generic import ListView, DetailView
from .models import GalleryEvent
from django.views.generic import ListView
from .models import GalleryEvent
from django.db.models import Count
from django.views.generic import ListView
from .models import GalleryEvent
from django.db.models import Count

class GalleryListView(ListView):
    model = GalleryEvent
    template_name = 'gallery.html'
    context_object_name = 'events'
    paginate_by = 12
    
    def get_queryset(self):
        # Получаем базовый queryset
        queryset = GalleryEvent.objects.annotate(
            image_count=Count('images')
        ).filter(image_count__gt=0)
        
        # Фильтрация по году
        year = self.request.GET.get('year')
        if year and year != 'all':
            queryset = queryset.filter(date__year=year)
        
        return queryset.order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем уникальные года из событий
        years = GalleryEvent.objects.annotate(
            image_count=Count('images')
        ).filter(image_count__gt=0).values_list('date__year', flat=True).distinct().order_by('-date__year')
        
        # Добавляем в контекст
        context['years'] = years
        context['current_year'] = self.request.GET.get('year', 'all')
        
        return context
class GalleryListView(ListView):
    model = GalleryEvent
    template_name = 'gallery.html'
    context_object_name = 'events'
    paginate_by = 12
    
    def get_queryset(self):
        # Убираем аннотацию image_count
        queryset = GalleryEvent.objects.filter(images__isnull=False).distinct()
        
        # Фильтрация по году
        year = self.request.GET.get('year')
        if year and year != 'all':
            queryset = queryset.filter(date__year=year)
        
        return queryset.order_by('-date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Получаем уникальные года из событий
        years = GalleryEvent.objects.values_list('date__year', flat=True).distinct().order_by('-date__year')
        
        # Добавляем в контекст
        context['years'] = years
        context['current_year'] = self.request.GET.get('year', 'all')
        
        return context
    
    

def teacher_view1(request):
    model = Teacher.objects.all()
    return render(request,'teacher.html',{'teachers':model})
class GalleryDetailView(DetailView):
    model = GalleryEvent
    template_name = 'gallery_detail.html'
    context_object_name = 'event'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'
    
from django.views.generic import DetailView
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
import os
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
# import datetime
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from io import BytesIO
import datetime
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont




from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from .pdf_utils import register_fonts
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm

from num2words import num2words

def expense_receipt_pdf(request, pk):
    expense = get_object_or_404(Expense, pk=pk)

    register_fonts()

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="receipt_{expense.id}.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4)

    elements = []
    styles = getSampleStyleSheet()

    style_heading = ParagraphStyle(
        'Heading1',
        parent=styles['Heading1'],
        fontName='Arial',
        fontSize=10,
        alignment=1,
        spaceAfter=6
    )

    style_normal = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontName='Arial',
        fontSize=10,
        leading=12
    )

    elements.append(Paragraph("РАСХОДНЫЙ КАССОВЫЙ ОРДЕР", style_heading))
    elements.append(Paragraph(f"№ {expense.id or 'БН'} от {expense.created_at.strftime('%d.%m.%Y')}", style_normal))
    elements.append(Spacer(1, 0.1*cm))

    # --- сумма с разделением по 3 символа
    formatted_amount = "{:,.2f}".format(expense.amount).replace(",", " ")

    # --- сумма прописью
    som_int = int(expense.amount)
    tiyin = int(round((expense.amount - som_int) * 100))

    amount_words = f"{num2words(som_int, lang='ru').capitalize()} сом {tiyin:02d} тыйын"

    data = [
        ["Дата расхода:", expense.date.strftime("%d.%m.%Y") if expense.date else ""],
        ["Номер документа:", str(expense.id)],
        ["Категория расхода:", expense.get_category_display()],
        ["Поставщик:", expense.supplier],
        ["Сумма расхода:", f"{formatted_amount} сом"],
        ["Сумма прописью:", amount_words],
        ["Способ оплаты:", expense.get_payment_method_display()],
        ["Основание:", expense.notes or "Оплата услуг"],
        ["Оформил:", request.user if request.user else "Не указан"],
    ]

    table = Table(data, colWidths=[4*cm, 8*cm])
    table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
        ('ALIGN', (1, 0), (1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    two_columns = Table([[table, ""]], colWidths=[12*cm, 8*cm])
    elements.append(two_columns)
    elements.append(Spacer(1, 0.4*cm))

    signatures = Table([
        [Paragraph("Директор:<br/>___________________<br/>Муртазо У.Б.", style_normal)]
    ], colWidths=[6*cm, 6*cm])

    elements.append(signatures)

    doc.build(elements)

    return response

# def expense_receipt_pdf(request, pk):
#     expense = get_object_or_404(Expense, pk=pk)
    
#     # Регистрируем шрифты
#     register_fonts()
    
#     # Создаем HttpResponse с заголовками PDF
#     response = HttpResponse(content_type='application/pdf')
#     response['Content-Disposition'] = f'inline; filename="receipt_{expense.id}.pdf"'
    
#     # Используем альбомную ориентацию
#     doc = SimpleDocTemplate(response, pagesize=A4)
    
#     # Контейнер для элементов PDF
#     elements = []
    
#     # Стили текста
#     styles = getSampleStyleSheet()
    
#     # Создаем кастомные стили
#     style_heading = ParagraphStyle(
#         'Heading1',
#         parent=styles['Heading1'],
#         fontName='Arial',
#         fontSize=10,
#         alignment=1,  # 0=left, 1=center, 2=right
#         spaceAfter=6
#     )
    
#     style_normal = ParagraphStyle(
#         'Normal',
#         parent=styles['Normal'],
#         fontName='Arial',
#         fontSize=10,
#         leading=12
#     )
    
#     # Добавляем заголовок
#     elements.append(Paragraph("РАСХОДНЫЙ КАССОВЫЙ ОРДЕР", style_heading))
#     elements.append(Paragraph(f"№ {expense.id or 'БН'} от {expense.created_at.strftime('%d.%m.%Y')}", style_normal))
#     elements.append(Spacer(1, 0.1*cm))
    
#     # Подготавливаем данные для таблицы (две колонки)
#     data = [
#         ["Дата расхода:", expense.date.strftime("%d.%m.%Y") if expense.date else ""],
#         ["Номер документа:", str(expense.id)],
#         ["Категория расхода:", expense.get_category_display()],
#         ["Поставщик:", expense.supplier],
#         ["Сумма расхода:", f"{expense.amount:.2f} сом"],
#         ["Способ оплаты:", expense.get_payment_method_display()],
#         ["Основание:", expense.notes or "Оплата услуг"],
#         ["Оформил:", request.user if request.user else "Не указан"],
#     ]
    
#     # Создаем таблицу (располагаем слева)
#     table = Table(data, colWidths=[4*cm, 8*cm])
#     table.setStyle(TableStyle([
#         ('FONTNAME', (0, 0), (-1, -1), 'Arial'),
#         ('FONTSIZE', (0, 0), (-1, -1), 10),
#         ('VALIGN', (0, 0), (-1, -1), 'TOP'),
#         ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
#         ('ALIGN', (1, 0), (1, -1), 'LEFT'),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
#         ('GRID', (0, 0), (-1, -1), 1, colors.black),
#     ]))
    
#     # Создаем основной контейнер с двумя колонками
#     two_columns = Table([
#         [table, ""]  # Левая колонка - таблица, правая - пустая
#     ], colWidths=[12*cm, 8*cm])
    
#     elements.append(two_columns)
#     elements.append(Spacer(1, 0.4*cm))
    
#     # Добавляем подписи (теперь в одну строку)
#     signatures = Table([
#         [
#             # Paragraph("Главный бухгалтер:<br/>___________________", style_normal),
#             Paragraph("Директор:<br/>___________________<br/>Муртазо У.Б.", style_normal)
#         ]
#     ], colWidths=[6*cm, 6*cm])
    
#     elements.append(signatures)
    
#     # Собираем PDF
#     doc.build(elements)
    
#     return response


from .models import Graduate

from django.shortcuts import render
from .models import Graduate
from django.views.generic import ListView
from .models import Application
def graduates_list(request):
    graduates = Graduate.objects.all().order_by('-graduation_year', '-order', 'username')
    unique_years = Graduate.objects.values_list('graduation_year', flat=True).distinct().order_by('-graduation_year')
    
    # Фильтрация по году, если указан параметр
    year_filter = request.GET.get('year')
    if year_filter:
        graduates = graduates.filter(graduation_year=year_filter)
    
    return render(request, 'school/graduates/graduates_list.html', {
        'graduates': graduates,
        'unique_years': unique_years,
        'selected_year': year_filter,
    })
    


class ApplicationListView(ListView):
    model = Application
    template_name = 'school/application/application_list.html'
    context_object_name = 'applications'
    paginate_by = 10  # Пагинация по 10 элементов
    
    def get_queryset(self):
        # Сортировка по дате создания (новые сначала)
        return Application.objects.all().order_by('-created_at')