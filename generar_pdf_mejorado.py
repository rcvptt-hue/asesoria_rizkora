# -*- coding: utf-8 -*-
"""
FUNCIÓN MEJORADA DE GENERACIÓN DE PDF
Incluye análisis de flujo financiero en el reporte

Integración: Reemplaza la función generar_pdf_asesoria() en tu código principal
"""

from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors as pdf_colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')

# Colores corporativos (ajusta según tus necesidades)
COLORES = {
    'azul_principal': '#064c78',
    'verde_oscuro': '#00796b',
    'verde_agua': '#00bfa5',
    'azul_claro': '#90caf9',
    'amarillo': '#fff59d',
    'rojo': '#ef5350',
    'verde': '#66bb6a',
    'naranja': '#ff9800'
}

def formatear_moneda(monto):
    """Formatea número como moneda"""
    try:
        return f"${float(monto):,.2f}"
    except:
        return "$0.00"

def generar_grafico_flujo_financiero(flujo_financiero):
    """
    Genera un gráfico visual del flujo financiero
    """
    try:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
        
        # Gráfico 1: Distribución de gastos (pastel)
        categorias = []
        valores = []
        colores_grafico = []
        
        if flujo_financiero.get('gastos_fijos', 0) > 0:
            categorias.append('Gastos\nFijos')
            valores.append(flujo_financiero['gastos_fijos'])
            colores_grafico.append(COLORES['azul_claro'])
        
        if flujo_financiero.get('gastos_variables', 0) > 0:
            categorias.append('Gastos\nVariables')
            valores.append(flujo_financiero['gastos_variables'])
            colores_grafico.append(COLORES['verde_agua'])
        
        if flujo_financiero.get('deudas', 0) > 0:
            categorias.append('Deudas')
            valores.append(flujo_financiero['deudas'])
            colores_grafico.append(COLORES['rojo'])
        
        if flujo_financiero.get('flujo_libre', 0) > 0:
            categorias.append('Flujo\nLibre')
            valores.append(flujo_financiero['flujo_libre'])
            colores_grafico.append(COLORES['verde'])
        
        if valores:
            wedges, texts, autotexts = ax1.pie(
                valores,
                labels=categorias,
                colors=colores_grafico,
                autopct='%1.1f%%',
                startangle=90,
                textprops={'fontsize': 8, 'weight': 'bold'}
            )
            
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(8)
        
        ax1.set_title('Distribución del Ingreso', fontsize=10, fontweight='bold', pad=10)
        
        # Gráfico 2: Comparación de porcentajes (barras horizontales)
        categorias_pct = ['G. Fijos', 'G. Variables', 'Deudas', 'Flujo Libre']
        valores_pct = [
            flujo_financiero.get('porcentaje_gastos_fijos', 0),
            flujo_financiero.get('porcentaje_gastos_variables', 0),
            flujo_financiero.get('porcentaje_deudas', 0),
            flujo_financiero.get('porcentaje_flujo', 0)
        ]
        colores_barras = [COLORES['azul_claro'], COLORES['verde_agua'], COLORES['rojo'], COLORES['verde']]
        
        bars = ax2.barh(categorias_pct, valores_pct, color=colores_barras, edgecolor='black', linewidth=1)
        
        # Agregar valores en las barras
        for i, (bar, val) in enumerate(zip(bars, valores_pct)):
            width = bar.get_width()
            ax2.text(width + 1, bar.get_y() + bar.get_height()/2, 
                    f'{val:.1f}%', ha='left', va='center', fontsize=8, fontweight='bold')
        
        ax2.set_xlabel('Porcentaje del Ingreso (%)', fontsize=9, fontweight='bold')
        ax2.set_title('Análisis por Categoría', fontsize=10, fontweight='bold', pad=10)
        ax2.set_xlim(0, max(valores_pct) + 15)
        ax2.grid(axis='x', alpha=0.3, linestyle='--')
        
        plt.tight_layout()
        
        # Guardar en buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer
        
    except Exception as e:
        print(f"Error al generar gráfico de flujo: {str(e)}")
        return None

def generar_pdf_asesoria_mejorado(datos_completos):
    """
    Genera PDF completo con análisis financiero incluido
    
    Parameters:
    -----------
    datos_completos : dict
        Diccionario completo con todos los datos de st.session_state.datos
        Debe incluir las claves: 'datos_generales', 'perfil_familiar', 'ingresos',
        'flujo_financiero', 'capacidad_ahorro', 'proteccion', 'retiro', 'educacion', 'ahorro'
    
    Returns:
    --------
    BytesIO : Buffer con el PDF generado
    """
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=letter, 
            rightMargin=72, 
            leftMargin=72, 
            topMargin=72, 
            bottomMargin=72
        )
        
        # Estilos
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=pdf_colors.HexColor(COLORES['azul_principal']),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=pdf_colors.HexColor(COLORES['verde_oscuro']),
            spaceAfter=15,
            fontName='Helvetica-Bold'
        )
        
        subsection_style = ParagraphStyle(
            'CustomSubsection',
            parent=styles['Heading3'],
            fontSize=12,
            textColor=pdf_colors.HexColor(COLORES['azul_principal']),
            spaceAfter=10,
            fontName='Helvetica-Bold'
        )
        
        highlight_style = ParagraphStyle(
            'Highlight',
            parent=styles['Normal'],
            fontSize=11,
            textColor=pdf_colors.HexColor(COLORES['verde_oscuro']),
            fontName='Helvetica-Bold',
            spaceAfter=10
        )
        
        story = []
        
        # ====================================================================
        # PORTADA
        # ====================================================================
        story.append(Spacer(1, 1*inch))
        story.append(Paragraph("REPORTE DE ASESORÍA FINANCIERA INTEGRAL", title_style))
        story.append(Spacer(1, 0.3*inch))
        story.append(Paragraph("Rizkora - Análisis Completo de Finanzas Personales", styles['Normal']))
        story.append(Spacer(1, 0.5*inch))
        
        datos_gen = datos_completos.get('datos_generales', {})
        flujo = datos_completos.get('flujo_financiero', {})
        
        portada_info = f"""
        <para alignment="center">
        <b>Cliente:</b> {datos_gen.get('nombre', 'N/A')}<br/>
        <b>Agente:</b> {datos_gen.get('nombre_agente', 'N/A')}<br/>
        <b>Fecha:</b> {datos_gen.get('fecha_asesoria', 'N/A')}<br/>
        <br/>
        <font size="12" color="{flujo.get('color_estado', '#000000')}">
        <b>{flujo.get('semaforo', '')} Estado Financiero: {flujo.get('estado_financiero', 'N/A').upper()}</b>
        </font>
        </para>
        """
        story.append(Paragraph(portada_info, styles['Normal']))
        
        story.append(PageBreak())
        
        # ====================================================================
        # SECCIÓN 1: INFORMACIÓN DEL CLIENTE
        # ====================================================================
        story.append(Paragraph("1. INFORMACIÓN DEL CLIENTE", subtitle_style))
        
        cliente_data = [
            ["Campo", "Información"],
            ["Nombre Completo", datos_gen.get('nombre', 'N/A')],
            ["Edad", f"{datos_gen.get('edad', 'N/A')} años"],
            ["Estado Civil", datos_gen.get('estado_civil', 'N/A')],
            ["Ocupación", datos_gen.get('ocupacion', 'N/A')],
            ["Teléfono", datos_gen.get('telefono', 'N/A')],
            ["Correo Electrónico", datos_gen.get('correo', 'N/A')],
            ["Fumador", datos_gen.get('fumador', 'N/A')],
            ["Tipo de Cita", datos_gen.get('tipo_cita', 'N/A')],
            ["Agente Asesor", datos_gen.get('nombre_agente', 'N/A')],
            ["Fecha de Asesoría", str(datos_gen.get('fecha_asesoria', 'N/A'))]
        ]
        
        cliente_table = Table(cliente_data, colWidths=[2.5*inch, 3.5*inch])
        cliente_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor(COLORES['azul_principal'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.black),
            ('BACKGROUND', (0, 1), (0, -1), pdf_colors.white),
            ('TEXTCOLOR', (0, 1), (0, -1), pdf_colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, pdf_colors.grey),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE')
        ]))
        
        story.append(cliente_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Perfil Familiar
        story.append(Paragraph("Perfil Familiar", subsection_style))
        perfil = datos_completos.get('perfil_familiar', {})
        
        perfil_info = [
            ["Característica", "Detalle"],
            ["Tiene Pareja", perfil.get('tiene_pareja', 'No')],
            ["Nombre de Pareja", perfil.get('nombre_pareja', 'N/A') if perfil.get('tiene_pareja') == 'Sí' else 'N/A'],
            ["Tiene Hijos", perfil.get('tiene_hijos', 'No')],
            ["Número de Hijos", str(perfil.get('num_hijos', 0))],
            ["Tiene Otros Dependientes", perfil.get('tiene_dependientes', 'No')],
            ["Número de Dependientes", str(perfil.get('num_dependientes', 0))]
        ]
        
        perfil_table = Table(perfil_info, colWidths=[2.5*inch, 3.5*inch])
        perfil_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor(COLORES['azul_principal'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
            ('BACKGROUND', (0, 1), (0, -1), pdf_colors.white),
            ('TEXTCOLOR', (0, 1), (0, -1), pdf_colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, pdf_colors.grey)
        ]))
        
        story.append(perfil_table)
        
        story.append(PageBreak())
        
        # ====================================================================
        # SECCIÓN 2: ANÁLISIS DE FLUJO FINANCIERO (NUEVO)
        # ====================================================================
        story.append(Paragraph("2. ANÁLISIS DE FLUJO FINANCIERO", subtitle_style))
        
        if flujo:
            # Estado Financiero en recuadro destacado
            estado = flujo.get('estado_financiero', 'N/A').upper()
            semaforo = flujo.get('semaforo', '')
            mensaje_estado = flujo.get('mensaje_estado', '')
            
            # Crear un Table con una celda para el recuadro (mejor control sobre el ancho)
            estado_data = [[
                f"<para alignment='center'>"
                f"<font size='14'><b>{semaforo} ESTADO FINANCIERO: {estado}</b></font><br/><br/>"
                f"<font size='11'>{mensaje_estado}</font>"
                f"</para>"
            ]]
            
            estado_table = Table(estado_data, colWidths=[6*inch])
            estado_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), pdf_colors.HexColor(flujo.get('color_estado', '#CCCCCC'))),
                ('TEXTCOLOR', (0, 0), (-1, -1), pdf_colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 15),
                ('LEFTPADDING', (0, 0), (-1, -1), 20),
                ('RIGHTPADDING', (0, 0), (-1, -1), 20),
                ('BOX', (0, 0), (-1, -1), 2, pdf_colors.white),
                ('WORDWRAP', (0, 0), (-1, -1), True)  # ¡ESTO ES IMPORTANTE!
            ]))
            
            story.append(estado_table)
            story.append(Spacer(1, 0.2*inch))
            
            # Tabla de Flujo Financiero
            story.append(Paragraph("2.1 Resumen del Flujo Mensual", subsection_style))
            
            flujo_data = [
                ["Concepto", "Monto", "% del Ingreso"],
                ["Ingreso Mensual Neto", formatear_moneda(flujo.get('ingreso_mensual', 0)), "100.0%"],
                ["Gastos Fijos", formatear_moneda(flujo.get('gastos_fijos', 0)), 
                 f"{flujo.get('porcentaje_gastos_fijos', 0):.1f}%"],
                ["Gastos Variables", formatear_moneda(flujo.get('gastos_variables', 0)), 
                 f"{flujo.get('porcentaje_gastos_variables', 0):.1f}%"],
                ["Pagos de Deudas", formatear_moneda(flujo.get('deudas', 0)), 
                 f"{flujo.get('porcentaje_deudas', 0):.1f}%"],
                ["Total de Gastos", formatear_moneda(flujo.get('gastos_totales', 0)),
                 f"{flujo.get('porcentaje_gastos_fijos', 0) + flujo.get('porcentaje_gastos_variables', 0) + flujo.get('porcentaje_deudas', 0):.1f}%"],
                ["FLUJO LIBRE", formatear_moneda(flujo.get('flujo_libre', 0)), 
                 f"{flujo.get('porcentaje_flujo', 0):.1f}%"]
            ]
            
            flujo_table = Table(flujo_data, colWidths=[2.5*inch, 2*inch, 1.5*inch])
            flujo_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor(COLORES['azul_principal'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 1, pdf_colors.grey),
                ('BACKGROUND', (0, 1), (-1, 1), pdf_colors.lightgrey),
                ('BACKGROUND', (0, 5), (-1, 5), pdf_colors.lightgrey),
                ('BACKGROUND', (0, 6), (-1, 6), pdf_colors.HexColor(COLORES['azul_claro'])),
                ('FONTNAME', (0, 6), (-1, 6), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0, 6), (-1, 6), pdf_colors.white),
                ('ROWBACKGROUNDS', (0, 2), (-1, 4), [pdf_colors.white, pdf_colors.lightgrey])
            ]))
            
            story.append(flujo_table)
            story.append(Spacer(1, 0.3*inch))
            
            # Desglose Detallado de Gastos
            story.append(Paragraph("2.2 Desglose Detallado de Gastos", subsection_style))
            
            # Gastos Fijos
            detalle_gastos_fijos = flujo.get('detalle_gastos_fijos', {})
            if detalle_gastos_fijos and any(detalle_gastos_fijos.values()):
                story.append(Paragraph("<b>Gastos Fijos:</b>", highlight_style))
                
                gastos_fijos_data = [["Categoría", "Monto Mensual"]]
                for categoria, monto in detalle_gastos_fijos.items():
                    if monto > 0:
                        gastos_fijos_data.append([categoria.capitalize(), formatear_moneda(monto)])
                gastos_fijos_data.append(["TOTAL", formatear_moneda(flujo.get('gastos_fijos', 0))])
                
                gastos_fijos_table = Table(gastos_fijos_data, colWidths=[3*inch, 2*inch])
                gastos_fijos_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor(COLORES['azul_principal'])),
                    ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, pdf_colors.grey),
                    ('BACKGROUND', (0, -1), (-1, -1), pdf_colors.lightgrey),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
                ]))
                
                story.append(gastos_fijos_table)
                story.append(Spacer(1, 0.2*inch))
            
            # Gastos Variables
            detalle_gastos_variables = flujo.get('detalle_gastos_variables', {})
            if detalle_gastos_variables and any(detalle_gastos_variables.values()):
                story.append(Paragraph("<b>Gastos Variables:</b>", highlight_style))
                
                gastos_var_data = [["Categoría", "Monto Mensual"]]
                for categoria, monto in detalle_gastos_variables.items():
                    if monto > 0:
                        gastos_var_data.append([categoria.capitalize(), formatear_moneda(monto)])
                gastos_var_data.append(["TOTAL", formatear_moneda(flujo.get('gastos_variables', 0))])
                
                gastos_var_table = Table(gastos_var_data, colWidths=[3*inch, 2*inch])
                gastos_var_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor(COLORES['azul_principal'])),
                    ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, pdf_colors.grey),
                    ('BACKGROUND', (0, -1), (-1, -1), pdf_colors.lightgrey),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
                ]))
                
                story.append(gastos_var_table)
                story.append(Spacer(1, 0.2*inch))
            
            # Deudas
            detalle_deudas = flujo.get('detalle_deudas', {})
            if detalle_deudas and any(detalle_deudas.values()):
                story.append(Paragraph("<b>Pagos de Deudas:</b>", highlight_style))
                
                deudas_data = [["Tipo de Deuda", "Pago Mensual"]]
                for categoria, monto in detalle_deudas.items():
                    if monto > 0:
                        deudas_data.append([categoria.capitalize(), formatear_moneda(monto)])
                deudas_data.append(["TOTAL", formatear_moneda(flujo.get('deudas', 0))])
                
                deudas_table = Table(deudas_data, colWidths=[3*inch, 2*inch])
                deudas_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor(COLORES['rojo'])),
                    ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTSIZE', (0, 0), (-1, -1), 9),
                    ('GRID', (0, 0), (-1, -1), 0.5, pdf_colors.grey),
                    ('BACKGROUND', (0, -1), (-1, -1), pdf_colors.lightgrey),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold')
                ]))
                
                story.append(deudas_table)
                story.append(Spacer(1, 0.2*inch))
            
            # Gráficos de Flujo Financiero
            story.append(Paragraph("2.3 Visualización del Flujo Financiero", subsection_style))
            
            grafico_buffer = generar_grafico_flujo_financiero(flujo)
            if grafico_buffer:
                img = Image(grafico_buffer, width=6*inch, height=2.4*inch)
                story.append(img)
                story.append(Spacer(1, 0.2*inch))
            
            # Indicadores de Salud Financiera
            story.append(Paragraph("2.4 Indicadores de Salud Financiera", subsection_style))
            
            indicadores = []
            
            # Indicador de flujo libre
            pct_flujo = flujo.get('porcentaje_flujo', 0)
            if pct_flujo >= 30:
                indicadores.append("✅ <b>Flujo Libre EXCELENTE</b>: " + f"{pct_flujo:.1f}% - Posición financiera óptima")
            elif pct_flujo >= 20:
                indicadores.append("✅ <b>Flujo Libre SALUDABLE</b>: " + f"{pct_flujo:.1f}% - Buena posición financiera")
            elif pct_flujo >= 10:
                indicadores.append("⚠️ <b>Flujo Libre AJUSTADO</b>: " + f"{pct_flujo:.1f}% - Margen limitado, requiere atención")
            elif pct_flujo >= 0:
                indicadores.append("🚨 <b>Flujo Libre CRÍTICO</b>: " + f"{pct_flujo:.1f}% - Acción urgente requerida")
            else:
                indicadores.append("🚨 <b>Flujo NEGATIVO</b>: " + f"{pct_flujo:.1f}% - URGENTE: Gastos superan ingresos")
            
            # Indicador de deudas
            pct_deudas = flujo.get('porcentaje_deudas', 0)
            if pct_deudas == 0:
                indicadores.append("✅ <b>Sin Deudas</b>: Excelente posición")
            elif pct_deudas <= 20:
                indicadores.append("✅ <b>Deudas Bajo Control</b>: " + f"{pct_deudas:.1f}% del ingreso")
            elif pct_deudas <= 35:
                indicadores.append("⚠️ <b>Deudas Moderadas</b>: " + f"{pct_deudas:.1f}% del ingreso - Mantén control")
            else:
                indicadores.append("🚨 <b>Deudas Altas</b>: " + f"{pct_deudas:.1f}% del ingreso - Requiere plan de reducción")
            
            # Indicador de gastos fijos
            pct_gastos_fijos = flujo.get('porcentaje_gastos_fijos', 0)
            if pct_gastos_fijos <= 50:
                indicadores.append("✅ <b>Gastos Fijos Adecuados</b>: " + f"{pct_gastos_fijos:.1f}% del ingreso")
            elif pct_gastos_fijos <= 60:
                indicadores.append("⚠️ <b>Gastos Fijos Elevados</b>: " + f"{pct_gastos_fijos:.1f}% del ingreso")
            else:
                indicadores.append("🚨 <b>Gastos Fijos Muy Elevados</b>: " + f"{pct_gastos_fijos:.1f}% - Busca reducirlos")
            
            for indicador in indicadores:
                story.append(Paragraph(f"• {indicador}", styles['Normal']))
                story.append(Spacer(1, 5))
            
        story.append(PageBreak())
        
        # ====================================================================
        # SECCIÓN 3: CAPACIDAD DE AHORRO E INVERSIÓN (NUEVO)
        # ====================================================================
        capacidad = datos_completos.get('capacidad_ahorro', {})
        
        story.append(Paragraph("3. CAPACIDAD DE AHORRO E INVERSIÓN", subtitle_style))
        
        if capacidad:
            if capacidad.get('ahorro_posible', False):
                # Tabla de capacidad
                capacidad_data = [
                    ["Concepto", "Monto Mensual"],
                    ["Rango Mínimo de Ahorro", formatear_moneda(capacidad.get('rango_min', 0))],
                    ["Ahorro Mensual Sugerido", formatear_moneda(capacidad.get('ahorro_sugerido', 0))],
                    ["Rango Máximo de Ahorro", formatear_moneda(capacidad.get('rango_max', 0))],
                    ["", ""],
                    ["Ahorro Mínimo Ideal (5% ingreso)", formatear_moneda(capacidad.get('ahorro_minimo', 0))],
                    ["Ahorro Óptimo Ideal (10% ingreso)", formatear_moneda(capacidad.get('ahorro_optimo', 0))]
                ]
                
                capacidad_table = Table(capacidad_data, colWidths=[3.5*inch, 2.5*inch])
                capacidad_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor(COLORES['verde_oscuro'])),
                    ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 0.5, pdf_colors.grey),
                    ('BACKGROUND', (0, 2), (-1, 2), pdf_colors.HexColor(COLORES['amarillo'])),
                    ('FONTNAME', (0, 2), (-1, 2), 'Helvetica-Bold'),
                    ('BACKGROUND', (0, 4), (-1, 4), pdf_colors.white),
                    ('GRID', (0, 4), (-1, 4), 0, pdf_colors.white),
                    ('BACKGROUND', (0, 5), (-1, 6), pdf_colors.lightgrey)
                ]))
                
                story.append(capacidad_table)
                story.append(Spacer(1, 0.2*inch))
                
                # Mensaje de capacidad
                mensaje_capacidad = capacidad.get('mensaje', '')
                story.append(Paragraph(f"<b>Análisis:</b> {mensaje_capacidad}", styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
                
                # Inversión mensual comprometida
                ingresos = datos_completos.get('ingresos', {})
                inversion_mensual = ingresos.get('inversion_mensual', 0)
                
                if inversion_mensual > 0:
                    story.append(Paragraph("<b>Inversión Mensual Comprometida:</b> " + 
                                         formatear_moneda(inversion_mensual), highlight_style))
                    
                    # Validar si está dentro del rango
                    if inversion_mensual <= capacidad.get('rango_max', 0):
                        validacion_msg = "✅ La inversión comprometida está dentro de la capacidad calculada."
                    else:
                        validacion_msg = "⚠️ La inversión comprometida excede la capacidad máxima sugerida."
                    
                    story.append(Paragraph(validacion_msg, styles['Normal']))
                
            else:
                # No hay capacidad de ahorro
                mensaje_sin_capacidad = capacidad.get('mensaje', 'No hay capacidad de ahorro disponible.')
                
                warning_text = f"""
                <para alignment="center" backColor="{COLORES['rojo']}" 
                      leftIndent="10" rightIndent="10" spaceBefore="5" spaceAfter="5">
                <font size="12" color="white"><b>⚠️ SIN CAPACIDAD DE AHORRO</b></font><br/>
                <font size="10" color="white">{mensaje_sin_capacidad}</font>
                </para>
                """
                story.append(Paragraph(warning_text, styles['Normal']))
                story.append(Spacer(1, 0.2*inch))
                
                story.append(Paragraph("<b>Recomendación Urgente:</b>", highlight_style))
                story.append(Paragraph("Es necesario estabilizar la situación financiera antes de realizar inversiones:", 
                                     styles['Normal']))
                story.append(Paragraph("• Reducir gastos no esenciales", styles['Normal']))
                story.append(Paragraph("• Generar un plan de pago de deudas", styles['Normal']))
                story.append(Paragraph("• Buscar formas de aumentar ingresos", styles['Normal']))
        
        story.append(PageBreak())
        
        # ====================================================================
        # SECCIÓN 4: PROTECCIÓN FINANCIERA
        # ====================================================================
        proteccion = datos_completos.get('proteccion', {})
        
        if proteccion.get('aplica', False):
            story.append(Paragraph("4. PROTECCIÓN FINANCIERA", subtitle_style))
            
            proteccion_data = [
                ["Concepto", "Detalle"],
                ["Presupuesto Mensual Familiar", formatear_moneda(proteccion.get('presupuesto_mensual', 0))],
                ["Presupuesto Anual", formatear_moneda(proteccion.get('presupuesto_anual', 0))],
                ["Monto de Protección Sugerido (10 años)", formatear_moneda(proteccion.get('monto_proteccion_sugerido', 0))],
                ["Responsable Principal", proteccion.get('responsable1', 'N/A')],
                ["Responsable Secundario", proteccion.get('responsable2', 'N/A') if proteccion.get('responsable2') else 'N/A']
            ]
            
            proteccion_table = Table(proteccion_data, colWidths=[3*inch, 3*inch])
            proteccion_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor(COLORES['azul_principal'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
                ('BACKGROUND', (0, 1), (0, -1), pdf_colors.HexColor(COLORES['azul_claro'])),
                ('TEXTCOLOR', (0, 1), (0, -1), pdf_colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, pdf_colors.grey),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8)
            ]))
            
            story.append(proteccion_table)
            story.append(Spacer(1, 0.2*inch))
            
            reflexion = proteccion.get('reflexion', '')
            if reflexion:
                story.append(Paragraph("<b>Reflexión del Cliente:</b>", highlight_style))
                story.append(Paragraph(reflexion, styles['Normal']))
            
            story.append(Spacer(1, 0.3*inch))
        
        # ====================================================================
        # SECCIÓN 5: PLAN DE RETIRO
        # ====================================================================
        retiro = datos_completos.get('retiro', {})
        
        if retiro.get('ingreso_mensual_retiro', 0) > 0:
            story.append(Paragraph("5. PLAN DE RETIRO", subtitle_style))
            
            retiro_data = [
                ["Concepto", "Valor"],
                ["Edad Actual", f"{datos_gen.get('edad', 'N/A')} años"],
                ["Edad de Retiro Deseada", f"{retiro.get('edad_retiro', 'N/A')} años"],
                ["Años para el Retiro", f"{retiro.get('anos_para_retiro', 'N/A')} años"],
                ["Años en Retiro (estimado)", f"{retiro.get('anos_en_retiro', 'N/A')} años"],
                ["Ingreso Mensual Deseado en Retiro", formatear_moneda(retiro.get('ingreso_mensual_retiro', 0))],
                ["Ingreso Anual en Retiro", formatear_moneda(retiro.get('monto_anual_retiro', 0))],
                ["Monto Total Requerido", formatear_moneda(retiro.get('monto_total_retiro', 0))],
                ["Ahorro Mensual Sugerido", formatear_moneda(retiro.get('ahorro_mensual_sugerido', 0))]
            ]
            
            retiro_table = Table(retiro_data, colWidths=[3.5*inch, 2.5*inch])
            retiro_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor(COLORES['verde_oscuro'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
                ('BACKGROUND', (0, 1), (0, -1), pdf_colors.HexColor(COLORES['azul_claro'])),
                ('TEXTCOLOR', (0, 1), (0, -1), pdf_colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('BACKGROUND', (0, -1), (-1, -1), pdf_colors.HexColor(COLORES['amarillo'])),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, pdf_colors.grey),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT')
            ]))
            
            story.append(retiro_table)
            story.append(Spacer(1, 0.3*inch))
        
        # ====================================================================
        # SECCIÓN 6: EDUCACIÓN
        # ====================================================================
        educacion = datos_completos.get('educacion', {})
        
        if educacion.get('aplica', False):
            story.append(Paragraph("6. PLAN DE EDUCACIÓN", subtitle_style))
            
            hijos_educacion = educacion.get('hijos', [])
            if hijos_educacion:
                for i, hijo in enumerate(hijos_educacion, 1):
                    story.append(Paragraph(f"<b>Hijo {i}: {hijo.get('nombre', 'N/A')}</b> ({hijo.get('edad', 'N/A')} años)", 
                                         highlight_style))
                    
                    hijo_data = [
                        ["Concepto", "Valor"],
                        ["Años hasta Universidad", f"{hijo.get('anos_restantes', 'N/A')} años"],
                        ["Costo Anual Estimado Universidad", formatear_moneda(hijo.get('costo_anual', 0))],
                        ["Costo Total (4 años)", formatear_moneda(hijo.get('costo_total', 0))],
                        ["Ahorro Mensual Sugerido", formatear_moneda(hijo.get('ahorro_mensual', 0))]
                    ]
                    
                    hijo_table = Table(hijo_data, colWidths=[3.5*inch, 2.5*inch])
                    hijo_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor(COLORES['verde_agua'])),
                        ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('GRID', (0, 0), (-1, -1), 0.5, pdf_colors.grey),
                        ('ALIGN', (1, 0), (1, -1), 'RIGHT')
                    ]))
                    
                    story.append(hijo_table)
                    story.append(Spacer(1, 0.15*inch))
            
            # Total de educación
            story.append(Paragraph("<b>Resumen Total de Educación:</b>", highlight_style))
            total_educacion = [
                ["Inversión Total en Educación", formatear_moneda(educacion.get('monto_total_educacion', 0))],
                ["Ahorro Mensual Total Sugerido", formatear_moneda(educacion.get('ahorro_mensual_total', 0))]
            ]
            
            total_edu_table = Table(total_educacion, colWidths=[3.5*inch, 2.5*inch])
            total_edu_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), pdf_colors.HexColor(COLORES['amarillo'])),
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, pdf_colors.grey),
                ('ALIGN', (1, 0), (1, -1), 'RIGHT')
            ]))
            
            story.append(total_edu_table)
            story.append(Spacer(1, 0.3*inch))
        
        # ====================================================================
        # SECCIÓN 7: PROYECTO / AHORRO
        # ====================================================================
        ahorro = datos_completos.get('ahorro', {})
        
        if ahorro.get('tiene_proyecto') == 'Sí':
            story.append(Paragraph("7. PROYECTO PERSONAL", subtitle_style))
            
            proyecto_data = [
                ["Concepto", "Detalle"],
                ["Descripción del Proyecto", ahorro.get('descripcion', 'N/A')],
                ["Costo Total del Proyecto", formatear_moneda(ahorro.get('costo', 0))],
                ["Ahorro Actual Disponible", formatear_moneda(ahorro.get('ahorro_actual', 0))],
                ["Inversión Requerida", formatear_moneda(ahorro.get('inversion_requerida', 0))],
                ["Plazo", f"{ahorro.get('plazo_anos', 'N/A')} años"],
                ["Ahorro Mensual Sugerido", formatear_moneda(ahorro.get('ahorro_mensual_sugerido', 0))]
            ]
            
            proyecto_table = Table(proyecto_data, colWidths=[3*inch, 3*inch])
            proyecto_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor(COLORES['verde_oscuro'])),
                ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
                ('BACKGROUND', (0, 1), (0, -1), pdf_colors.HexColor(COLORES['azul_claro'])),
                ('TEXTCOLOR', (0, 1), (0, -1), pdf_colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('GRID', (0, 0), (-1, -1), 1, pdf_colors.grey)
            ]))
            
            story.append(proyecto_table)
            story.append(Spacer(1, 0.3*inch))
        
        story.append(PageBreak())
        
        # ====================================================================
        # SECCIÓN 8: RECOMENDACIONES PERSONALIZADAS (BASADAS EN FLUJO FINANCIERO)
        # ====================================================================
        story.append(Paragraph("8. RECOMENDACIONES PERSONALIZADAS", subtitle_style))
        
        # Importar función de recomendaciones si está disponible
        try:
            from modulo_financiero import generar_recomendaciones_financieras
            
            if flujo and capacidad:
                recomendaciones = generar_recomendaciones_financieras(flujo, capacidad)
                
                story.append(Paragraph("Basándose en el análisis de tu flujo financiero y capacidad de ahorro, " +
                                     "se sugieren las siguientes acciones priorizadas:", styles['Normal']))
                story.append(Spacer(1, 0.15*inch))
                
                for i, rec in enumerate(recomendaciones[:10], 1):  # Máximo 10 en PDF
                    story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
                    story.append(Spacer(1, 8))
        
        except ImportError:
            # Si no hay módulo, usar recomendaciones básicas
            story.append(Paragraph("Recomendaciones generales basadas en tu perfil financiero:", styles['Normal']))
            story.append(Spacer(1, 0.15*inch))
            
            recomendaciones_basicas = [
                "Mantén un registro detallado de tus gastos mensuales",
                "Establece un fondo de emergencia equivalente a 3-6 meses de gastos",
                "Revisa y ajusta tu presupuesto periódicamente",
                "Considera diversificar tus fuentes de ingreso",
                "Planifica tus objetivos financieros a corto, mediano y largo plazo"
            ]
            
            for i, rec in enumerate(recomendaciones_basicas, 1):
                story.append(Paragraph(f"{i}. {rec}", styles['Normal']))
                story.append(Spacer(1, 8))
        
        story.append(Spacer(1, 0.3*inch))
        
        # ====================================================================
        # RESUMEN EJECUTIVO
        # ====================================================================
        story.append(Paragraph("RESUMEN EJECUTIVO", subtitle_style))
        
        resumen_text = f"""
        Este reporte presenta un análisis integral de la situación financiera de {datos_gen.get('nombre', 'el cliente')}.
        
        <b>Estado Financiero Actual:</b> {flujo.get('semaforo', '')} {flujo.get('estado_financiero', 'N/A').upper()}
        
        <b>Puntos Clave:</b>
        • Flujo libre mensual: {formatear_moneda(flujo.get('flujo_libre', 0))} ({flujo.get('porcentaje_flujo', 0):.1f}% del ingreso)
        • Capacidad de ahorro: {formatear_moneda(capacidad.get('ahorro_sugerido', 0)) if capacidad.get('ahorro_posible') else '$0.00'} mensuales
        • Inversión comprometida: {formatear_moneda(datos_completos.get('ingresos', {}).get('inversion_mensual', 0))}
        
        <b>Próximos Pasos:</b>
        1. Implementar las recomendaciones priorizadas
        2. Establecer seguimiento mensual del flujo financiero
        3. Ajustar plan según evolución de la situación
        4. Programar revisión trimestral
        """
        
        story.append(Paragraph(resumen_text, styles['Normal']))
        
        # ====================================================================
        # FOOTER
        # ====================================================================
        story.append(Spacer(1, 0.5*inch))
        
        footer_text = f"""
        <para alignment="center">
        <font size="8" color="gray">
        Reporte generado: {datetime.now().strftime('%d/%m/%Y a las %H:%M')}<br/>
        Asesoría Financiera Rizkora - Análisis Integral de Finanzas Personales<br/>
        Este reporte es confidencial y para uso exclusivo del cliente.<br/>
        <br/>
        <i>Nota: Los montos y recomendaciones son estimados basados en la información proporcionada.
        Se recomienda una sesión de seguimiento para revisar opciones de ahorro/inversión específicas.</i>
        </font>
        </para>
        """
        
        story.append(Paragraph(footer_text, styles['Normal']))
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    except Exception as e:
        print(f"Error al generar PDF: {str(e)}")
        import traceback
        traceback.print_exc()
        return None


# ====================================================================
# EJEMPLO DE USO
# ====================================================================

if __name__ == "__main__":
    """
    Ejemplo de cómo usar la función mejorada
    """
    
    # Datos de ejemplo completos
    datos_ejemplo = {
        'datos_generales': {
            'nombre': 'Juan Pérez López',
            'edad': 35,
            'telefono': '5512345678',
            'correo': 'juan.perez@email.com',
            'ocupacion': 'Ingeniero de Software',
            'estado_civil': 'Casado',
            'fecha_nacimiento': '1989-05-15',
            'fumador': 'No',
            'tipo_cita': 'Presencial',
            'nombre_agente': 'María González',
            'fecha_asesoria': '2026-02-03'
        },
        'perfil_familiar': {
            'tiene_pareja': 'Sí',
            'nombre_pareja': 'Ana Pérez',
            'edad_pareja': 33,
            'tiene_hijos': 'Sí',
            'num_hijos': 2,
            'hijos': [
                {'nombre': 'Carlos', 'edad': 8},
                {'nombre': 'Laura', 'edad': 5}
            ],
            'tiene_dependientes': 'No',
            'num_dependientes': 0
        },
        'ingresos': {
            'ingreso_mensual': 50000,
            'ingreso_anual': 600000,
            'inversion_mensual': 1500
        },
        'flujo_financiero': {
            'ingreso_mensual': 50000,
            'gastos_fijos': 31500,
            'gastos_variables': 7500,
            'deudas': 7000,
            'gastos_totales': 46000,
            'flujo_libre': 4000,
            'porcentaje_flujo': 8.0,
            'porcentaje_gastos_fijos': 63.0,
            'porcentaje_gastos_variables': 15.0,
            'porcentaje_deudas': 14.0,
            'estado_financiero': 'crítico',
            'color_estado': '#ef5350',
            'semaforo': '🔴',
            'mensaje_estado': 'ATENCIÓN: Tu margen financiero es muy ajustado',
            'detalle_gastos_fijos': {
                'vivienda': 15000,
                'servicios': 2500,
                'transporte': 3000,
                'alimentacion': 6000,
                'seguros': 2000,
                'educacion': 3000
            },
            'detalle_gastos_variables': {
                'entretenimiento': 3000,
                'ropa': 1500,
                'salud': 1000,
                'otros': 2000
            },
            'detalle_deudas': {
                'tarjetas': 4000,
                'prestamos': 0,
                'auto': 3000,
                'otras': 0
            }
        },
        'capacidad_ahorro': {
            'ahorro_posible': True,
            'rango_min': 1200,
            'rango_max': 2000,
            'ahorro_sugerido': 1600,
            'ahorro_minimo': 2500,
            'ahorro_optimo': 5000,
            'mensaje': 'Tu margen es ajustado. Considera invertir conservadoramente.',
            'porcentaje_min': 30,
            'porcentaje_max': 50,
            'puede_invertir': True
        },
        'proteccion': {
            'aplica': True,
            'presupuesto_mensual': 25000,
            'presupuesto_anual': 300000,
            'monto_proteccion_sugerido': 3000000,
            'responsable1': 'Ana Pérez (Esposa)',
            'responsable2': 'María López (Madre)',
            'reflexion': 'Mi familia dependería de mis ahorros y el apoyo familiar.'
        },
        'retiro': {
            'edad_retiro': 65,
            'ingreso_mensual_retiro': 30000,
            'anos_para_retiro': 30,
            'anos_en_retiro': 15,
            'monto_anual_retiro': 360000,
            'monto_total_retiro': 5400000,
            'ahorro_mensual_sugerido': 15000
        },
        'educacion': {
            'aplica': True,
            'hijos': [
                {
                    'nombre': 'Carlos',
                    'edad': 8,
                    'costo_anual': 120000,
                    'anos_restantes': 10,
                    'costo_total': 480000,
                    'ahorro_mensual': 4000
                },
                {
                    'nombre': 'Laura',
                    'edad': 5,
                    'costo_anual': 120000,
                    'anos_restantes': 13,
                    'costo_total': 480000,
                    'ahorro_mensual': 3077
                }
            ],
            'monto_total_educacion': 960000,
            'ahorro_mensual_total': 7077
        },
        'ahorro': {
            'preparado_crisis': 'Parcialmente',
            'tiene_proyecto': 'Sí',
            'descripcion': 'Compra de casa propia',
            'costo': 2000000,
            'ahorro_actual': 150000,
            'plazo_anos': 10,
            'inversion_requerida': 1850000,
            'ahorro_mensual_sugerido': 15417
        }
    }
    
    print("Generando PDF de ejemplo...")
    pdf_buffer = generar_pdf_asesoria_mejorado(datos_ejemplo)
    
    if pdf_buffer:
        # Guardar PDF de ejemplo
        with open('ejemplo_reporte_financiero.pdf', 'wb') as f:
            f.write(pdf_buffer.getvalue())
        print("✅ PDF generado exitosamente: ejemplo_reporte_financiero.pdf")
    else:
        print("❌ Error al generar PDF")
