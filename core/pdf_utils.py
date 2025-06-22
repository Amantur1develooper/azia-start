from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
import os
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def register_font():
    """Пытаемся зарегистрировать стандартные шрифты, поддерживающие кириллицу"""
    try:
        # Попробуем использовать встроенный шрифт DejaVu Sans (если установлен)
        from reportlab.rl_config import TTFSearchPath
        for path in TTFSearchPath:
            dejavu_path = os.path.join(path, 'DejaVuSans.ttf')
            if os.path.exists(dejavu_path):
                pdfmetrics.registerFont(TTFont('DejaVuSans', dejavu_path))
                return 'DejaVuSans'
        
        # Если DejaVu не найден, используем стандартный шрифт Helvetica
        return 'Helvetica'
    except:
        return 'Helvetica'

def generate_receipt(income):
    buffer = BytesIO()
    width, height = A5
    p = canvas.Canvas(buffer, pagesize=A5)
    
    # Получаем доступный шрифт
    font_name = register_font()
    
    # Проверяем поддержку кириллицы
    test_text = "Тест"
    p.setFont(font_name, 10)
    try:
        p.drawString(10*mm, height-10*mm, test_text)
    except:
        # Если шрифт не поддерживает кириллицу, используем только латиницу
        font_name = 'Helvetica'
        test_text = "Receipt"
    
    # Шапка квитанции
    p.setFont(font_name, 14)
    p.drawString(20*mm, height-20*mm, "КВИТАНЦИЯ ОБ ОПЛАТЕ")
    
    # Основная информация (проверяем каждый текст на поддержку кириллицы)
    p.setFont(font_name, 10)
    y_pos = height-40*mm
    
    try:
        p.drawString(20*mm, y_pos, f"Ученик: {income.student.full_name}")
    except:
        p.drawString(20*mm, y_pos, f"Student: {income.student.full_name}")
    
    y_pos -= 8*mm
    p.drawString(20*mm, y_pos, f"Класс: {income.student.grade.number}{income.student.grade.parallel}")
    
    y_pos -= 8*mm
    p.drawString(20*mm, y_pos, f"Сумма: {income.amount:,.2f} KGS".replace(",", " "))
    
    y_pos -= 8*mm
    try:
        p.drawString(20*mm, y_pos, f"Способ оплаты: {income.get_payment_method_display()}")
    except:
        p.drawString(20*mm, y_pos, f"Payment method: {income.get_payment_method_display()}")
    
    # Сохраняем PDF
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
# def register_fonts():
#     try:
#         # Попробуем использовать стандартные системные шрифты
#         font_paths = [
#             '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',  # Linux
#             'C:/Windows/Fonts/arial.ttf',  # Windows
#             '/Library/Fonts/Arial.ttf'  # MacOS
#         ]
        
#         for path in font_paths:
#             if os.path.exists(path):
#                 pdfmetrics.registerFont(TTFont('Arial', path))
#                 return True
        
#         # Если системные шрифты не найдены, используем встроенный DejaVu Sans
#         from django.conf import settings
#         font_path = os.path.join(settings.BASE_DIR, 'static/fonts/DejaVuSans.ttf')
#         if os.path.exists(font_path):
#             pdfmetrics.registerFont(TTFont('DejaVuSans', font_path))
#             return True
        
#     except:
#         pass
    
#     # Если ничего не сработало, используем стандартный шрифт (может не поддерживать кириллицу)
#     return False

# def generate_receipt(income):
#     buffer = BytesIO()
#     width, height = A5
#     p = canvas.Canvas(buffer, pagesize=A5)
    
#     # Регистрируем шрифты
#     font_registered = register_fonts()
#     font_name = 'Arial' if font_registered else 'Helvetica'
    
#     # Верхняя часть (для клиента)
#     p.setFont(font_name, 14)
#     p.drawString(20*mm, height-20*mm, "КВИТАНЦИЯ ОБ ОПЛАТЕ")
#     p.setFont(font_name, 10)
#     p.drawString(20*mm, height-27*mm, f"№ {income.transaction_id} от {income.date.strftime('%d.%m.%Y')}")
    
#     # Линия перфорации
#     p.setDash(3, 3)
#     p.line(15*mm, height-35*mm, width-15*mm, height-35*mm)
#     p.setDash()
    
#     # Основная информация
#     y_pos = height-45*mm
#     p.setFont(font_name, 10)
#     p.drawString(20*mm, y_pos, "Учебное заведение: Школа 'Азия Старт'")
#     p.drawString(20*mm, y_pos-8*mm, f"Ученик: {income.student.full_name}")
#     p.drawString(20*mm, y_pos-16*mm, f"Класс: {income.student.grade.number}{income.student.grade.parallel}")
#     p.drawString(20*mm, y_pos-24*mm, f"Сумма: {income.amount:,.2f} тенге".replace(",", " "))
#     p.drawString(20*mm, y_pos-32*mm, f"Способ оплаты: {income.get_payment_method_display()}")
#     p.drawString(20*mm, y_pos-40*mm, f"Статья дохода: {income.income_type}")
    
#     # Подпись клиента
#     p.drawString(20*mm, y_pos-52*mm, "Клиент получил квитанцию:")
#     p.drawString(20*mm, y_pos-60*mm, "_________________________")
#     p.drawString(20*mm, y_pos-65*mm, "(подпись)")
    
#     # Линия отреза
#     p.setLineWidth(1.5)
#     p.line(10*mm, height-85*mm, width-10*mm, height-85*mm)
#     p.setLineWidth(1)
    
#     # Нижняя часть (корешок)
#     p.setFont(font_name, 12)
#     p.drawString(20*mm, height-95*mm, "КОРЕШОК КВИТАНЦИИ")
    
#     p.setFont(font_name, 10)
#     y_pos = height-105*mm
#     p.drawString(20*mm, y_pos, f"Ученик: {income.student.full_name}")
#     p.drawString(20*mm, y_pos-8*mm, f"Класс: {income.student.grade.number}{income.student.grade.parallel}")
#     p.drawString(20*mm, y_pos-16*mm, f"Сумма: {income.amount:,.2f} тенге".replace(",", " "))
#     p.drawString(20*mm, y_pos-24*mm, f"Дата: {income.date.strftime('%d.%m.%Y')}")
#     p.drawString(20*mm, y_pos-32*mm, f"Номер: {income.transaction_id}")
    
#     # Подпись кассира
#     p.drawString(20*mm, y_pos-44*mm, "Кассир: _________________________")
#     p.drawString(20*mm, y_pos-49*mm, "М.П.")
    
#     p.showPage()
#     p.save()
#     buffer.seek(0)
#     return buffer