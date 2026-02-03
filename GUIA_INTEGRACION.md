# 🚀 GUÍA DE INTEGRACIÓN RÁPIDA
## Cómo Integrar el Análisis Financiero Mejorado en tu Código Rizkora

---

## 📋 CONTENIDO

1. [Opción 1: Integración Modular (Recomendada)](#opción-1-integración-modular)
2. [Opción 2: Integración Directa](#opción-2-integración-directa)
3. [Cambios Necesarios en el Paso 3](#cambios-en-el-paso-3)
4. [Pruebas y Validación](#pruebas-y-validación)

---

## OPCIÓN 1: INTEGRACIÓN MODULAR (RECOMENDADA)

Esta es la forma más limpia y mantenible de integrar las mejoras.

### Paso 1: Agregar el Módulo

Coloca el archivo `modulo_financiero.py` en la misma carpeta que tu `asesoria_rizkora.py`

```
tu_proyecto/
├── asesoria_rizkora.py
├── modulo_financiero.py  ← NUEVO
└── .streamlit/
    └── secrets.toml
```

### Paso 2: Importar el Módulo

En la parte superior de tu `asesoria_rizkora.py`, después de los imports existentes, agrega:

```python
# Importar módulo de análisis financiero (NUEVO)
from modulo_financiero import (
    calcular_flujo_financiero,
    calcular_capacidad_ahorro,
    validar_inversion_propuesta,
    generar_recomendaciones_financieras,
    analizar_salud_financiera,
    formatear_moneda  # Ya existe, pero usar la del módulo
)
```

### Paso 3: Modificar el Session State

En la sección de inicialización, actualiza:

```python
if 'datos' not in st.session_state:
    st.session_state.datos = {
        'datos_generales': {},
        'perfil_familiar': {},
        'ingresos': {},
        'flujo_financiero': {},      # ← NUEVO
        'capacidad_ahorro': {},      # ← NUEVO
        'proteccion': {},
        'ahorro': {},
        'retiro': {},
        'educacion': {},
        'cierre': {}
    }
```

### Paso 4: Reemplazar el Paso 3 Completo

Busca la sección que dice:

```python
elif st.session_state.step == 3:
    st.header("3️⃣ Ingresos y Capacidad Financiera")
```

Y reemplázala con el siguiente código:

---

## CÓDIGO COMPLETO DEL PASO 3 MEJORADO

```python
elif st.session_state.step == 3:
    st.header("3️⃣ Análisis Financiero Integral")
    
    st.info("""
    📊 **Análisis de Flujo Financiero**
    
    Realizaremos un análisis detallado de tus ingresos, gastos y capacidad de ahorro.
    Esta información es fundamental para diseñar un plan financiero personalizado.
    """)
    
    with st.form("form_analisis_financiero"):
        # SECCIÓN 1: INGRESOS
        st.subheader("💰 Ingresos")
        
        ingreso_mensual = st.number_input(
            "Ingreso mensual neto* (después de impuestos)", 
            min_value=0.0, 
            value=float(st.session_state.datos['ingresos'].get('ingreso_mensual', 0)),
            step=1000.0,
            format="%.2f",
            help="Ingresa tu sueldo neto mensual después de deducciones de ley"
        )
        
        st.markdown("---")
        
        # SECCIÓN 2: GASTOS FIJOS
        st.subheader("🏠 Gastos Fijos Mensuales")
        st.write("Gastos que pagas regularmente cada mes por el mismo monto")
        
        col1, col2 = st.columns(2)
        
        gastos_fijos_previos = st.session_state.datos.get('flujo_financiero', {}).get('detalle_gastos_fijos', {})
        
        with col1:
            gasto_vivienda = st.number_input("Vivienda (renta/hipoteca)", min_value=0.0,
                value=float(gastos_fijos_previos.get('vivienda', 0)), step=500.0, format="%.2f")
            
            gasto_servicios = st.number_input("Servicios (luz, agua, gas, internet)", min_value=0.0,
                value=float(gastos_fijos_previos.get('servicios', 0)), step=100.0, format="%.2f")
            
            gasto_transporte = st.number_input("Transporte (gasolina, transporte público)", min_value=0.0,
                value=float(gastos_fijos_previos.get('transporte', 0)), step=100.0, format="%.2f")
        
        with col2:
            gasto_alimentacion = st.number_input("Alimentación (supermercado)", min_value=0.0,
                value=float(gastos_fijos_previos.get('alimentacion', 0)), step=500.0, format="%.2f")
            
            gasto_seguros = st.number_input("Seguros (auto, vida, gastos médicos)", min_value=0.0,
                value=float(gastos_fijos_previos.get('seguros', 0)), step=100.0, format="%.2f")
            
            gasto_educacion = st.number_input("Educación (colegiaturas, libros)", min_value=0.0,
                value=float(gastos_fijos_previos.get('educacion', 0)), step=500.0, format="%.2f")
        
        st.markdown("---")
        
        # SECCIÓN 3: GASTOS VARIABLES
        st.subheader("🛍️ Gastos Variables Mensuales")
        st.write("Gastos que varían mes con mes")
        
        col1, col2 = st.columns(2)
        
        gastos_variables_previos = st.session_state.datos.get('flujo_financiero', {}).get('detalle_gastos_variables', {})
        
        with col1:
            gasto_entretenimiento = st.number_input("Entretenimiento (cine, salidas, hobbies)", 
                min_value=0.0, value=float(gastos_variables_previos.get('entretenimiento', 0)), step=100.0, format="%.2f")
            
            gasto_ropa = st.number_input("Ropa y calzado", min_value=0.0,
                value=float(gastos_variables_previos.get('ropa', 0)), step=100.0, format="%.2f")
        
        with col2:
            gasto_salud = st.number_input("Salud (medicamentos, consultas)", min_value=0.0,
                value=float(gastos_variables_previos.get('salud', 0)), step=100.0, format="%.2f")
            
            gasto_otros_variables = st.number_input("Otros gastos variables", min_value=0.0,
                value=float(gastos_variables_previos.get('otros', 0)), step=100.0, format="%.2f")
        
        st.markdown("---")
        
        # SECCIÓN 4: DEUDAS
        st.subheader("💳 Pagos de Deudas Mensuales")
        st.write("Pagos mínimos o mensuales de tus deudas")
        
        col1, col2 = st.columns(2)
        
        deudas_previas = st.session_state.datos.get('flujo_financiero', {}).get('detalle_deudas', {})
        
        with col1:
            pago_tarjetas = st.number_input("Tarjetas de crédito", min_value=0.0,
                value=float(deudas_previas.get('tarjetas', 0)), step=500.0, format="%.2f")
            
            pago_prestamos = st.number_input("Préstamos personales", min_value=0.0,
                value=float(deudas_previas.get('prestamos', 0)), step=500.0, format="%.2f")
        
        with col2:
            pago_credito_auto = st.number_input("Crédito automotriz", min_value=0.0,
                value=float(deudas_previas.get('auto', 0)), step=500.0, format="%.2f")
            
            pago_otras_deudas = st.number_input("Otras deudas", min_value=0.0,
                value=float(deudas_previas.get('otras', 0)), step=100.0, format="%.2f")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("⬅️ Anterior", use_container_width=True):
                navegar_a_paso(2)
        with col2:
            submitted = st.form_submit_button("📊 Calcular Análisis", type="primary", use_container_width=True)
        
        if submitted:
            if ingreso_mensual <= 0:
                st.error("❌ El ingreso mensual debe ser mayor a 0")
            else:
                # Preparar datos de gastos
                gastos_fijos = {
                    'vivienda': gasto_vivienda,
                    'servicios': gasto_servicios,
                    'transporte': gasto_transporte,
                    'alimentacion': gasto_alimentacion,
                    'seguros': gasto_seguros,
                    'educacion': gasto_educacion
                }
                
                gastos_variables = {
                    'entretenimiento': gasto_entretenimiento,
                    'ropa': gasto_ropa,
                    'salud': gasto_salud,
                    'otros': gasto_otros_variables
                }
                
                deudas = {
                    'tarjetas': pago_tarjetas,
                    'prestamos': pago_prestamos,
                    'auto': pago_credito_auto,
                    'otras': pago_otras_deudas
                }
                
                # Calcular flujo financiero usando el módulo
                flujo = calcular_flujo_financiero(ingreso_mensual, gastos_fijos, gastos_variables, deudas)
                
                # Calcular capacidad de ahorro
                capacidad = calcular_capacidad_ahorro(flujo)
                
                # Guardar en session state
                st.session_state.datos['flujo_financiero'] = flujo
                st.session_state.datos['capacidad_ahorro'] = capacidad
                st.session_state.datos['ingresos'] = {
                    'ingreso_mensual': ingreso_mensual,
                    'ingreso_anual': ingreso_mensual * 12,
                    'ahorro_ideal_10': ingreso_mensual * 12 * 0.10,
                    'ahorro_conservador_7': ingreso_mensual * 0.07,
                    'inversion_mensual': capacidad.get('ahorro_sugerido', 0)
                }
                
                st.success("✅ Análisis financiero completado")
                st.rerun()
    
    # MOSTRAR RESULTADOS SI YA SE CALCULÓ
    if st.session_state.datos.get('flujo_financiero') and st.session_state.datos.get('capacidad_ahorro'):
        st.markdown("---")
        st.header("📊 Resultados del Análisis")
        
        flujo = st.session_state.datos['flujo_financiero']
        capacidad = st.session_state.datos['capacidad_ahorro']
        
        # TARJETA DE ESTADO FINANCIERO
        estado = flujo['estado_financiero']
        semaforo = flujo['semaforo']
        color = flujo['color_estado']
        
        st.markdown(f"""
        <div style='background-color: {color}; padding: 20px; border-radius: 10px; text-align: center;'>
            <h2 style='color: white; margin: 0;'>{semaforo} Estado Financiero: {estado.upper()}</h2>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("###")
        
        # MÉTRICAS PRINCIPALES
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("💰 Ingreso Mensual", formatear_moneda(flujo['ingreso_mensual']))
        
        with col2:
            st.metric("💸 Gastos Totales", formatear_moneda(flujo['gastos_totales']),
                delta=f"-{flujo['porcentaje_gastos_fijos'] + flujo['porcentaje_gastos_variables'] + flujo['porcentaje_deudas']:.1f}%",
                delta_color="inverse")
        
        with col3:
            st.metric("✨ Flujo Libre", formatear_moneda(flujo['flujo_libre']),
                delta=f"{flujo['porcentaje_flujo']:.1f}%",
                delta_color="normal" if flujo['flujo_libre'] > 0 else "inverse")
        
        with col4:
            if capacidad['ahorro_posible']:
                st.metric("💎 Ahorro Sugerido", formatear_moneda(capacidad['ahorro_sugerido']))
            else:
                st.metric("⚠️ Ahorro", "$0.00", delta="No disponible", delta_color="inverse")
        
        st.markdown("---")
        
        # DESGLOSE DETALLADO
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📋 Desglose de Gastos")
            
            import pandas as pd
            desglose_data = {
                'Categoría': ['Gastos Fijos', 'Gastos Variables', 'Deudas', 'Flujo Libre'],
                'Monto': [
                    formatear_moneda(flujo['gastos_fijos']),
                    formatear_moneda(flujo['gastos_variables']),
                    formatear_moneda(flujo['deudas']),
                    formatear_moneda(flujo['flujo_libre'])
                ],
                '% Ingreso': [
                    f"{flujo['porcentaje_gastos_fijos']:.1f}%",
                    f"{flujo['porcentaje_gastos_variables']:.1f}%",
                    f"{flujo['porcentaje_deudas']:.1f}%",
                    f"{flujo['porcentaje_flujo']:.1f}%"
                ]
            }
            
            df_desglose = pd.DataFrame(desglose_data)
            st.dataframe(df_desglose, use_container_width=True, hide_index=True)
        
        with col2:
            st.subheader("💡 Indicadores Clave")
            
            # Indicador de salud financiera
            if flujo['porcentaje_flujo'] >= 30:
                st.success(f"✅ Flujo libre excelente: {flujo['porcentaje_flujo']:.1f}%")
            elif flujo['porcentaje_flujo'] >= 20:
                st.info(f"👍 Flujo libre saludable: {flujo['porcentaje_flujo']:.1f}%")
            elif flujo['porcentaje_flujo'] >= 10:
                st.warning(f"⚠️ Flujo libre ajustado: {flujo['porcentaje_flujo']:.1f}%")
            else:
                st.error(f"🚨 Flujo libre crítico: {flujo['porcentaje_flujo']:.1f}%")
            
            # Indicador de deudas
            if flujo['porcentaje_deudas'] <= 20:
                st.success(f"✅ Deudas bajo control: {flujo['porcentaje_deudas']:.1f}%")
            elif flujo['porcentaje_deudas'] <= 35:
                st.warning(f"⚠️ Deudas moderadas: {flujo['porcentaje_deudas']:.1f}%")
            else:
                st.error(f"🚨 Deudas altas: {flujo['porcentaje_deudas']:.1f}%")
            
            # Indicador de gastos fijos
            if flujo['porcentaje_gastos_fijos'] <= 50:
                st.success(f"✅ Gastos fijos adecuados: {flujo['porcentaje_gastos_fijos']:.1f}%")
            else:
                st.warning(f"⚠️ Gastos fijos elevados: {flujo['porcentaje_gastos_fijos']:.1f}%")
        
        st.markdown("---")
        
        # CAPACIDAD DE AHORRO
        st.subheader("💎 Capacidad de Ahorro e Inversión")
        
        if capacidad['ahorro_posible']:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Rango Mínimo", formatear_moneda(capacidad['rango_min']),
                    f"{capacidad['porcentaje_min']:.0f}% del flujo")
            
            with col2:
                st.metric("Ahorro Sugerido", formatear_moneda(capacidad['ahorro_sugerido']), "Recomendado")
            
            with col3:
                st.metric("Rango Máximo", formatear_moneda(capacidad['rango_max']),
                    f"{capacidad['porcentaje_max']:.0f}% del flujo")
            
            st.info(f"💡 {capacidad['mensaje']}")
            
            # Referencias adicionales
            st.write("**Referencias de ahorro ideal:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"• Ahorro mínimo (5% ingreso): {formatear_moneda(capacidad['ahorro_minimo'])}")
            with col2:
                st.write(f"• Ahorro óptimo (10% ingreso): {formatear_moneda(capacidad['ahorro_optimo'])}")
            
        else:
            st.error("⚠️ " + capacidad['mensaje'])
            st.warning("""
            **Recomendación Urgente:**
            
            1. Reducir gastos no esenciales
            2. Generar un plan de pago de deudas
            3. Buscar formas de aumentar ingresos
            4. Estabilizar tu situación financiera
            """)
        
        st.markdown("---")
        
        # RECOMENDACIONES PERSONALIZADAS
        st.subheader("🎯 Recomendaciones Personalizadas")
        
        recomendaciones = generar_recomendaciones_financieras(flujo, capacidad)
        
        for i, rec in enumerate(recomendaciones, 1):
            st.write(f"{i}. {rec}")
        
        st.markdown("---")
        
        # PREGUNTA FINAL: INVERSIÓN MENSUAL
        st.subheader("💼 Capacidad de Inversión Mensual")
        
        if capacidad['ahorro_posible']:
            with st.form("form_inversion_mensual"):
                st.write(f"""
                Tu capacidad de ahorro está entre **{formatear_moneda(capacidad['rango_min'])}** 
                y **{formatear_moneda(capacidad['rango_max'])}** mensuales.
                
                ¿Cuánto estarías dispuesto a invertir mensualmente?
                """)
                
                inversion_propuesta = st.number_input(
                    "Inversión mensual propuesta*",
                    min_value=0.0,
                    max_value=float(capacidad['rango_max'] * 1.5),
                    value=float(capacidad['ahorro_sugerido']),
                    step=100.0,
                    format="%.2f"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("⬅️ Regresar", use_container_width=True):
                        st.session_state.datos.pop('flujo_financiero', None)
                        st.session_state.datos.pop('capacidad_ahorro', None)
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("➡️ Continuar", type="primary", use_container_width=True):
                        # Validar inversión propuesta
                        validacion = validar_inversion_propuesta(inversion_propuesta, capacidad)
                        
                        if validacion['valida']:
                            st.session_state.datos['ingresos']['inversion_mensual'] = inversion_propuesta
                            st.success(validacion['mensaje'])
                            navegar_a_paso(4)
                        else:
                            st.warning(validacion['mensaje'])
                            st.session_state.datos['ingresos']['inversion_mensual'] = validacion['monto_ajustado']
                            
                            if st.button("Aceptar monto ajustado", type="primary"):
                                navegar_a_paso(4)
        else:
            st.error("""
            ⚠️ **No puedes continuar con inversiones ahora**
            
            Tu situación requiere estabilización financiera primero.
            """)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ Regresar", use_container_width=True):
                    st.session_state.datos.pop('flujo_financiero', None)
                    st.session_state.datos.pop('capacidad_ahorro', None)
                    st.rerun()
            
            with col2:
                if st.button("Continuar ➡️", type="secondary", use_container_width=True):
                    st.session_state.datos['ingresos']['inversion_mensual'] = 0
                    navegar_a_paso(4)
```

---

## PRUEBAS Y VALIDACIÓN

### Paso 1: Prueba el Módulo Independiente

Ejecuta el módulo directamente para verificar que funciona:

```bash
python modulo_financiero.py
```

Deberías ver un ejemplo completo de análisis financiero.

### Paso 2: Prueba la Aplicación

Ejecuta tu aplicación Streamlit:

```bash
streamlit run asesoria_rizkora.py
```

### Paso 3: Casos de Prueba

Prueba con estos escenarios:

**Caso 1: Flujo Saludable**
- Ingreso: $50,000
- Gastos fijos totales: $20,000
- Gastos variables: $8,000
- Deudas: $5,000
- Resultado esperado: Estado EXCELENTE 🟢

**Caso 2: Flujo Crítico**
- Ingreso: $20,000
- Gastos fijos totales: $14,000
- Gastos variables: $4,000
- Deudas: $1,500
- Resultado esperado: Estado CRÍTICO 🔴

**Caso 3: Flujo Negativo**
- Ingreso: $15,000
- Gastos fijos totales: $12,000
- Gastos variables: $3,000
- Deudas: $2,000
- Resultado esperado: Estado NEGATIVO 🔴 (sin capacidad de ahorro)

---

## SOLUCIÓN DE PROBLEMAS

### Error: "module 'modulo_financiero' has no attribute..."

**Solución:** Verifica que el archivo `modulo_financiero.py` esté en el mismo directorio y que hayas importado correctamente las funciones.

### Error: Los resultados no se guardan

**Solución:** Verifica que estás usando `st.session_state.datos` correctamente y que has actualizado la estructura del session state.

### Los gráficos no aparecen

**Solución:** Asegúrate de tener instalado `matplotlib`. Ejecuta: `pip install matplotlib`

---

## PRÓXIMOS PASOS

Una vez que el Paso 3 funcione correctamente:

1. ✅ Actualiza el Paso 4 (Protección) para usar los datos del flujo financiero
2. ✅ Actualiza el Paso 8 (Resumen) para mostrar el análisis completo
3. ✅ Actualiza la función de Google Sheets para guardar los nuevos campos
4. ✅ Actualiza el PDF para incluir el análisis financiero

---

## SOPORTE

Si tienes problemas con la integración:
1. Verifica que todos los archivos estén en el directorio correcto
2. Revisa los mensajes de error en la consola de Streamlit
3. Asegúrate de que todas las dependencias estén instaladas
4. Prueba primero con el módulo independiente

---

¡Felicidades! Tu sistema de asesoría ahora tiene un análisis financiero profesional y completo. 🎉
