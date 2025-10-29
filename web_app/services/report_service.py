"""
Report service - generate PDF reports with recommendations
"""
import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from web_app.models import Upload, Product, CompetitorPrice, Statistic
from web_app.database import db

def generate_pdf_report(upload_id):
    """
    Generate PDF report with recommendations (similar to local version)
    
    Args:
        upload_id: Upload ID
    
    Returns:
        BytesIO: PDF file as BytesIO object
    """
    upload = Upload.query.get(upload_id)
    if not upload:
        raise Exception(f"Upload not found: {upload_id}")
    
    products = Product.query.filter_by(upload_id=upload_id).all()
    statistics = Statistic.query.filter_by(upload_id=upload_id).first()
    
    # Create PDF in memory
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch)
    
    # Container for the 'Flowable' objects
    elements = []
    styles = getSampleStyleSheet()
    
    # Title
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=30,
        alignment=1  # Center
    )
    elements.append(Paragraph("Отчет по ценам конкурентов", title_style))
    elements.append(Paragraph(f"Дата: {upload.upload_date.strftime('%d.%m.%Y')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))
    
    # Summary statistics
    if statistics:
        summary_data = [
            ['Метрика', 'Значение'],
            ['Всего продуктов', f"{statistics.total_products or 0}"],
            ['Общая стоимость', f"{float(statistics.total_value):,.0f} GEL" if statistics.total_value else "0 GEL"],
            ['Средняя цена', f"{float(statistics.avg_our_price):,.2f} GEL" if statistics.avg_our_price else "0 GEL"],
            ['Мы дешевле', f"{statistics.products_cheaper or 0}"],
            ['Мы дороже', f"{statistics.products_expensive or 0}"],
            ['Без конкурентов', f"{statistics.products_no_competitors or 0}"],
        ]
        
        summary_table = Table(summary_data, colWidths=[4*inch, 2*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 0.3*inch))
    
    # Analyze and get recommendations
    analysis = _analyze_competitiveness(products)
    recommendations = _generate_recommendations(analysis, statistics)
    
    # Recommendations section
    elements.append(PageBreak())
    elements.append(Paragraph("Рекомендации", styles['Heading1']))
    elements.append(Spacer(1, 0.2*inch))
    
    for i, rec in enumerate(recommendations, 1):
        elements.append(Paragraph(f"{i}. {rec}", styles['Normal']))
        elements.append(Spacer(1, 0.1*inch))
    
    # Top opportunities
    if analysis['opportunities']:
        elements.append(Spacer(1, 0.2*inch))
        elements.append(Paragraph("Возможности увеличения прибыли", styles['Heading2']))
        
        opp_data = [['Модель', 'Текущая цена', 'Рекомендуемая', 'Доп. прибыль']]
        for opp in sorted(analysis['opportunities'], key=lambda x: x.get('additional_profit', 0), reverse=True)[:10]:
            opp_data.append([
                opp['model'],
                f"{opp['current_website_price']:,.2f}",
                f"{opp['suggested_price']:,.2f}",
                f"{opp['additional_profit']:,.2f} GEL"
            ])
        
        opp_table = Table(opp_data, colWidths=[1.5*inch, 1.2*inch, 1.2*inch, 1.2*inch])
        opp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#27ae60')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(opp_table)
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def _analyze_competitiveness(products):
    """Analyze price competitiveness"""
    results = {
        'cheaper': [],
        'more_expensive': [],
        'opportunities': []
    }
    
    for product in products:
        competitor_prices = CompetitorPrice.query.filter_by(product_id=product.id).all()
        
        if not competitor_prices:
            continue
        
        prices = [float(cp.price) for cp in competitor_prices if cp.price]
        if not prices:
            continue
        
        our_price = float(product.our_price) if product.our_price else 0
        min_competitor = min(prices)
        max_competitor = max(prices)
        avg_competitor = sum(prices) / len(prices)
        
        # Check if we are cheaper
        if our_price < min_competitor:
            results['cheaper'].append({
                'model': product.model,
                'name': product.name,
                'our_price': our_price,
                'min_competitor': min_competitor,
                'difference': min_competitor - our_price
            })
        
        # Check opportunities
        if our_price < avg_competitor * 0.85:
            potential_price = avg_competitor * 0.95
            qty = product.quantity or 0
            current_margin = our_price * 0.3  # Assume 30% margin
            new_margin = potential_price * 0.35  # Assume 35% margin
            additional_profit = (new_margin - current_margin) * qty
            
            if additional_profit > 500:
                results['opportunities'].append({
                    'model': product.model,
                    'name': product.name,
                    'current_website_price': our_price,
                    'suggested_price': potential_price,
                    'additional_profit': additional_profit
                })
    
    return results

def _generate_recommendations(analysis, statistics):
    """Generate recommendations based on analysis"""
    recommendations = []
    
    opportunities = analysis.get('opportunities', [])
    cheaper_count = len(analysis.get('cheaper', []))
    
    if opportunities:
        total_profit = sum(o.get('additional_profit', 0) for o in opportunities[:5])
        recommendations.append(
            f"Поднять цены на товары с большим потенциалом (топ-5 дадут +{total_profit:,.0f} GEL)"
        )
    
    if cheaper_count > 0:
        recommendations.append(
            f"Использовать низкие цены (где мы дешевле, {cheaper_count} товаров) в маркетинге и рекламе"
        )
    
    recommendations.extend([
        "Пересмотреть цены на товары, где мы дороже конкурентов (риск потери продаж)",
        "Продолжать еженедельный мониторинг для отслеживания изменений",
        "Настроить автоматический запуск системы каждое утро в 9:00",
    ])
    
    return recommendations

