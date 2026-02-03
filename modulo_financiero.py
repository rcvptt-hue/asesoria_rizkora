# -*- coding: utf-8 -*-
"""
MÓDULO DE ANÁLISIS FINANCIERO MEJORADO
Para integración con Asesoría Financiera Rizkora

Este módulo contiene las funciones principales para el análisis de flujo financiero.
Puedes importar estas funciones en tu código principal.

Autor: Rizkora
Versión: 3.0
Fecha: 2026
"""

# ================================
# CONSTANTES
# ================================

COLORES_FINANCIEROS = {
    'rojo': '#ef5350',
    'amarillo': '#ff9800',
    'verde': '#66bb6a',
    'verde_agua': '#00bfa5',
    'azul': '#064c78'
}

# ================================
# FUNCIÓN PRINCIPAL: FLUJO FINANCIERO
# ================================

def calcular_flujo_financiero(ingreso_mensual, gastos_fijos, gastos_variables, deudas):
    """
    Calcula el flujo financiero completo del cliente con análisis detallado.
    
    Parameters:
    -----------
    ingreso_mensual : float
        Ingreso neto mensual del cliente
    gastos_fijos : dict
        Diccionario con categorías de gastos fijos
        Ejemplo: {'vivienda': 8000, 'servicios': 1500, ...}
    gastos_variables : dict
        Diccionario con categorías de gastos variables
        Ejemplo: {'entretenimiento': 2000, 'ropa': 1000, ...}
    deudas : dict
        Diccionario con pagos de deudas mensuales
        Ejemplo: {'tarjetas': 3000, 'prestamos': 2000, ...}
    
    Returns:
    --------
    dict : Análisis completo del flujo financiero
    
    Example:
    --------
    >>> gastos_fijos = {'vivienda': 8000, 'servicios': 1500}
    >>> gastos_variables = {'entretenimiento': 2000}
    >>> deudas = {'tarjetas': 1500}
    >>> resultado = calcular_flujo_financiero(25000, gastos_fijos, gastos_variables, deudas)
    >>> print(resultado['estado_financiero'])
    'saludable'
    """
    
    # Calcular totales
    total_gastos_fijos = sum(gastos_fijos.values()) if gastos_fijos else 0
    total_gastos_variables = sum(gastos_variables.values()) if gastos_variables else 0
    total_deudas = sum(deudas.values()) if deudas else 0
    
    gastos_totales = total_gastos_fijos + total_gastos_variables + total_deudas
    flujo_libre = ingreso_mensual - gastos_totales
    
    # Calcular porcentajes
    if ingreso_mensual > 0:
        porcentaje_flujo = (flujo_libre / ingreso_mensual) * 100
        porcentaje_gastos_fijos = (total_gastos_fijos / ingreso_mensual) * 100
        porcentaje_gastos_variables = (total_gastos_variables / ingreso_mensual) * 100
        porcentaje_deudas = (total_deudas / ingreso_mensual) * 100
    else:
        porcentaje_flujo = 0
        porcentaje_gastos_fijos = 0
        porcentaje_gastos_variables = 0
        porcentaje_deudas = 0
    
    # Determinar estado financiero con sistema de semáforo
    if flujo_libre < 0:
        estado = "negativo"
        color = COLORES_FINANCIEROS['rojo']
        semaforo = "🔴"
        mensaje = "URGENTE: Tus gastos superan tus ingresos"
    elif porcentaje_flujo < 10:
        estado = "crítico"
        color = COLORES_FINANCIEROS['rojo']
        semaforo = "🔴"
        mensaje = "ATENCIÓN: Tu margen financiero es muy ajustado"
    elif porcentaje_flujo < 20:
        estado = "ajustado"
        color = COLORES_FINANCIEROS['amarillo']
        semaforo = "🟡"
        mensaje = "PRECAUCIÓN: Tu margen financiero es limitado"
    elif porcentaje_flujo < 30:
        estado = "saludable"
        color = COLORES_FINANCIEROS['verde_agua']
        semaforo = "🟢"
        mensaje = "BIEN: Tienes un margen financiero saludable"
    else:
        estado = "excelente"
        color = COLORES_FINANCIEROS['verde']
        semaforo = "🟢"
        mensaje = "EXCELENTE: Tu situación financiera es óptima"
    
    return {
        # Datos básicos
        "ingreso_mensual": round(ingreso_mensual, 2),
        "gastos_fijos": round(total_gastos_fijos, 2),
        "gastos_variables": round(total_gastos_variables, 2),
        "deudas": round(total_deudas, 2),
        "gastos_totales": round(gastos_totales, 2),
        "flujo_libre": round(flujo_libre, 2),
        
        # Porcentajes
        "porcentaje_flujo": round(porcentaje_flujo, 2),
        "porcentaje_gastos_fijos": round(porcentaje_gastos_fijos, 2),
        "porcentaje_gastos_variables": round(porcentaje_gastos_variables, 2),
        "porcentaje_deudas": round(porcentaje_deudas, 2),
        
        # Estado financiero
        "estado_financiero": estado,
        "color_estado": color,
        "semaforo": semaforo,
        "mensaje_estado": mensaje,
        
        # Detalles para análisis
        "detalle_gastos_fijos": gastos_fijos,
        "detalle_gastos_variables": gastos_variables,
        "detalle_deudas": deudas
    }

# ================================
# FUNCIÓN: CAPACIDAD DE AHORRO
# ================================

def calcular_capacidad_ahorro(flujo_financiero):
    """
    Calcula la capacidad real de ahorro e inversión según el estado financiero.
    
    Parameters:
    -----------
    flujo_financiero : dict
        Resultado de la función calcular_flujo_financiero()
    
    Returns:
    --------
    dict : Capacidad de ahorro con rangos y recomendaciones
    
    Example:
    --------
    >>> flujo = calcular_flujo_financiero(25000, {...}, {...}, {...})
    >>> capacidad = calcular_capacidad_ahorro(flujo)
    >>> print(capacidad['ahorro_sugerido'])
    7500.0
    """
    
    flujo_libre = flujo_financiero.get("flujo_libre", 0)
    estado = flujo_financiero.get("estado_financiero", "crítico")
    ingreso = flujo_financiero.get("ingreso_mensual", 0)
    
    # Si el flujo es negativo, no hay capacidad de ahorro
    if estado == "negativo":
        return {
            "ahorro_posible": False,
            "rango_min": 0,
            "rango_max": 0,
            "ahorro_sugerido": 0,
            "ahorro_minimo": 0,
            "ahorro_optimo": 0,
            "mensaje": "⚠️ Tus gastos superan tus ingresos. Es prioritario ordenar tus finanzas antes de considerar inversiones.",
            "recomendacion": "reducir_gastos_urgente",
            "puede_invertir": False,
            "nivel_urgencia": "critico"
        }
    
    # Definir porcentajes de ahorro según estado financiero
    # Estos porcentajes se aplican sobre el flujo libre disponible
    if estado == "crítico":
        min_pct, max_pct = 0.30, 0.50  # 30-50% del flujo libre
        mensaje = "Tu margen es ajustado. Considera invertir conservadoramente mientras mejoras tu flujo."
        nivel = "basico"
    elif estado == "ajustado":
        min_pct, max_pct = 0.40, 0.60  # 40-60% del flujo libre
        mensaje = "Tienes capacidad de ahorro. Puedes comenzar a invertir de forma estructurada."
        nivel = "moderado"
    elif estado == "saludable":
        min_pct, max_pct = 0.50, 0.70  # 50-70% del flujo libre
        mensaje = "Excelente posición financiera. Puedes destinar una buena parte al ahorro e inversión."
        nivel = "avanzado"
    else:  # excelente
        min_pct, max_pct = 0.60, 0.80  # 60-80% del flujo libre
        mensaje = "Tu situación financiera es óptima. Maximiza tu capacidad de inversión."
        nivel = "optimo"
    
    # Calcular rangos basados en flujo libre
    rango_min = round(flujo_libre * min_pct, 2)
    rango_max = round(flujo_libre * max_pct, 2)
    ahorro_sugerido = round((rango_min + rango_max) / 2, 2)
    
    # Cálculo adicional: ahorro mínimo recomendado (5%) y óptimo (10%) del ingreso total
    ahorro_minimo = round(ingreso * 0.05, 2)  # 5% del ingreso
    ahorro_optimo = round(ingreso * 0.10, 2)  # 10% del ingreso
    
    return {
        "ahorro_posible": True,
        "rango_min": rango_min,
        "rango_max": rango_max,
        "ahorro_sugerido": ahorro_sugerido,
        "ahorro_minimo": ahorro_minimo,
        "ahorro_optimo": ahorro_optimo,
        "mensaje": mensaje,
        "porcentaje_min": round(min_pct * 100, 1),
        "porcentaje_max": round(max_pct * 100, 1),
        "puede_invertir": True,
        "estado_base": estado,
        "nivel_inversion": nivel
    }

# ================================
# FUNCIÓN: VALIDAR INVERSIÓN
# ================================

def validar_inversion_propuesta(inversion_propuesta, capacidad_ahorro):
    """
    Valida que la inversión propuesta por el cliente sea realista y sostenible.
    
    Parameters:
    -----------
    inversion_propuesta : float
        Monto que el cliente desea invertir mensualmente
    capacidad_ahorro : dict
        Resultado de la función calcular_capacidad_ahorro()
    
    Returns:
    --------
    dict : Validación con monto ajustado si es necesario
    
    Example:
    --------
    >>> capacidad = calcular_capacidad_ahorro(flujo)
    >>> validacion = validar_inversion_propuesta(15000, capacidad)
    >>> if not validacion['valida']:
    >>>     print(f"Monto ajustado: {validacion['monto_ajustado']}")
    """
    
    if not capacidad_ahorro.get("ahorro_posible", False):
        return {
            "valida": False,
            "monto_ajustado": 0,
            "mensaje": "⚠️ No es posible realizar inversiones en este momento. Primero necesitas estabilizar tus finanzas.",
            "nivel_riesgo": "alto",
            "accion_recomendada": "ordenar_finanzas"
        }
    
    rango_min = capacidad_ahorro.get("rango_min", 0)
    rango_max = capacidad_ahorro.get("rango_max", 0)
    ahorro_sugerido = capacidad_ahorro.get("ahorro_sugerido", 0)
    
    # Validar si la inversión está dentro del rango
    if inversion_propuesta < rango_min:
        return {
            "valida": True,
            "monto_ajustado": inversion_propuesta,
            "mensaje": f"✅ La inversión de ${inversion_propuesta:,.2f} es conservadora y viable. Considera aumentarla gradualmente.",
            "nivel_riesgo": "bajo",
            "accion_recomendada": "aceptar"
        }
    
    elif inversion_propuesta <= rango_max:
        porcentaje_uso = (inversion_propuesta / rango_max) * 100
        
        return {
            "valida": True,
            "monto_ajustado": inversion_propuesta,
            "mensaje": f"✅ La inversión de ${inversion_propuesta:,.2f} es viable y representa el {porcentaje_uso:.1f}% de tu capacidad máxima.",
            "nivel_riesgo": "moderado" if porcentaje_uso > 80 else "bajo",
            "accion_recomendada": "aceptar"
        }
    
    else:
        exceso = inversion_propuesta - rango_max
        porcentaje_exceso = (exceso / rango_max) * 100
        
        # Si el exceso es menor al 20%, ofrecer opción
        if porcentaje_exceso <= 20:
            return {
                "valida": False,
                "monto_ajustado": rango_max,
                "mensaje": f"⚠️ La inversión propuesta (${inversion_propuesta:,.2f}) excede ligeramente tu capacidad máxima (${rango_max:,.2f}). Se sugiere ${rango_max:,.2f} para mantener estabilidad financiera.",
                "nivel_riesgo": "medio",
                "accion_recomendada": "ajustar_monto",
                "alternativa_monto": ahorro_sugerido
            }
        else:
            return {
                "valida": False,
                "monto_ajustado": ahorro_sugerido,
                "mensaje": f"🚫 La inversión propuesta (${inversion_propuesta:,.2f}) excede significativamente tu capacidad ({porcentaje_exceso:.1f}% por encima). Se recomienda firmemente ${ahorro_sugerido:,.2f} para evitar comprometer tu estabilidad financiera.",
                "nivel_riesgo": "alto",
                "accion_recomendada": "reducir_significativamente",
                "alternativa_monto": ahorro_sugerido
            }

# ================================
# FUNCIÓN: RECOMENDACIONES
# ================================

def generar_recomendaciones_financieras(flujo_financiero, capacidad_ahorro):
    """
    Genera recomendaciones personalizadas según el análisis financiero completo.
    
    Parameters:
    -----------
    flujo_financiero : dict
        Resultado de calcular_flujo_financiero()
    capacidad_ahorro : dict
        Resultado de calcular_capacidad_ahorro()
    
    Returns:
    --------
    list : Lista de recomendaciones en orden de prioridad
    
    Example:
    --------
    >>> recomendaciones = generar_recomendaciones_financieras(flujo, capacidad)
    >>> for rec in recomendaciones:
    >>>     print(rec)
    """
    
    recomendaciones = []
    estado = flujo_financiero.get("estado_financiero", "crítico")
    porcentaje_deudas = flujo_financiero.get("porcentaje_deudas", 0)
    porcentaje_gastos_fijos = flujo_financiero.get("porcentaje_gastos_fijos", 0)
    porcentaje_flujo = flujo_financiero.get("porcentaje_flujo", 0)
    
    # ===========================================
    # RECOMENDACIONES SEGÚN ESTADO FINANCIERO
    # ===========================================
    
    if estado == "negativo":
        recomendaciones.extend([
            "🚨 URGENTE: Reduce gastos inmediatamente. Identifica gastos no esenciales que puedes eliminar",
            "📊 Crea un presupuesto detallado y realiza seguimiento diario de gastos",
            "💳 Evita nuevas deudas. Congela uso de tarjetas de crédito",
            "🔍 Busca fuentes adicionales de ingreso (freelance, venta de artículos, etc.)",
            "📞 Considera asesoría de consolidación de deudas",
            "🏦 Contacta a tus acreedores para renegociar tasas o plazos",
            "💰 Establece como meta alcanzar un flujo libre positivo en 3 meses"
        ])
    
    elif estado == "crítico":
        recomendaciones.extend([
            "⚠️ Crea un fondo de emergencia pequeño (equivalente a 1 mes de gastos básicos)",
            "💰 Reduce gastos variables en al menos 10-15%",
            "📝 Revisa y elimina suscripciones no esenciales (streaming, gimnasio, etc.)",
            "💳 Prioriza pagar deudas de alto interés (tarjetas de crédito)",
            "📈 Busca oportunidades de incrementar ingresos en tu trabajo actual",
            "🎯 Establece como meta alcanzar un flujo libre del 15% en 6 meses"
        ])
    
    elif estado == "ajustado":
        recomendaciones.extend([
            "💪 Incrementa tu fondo de emergencia a 3 meses de gastos",
            "📈 Inicia inversiones pequeñas pero constantes",
            "🎯 Mantén gastos bajo control, evita gastos hormiga",
            "📊 Busca formas de diversificar tus fuentes de ingreso",
            "💳 Acelera el pago de deudas cuando sea posible",
            "🏦 Investiga opciones de inversión con bajo riesgo para iniciar"
        ])
    
    elif estado == "saludable":
        recomendaciones.extend([
            "🎯 Maximiza aportaciones a planes de retiro (PPR, Afore voluntaria)",
            "📈 Diversifica tus inversiones en diferentes instrumentos",
            "🏦 Mantén un fondo de emergencia robusto (6 meses de gastos)",
            "🎓 Invierte en educación financiera y personal",
            "💼 Considera inversiones de mediano plazo (CETES, fondos indexados)",
            "📊 Evalúa oportunidades de inversión en bienes raíces o negocios"
        ])
    
    else:  # excelente
        recomendaciones.extend([
            "🚀 Optimiza tu estrategia fiscal con un contador especializado",
            "📈 Implementa estrategia de inversión avanzada y diversificada",
            "🏠 Evalúa inversión en bienes raíces como fuente de ingreso pasivo",
            "👨‍👩‍👧 Inicia planificación patrimonial (testamento, fideicomisos)",
            "💼 Considera asesoría financiera especializada para maximizar rendimientos",
            "🌍 Explora inversiones internacionales para diversificación global"
        ])
    
    # ===========================================
    # RECOMENDACIONES POR DEUDAS
    # ===========================================
    
    if porcentaje_deudas > 30:
        recomendaciones.insert(0, f"🚨 CRÍTICO: Tus deudas representan el {porcentaje_deudas:.1f}% de tu ingreso (más del 30%). Prioriza su reducción inmediata")
    elif porcentaje_deudas > 20:
        recomendaciones.insert(0, f"⚠️ ATENCIÓN: Tus deudas representan el {porcentaje_deudas:.1f}% de tu ingreso. Trabaja en reducirlas por debajo del 20%")
    elif porcentaje_deudas > 0:
        recomendaciones.append(f"✅ Tus deudas están en un nivel manejable ({porcentaje_deudas:.1f}%). Mantén este control")
    
    # ===========================================
    # RECOMENDACIONES POR GASTOS FIJOS
    # ===========================================
    
    if porcentaje_gastos_fijos > 60:
        recomendaciones.append(f"🏠 Tus gastos fijos son muy altos ({porcentaje_gastos_fijos:.1f}%). Evalúa opciones para reducirlos (mudanza, renegociación, etc.)")
    elif porcentaje_gastos_fijos > 50:
        recomendaciones.append(f"⚠️ Tus gastos fijos son elevados ({porcentaje_gastos_fijos:.1f}%). Busca formas graduales de reducirlos")
    
    # ===========================================
    # RECOMENDACIONES SEGÚN CAPACIDAD DE AHORRO
    # ===========================================
    
    if capacidad_ahorro.get('ahorro_posible'):
        nivel = capacidad_ahorro.get('nivel_inversion', 'basico')
        
        if nivel == 'basico':
            recomendaciones.append("💎 Inicia con inversiones de bajo riesgo: CETES, cuenta de ahorro con rendimientos")
        elif nivel == 'moderado':
            recomendaciones.append("💎 Considera fondos de inversión mixtos y CETES Plus")
        elif nivel == 'avanzado':
            recomendaciones.append("💎 Diversifica en fondos indexados, PPR y bonos corporativos")
        else:  # optimo
            recomendaciones.append("💎 Explora portafolio completo: acciones, bienes raíces, fondos internacionales")
    
    # ===========================================
    # RECOMENDACIÓN DE FONDO DE EMERGENCIA
    # ===========================================
    
    if porcentaje_flujo >= 20:
        recomendaciones.append("🏦 Prioridad: Establece fondo de emergencia de 6 meses antes de inversiones agresivas")
    else:
        recomendaciones.append("🏦 Prioridad: Establece fondo de emergencia de 3 meses como mínimo")
    
    return recomendaciones[:12]  # Máximo 12 recomendaciones

# ================================
# FUNCIÓN: ANÁLISIS DE SALUD FINANCIERA
# ================================

def analizar_salud_financiera(flujo_financiero):
    """
    Genera un análisis detallado de la salud financiera del cliente.
    
    Parameters:
    -----------
    flujo_financiero : dict
        Resultado de calcular_flujo_financiero()
    
    Returns:
    --------
    dict : Análisis con puntuación y áreas de mejora
    
    Example:
    --------
    >>> analisis = analizar_salud_financiera(flujo)
    >>> print(f"Puntuación: {analisis['puntuacion']}/100")
    >>> print(f"Estado: {analisis['calificacion']}")
    """
    
    puntuacion = 0
    areas_fortaleza = []
    areas_mejora = []
    
    # Evaluar flujo libre (0-35 puntos)
    porcentaje_flujo = flujo_financiero.get("porcentaje_flujo", 0)
    if porcentaje_flujo >= 30:
        puntuacion += 35
        areas_fortaleza.append("Excelente flujo libre de efectivo")
    elif porcentaje_flujo >= 20:
        puntuacion += 28
        areas_fortaleza.append("Buen flujo libre de efectivo")
    elif porcentaje_flujo >= 10:
        puntuacion += 18
        areas_mejora.append("Flujo libre limitado, busca incrementarlo")
    elif porcentaje_flujo >= 0:
        puntuacion += 8
        areas_mejora.append("Flujo libre crítico, acción urgente requerida")
    else:
        areas_mejora.append("URGENTE: Flujo negativo, gastos superan ingresos")
    
    # Evaluar nivel de deudas (0-30 puntos)
    porcentaje_deudas = flujo_financiero.get("porcentaje_deudas", 0)
    if porcentaje_deudas == 0:
        puntuacion += 30
        areas_fortaleza.append("Sin deudas, excelente posición")
    elif porcentaje_deudas <= 15:
        puntuacion += 25
        areas_fortaleza.append("Nivel de deudas bajo y manejable")
    elif porcentaje_deudas <= 30:
        puntuacion += 15
        areas_mejora.append("Nivel de deudas moderado, mantén control")
    else:
        puntuacion += 5
        areas_mejora.append("Nivel de deudas alto, requiere plan de reducción")
    
    # Evaluar gastos fijos (0-20 puntos)
    porcentaje_gastos_fijos = flujo_financiero.get("porcentaje_gastos_fijos", 0)
    if porcentaje_gastos_fijos <= 50:
        puntuacion += 20
        areas_fortaleza.append("Gastos fijos bajo control")
    elif porcentaje_gastos_fijos <= 60:
        puntuacion += 12
    else:
        puntuacion += 5
        areas_mejora.append("Gastos fijos muy elevados, busca reducirlos")
    
    # Evaluar gastos variables (0-15 puntos)
    porcentaje_gastos_variables = flujo_financiero.get("porcentaje_gastos_variables", 0)
    if porcentaje_gastos_variables <= 20:
        puntuacion += 15
        areas_fortaleza.append("Gastos variables controlados")
    elif porcentaje_gastos_variables <= 30:
        puntuacion += 10
    else:
        puntuacion += 5
        areas_mejora.append("Gastos variables elevados, identifica gastos hormiga")
    
    # Determinar calificación
    if puntuacion >= 85:
        calificacion = "EXCELENTE"
        estado_general = "Tu salud financiera es excepcional. Continúa maximizando tu patrimonio."
    elif puntuacion >= 70:
        calificacion = "MUY BUENA"
        estado_general = "Tu salud financiera es sólida. Pequeños ajustes te llevarán a la excelencia."
    elif puntuacion >= 55:
        calificacion = "BUENA"
        estado_general = "Tu salud financiera es aceptable pero hay áreas importantes de mejora."
    elif puntuacion >= 40:
        calificacion = "REGULAR"
        estado_general = "Tu salud financiera requiere atención. Trabaja en las áreas de mejora identificadas."
    else:
        calificacion = "CRÍTICA"
        estado_general = "Tu salud financiera requiere acción inmediata. Prioriza estabilización."
    
    return {
        "puntuacion": puntuacion,
        "puntuacion_maxima": 100,
        "calificacion": calificacion,
        "estado_general": estado_general,
        "areas_fortaleza": areas_fortaleza,
        "areas_mejora": areas_mejora,
        "porcentaje_salud": round((puntuacion / 100) * 100, 1)
    }

# ================================
# FUNCIÓN AUXILIAR: FORMATEAR MONEDA
# ================================

def formatear_moneda(monto):
    """Formatea un número como moneda mexicana."""
    try:
        return f"${float(monto):,.2f}"
    except:
        return "$0.00"

# ================================
# EJEMPLO DE USO
# ================================

if __name__ == "__main__":
    """
    Ejemplo de cómo usar las funciones del módulo
    """
    
    print("="*60)
    print("EJEMPLO DE ANÁLISIS FINANCIERO")
    print("="*60)
    
    # Datos de ejemplo
    ingreso = 50000
    gastos_fijos_ej = {
        'vivienda': 15000,
        'servicios': 2500,
        'transporte': 3000,
        'alimentacion': 6000,
        'seguros': 2000,
        'educacion': 3000
    }
    gastos_variables_ej = {
        'entretenimiento': 3000,
        'ropa': 1500,
        'salud': 1000,
        'otros': 2000
    }
    deudas_ej = {
        'tarjetas': 4000,
        'prestamos': 0,
        'auto': 3000,
        'otras': 0
    }
    
    # Paso 1: Calcular flujo financiero
    print("\n1. CALCULANDO FLUJO FINANCIERO...")
    flujo = calcular_flujo_financiero(ingreso, gastos_fijos_ej, gastos_variables_ej, deudas_ej)
    
    print(f"\n   Ingreso mensual: {formatear_moneda(flujo['ingreso_mensual'])}")
    print(f"   Gastos totales: {formatear_moneda(flujo['gastos_totales'])}")
    print(f"   Flujo libre: {formatear_moneda(flujo['flujo_libre'])} ({flujo['porcentaje_flujo']:.1f}%)")
    print(f"   Estado: {flujo['semaforo']} {flujo['estado_financiero'].upper()}")
    
    # Paso 2: Calcular capacidad de ahorro
    print("\n2. CALCULANDO CAPACIDAD DE AHORRO...")
    capacidad = calcular_capacidad_ahorro(flujo)
    
    if capacidad['ahorro_posible']:
        print(f"\n   Rango de ahorro: {formatear_moneda(capacidad['rango_min'])} - {formatear_moneda(capacidad['rango_max'])}")
        print(f"   Ahorro sugerido: {formatear_moneda(capacidad['ahorro_sugerido'])}")
        print(f"   Mensaje: {capacidad['mensaje']}")
    else:
        print(f"\n   {capacidad['mensaje']}")
    
    # Paso 3: Validar inversión propuesta
    print("\n3. VALIDANDO INVERSIÓN PROPUESTA...")
    inversion_cliente = 5000
    validacion = validar_inversion_propuesta(inversion_cliente, capacidad)
    
    print(f"\n   Inversión propuesta: {formatear_moneda(inversion_cliente)}")
    print(f"   ¿Es válida?: {'SÍ' if validacion['valida'] else 'NO'}")
    print(f"   {validacion['mensaje']}")
    
    # Paso 4: Generar recomendaciones
    print("\n4. GENERANDO RECOMENDACIONES...")
    recomendaciones = generar_recomendaciones_financieras(flujo, capacidad)
    
    print("\n   Top 5 recomendaciones:")
    for i, rec in enumerate(recomendaciones[:5], 1):
        print(f"   {i}. {rec}")
    
    # Paso 5: Analizar salud financiera
    print("\n5. ANÁLISIS DE SALUD FINANCIERA...")
    analisis = analizar_salud_financiera(flujo)
    
    print(f"\n   Puntuación: {analisis['puntuacion']}/100 ({analisis['porcentaje_salud']}%)")
    print(f"   Calificación: {analisis['calificacion']}")
    print(f"   {analisis['estado_general']}")
    
    if analisis['areas_fortaleza']:
        print(f"\n   Fortalezas:")
        for fortaleza in analisis['areas_fortaleza']:
            print(f"   ✅ {fortaleza}")
    
    if analisis['areas_mejora']:
        print(f"\n   Áreas de mejora:")
        for mejora in analisis['areas_mejora']:
            print(f"   ⚠️ {mejora}")
    
    print("\n" + "="*60)
    print("FIN DEL EJEMPLO")
    print("="*60)
