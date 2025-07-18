"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static
from django.urls import path
from core import views
from django.urls import path
from django.views.generic import TemplateView
from core.views import CustomLoginView, application_view, login_view, logout_view, ClassDebtsReportView, DownloadReceiptView, IncomeCreateView, ReceiptPrintView, StudentListView, StudentDetailView, StudentCreateView, StudentUpdateView, student_search
from core.views import (
    EmployeeListView, EmployeeCreateView, 
    EmployeeUpdateView, EmployeeDetailView,
    SalaryPaymentCreateView, SalaryReportView
)
from core.receipts import download_receipt_view
urlpatterns = [
    path('', views.home, name='home'),
     path('accounts/', include('django.contrib.auth.urls')),
    # Студенты
    path('logout/', logout_view, name='logout'),
    path('students/<int:student_id>/payments/<int:payment_id>/receipt/', 
     ReceiptPrintView.as_view(), 
     name='print-receipt'),
    path('accounts/login/', login_view, name='login'),
    path('reports/class-debts/', ClassDebtsReportView.as_view(), name='class-debts-report'),
    path('students/', StudentListView.as_view(), name='student-list'),
    path('students/<int:pk>/', StudentDetailView.as_view(), name='student-detail'),
    path('students/add/', StudentCreateView.as_view(), name='student-create'),
    path('students/<int:pk>/edit/', StudentUpdateView.as_view(), name='student-update'),
    # ... остальные URL
    path('incomes/<int:pk>/download/', DownloadReceiptView.as_view(), name='download-receipt'),
    path('incomes/<int:pk>/receipt/', download_receipt_view, name='download-receipt'),
    # Доходы
    
    path('incomes/export/', views.IncomeListView.as_view(), name='income-export'),
    
    path('incomes/', views.IncomeListView.as_view(), name='income-list'),
    path('incomes/add/', views.IncomeCreateView.as_view(), name='income-create'),
    path('students/<int:student_id>/add-income/', IncomeCreateView.as_view(), name='student-add-income'),
    # Расходы
    path('expenses/', views.ExpenseListView.as_view(), name='expense-list'),
    path('expenses/add/', views.ExpenseCreateView.as_view(), name='expense-create'),
    path('students/search/', student_search, name='student-search'),
    # Отчеты
    path('expenses/<int:pk>/edit/', views.ExpenseCreateView.as_view(), name='expense-update'),
    path('reports/', views.reports, name='reports'),

    path('admin/', admin.site.urls),
    
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('thanks/', application_view, name='thanks'),
    path('get_teacher/<int:teacher_id>/', views.get_teacher, name='get_teacher'),
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employees/add/', EmployeeCreateView.as_view(), name='employee-add'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/edit/', EmployeeUpdateView.as_view(), name='employee-edit'),
    path('salary-payments/add/', SalaryPaymentCreateView.as_view(), name='salary-payment-add'),
    path('salary-report/', SalaryReportView.as_view(), name='salary-report'),
]

#  {% load  path('students/', views.StudentListView.as_view(), name='student-list'),
#     path('students/<int:pk>/', views.StudentDetailView.as_view(), name='student-detail'),
#     path('students/add/', views.StudentCreateView.as_view(), name='student-create'),
#     path('students/<int:pk>/edit/', views.StudentUpdateView.as_view(), name='student-update'),
#     _tags %}
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
