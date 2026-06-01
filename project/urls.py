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
from core.views import ApplicationListView, CustomLoginView, DocumentListView, GalleryDetailView, GalleryListView, application_view, best_student, login_view, logout_view, ClassDebtsReportView, DiscountCreateView, DiscountDeleteView, DownloadReceiptView, IncomeCreateView, ReceiptPrintView, StudentListView, StudentDetailView, StudentCreateView, StudentUpdateView, student_search, teacher_view1
from core.views import (
    EmployeeListView, EmployeeCreateView,
    EmployeeUpdateView, EmployeeDetailView,
    SalaryPaymentCreateView, SalaryReportView,
    # CMS
    cms_dashboard,
    CMSNewsListView, CMSNewsCreateView, CMSNewsUpdateView, CMSNewsDeleteView,
    CMSTeacherListView, CMSTeacherCreateView, CMSTeacherUpdateView, CMSTeacherDeleteView,
    CMSBestStudentListView, CMSBestStudentCreateView, CMSBestStudentUpdateView, CMSBestStudentDeleteView,
    CMSGraduateListView, CMSGraduateCreateView, CMSGraduateUpdateView, CMSGraduateDeleteView,
    CMSGalleryListView, CMSGalleryCreateView, CMSGalleryUpdateView, CMSGalleryDeleteView,
)
from core.receipts import download_receipt_view
urlpatterns = [
    path('s/', views.home, name='home'),
     path('accounts/', include('django.contrib.auth.urls')),
    # Студенты
    path('logout/', logout_view, name='logout'),
    path('students/<int:student_id>/payments/<int:payment_id>/receipt/', 
     ReceiptPrintView.as_view(), 
     name='print-receipt'),
    path('expenses/<int:pk>/receipt/', views.expense_receipt_pdf, name='expense_receipt_pdf'),
    # path('expenses/<int:pk>/receipt/', views.ExpenseReceiptView.as_view(), name='expense_receipt'),
    path('documents/', DocumentListView.as_view(), name='documents'),
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
    path('applications/', ApplicationListView.as_view(), name='application_list'),
    path('graduates/', views.graduates_list, name='graduates_list'),
    path('gallery/', GalleryListView.as_view(), name='gallery'),
    path('gallery/<slug:slug>/', GalleryDetailView.as_view(), name='gallery_detail'),
    
    path('incomes/export/', views.IncomeListView.as_view(), name='income-export'),
    
    path('incomes/', views.IncomeListView.as_view(), name='income-list'),
    path('incomes/add/', views.IncomeCreateView.as_view(), name='income-create'),
    path('students/<int:student_id>/add-income/', IncomeCreateView.as_view(), name='student-add-income'),
    # Расходы /students/2/payments/20/receipt/
    path('expenses/', views.ExpenseListView.as_view(), name='expense-list'),
    path('expenses/add/', views.ExpenseCreateView.as_view(), name='expense-create'),
    path('students/search/', student_search, name='student-search'),
    path('students/<int:pk>/discounts/add/', DiscountCreateView.as_view(), name='student-add-discount'),
    path('discounts/<int:pk>/delete/', DiscountDeleteView.as_view(), name='discount-delete'),
    # Отчеты
    path('expenses/<int:pk>/edit/', views.ExpenseCreateView.as_view(), name='expense-update'),
    path('reports/', views.reports, name='reports'),

    path('admin/', admin.site.urls),
    path('best_student/', best_student, name='best_student'),
    path('teachers/',teacher_view1, name='teacher_view1'),
    path('news/', views.NewsListView.as_view(), name='news_list'),
    path('news/<int:pk>/', views.NewsDetailView.as_view(), name='news_detail'),
    path('', application_view, name='thanks'),
    path('get_teacher/<int:teacher_id>/', views.get_teacher, name='get_teacher'),
    path('employees/', EmployeeListView.as_view(), name='employee-list'),
    path('employees/add/', EmployeeCreateView.as_view(), name='employee-add'),
    path('employees/<int:pk>/', EmployeeDetailView.as_view(), name='employee-detail'),
    path('employees/<int:pk>/edit/', EmployeeUpdateView.as_view(), name='employee-edit'),
    path('salary-payments/add/', SalaryPaymentCreateView.as_view(), name='salary-payment-add'),
    path('salary-report/', SalaryReportView.as_view(), name='salary-report'),

    # ── CMS ──────────────────────────────────────────────────────
    path('cms/login/', views.cms_login, name='cms-login'),
    path('cms/logout/', views.cms_logout, name='cms-logout'),
    path('cms/', cms_dashboard, name='cms-dashboard'),

    # Новости
    path('cms/news/', CMSNewsListView.as_view(), name='cms-news-list'),
    path('cms/news/add/', CMSNewsCreateView.as_view(), name='cms-news-create'),
    path('cms/news/<int:pk>/edit/', CMSNewsUpdateView.as_view(), name='cms-news-edit'),
    path('cms/news/<int:pk>/delete/', CMSNewsDeleteView.as_view(), name='cms-news-delete'),

    # Учителя
    path('cms/teachers/', CMSTeacherListView.as_view(), name='cms-teacher-list'),
    path('cms/teachers/add/', CMSTeacherCreateView.as_view(), name='cms-teacher-create'),
    path('cms/teachers/<int:pk>/edit/', CMSTeacherUpdateView.as_view(), name='cms-teacher-edit'),
    path('cms/teachers/<int:pk>/delete/', CMSTeacherDeleteView.as_view(), name='cms-teacher-delete'),

    # Лучшие ученики
    path('cms/best-students/', CMSBestStudentListView.as_view(), name='cms-best-student-list'),
    path('cms/best-students/add/', CMSBestStudentCreateView.as_view(), name='cms-best-student-create'),
    path('cms/best-students/<int:pk>/edit/', CMSBestStudentUpdateView.as_view(), name='cms-best-student-edit'),
    path('cms/best-students/<int:pk>/delete/', CMSBestStudentDeleteView.as_view(), name='cms-best-student-delete'),

    # Выпускники
    path('cms/graduates/', CMSGraduateListView.as_view(), name='cms-graduate-list'),
    path('cms/graduates/add/', CMSGraduateCreateView.as_view(), name='cms-graduate-create'),
    path('cms/graduates/<int:pk>/edit/', CMSGraduateUpdateView.as_view(), name='cms-graduate-edit'),
    path('cms/graduates/<int:pk>/delete/', CMSGraduateDeleteView.as_view(), name='cms-graduate-delete'),

    # Галерея
    path('cms/gallery/', CMSGalleryListView.as_view(), name='cms-gallery-list'),
    path('cms/gallery/add/', CMSGalleryCreateView.as_view(), name='cms-gallery-create'),
    path('cms/gallery/<int:pk>/edit/', CMSGalleryUpdateView.as_view(), name='cms-gallery-edit'),
    path('cms/gallery/<int:pk>/delete/', CMSGalleryDeleteView.as_view(), name='cms-gallery-delete'),
]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
