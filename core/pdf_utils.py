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





from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.conf import settings
import os

def register_fonts():
    # Путь к шрифту в вашей системе (пример для Windows)
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'arial.ttf')
    
    if os.path.exists(font_path):
        pdfmetrics.registerFont(TTFont('Arial', font_path))
    else:
        # Попробуем найти стандартный шрифт
        try:
            pdfmetrics.registerFont(TTFont('Arial', 'arial.ttf'))
        except:
            # Используем встроенный шрифт (может не поддерживать кириллицу)
            pass