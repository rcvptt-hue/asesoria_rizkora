# -*- coding: utf-8 -*-
"""
ASESORÍA FINANCIERA RIZKORA
App independiente para detección de necesidades financieras
Versión: 2.0
Fecha: 2026
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date
import json
from io import BytesIO
import warnings
import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors as pdf_colors
import tempfile
warnings.filterwarnings('ignore')

# ================================
# CONFIGURACIÓN DE LA APP
# ================================
st.set_page_config(
    page_title="Asesoría Financiera Rizkora",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para alinear botones de navegación
st.markdown("""
<style>
    /* Alinear texto de botones a la izquierda */
    .stButton button {
        text-align: left !important;
        padding-left: 1rem !important;
    }
    
    /* Asegurar que el contenido del botón esté alineado */
    .stButton button p {
        text-align: left !important;
    }
    
    /* Mejorar espaciado en sidebar */
    section[data-testid="stSidebar"] .stButton {
        margin-bottom: 0.5rem;
    }
    
    /* Estilo para botones deshabilitados */
    .stButton button:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }
</style>
""", unsafe_allow_html=True)

# Colores corporativos
COLORES = {
    'azul_principal': '#064c78',
    'verde_oscuro': '#00796b',
    'verde_agua': '#00bfa5',
    'azul_claro': '#90caf9',
    'amarillo': '#fff59d'
}

# ================================
# INICIALIZAR SESSION STATE
# ================================
if 'step' not in st.session_state:
    st.session_state.step = 1

if 'datos' not in st.session_state:
    st.session_state.datos = {
        'datos_generales': {},
        'perfil_familiar': {},
        'ingresos': {},
        'proteccion': {},
        'ahorro': {},
        'retiro': {},
        'educacion': {},
        'cierre': {}
    }

if 'google_sheets_habilitado' not in st.session_state:
    st.session_state.google_sheets_habilitado = False

if 'confirmar_reinicio' not in st.session_state:
    st.session_state.confirmar_reinicio = False

# ================================
# CONFIGURACIÓN GOOGLE SHEETS
# ================================
@st.cache_resource
def init_google_sheets():
    """Inicializa conexión con Google Sheets"""
    try:
        if 'google_service_account' not in st.secrets:
            return None
        
        creds = Credentials.from_service_account_info(
            st.secrets["google_service_account"],
            scopes=[
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
        )
        
        client = gspread.authorize(creds)
        st.session_state.google_sheets_habilitado = True
        return client
    except Exception as e:
        st.session_state.google_sheets_habilitado = False
        return None

def guardar_asesoria_sheets(datos_completos):
    """Guarda la asesoría en Google Sheets"""
    try:
        client = init_google_sheets()
        if not client:
            return False, "No se pudo conectar con Google Sheets"
        
        # Abrir o crear spreadsheet
        try:
            spreadsheet = client.open("asesorias_rizkora")
        except:
            spreadsheet = client.create("asesorias_rizkora")
            spreadsheet.share('', perm_type='anyone', role='reader')
        
        # Preparar datos para la hoja
        datos_gen = datos_completos['datos_generales']
        necesidades = detectar_necesidades()
        
        fila_nueva = {
            'Fecha Asesoría': str(datos_gen.get('fecha_asesoria', '')),
            'Hora Registro': datetime.now().strftime("%H:%M:%S"),
            'Agente': datos_gen.get('nombre_agente', ''),
            'Cliente': datos_gen.get('nombre', ''),
            'Edad': datos_gen.get('edad', ''),
            'Teléfono': datos_gen.get('telefono', ''),
            'Correo': datos_gen.get('correo', ''),
            'Ocupación': datos_gen.get('ocupacion', ''),
            'Estado Civil': datos_gen.get('estado_civil', ''),
            'Fumador': datos_gen.get('fumador', ''),
            'Tipo Cita': datos_gen.get('tipo_cita', ''),
            'Ingreso Mensual': datos_completos['ingresos'].get('ingreso_mensual', 0),
            'Inversión Mensual Disponible': datos_completos['ingresos'].get('inversion_mensual', 0),
            'Necesidad Principal': necesidades['principal'].upper(),
            'Monto Protección': necesidades['montos']['proteccion'],
            'Monto Retiro': necesidades['montos']['retiro'],
            'Monto Educación': necesidades['montos']['educacion'],
            'Monto Ahorro/Proyecto': necesidades['montos']['ahorro'],
            'Tiene Pareja': datos_completos['perfil_familiar'].get('tiene_pareja', 'No'),
            'Tiene Hijos': datos_completos['perfil_familiar'].get('tiene_hijos', 'No'),
            'Num Hijos': datos_completos['perfil_familiar'].get('num_hijos', 0),
            'Segunda Cita': datos_completos['cierre'].get('segunda_cita', 'No'),
            'Fecha Segunda Cita': str(datos_completos['cierre'].get('fecha_segunda_cita', '')),
            'Num Referidos': datos_completos['cierre'].get('num_referidos', 0),
            'Satisfacción': datos_completos['cierre'].get('satisfaccion', '')
        }
        
        # Obtener o crear worksheet
        try:
            worksheet = spreadsheet.worksheet("Asesorías")
        except:
            worksheet = spreadsheet.add_worksheet(title="Asesorías", rows=1000, cols=25)
            # Agregar encabezados
            headers = list(fila_nueva.keys())
            worksheet.update('A1', [headers])
        
        # Agregar nueva fila
        worksheet.append_row(list(fila_nueva.values()), value_input_option='USER_ENTERED')
        
        return True, "Asesoría guardada exitosamente en Google Sheets"
    
    except Exception as e:
        return False, f"Error al guardar: {str(e)}"

# ================================
# FUNCIONES AUXILIARES
# ================================

def calcular_edad(fecha_nacimiento):
    """Calcula edad a partir de fecha de nacimiento"""
    try:
        if isinstance(fecha_nacimiento, str):
            fecha_nac = datetime.strptime(fecha_nacimiento, "%d/%m/%Y").date()
        else:
            fecha_nac = fecha_nacimiento
        
        hoy = date.today()
        edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
        return edad
    except:
        return None

def validar_email(email):
    """Valida formato de email básico"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validar_telefono(telefono):
    """Valida formato de teléfono (10 dígitos)"""
    telefono_limpio = ''.join(filter(str.isdigit, telefono))
    return len(telefono_limpio) == 10

def formatear_moneda(monto):
    """Formatea número como moneda"""
    try:
        return f"${float(monto):,.2f}"
    except:
        return "$0.00"

def navegar_a_paso(paso):
    """Navega a un paso específico"""
    st.session_state.step = paso
    st.rerun()

def exportar_json():
    """Exporta datos a JSON"""
    datos_export = {
        'fecha_generacion': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'datos_completos': st.session_state.datos,
        'necesidades_detectadas': detectar_necesidades()
    }
    return json.dumps(datos_export, indent=2, ensure_ascii=False)

def generar_pdf_asesoria():
    """Genera PDF con el resumen de la asesoría"""
    try:
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=72)
        
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=pdf_colors.HexColor(COLORES['azul_principal']),
            spaceAfter=30,
            alignment=1
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Heading2'],
            fontSize=14,
            textColor=pdf_colors.HexColor(COLORES['verde_oscuro']),
            spaceAfter=15
        )
        
        story = []
        
        # Título
        story.append(Paragraph("REPORTE DE ASESORÍA FINANCIERA", title_style))
        story.append(Paragraph("Rizkora - Detección de Necesidades", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Datos del cliente
        story.append(Paragraph("INFORMACIÓN DEL CLIENTE", subtitle_style))
        datos_gen = st.session_state.datos['datos_generales']
        
        cliente_data = [
            ["Nombre:", datos_gen.get('nombre', '')],
            ["Edad:", f"{datos_gen.get('edad', '')} años"],
            ["Teléfono:", datos_gen.get('telefono', '')],
            ["Correo:", datos_gen.get('correo', '')],
            ["Ocupación:", datos_gen.get('ocupacion', '')],
            ["Estado Civil:", datos_gen.get('estado_civil', '')],
            ["Fumador:", datos_gen.get('fumador', '')],
            ["Tipo de Cita:", datos_gen.get('tipo_cita', '')],
            ["Agente:", datos_gen.get('nombre_agente', '')],
            ["Fecha Asesoría:", str(datos_gen.get('fecha_asesoria', ''))]
        ]
        
        cliente_table = Table(cliente_data, colWidths=[2*inch, 4*inch])
        cliente_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), pdf_colors.HexColor(COLORES['azul_claro'])),
            ('TEXTCOLOR', (0, 0), (0, -1), pdf_colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, pdf_colors.grey)
        ]))
        
        story.append(cliente_table)
        story.append(Spacer(1, 20))
        
        # Perfil Familiar
        story.append(Paragraph("PERFIL FAMILIAR", subtitle_style))
        perfil = st.session_state.datos['perfil_familiar']
        
        perfil_info = [
            ["Tiene Pareja:", perfil.get('tiene_pareja', 'No')],
            ["Tiene Hijos:", perfil.get('tiene_hijos', 'No')],
            ["Número de Hijos:", str(perfil.get('num_hijos', 0))],
            ["Otros Dependientes:", perfil.get('tiene_dependientes', 'No')]
        ]
        
        perfil_table = Table(perfil_info, colWidths=[2*inch, 4*inch])
        perfil_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), pdf_colors.HexColor(COLORES['verde_agua'])),
            ('TEXTCOLOR', (0, 0), (0, -1), pdf_colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, pdf_colors.grey)
        ]))
        
        story.append(perfil_table)
        story.append(Spacer(1, 20))
        
        # Información Financiera
        story.append(Paragraph("INFORMACIÓN FINANCIERA", subtitle_style))
        ingresos = st.session_state.datos['ingresos']
        
        finanzas_info = [
            ["Ingreso Mensual:", formatear_moneda(ingresos.get('ingreso_mensual', 0))],
            ["Ingreso Anual:", formatear_moneda(ingresos.get('ingreso_anual', 0))],
            ["Inversión Mensual Disponible:", formatear_moneda(ingresos.get('inversion_mensual', 0))],
            ["Ahorro Ideal 10%:", formatear_moneda(ingresos.get('ahorro_ideal_10', 0))],
            ["Ahorro Conservador 7%:", formatear_moneda(ingresos.get('ahorro_conservador_7', 0))]
        ]
        
        finanzas_table = Table(finanzas_info, colWidths=[2.5*inch, 3.5*inch])
        finanzas_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), pdf_colors.HexColor(COLORES['azul_principal'])),
            ('TEXTCOLOR', (0, 0), (0, -1), pdf_colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('GRID', (0, 0), (-1, -1), 1, pdf_colors.grey)
        ]))
        
        story.append(finanzas_table)
        story.append(Spacer(1, 20))
        
        # Nueva página para necesidades
        story.append(PageBreak())
        
        # Necesidades Detectadas
        story.append(Paragraph("NECESIDADES DETECTADAS", subtitle_style))
        necesidades = detectar_necesidades()
        
        story.append(Paragraph(f"<b>Necesidad Principal:</b> {necesidades['principal'].upper()}", styles['Normal']))
        story.append(Spacer(1, 10))
        
        necesidades_data = [
            ["Categoría", "Monto Estimado", "Prioridad"],
            ["Protección", formatear_moneda(necesidades['montos']['proteccion']), "#1" if necesidades['prioridades'][0][0] == 'proteccion' else "#2+" if necesidades['montos']['proteccion'] > 0 else "-"],
            ["Retiro", formatear_moneda(necesidades['montos']['retiro']), "#1" if necesidades['prioridades'][0][0] == 'retiro' else "#2+" if necesidades['montos']['retiro'] > 0 else "-"],
            ["Educación", formatear_moneda(necesidades['montos']['educacion']), "#1" if necesidades['prioridades'][0][0] == 'educacion' else "#2+" if necesidades['montos']['educacion'] > 0 else "-"],
            ["Ahorro/Proyecto", formatear_moneda(necesidades['montos']['ahorro']), "#1" if necesidades['prioridades'][0][0] == 'ahorro' else "#2+" if necesidades['montos']['ahorro'] > 0 else "-"]
        ]
        
        necesidades_table = Table(necesidades_data, colWidths=[2*inch, 2.5*inch, 1.5*inch])
        necesidades_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), pdf_colors.HexColor(COLORES['verde_oscuro'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), pdf_colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, pdf_colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [pdf_colors.white, pdf_colors.lightgrey])
        ]))
        
        story.append(necesidades_table)
        story.append(Spacer(1, 20))
        
        # Detalles por pilar
        story.append(Paragraph("DETALLES POR PILAR FINANCIERO", subtitle_style))
        
        # Protección
        if st.session_state.datos['proteccion'].get('aplica'):
            story.append(Paragraph("<b>🛡️ PROTECCIÓN</b>", styles['Normal']))
            proteccion = st.session_state.datos['proteccion']
            story.append(Paragraph(f"Presupuesto Mensual Familiar: {formatear_moneda(proteccion.get('presupuesto_mensual', 0))}", styles['Normal']))
            story.append(Paragraph(f"Monto de Protección Sugerido: {formatear_moneda(proteccion.get('monto_proteccion_sugerido', 0))}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Retiro
        retiro = st.session_state.datos['retiro']
        if retiro.get('ingreso_mensual_retiro', 0) > 0:
            story.append(Paragraph("<b>👴 RETIRO</b>", styles['Normal']))
            story.append(Paragraph(f"Edad de Retiro Deseada: {retiro.get('edad_retiro', '')} años", styles['Normal']))
            story.append(Paragraph(f"Ingreso Mensual Deseado: {formatear_moneda(retiro.get('ingreso_mensual_retiro', 0))}", styles['Normal']))
            story.append(Paragraph(f"Monto Total Requerido: {formatear_moneda(retiro.get('monto_total_retiro', 0))}", styles['Normal']))
            story.append(Paragraph(f"Ahorro Mensual Sugerido: {formatear_moneda(retiro.get('ahorro_mensual_sugerido', 0))}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Educación
        if st.session_state.datos['educacion'].get('aplica'):
            story.append(Paragraph("<b>🎓 EDUCACIÓN</b>", styles['Normal']))
            educacion = st.session_state.datos['educacion']
            story.append(Paragraph(f"Monto Total para Educación: {formatear_moneda(educacion.get('monto_total_educacion', 0))}", styles['Normal']))
            story.append(Paragraph(f"Ahorro Mensual Total: {formatear_moneda(educacion.get('ahorro_mensual_total', 0))}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Proyecto
        if st.session_state.datos['ahorro'].get('tiene_proyecto') == "Sí":
            story.append(Paragraph("<b>💰 PROYECTO</b>", styles['Normal']))
            ahorro = st.session_state.datos['ahorro']
            story.append(Paragraph(f"Proyecto: {ahorro.get('descripcion', '')}", styles['Normal']))
            story.append(Paragraph(f"Costo: {formatear_moneda(ahorro.get('costo', 0))}", styles['Normal']))
            story.append(Paragraph(f"Ahorro Mensual Sugerido: {formatear_moneda(ahorro.get('ahorro_mensual_sugerido', 0))}", styles['Normal']))
            story.append(Spacer(1, 10))
        
        # Recomendaciones
        story.append(PageBreak())
        story.append(Paragraph("RECOMENDACIONES", subtitle_style))
        
        recomendaciones = []
        if necesidades['montos']['proteccion'] > 0:
            recomendaciones.append(f"• Protección: Considerar seguro de vida por {formatear_moneda(necesidades['montos']['proteccion'])}")
        if necesidades['montos']['retiro'] > 0:
            recomendaciones.append(f"• Retiro: Plan de ahorro con {formatear_moneda(retiro.get('ahorro_mensual_sugerido', 0))} mensuales")
        if necesidades['montos']['educacion'] > 0:
            recomendaciones.append(f"• Educación: Inversión de {formatear_moneda(st.session_state.datos['educacion'].get('ahorro_mensual_total', 0))} mensuales")
        if necesidades['montos']['ahorro'] > 0:
            recomendaciones.append(f"• Proyecto: Ahorro de {formatear_moneda(st.session_state.datos['ahorro'].get('ahorro_mensual_sugerido', 0))} mensuales")
        
        for rec in recomendaciones:
            story.append(Paragraph(rec, styles['Normal']))
            story.append(Spacer(1, 5))
        
        # Footer
        story.append(Spacer(1, 30))
        footer = Paragraph(
            f"Reporte generado: {datetime.now().strftime('%d/%m/%Y %H:%M')} | Asesoría Financiera Rizkora",
            ParagraphStyle('Footer', parent=styles['Normal'], fontSize=8, textColor=pdf_colors.grey, alignment=1)
        )
        story.append(footer)
        
        # Construir PDF
        doc.build(story)
        buffer.seek(0)
        
        return buffer
    
    except Exception as e:
        st.error(f"Error al generar PDF: {str(e)}")
        return None

def generar_graficos_necesidades():
    """Genera gráficos de distribución de necesidades"""
    try:
        necesidades = detectar_necesidades()
        
        # Filtrar solo necesidades con monto > 0
        labels = []
        valores = []
        colores = []
        
        color_map = {
            'proteccion': COLORES['azul_principal'],
            'retiro': COLORES['verde_oscuro'],
            'educacion': COLORES['verde_agua'],
            'ahorro': COLORES['amarillo']
        }
        
        nombre_map = {
            'proteccion': 'Protección',
            'retiro': 'Retiro',
            'educacion': 'Educación',
            'ahorro': 'Ahorro/Proyecto'
        }
        
        for key, valor in necesidades['montos'].items():
            if valor > 0:
                labels.append(nombre_map[key])
                valores.append(valor)
                colores.append(color_map[key])
        
        if not valores:
            return None
        
        # Crear gráfico de pastel
        fig, ax = plt.subplots(figsize=(10, 6))
        wedges, texts, autotexts = ax.pie(
            valores,
            labels=labels,
            colors=colores,
            autopct='%1.1f%%',
            startangle=90,
            textprops={'fontsize': 11, 'weight': 'bold'}
        )
        
        ax.set_title('Distribución de Necesidades Financieras', 
                    fontsize=14, 
                    fontweight='bold',
                    color=COLORES['azul_principal'],
                    pad=20)
        
        # Mejorar estilo
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontsize(10)
            autotext.set_weight('bold')
        
        plt.tight_layout()
        
        # Guardar en buffer
        buffer = BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        plt.close(fig)
        
        return buffer
        
    except Exception as e:
        st.error(f"Error al generar gráfico: {str(e)}")
        return None

def detectar_necesidades():
    """Detecta y prioriza necesidades financieras"""
    necesidades = {
        'proteccion': 0,
        'retiro': 0,
        'educacion': 0,
        'ahorro': 0
    }
    
    # Protección (si tiene dependientes)
    if st.session_state.datos['perfil_familiar'].get('tiene_pareja') or \
       st.session_state.datos['perfil_familiar'].get('tiene_hijos') or \
       st.session_state.datos['perfil_familiar'].get('tiene_dependientes'):
        necesidades['proteccion'] = st.session_state.datos['proteccion'].get('monto_proteccion_sugerido', 0)
    
    # Retiro
    necesidades['retiro'] = st.session_state.datos['retiro'].get('monto_total_retiro', 0)
    
    # Educación
    necesidades['educacion'] = st.session_state.datos['educacion'].get('monto_total_educacion', 0)
    
    # Ahorro/Proyecto
    necesidades['ahorro'] = st.session_state.datos['ahorro'].get('inversion_requerida', 0)
    
    # Ordenar por prioridad (mayor monto)
    necesidades_ordenadas = sorted(necesidades.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'principal': necesidades_ordenadas[0][0] if necesidades_ordenadas[0][1] > 0 else 'ninguna',
        'montos': necesidades,
        'prioridades': necesidades_ordenadas
    }

# ================================
# BARRA LATERAL DE NAVEGACIÓN
# ================================
with st.sidebar:
    st.title("📊 Asesoría Financiera")
    st.markdown("---")
    
    # Progreso
    progreso = (st.session_state.step - 1) / 9 * 100
    st.progress(progreso / 100)
    st.write(f"Paso {st.session_state.step} de 9")
    
    st.markdown("---")
    
    # Menú de navegación
    st.subheader("Navegación")
    
    pasos = [
        "1️⃣ Datos Generales",
        "2️⃣ Perfil Familiar",
        "3️⃣ Ingresos",
        "4️⃣ Protección",
        "5️⃣ Ahorro/Proyectos",
        "6️⃣ Retiro",
        "7️⃣ Educación",
        "8️⃣ Resumen",
        "9️⃣ Cierre"
    ]
    
    for i, paso in enumerate(pasos, 1):
        if st.button(paso, key=f"nav_{i}", use_container_width=True, 
                     disabled=(i > st.session_state.step),
                     type="secondary" if i != st.session_state.step else "primary"):
            navegar_a_paso(i)
    
    st.markdown("---")
    
    # Información del agente
    if st.session_state.datos['datos_generales'].get('nombre_agente'):
        st.info(f"**Agente:** {st.session_state.datos['datos_generales']['nombre_agente']}")
    
    # Botón de exportar (solo si completó al menos paso 8)
    if st.session_state.step >= 8:
        st.markdown("---")
        st.subheader("💾 Exportar")
        
        # JSON
        if st.button("📥 Descargar JSON", use_container_width=True):
            json_data = exportar_json()
            st.download_button(
                label="📄 Descargar JSON",
                data=json_data,
                file_name=f"asesoria_{st.session_state.datos['datos_generales'].get('nombre', 'cliente')}_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        # PDF
        if st.button("📑 Generar PDF", use_container_width=True):
            with st.spinner("Generando PDF..."):
                pdf_buffer = generar_pdf_asesoria()
                if pdf_buffer:
                    st.download_button(
                        label="📥 Descargar PDF",
                        data=pdf_buffer,
                        file_name=f"asesoria_{st.session_state.datos['datos_generales'].get('nombre', 'cliente').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
        
        # Google Sheets
        if st.session_state.google_sheets_habilitado:
            if st.button("☁️ Guardar en Sheets", use_container_width=True):
                with st.spinner("Guardando en Google Sheets..."):
                    exito, mensaje = guardar_asesoria_sheets(st.session_state.datos)
                    if exito:
                        st.success(mensaje)
                    else:
                        st.error(mensaje)
        else:
            st.info("ℹ️ Google Sheets no configurado")

# ================================
# CONTENIDO PRINCIPAL
# ================================
st.title("🎯 Asesoría Financiera Integral Rizkora")

# ================================
# PASO 1: DATOS GENERALES
# ================================
if st.session_state.step == 1:
    st.header("1️⃣ Datos Generales")
    
    with st.form("form_datos_generales"):
        col1, col2 = st.columns(2)
        
        with col1:
            nombre = st.text_input("Nombre completo*", 
                                  value=st.session_state.datos['datos_generales'].get('nombre', ''))
            telefono = st.text_input("Teléfono* (10 dígitos)", 
                                    value=st.session_state.datos['datos_generales'].get('telefono', ''),
                                    placeholder="5512345678")
            correo = st.text_input("Correo electrónico*", 
                                  value=st.session_state.datos['datos_generales'].get('correo', ''),
                                  placeholder="ejemplo@email.com")
            ocupacion = st.text_input("Ocupación*", 
                                     value=st.session_state.datos['datos_generales'].get('ocupacion', ''))
        
        with col2:
            estado_civil = st.selectbox("Estado civil*", 
                                       ["", "Soltero", "Casado", "Unión libre", "Divorciado", "Viudo"],
                                       index=["", "Soltero", "Casado", "Unión libre", "Divorciado", "Viudo"].index(
                                           st.session_state.datos['datos_generales'].get('estado_civil', '')))
            
            fecha_nacimiento = st.date_input("Fecha de nacimiento*",
                                            value=st.session_state.datos['datos_generales'].get('fecha_nacimiento', date.today()),
                                            min_value=date(1920, 1, 1),
                                            max_value=date.today())
            
            fumador = st.radio("¿Ha fumado en los últimos 2 años?*", 
                              ["Sí", "No"],
                              index=0 if st.session_state.datos['datos_generales'].get('fumador') == "Sí" else 1)
            
            tipo_cita = st.radio("Tipo de cita*", 
                               ["Presencial", "Virtual"],
                               index=0 if st.session_state.datos['datos_generales'].get('tipo_cita') == "Presencial" else 1)
        
        col3, col4 = st.columns(2)
        with col3:
            nombre_agente = st.text_input("Nombre del agente*", 
                                         value=st.session_state.datos['datos_generales'].get('nombre_agente', ''))
        with col4:
            fecha_asesoria = st.date_input("Fecha de asesoría*",
                                          value=st.session_state.datos['datos_generales'].get('fecha_asesoria', date.today()))
        
        # Mostrar edad calculada en tiempo real
        edad_calculada = None
        if fecha_nacimiento:
            edad_calculada = calcular_edad(fecha_nacimiento)
            if edad_calculada:
                st.success(f"✅ Edad calculada: **{edad_calculada} años**")
        
        submitted = st.form_submit_button("➡️ Siguiente", type="primary", use_container_width=True)
        
        if submitted:
            errores = []
            
            # Validaciones
            if not nombre.strip():
                errores.append("El nombre es obligatorio")
            if not telefono.strip() or not validar_telefono(telefono):
                errores.append("El teléfono debe tener 10 dígitos")
            if not correo.strip() or not validar_email(correo):
                errores.append("El correo electrónico no es válido")
            if not ocupacion.strip():
                errores.append("La ocupación es obligatoria")
            if not estado_civil:
                errores.append("El estado civil es obligatorio")
            if not nombre_agente.strip():
                errores.append("El nombre del agente es obligatorio")
            
            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                # Guardar datos
                st.session_state.datos['datos_generales'] = {
                    'nombre': nombre.strip(),
                    'telefono': telefono.strip(),
                    'correo': correo.strip(),
                    'ocupacion': ocupacion.strip(),
                    'estado_civil': estado_civil,
                    'fecha_nacimiento': fecha_nacimiento,
                    'edad': calcular_edad(fecha_nacimiento),
                    'fumador': fumador,
                    'tipo_cita': tipo_cita,
                    'nombre_agente': nombre_agente.strip(),
                    'fecha_asesoria': fecha_asesoria
                }
                
                st.success("✅ Datos guardados correctamente")
                navegar_a_paso(2)

# ================================
# PASO 2: PERFIL FAMILIAR
# ================================
elif st.session_state.step == 2:
    st.header("2️⃣ Perfil Familiar")
    
    with st.form("form_perfil_familiar"):
        # Pareja
        tiene_pareja = st.radio("¿Tienes pareja?*", ["Sí", "No"],
                               index=0 if st.session_state.datos['perfil_familiar'].get('tiene_pareja') == "Sí" else 1)
        
        nombre_pareja = ""
        edad_pareja = None
        if tiene_pareja == "Sí":
            col1, col2 = st.columns(2)
            with col1:
                nombre_pareja = st.text_input("Nombre de tu pareja", 
                                             value=st.session_state.datos['perfil_familiar'].get('nombre_pareja', ''))
            with col2:
                edad_pareja = st.number_input("Edad de tu pareja", 
                                            min_value=18, max_value=100, 
                                            value=st.session_state.datos['perfil_familiar'].get('edad_pareja', 30))
        
        # Hijos
        tiene_hijos = st.radio("¿Tienes hijos?*", ["Sí", "No"],
                              index=0 if st.session_state.datos['perfil_familiar'].get('tiene_hijos') == "Sí" else 1)
        
        hijos = []
        if tiene_hijos == "Sí":
            num_hijos = st.number_input("¿Cuántos hijos tienes?", 
                                       min_value=1, max_value=10, 
                                       value=st.session_state.datos['perfil_familiar'].get('num_hijos', 1))
            
            st.subheader("Información de hijos")
            hijos_previos = st.session_state.datos['perfil_familiar'].get('hijos', [])
            
            for i in range(num_hijos):
                col1, col2 = st.columns(2)
                with col1:
                    nombre_hijo = st.text_input(f"Nombre hijo(a) {i+1}", 
                                               value=hijos_previos[i]['nombre'] if i < len(hijos_previos) else '',
                                               key=f"nombre_hijo_{i}")
                with col2:
                    edad_hijo = st.number_input(f"Edad hijo(a) {i+1}", 
                                              min_value=0, max_value=50,
                                              value=hijos_previos[i]['edad'] if i < len(hijos_previos) else 0,
                                              key=f"edad_hijo_{i}")
                hijos.append({'nombre': nombre_hijo, 'edad': edad_hijo})
        
        # Otros dependientes
        tiene_dependientes = st.radio("¿Tienes otro dependiente económico?*", ["Sí", "No"],
                                     index=0 if st.session_state.datos['perfil_familiar'].get('tiene_dependientes') == "Sí" else 1)
        
        dependientes = []
        if tiene_dependientes == "Sí":
            num_dependientes = st.number_input("¿Cuántos dependientes?", 
                                              min_value=1, max_value=5, 
                                              value=st.session_state.datos['perfil_familiar'].get('num_dependientes', 1))
            
            st.subheader("Información de dependientes")
            dependientes_previos = st.session_state.datos['perfil_familiar'].get('dependientes', [])
            
            for i in range(num_dependientes):
                col1, col2 = st.columns(2)
                with col1:
                    nombre_dep = st.text_input(f"Nombre dependiente {i+1}", 
                                              value=dependientes_previos[i]['nombre'] if i < len(dependientes_previos) else '',
                                              key=f"nombre_dep_{i}")
                with col2:
                    edad_dep = st.number_input(f"Edad dependiente {i+1}", 
                                             min_value=0, max_value=100,
                                             value=dependientes_previos[i]['edad'] if i < len(dependientes_previos) else 0,
                                             key=f"edad_dep_{i}")
                dependientes.append({'nombre': nombre_dep, 'edad': edad_dep})
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("⬅️ Anterior", use_container_width=True):
                navegar_a_paso(1)
        with col2:
            submitted = st.form_submit_button("➡️ Siguiente", type="primary", use_container_width=True)
        
        if submitted:
            # Guardar datos
            st.session_state.datos['perfil_familiar'] = {
                'tiene_pareja': tiene_pareja,
                'nombre_pareja': nombre_pareja if tiene_pareja == "Sí" else '',
                'edad_pareja': edad_pareja if tiene_pareja == "Sí" else None,
                'tiene_hijos': tiene_hijos,
                'num_hijos': len(hijos) if tiene_hijos == "Sí" else 0,
                'hijos': hijos if tiene_hijos == "Sí" else [],
                'tiene_dependientes': tiene_dependientes,
                'num_dependientes': len(dependientes) if tiene_dependientes == "Sí" else 0,
                'dependientes': dependientes if tiene_dependientes == "Sí" else []
            }
            
            st.success("✅ Perfil familiar guardado")
            navegar_a_paso(3)

# ================================
# PASO 3: INGRESOS Y CAPACIDAD
# ================================
elif st.session_state.step == 3:
    st.header("3️⃣ Ingresos y Capacidad Financiera")
    
    with st.form("form_ingresos"):
        ingreso_mensual = st.number_input("Ingreso mensual neto*", 
                                         min_value=0.0, 
                                         value=float(st.session_state.datos['ingresos'].get('ingreso_mensual', 0)),
                                         step=1000.0,
                                         format="%.2f")
        
        if ingreso_mensual > 0:
            ingreso_anual = ingreso_mensual * 12
            ahorro_ideal_10 = ingreso_anual * 0.10
            ahorro_conservador_7 = ingreso_mensual * 0.07
            
            st.markdown("---")
            st.subheader("📊 Análisis Automático")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Ingreso Anual", formatear_moneda(ingreso_anual))
            with col2:
                st.metric("Ahorro Ideal (10% anual)", formatear_moneda(ahorro_ideal_10))
            with col3:
                st.metric("Ahorro Conservador (7% mensual)", formatear_moneda(ahorro_conservador_7))
            
            st.info(f"""
            💡 **Recomendación:**
            - Para una salud financiera óptima, considera ahorrar al menos el **7% de tu ingreso mensual** ({formatear_moneda(ahorro_conservador_7)})
            - Idealmente, apunta al **10% anual** ({formatear_moneda(ahorro_ideal_10)})
            """)
        
        st.markdown("---")
        
        inversion_mensual = st.number_input(
            "¿Cuánto estarías dispuesto a invertir mensualmente si el plan coincide contigo?*", 
            min_value=0.0,
            value=float(st.session_state.datos['ingresos'].get('inversion_mensual', 0)),
            step=100.0,
            format="%.2f"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("⬅️ Anterior", use_container_width=True):
                navegar_a_paso(2)
        with col2:
            submitted = st.form_submit_button("➡️ Siguiente", type="primary", use_container_width=True)
        
        if submitted:
            if ingreso_mensual <= 0:
                st.error("❌ El ingreso mensual debe ser mayor a 0")
            else:
                # Guardar datos
                st.session_state.datos['ingresos'] = {
                    'ingreso_mensual': ingreso_mensual,
                    'ingreso_anual': ingreso_mensual * 12,
                    'ahorro_ideal_10': ingreso_mensual * 12 * 0.10,
                    'ahorro_conservador_7': ingreso_mensual * 0.07,
                    'inversion_mensual': inversion_mensual
                }
                
                st.success("✅ Información financiera guardada")
                navegar_a_paso(4)

# ================================
# PASO 4: PROTECCIÓN FINANCIERA
# ================================
elif st.session_state.step == 4:
    st.header("4️⃣ Protección Financiera")
    
    # Verificar si tiene dependientes
    tiene_dependientes = (
        st.session_state.datos['perfil_familiar'].get('tiene_pareja') == "Sí" or
        st.session_state.datos['perfil_familiar'].get('tiene_hijos') == "Sí" or
        st.session_state.datos['perfil_familiar'].get('tiene_dependientes') == "Sí"
    )
    
    if not tiene_dependientes:
        st.info("✅ No tienes dependientes económicos registrados. Esta sección se omitirá.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Anterior", use_container_width=True):
                navegar_a_paso(3)
        with col2:
            if st.button("➡️ Siguiente", type="primary", use_container_width=True):
                st.session_state.datos['proteccion'] = {
                    'aplica': False
                }
                navegar_a_paso(5)
    else:
        with st.form("form_proteccion"):
            st.write("""
            La protección financiera asegura que tu familia pueda mantener su nivel de vida 
            en caso de fallecimiento, invalidez o enfermedad grave.
            """)
            
            reflexion = st.text_area(
                "¿Qué pasaría con tu familia si fallecieras, tuvieras invalidez o enfermedad grave?",
                value=st.session_state.datos['proteccion'].get('reflexion', ''),
                height=100
            )
            
            st.subheader("Personas Responsables")
            col1, col2 = st.columns(2)
            with col1:
                responsable1 = st.text_input("Responsable 1", 
                                            value=st.session_state.datos['proteccion'].get('responsable1', ''))
            with col2:
                responsable2 = st.text_input("Responsable 2 (opcional)", 
                                            value=st.session_state.datos['proteccion'].get('responsable2', ''))
            
            presupuesto_mensual = st.number_input(
                "¿Cuál es el presupuesto mensual requerido para mantener a tu familia?*",
                min_value=0.0,
                value=float(st.session_state.datos['proteccion'].get('presupuesto_mensual', 0)),
                step=1000.0,
                format="%.2f"
            )
            
            if presupuesto_mensual > 0:
                presupuesto_anual = presupuesto_mensual * 12
                monto_proteccion = presupuesto_anual * 10  # 10 años de protección
                
                st.markdown("---")
                st.subheader("📊 Cálculo de Protección")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Presupuesto Mensual", formatear_moneda(presupuesto_mensual))
                with col2:
                    st.metric("Presupuesto Anual", formatear_moneda(presupuesto_anual))
                with col3:
                    st.metric("Protección Sugerida (10 años)", formatear_moneda(monto_proteccion))
                
                st.success(f"""
                💡 **Recomendación de Protección:**
                Se sugiere una protección de **{formatear_moneda(monto_proteccion)}** para cubrir 10 años 
                del presupuesto familiar en caso de contingencia.
                """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("⬅️ Anterior", use_container_width=True):
                    navegar_a_paso(3)
            with col2:
                submitted = st.form_submit_button("➡️ Siguiente", type="primary", use_container_width=True)
            
            if submitted:
                if presupuesto_mensual <= 0:
                    st.error("❌ El presupuesto mensual debe ser mayor a 0")
                elif not responsable1.strip():
                    st.error("❌ Debe indicar al menos un responsable")
                else:
                    # Guardar datos
                    st.session_state.datos['proteccion'] = {
                        'aplica': True,
                        'reflexion': reflexion,
                        'responsable1': responsable1.strip(),
                        'responsable2': responsable2.strip() if responsable2 else '',
                        'presupuesto_mensual': presupuesto_mensual,
                        'presupuesto_anual': presupuesto_mensual * 12,
                        'monto_proteccion_sugerido': presupuesto_mensual * 12 * 10
                    }
                    
                    st.success("✅ Protección financiera configurada")
                    navegar_a_paso(5)

# ================================
# PASO 5: AHORRO / CRISIS / PROYECTOS
# ================================
elif st.session_state.step == 5:
    st.header("5️⃣ Ahorro / Crisis / Proyectos")
    
    with st.form("form_ahorro"):
        preparado_crisis = st.radio(
            "¿Estás preparado para una crisis financiera?*",
            ["Sí", "No", "Parcialmente"],
            index=["Sí", "No", "Parcialmente"].index(st.session_state.datos['ahorro'].get('preparado_crisis', 'No'))
        )
        
        if preparado_crisis in ["No", "Parcialmente"]:
            st.info("""
            💡 **Recomendación:**
            Es importante contar con un fondo de emergencia equivalente a 3-6 meses de tus gastos mensuales.
            """)
        
        st.markdown("---")
        st.subheader("Proyectos a Mediano/Largo Plazo")
        
        tiene_proyecto = st.radio("¿Tienes un proyecto a mediano o largo plazo?*", ["Sí", "No"],
                                 index=0 if st.session_state.datos['ahorro'].get('tiene_proyecto') == "Sí" else 1)
        
        proyecto_info = {}
        if tiene_proyecto == "Sí":
            descripcion_proyecto = st.text_input("Describe tu proyecto", 
                                                value=st.session_state.datos['ahorro'].get('descripcion_proyecto', ''),
                                                placeholder="Ej: Comprar casa, iniciar negocio, viaje...")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                costo_proyecto = st.number_input("Costo estimado del proyecto*", 
                                                min_value=0.0,
                                                value=float(st.session_state.datos['ahorro'].get('costo_proyecto', 0)),
                                                step=10000.0,
                                                format="%.2f")
            with col2:
                ahorro_actual = st.number_input("Ahorro actual disponible", 
                                               min_value=0.0,
                                               value=float(st.session_state.datos['ahorro'].get('ahorro_actual', 0)),
                                               step=1000.0,
                                               format="%.2f")
            with col3:
                plazo_anos = st.number_input("Plazo en años*", 
                                            min_value=1, max_value=30,
                                            value=st.session_state.datos['ahorro'].get('plazo_anos', 5))
            
            if costo_proyecto > 0 and plazo_anos > 0:
                inversion_requerida = max(0, costo_proyecto - ahorro_actual)
                ahorro_mensual_sugerido = inversion_requerida / (plazo_anos * 12)
                
                st.markdown("---")
                st.subheader("📊 Cálculo del Proyecto")
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Costo Total", formatear_moneda(costo_proyecto))
                with col2:
                    st.metric("Inversión Requerida", formatear_moneda(inversion_requerida))
                with col3:
                    st.metric("Ahorro Mensual Sugerido", formatear_moneda(ahorro_mensual_sugerido))
                
                proyecto_info = {
                    'descripcion': descripcion_proyecto,
                    'costo': costo_proyecto,
                    'ahorro_actual': ahorro_actual,
                    'plazo_anos': plazo_anos,
                    'inversion_requerida': inversion_requerida,
                    'ahorro_mensual_sugerido': ahorro_mensual_sugerido
                }
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("⬅️ Anterior", use_container_width=True):
                navegar_a_paso(4)
        with col2:
            submitted = st.form_submit_button("➡️ Siguiente", type="primary", use_container_width=True)
        
        if submitted:
            errores = []
            
            if tiene_proyecto == "Sí":
                if not descripcion_proyecto.strip():
                    errores.append("Describe tu proyecto")
                if costo_proyecto <= 0:
                    errores.append("El costo del proyecto debe ser mayor a 0")
                if plazo_anos <= 0:
                    errores.append("El plazo debe ser mayor a 0")
            
            if errores:
                for error in errores:
                    st.error(f"❌ {error}")
            else:
                # Guardar datos
                st.session_state.datos['ahorro'] = {
                    'preparado_crisis': preparado_crisis,
                    'tiene_proyecto': tiene_proyecto,
                    **proyecto_info
                }
                
                st.success("✅ Información de ahorro guardada")
                navegar_a_paso(6)

# ================================
# PASO 6: RETIRO
# ================================
elif st.session_state.step == 6:
    st.header("6️⃣ Retiro")
    
    edad_actual = st.session_state.datos['datos_generales'].get('edad', 30)
    
    with st.form("form_retiro"):
        st.write(f"**Tu edad actual:** {edad_actual} años")
        
        edad_retiro = st.number_input("¿A qué edad te gustaría retirarte?*", 
                                     min_value=edad_actual + 1, 
                                     max_value=80,
                                     value=st.session_state.datos['retiro'].get('edad_retiro', 65))
        
        ingreso_mensual_retiro = st.number_input(
            "¿Cuánto te gustaría recibir mensualmente en el retiro?*",
            min_value=0.0,
            value=float(st.session_state.datos['retiro'].get('ingreso_mensual_retiro', 0)),
            step=1000.0,
            format="%.2f"
        )
        
        if ingreso_mensual_retiro > 0 and edad_retiro > edad_actual:
            anos_para_retiro = edad_retiro - edad_actual
            anos_en_retiro = 80 - edad_retiro  # Esperanza de vida 80 años
            
            monto_anual_retiro = ingreso_mensual_retiro * 12
            monto_total_retiro = monto_anual_retiro * anos_en_retiro
            
            # Cálculo simplificado de ahorro mensual requerido
            # (sin considerar inflación ni rendimientos para simplicidad)
            ahorro_mensual_retiro = monto_total_retiro / (anos_para_retiro * 12)
            
            st.markdown("---")
            st.subheader("📊 Proyección de Retiro")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Años para el retiro", f"{anos_para_retiro} años")
                st.metric("Años en retiro", f"{anos_en_retiro} años")
                st.metric("Ingreso anual deseado", formatear_moneda(monto_anual_retiro))
            
            with col2:
                st.metric("Monto total requerido", formatear_moneda(monto_total_retiro))
                st.metric("Ahorro mensual sugerido", formatear_moneda(ahorro_mensual_retiro))
            
            st.info(f"""
            💡 **Proyección de Retiro:**
            - Te faltan **{anos_para_retiro} años** para retirarte
            - Vivirás aproximadamente **{anos_en_retiro} años** en retiro
            - Necesitarás un total de **{formatear_moneda(monto_total_retiro)}**
            - Se sugiere ahorrar **{formatear_moneda(ahorro_mensual_retiro)}** mensuales
            
            *Nota: Este es un cálculo simplificado. Se recomienda una asesoría detallada considerando inflación y rendimientos.*
            """)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("⬅️ Anterior", use_container_width=True):
                navegar_a_paso(5)
        with col2:
            submitted = st.form_submit_button("➡️ Siguiente", type="primary", use_container_width=True)
        
        if submitted:
            if ingreso_mensual_retiro <= 0:
                st.error("❌ El ingreso mensual de retiro debe ser mayor a 0")
            elif edad_retiro <= edad_actual:
                st.error("❌ La edad de retiro debe ser mayor a tu edad actual")
            else:
                # Guardar datos
                anos_para_retiro = edad_retiro - edad_actual
                anos_en_retiro = max(1, 80 - edad_retiro)
                monto_total = ingreso_mensual_retiro * 12 * anos_en_retiro
                
                st.session_state.datos['retiro'] = {
                    'edad_retiro': edad_retiro,
                    'ingreso_mensual_retiro': ingreso_mensual_retiro,
                    'anos_para_retiro': anos_para_retiro,
                    'anos_en_retiro': anos_en_retiro,
                    'monto_anual_retiro': ingreso_mensual_retiro * 12,
                    'monto_total_retiro': monto_total,
                    'ahorro_mensual_sugerido': monto_total / max(1, anos_para_retiro * 12)
                }
                
                st.success("✅ Plan de retiro configurado")
                navegar_a_paso(7)

# ================================
# PASO 7: EDUCACIÓN
# ================================
elif st.session_state.step == 7:
    st.header("7️⃣ Educación")
    
    tiene_hijos = st.session_state.datos['perfil_familiar'].get('tiene_hijos') == "Sí"
    
    if not tiene_hijos:
        st.info("✅ No tienes hijos registrados. Esta sección se omitirá.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Anterior", use_container_width=True):
                navegar_a_paso(6)
        with col2:
            if st.button("➡️ Siguiente", type="primary", use_container_width=True):
                st.session_state.datos['educacion'] = {
                    'aplica': False,
                    'monto_total_educacion': 0
                }
                navegar_a_paso(8)
    else:
        hijos = st.session_state.datos['perfil_familiar'].get('hijos', [])
        
        with st.form("form_educacion"):
            st.write("Planifica la educación universitaria de tus hijos")
            
            educacion_hijos = []
            monto_total_educacion = 0
            
            for i, hijo in enumerate(hijos):
                st.subheader(f"👤 {hijo['nombre']} ({hijo['edad']} años)")
                
                col1, col2 = st.columns(2)
                with col1:
                    costo_anual_universidad = st.number_input(
                        f"Costo anual estimado de universidad",
                        min_value=0.0,
                        value=float(st.session_state.datos['educacion'].get(f'costo_hijo_{i}', 100000)),
                        step=10000.0,
                        format="%.2f",
                        key=f"costo_univ_{i}"
                    )
                
                with col2:
                    edad_universidad = 18
                    anos_restantes = max(0, edad_universidad - hijo['edad'])
                    st.metric("Años hasta universidad", f"{anos_restantes} años")
                
                # Calcular costo total (4 años de universidad)
                costo_total_hijo = costo_anual_universidad * 4
                
                # Ahorro mensual sugerido
                if anos_restantes > 0:
                    ahorro_mensual_hijo = costo_total_hijo / (anos_restantes * 12)
                else:
                    ahorro_mensual_hijo = costo_anual_universidad / 12
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Costo total estimado (4 años)", formatear_moneda(costo_total_hijo))
                with col2:
                    st.metric("Ahorro mensual sugerido", formatear_moneda(ahorro_mensual_hijo))
                
                educacion_hijos.append({
                    'nombre': hijo['nombre'],
                    'edad': hijo['edad'],
                    'costo_anual': costo_anual_universidad,
                    'anos_restantes': anos_restantes,
                    'costo_total': costo_total_hijo,
                    'ahorro_mensual': ahorro_mensual_hijo
                })
                
                monto_total_educacion += costo_total_hijo
                
                st.markdown("---")
            
            # Resumen total
            st.subheader("📊 Resumen Total de Educación")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Inversión Total en Educación", formatear_moneda(monto_total_educacion))
            with col2:
                ahorro_mensual_total = sum([h['ahorro_mensual'] for h in educacion_hijos])
                st.metric("Ahorro Mensual Total Sugerido", formatear_moneda(ahorro_mensual_total))
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("⬅️ Anterior", use_container_width=True):
                    navegar_a_paso(6)
            with col2:
                submitted = st.form_submit_button("➡️ Siguiente", type="primary", use_container_width=True)
            
            if submitted:
                # Guardar datos
                st.session_state.datos['educacion'] = {
                    'aplica': True,
                    'hijos': educacion_hijos,
                    'monto_total_educacion': monto_total_educacion,
                    'ahorro_mensual_total': sum([h['ahorro_mensual'] for h in educacion_hijos])
                }
                
                st.success("✅ Plan educativo configurado")
                navegar_a_paso(8)

# ================================
# PASO 8: RESUMEN Y NECESIDADES
# ================================
elif st.session_state.step == 8:
    st.header("8️⃣ Resumen y Detección de Necesidades")
    
    # Detectar necesidades
    necesidades = detectar_necesidades()
    
    # Información del cliente
    st.subheader("👤 Información del Cliente")
    datos_gen = st.session_state.datos['datos_generales']
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"**Nombre:** {datos_gen.get('nombre')}")
        st.write(f"**Edad:** {datos_gen.get('edad')} años")
        st.write(f"**Ocupación:** {datos_gen.get('ocupacion')}")
    with col2:
        st.write(f"**Estado Civil:** {datos_gen.get('estado_civil')}")
        st.write(f"**Teléfono:** {datos_gen.get('telefono')}")
        st.write(f"**Correo:** {datos_gen.get('correo')}")
    with col3:
        st.write(f"**Fumador:** {datos_gen.get('fumador')}")
        st.write(f"**Tipo de Cita:** {datos_gen.get('tipo_cita')}")
        st.write(f"**Agente:** {datos_gen.get('nombre_agente')}")
    
    st.markdown("---")
    
    # Necesidad Principal
    st.subheader("🎯 Necesidad Principal Detectada")
    
    necesidad_principal = necesidades['principal']
    if necesidad_principal == 'proteccion':
        st.error("🛡️ **PROTECCIÓN FINANCIERA**")
        st.write("Tu familia necesita protección en caso de contingencia.")
    elif necesidad_principal == 'retiro':
        st.warning("👴 **RETIRO**")
        st.write("Es prioritario planificar tu retiro para asegurar tu futuro.")
    elif necesidad_principal == 'educacion':
        st.info("🎓 **EDUCACIÓN**")
        st.write("La educación de tus hijos requiere planificación financiera.")
    elif necesidad_principal == 'ahorro':
        st.success("💰 **AHORRO/PROYECTO**")
        st.write("Tu proyecto requiere un plan de ahorro estructurado.")
    else:
        st.info("ℹ️ No se detectaron necesidades específicas prioritarias.")
    
    st.markdown("---")
    
    # Tabla de montos
    st.subheader("💰 Montos Estimados por Pilar")
    
    datos_tabla = {
        'Pilar': ['Protección', 'Retiro', 'Educación', 'Ahorro/Proyecto'],
        'Monto Estimado': [
            formatear_moneda(necesidades['montos']['proteccion']),
            formatear_moneda(necesidades['montos']['retiro']),
            formatear_moneda(necesidades['montos']['educacion']),
            formatear_moneda(necesidades['montos']['ahorro'])
        ],
        'Prioridad': []
    }
    
    # Asignar prioridades
    for pilar in datos_tabla['Pilar']:
        pilar_key = pilar.lower().replace('/', '').replace(' ', '').replace('proyecto', '')
        if pilar_key == 'ahorroproyecto':
            pilar_key = 'ahorro'
        
        # Buscar en prioridades
        encontrado = False
        for idx, (p, m) in enumerate(necesidades['prioridades'], 1):
            if p == pilar_key:
                datos_tabla['Prioridad'].append(f"#{idx}")
                encontrado = True
                break
        
        if not encontrado:
            datos_tabla['Prioridad'].append("-")
    
    df_resumen = pd.DataFrame(datos_tabla)
    st.dataframe(df_resumen, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Capacidad vs Necesidad
    st.subheader("📊 Análisis de Capacidad")
    
    inversion_mensual = st.session_state.datos['ingresos'].get('inversion_mensual', 0)
    ingreso_mensual = st.session_state.datos['ingresos'].get('ingreso_mensual', 0)
    
    # Calcular necesidad mensual total estimada
    necesidad_mensual_total = 0
    
    # Protección (estimado 2-5% del ingreso)
    if necesidades['montos']['proteccion'] > 0:
        necesidad_mensual_total += ingreso_mensual * 0.03
    
    # Retiro
    necesidad_mensual_total += st.session_state.datos['retiro'].get('ahorro_mensual_sugerido', 0)
    
    # Educación
    necesidad_mensual_total += st.session_state.datos['educacion'].get('ahorro_mensual_total', 0)
    
    # Proyecto
    if st.session_state.datos['ahorro'].get('tiene_proyecto') == "Sí":
        necesidad_mensual_total += st.session_state.datos['ahorro'].get('ahorro_mensual_sugerido', 0)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Inversión Mensual Disponible", formatear_moneda(inversion_mensual))
    with col2:
        st.metric("Necesidad Mensual Estimada", formatear_moneda(necesidad_mensual_total))
    with col3:
        brecha = inversion_mensual - necesidad_mensual_total
        st.metric("Brecha", formatear_moneda(brecha), 
                 delta="Superávit" if brecha >= 0 else "Déficit")
    
    if brecha < 0:
        st.warning(f"""
        ⚠️ **Atención:** Existe un déficit de {formatear_moneda(abs(brecha))} entre tu capacidad 
        de inversión y las necesidades detectadas. Se recomienda:
        - Priorizar las necesidades más urgentes
        - Considerar aumentar la capacidad de ahorro
        - Explorar opciones de inversión con mejores rendimientos
        """)
    else:
        st.success(f"""
        ✅ **Excelente:** Tu capacidad de inversión cubre las necesidades detectadas con un 
        margen de {formatear_moneda(brecha)}. Esto permite:
        - Cubrir todas las necesidades identificadas
        - Tener un margen de seguridad
        - Considerar objetivos adicionales
        """)
    
    st.markdown("---")
    
    # Recomendaciones
    st.subheader("📋 Recomendaciones para la Asesoría")
    
    recomendaciones = []
    
    if necesidades['montos']['proteccion'] > 0:
        recomendaciones.append(f"🛡️ **Protección:** Considerar un seguro de vida por {formatear_moneda(necesidades['montos']['proteccion'])}")
    
    if necesidades['montos']['retiro'] > 0:
        recomendaciones.append(f"👴 **Retiro:** Iniciar plan de retiro con ahorro mensual de {formatear_moneda(st.session_state.datos['retiro'].get('ahorro_mensual_sugerido', 0))}")
    
    if necesidades['montos']['educacion'] > 0:
        recomendaciones.append(f"🎓 **Educación:** Plan educativo que requiere {formatear_moneda(st.session_state.datos['educacion'].get('ahorro_mensual_total', 0))} mensuales")
    
    if necesidades['montos']['ahorro'] > 0:
        recomendaciones.append(f"💰 **Proyecto:** Ahorro sistemático de {formatear_moneda(st.session_state.datos['ahorro'].get('ahorro_mensual_sugerido', 0))} mensuales")
    
    if st.session_state.datos['ahorro'].get('preparado_crisis') in ["No", "Parcialmente"]:
        recomendaciones.append("🚨 **Fondo de Emergencia:** Crear fondo equivalente a 3-6 meses de gastos")
    
    for rec in recomendaciones:
        st.write(rec)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("⬅️ Anterior", use_container_width=True):
            navegar_a_paso(7)
    with col2:
        if st.button("➡️ Siguiente", type="primary", use_container_width=True):
            navegar_a_paso(9)

# ================================
# PASO 9: CIERRE
# ================================
elif st.session_state.step == 9:
    st.header("9️⃣ Cierre de la Asesoría")
    
    with st.form("form_cierre"):
        st.subheader("📝 Retroalimentación")
        
        satisfaccion = st.text_area(
            "¿Qué fue lo que más te agradó de esta asesoría?*",
            value=st.session_state.datos['cierre'].get('satisfaccion', ''),
            height=100
        )
        
        segunda_cita = st.radio("¿Te gustaría agendar una segunda cita?*", ["Sí", "No"],
                               index=0 if st.session_state.datos['cierre'].get('segunda_cita') == "Sí" else 1)
        
        fecha_segunda_cita = None
        hora_segunda_cita = None
        if segunda_cita == "Sí":
            col1, col2 = st.columns(2)
            with col1:
                fecha_segunda_cita = st.date_input("Fecha de segunda cita",
                                                   value=st.session_state.datos['cierre'].get('fecha_segunda_cita', date.today()),
                                                   min_value=date.today())
            with col2:
                hora_segunda_cita = st.time_input("Hora de segunda cita",
                                                 value=st.session_state.datos['cierre'].get('hora_segunda_cita'))
        
        st.markdown("---")
        st.subheader("👥 Referidos")
        st.write("¿Conoces a alguien que pudiera beneficiarse de una asesoría financiera?")
        
        num_referidos = st.number_input("¿Cuántos referidos tienes?", 
                                       min_value=0, max_value=5,
                                       value=st.session_state.datos['cierre'].get('num_referidos', 0))
        
        referidos = []
        referidos_previos = st.session_state.datos['cierre'].get('referidos', [])
        
        for i in range(num_referidos):
            st.write(f"**Referido {i+1}**")
            col1, col2 = st.columns(2)
            with col1:
                nombre_ref = st.text_input(f"Nombre", 
                                          value=referidos_previos[i]['nombre'] if i < len(referidos_previos) else '',
                                          key=f"nombre_ref_{i}")
                edad_ref = st.number_input(f"Edad", 
                                          min_value=18, max_value=100,
                                          value=referidos_previos[i]['edad'] if i < len(referidos_previos) else 30,
                                          key=f"edad_ref_{i}")
            with col2:
                parentesco_ref = st.text_input(f"Parentesco/Relación", 
                                              value=referidos_previos[i]['parentesco'] if i < len(referidos_previos) else '',
                                              placeholder="Ej: Hermano, Amigo, Compañero",
                                              key=f"parentesco_ref_{i}")
                comentarios_ref = st.text_area(f"Comentarios", 
                                              value=referidos_previos[i]['comentarios'] if i < len(referidos_previos) else '',
                                              key=f"comentarios_ref_{i}",
                                              height=60)
            
            referidos.append({
                'nombre': nombre_ref,
                'edad': edad_ref,
                'parentesco': parentesco_ref,
                'comentarios': comentarios_ref
            })
            
            st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("⬅️ Anterior", use_container_width=True):
                navegar_a_paso(8)
        with col2:
            submitted = st.form_submit_button("✅ Finalizar Asesoría", type="primary", use_container_width=True)
        
        if submitted:
            if not satisfaccion.strip():
                st.error("❌ Por favor comparte tu experiencia con la asesoría")
            else:
                # Guardar datos
                st.session_state.datos['cierre'] = {
                    'satisfaccion': satisfaccion,
                    'segunda_cita': segunda_cita,
                    'fecha_segunda_cita': fecha_segunda_cita,
                    'hora_segunda_cita': hora_segunda_cita,
                    'num_referidos': num_referidos,
                    'referidos': referidos
                }
                
                st.success("✅ ¡Asesoría completada exitosamente!")
                st.balloons()
                
                # Guardar automáticamente en Google Sheets si está habilitado
                if st.session_state.google_sheets_habilitado:
                    with st.spinner("Guardando en Google Sheets..."):
                        exito, mensaje = guardar_asesoria_sheets(st.session_state.datos)
                        if exito:
                            st.success(f"☁️ {mensaje}")
                        else:
                            st.warning(f"⚠️ {mensaje}")
                
                # Mostrar resumen final
                st.markdown("---")
                st.subheader("📊 Resumen Final")
                
                necesidades = detectar_necesidades()
                
                # Mostrar gráfico
                grafico_buffer = generar_graficos_necesidades()
                if grafico_buffer:
                    st.image(grafico_buffer, use_container_width=True)
                
                st.write(f"""
                **Cliente:** {st.session_state.datos['datos_generales'].get('nombre')}
                
                **Necesidad Principal:** {necesidades['principal'].upper()}
                
                **Próximos Pasos:**
                - Revisar propuestas específicas para las necesidades detectadas
                - {"Agendar segunda cita para el " + str(fecha_segunda_cita) if segunda_cita == "Sí" else "Dar seguimiento vía telefónica"}
                - {f"Contactar a {num_referidos} referido(s)" if num_referidos > 0 else ""}
                
                **Agente:** {st.session_state.datos['datos_generales'].get('nombre_agente')}
                **Fecha:** {st.session_state.datos['datos_generales'].get('fecha_asesoria')}
                """)
                
                # Botones de exportar
                st.markdown("---")
                st.subheader("💾 Descargar Reporte")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    json_data = exportar_json()
                    st.download_button(
                        label="📄 Descargar JSON",
                        data=json_data,
                        file_name=f"asesoria_{st.session_state.datos['datos_generales'].get('nombre', 'cliente').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                with col2:
                    pdf_buffer = generar_pdf_asesoria()
                    if pdf_buffer:
                        st.download_button(
                            label="📑 Descargar PDF",
                            data=pdf_buffer,
                            file_name=f"asesoria_{st.session_state.datos['datos_generales'].get('nombre', 'cliente').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                
                with col3:
                    if grafico_buffer:
                        st.download_button(
                            label="📊 Descargar Gráfico",
                            data=grafico_buffer,
                            file_name=f"grafico_necesidades_{datetime.now().strftime('%Y%m%d')}.png",
                            mime="image/png",
                            use_container_width=True
                        )
                
                # Botón para nueva asesoría
                st.markdown("---")
                st.subheader("🔄 Nueva Asesoría")
                
                # Mostrar advertencia y botón de confirmación
                if not st.session_state.confirmar_reinicio:
                    if st.button("🆕 Iniciar Nueva Asesoría", type="secondary", use_container_width=True):
                        st.session_state.confirmar_reinicio = True
                        st.rerun()
                else:
                    st.warning("⚠️ **¿Estás seguro?** Se perderán todos los datos de la asesoría actual.")
                    
                    col_confirm1, col_confirm2 = st.columns(2)
                    
                    with col_confirm1:
                        if st.button("✅ Sí, iniciar nueva", type="primary", use_container_width=True):
                            # Limpiar todos los datos
                            st.session_state.step = 1
                            st.session_state.datos = {
                                'datos_generales': {},
                                'perfil_familiar': {},
                                'ingresos': {},
                                'proteccion': {},
                                'ahorro': {},
                                'retiro': {},
                                'educacion': {},
                                'cierre': {}
                            }
                            st.session_state.confirmar_reinicio = False
                            st.success("✅ Datos limpiados. Iniciando nueva asesoría...")
                            st.rerun()
                    
                    with col_confirm2:
                        if st.button("❌ Cancelar", type="secondary", use_container_width=True):
                            st.session_state.confirmar_reinicio = False
                            st.rerun()

# ================================
# PIE DE PÁGINA
# ================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>Asesoría Financiera Rizkora © 2026 | Versión 2.0</p>
    <p>Esta herramienta es solo para fines de detección de necesidades. 
    No sustituye una asesoría financiera profesional completa.</p>
</div>
""", unsafe_allow_html=True)

