from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib import colors
from io import BytesIO
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse

def generate_receipt_pdf(income):
    # Рендерим HTML шаблон
    html = render_to_string('receipt_template.html', {'income': income})
    
    # Конвертируем HTML в PDF
    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), result)
    
    if not pdf.err:
        return result.getvalue()
    return None

def download_receipt_view(request, pk):
    from .models import Income
    income = Income.objects.get(pk=pk)
    pdf_content = generate_receipt_pdf(income)
    
    if pdf_content:
        response = HttpResponse(pdf_content, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="receipt_{income.transaction_id}.pdf"'
        return response
    return HttpResponse("Ошибка генерации квитанции", status=500)
# def generate_receipt_pdf(income):
#     buffer = BytesIO()
#     p = canvas.Canvas(buffer, pagesize=A4)
#     width, height = A4
    
#     # Заголовок
#     p.setFont("Helvetica-Bold", 16)
#     p.drawString(30*mm, height-30*mm, "КВИТАНЦИЯ ОБ ОПЛАТЕ")
    
#     # Школа
#     p.setFont("Helvetica", 12)
#     p.drawString(30*mm, height-40*mm, "Школа 'Азия Старт'")
    
#     # Номер и дата
#     p.setFont("Helvetica", 10)
#     p.drawString(30*mm, height-55*mm, f"Номер: {income.transaction_id}")
#     p.drawString(30*mm, height-60*mm, f"Дата: {income.date.strftime('%d.%m.%Y')}")
    
#     # Линия разделения
#     p.line(30*mm, height-65*mm, width-30*mm, height-65*mm)
    
#     # Информация об ученике
#     p.setFont("Helvetica-Bold", 12)
#     p.drawString(30*mm, height-80*mm, "Ученик:")
#     p.setFont("Helvetica", 12)
#     p.drawString(80*mm, height-80*mm, income.student.full_name)
    
#     p.drawString(30*mm, height-90*mm, "Класс:")
#     p.drawString(80*mm, height-90*mm, f"{income.student.grade.number}{income.student.grade.parallel}")
    
#     # Детали платежа
#     p.setFont("Helvetica-Bold", 12)
#     p.drawString(30*mm, height-110*mm, "Детали платежа:")
#     p.setFont("Helvetica", 12)
    
#     p.drawString(30*mm, height-125*mm, "Сумма:")
#     p.drawString(80*mm, height-125*mm, f"{income.amount:.2f} тенге")
    
#     p.drawString(30*mm, height-135*mm, "Способ оплаты:")
#     p.drawString(80*mm, height-135*mm, income.get_payment_method_display())
    
#     p.drawString(30*mm, height-145*mm, "Статус:")
#     p.drawString(80*mm, height-145*mm, income.get_status_display())
    
#     # Подпись
#     p.setFont("Helvetica", 10)
#     p.drawString(30*mm, 40*mm, "Кассир: _________________________")
#     p.drawString(30*mm, 30*mm, "М.П.")
    
#     # Сохраняем PDF
#     p.showPage()
#     p.save()
#     buffer.seek(0)
#     return buffer
# from io import BytesIO
# from django.http import HttpResponse
# from reportlab.pdfgen import canvas
# from reportlab.lib.pagesizes import A4
# from reportlab.lib.units import mm
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.platypus import Paragraph, Table, TableStyle
# from reportlab.lib import colors
# from django.template.loader import render_to_string
# from xhtml2pdf import pisa

# def generate_receipt_pdf(income):
#     buffer = BytesIO()
    
#     # Создаем PDF документ
#     p = canvas.Canvas(buffer, pagesize=A4)
#     width, height = A4
    
#     # Логотип (можно добавить позже)
#     # p.drawImage("logo.png", 30*mm, height-30*mm, width=50*mm, height=20*mm)
    
#     # Заголовок
#     p.setFont("Helvetica-Bold", 14)
#     p.drawString(30*mm, height-40*mm, "КВИТАНЦИЯ ОБ ОПЛАТЕ")
    
#     # Номер квитанции
#     p.setFont("Helvetica", 10)
#     p.drawString(30*mm, height-50*mm, f"Номер: {income.transaction_id}")
#     p.drawString(30*mm, height-55*mm, f"Дата: {income.date.strftime('%d.%m.%Y')}")
    
#     # Информация о платеже
#     data = [
#         ["Ученик:", income.student.full_name],
#         ["Класс:", f"{income.student.grade.number}{income.student.grade.parallel}"],
#         ["Статья дохода:", income.income_type],
#         ["Сумма оплаты:", f"{income.amount:.2f} тенге"],
#         ["Способ оплаты:", income.get_payment_method_display()],
#         ["Статус:", income.get_status_display()],
#     ]
    
#     # Создаем таблицу с данными
#     table = Table(data, colWidths=[40*mm, 120*mm])
#     table.setStyle(TableStyle([
#         ('FONT', (0,0), (-1,-1), 'Helvetica'),
#         ('FONTSIZE', (0,0), (-1,-1), 10),
#         ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
#         ('LINEBELOW', (0,0), (-1,-1), 0.25, colors.black),
#         ('BOX', (0,0), (-1,-1), 0.25, colors.black),
#     ]))
    
#     # Размещаем таблицу на странице
#     table.wrapOn(p, width, height)
#     table.drawOn(p, 30*mm, height-120*mm)
    
#     # Подпись
#     p.setFont("Helvetica", 10)
#     p.drawString(30*mm, 50*mm, "Кассир: _________________________")
#     p.drawString(30*mm, 45*mm, "М.П.")
    
#     # Сохраняем PDF
#     p.showPage()
#     p.save()
    
#     buffer.seek(0)
#     return buffer

# def generate_html_receipt(income):
#     context = {
#         'income': income,
#         'student': income.student
#     }
#     return render_to_string('school/receipts/receipt.html', context)

# def generate_pdf_from_html(html):
#     result = BytesIO()

#     pdf = pisa.CreatePDF(BytesIO(html.encode("UTF-8")), result)
#     if not pdf.err:
#         return result.getvalue()
#     return None