import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="Censor de Volumen - IICU-100", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, h2, h3 { color: #00FFAA; text-shadow: 0px 0px 8px rgba(0, 255, 170, 0.4); }
    .report-box { padding: 20px; border-radius: 10px; margin: 15px 0px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ CENSOR DE VOLUMEN E HISTOGRAMA INSTITUCIONAL")
st.subheader("Filtro de Segunda Línea con Control de Gravedad POC (2026)")
st.write("Inserta el ticker detectado por el IICU-100 para diagnosticar su estructura de acumulación y su rango de riesgo de ejecución.")

# --- ENTRADA DE DATOS SINCRO-ESTADOS ---
col_ticker, col_maestro = st.columns(2)

with col_ticker:
    ticker = st.text_input("INGRESA EL TICKER:", "").upper().strip()

with col_maestro:
    estado_maestro = st.selectbox(
        "ESTADO DEL PANEL MAESTRO:", 
        [
            "🔥 CRUCE DE URANO", 
            "💎 SOBERANO", 
            "⚡ OLLA DE PRESIÓN", 
            "🚀 MOMENTUM TEMPRANO", 
            "🛡️ SACUDIDA INSTITUCIONAL",
            "📡 RADAR"
        ]
    )

if ticker:
    with st.spinner(f"Analizando perfil de volumen para {ticker}..."):
        try:
            asset = yf.Ticker(ticker)
            # Extraemos 1 año de datos diarios
            hist = asset.history(period="1y")
            
            if hist.empty:
                st.error("No se encontraron datos para este Ticker. Verifica las siglas.")
            else:
                precio_actual = hist['Close'].iloc[-1]
                valores_precio = hist['Close'].values
                volumenes = hist['Volume'].values
                
                # 1. CÁLCULO MATEMÁTICO DEL PERFIL DE VOLUMEN (POC)
                counts, bin_edges = np.histogram(valores_precio, bins=20, weights=volumenes)
                max_volume_bin_index = np.argmax(counts)
                poc_inferior = bin_edges[max_volume_bin_index]
                poc_superior = bin_edges[max_volume_bin_index + 1]
                poc_promedio = (poc_inferior + poc_superior) / 2
                
                # Cálculo de la distancia porcentual absoluta al POC
                distancia_al_poc = (abs(precio_actual - poc_promedio) / poc_promedio) * 100
                
                # Definimos la métrica base del antiguo umbral (1.5% para delimitación de zona del canal)
                umbral_paciencia = poc_promedio * 0.015
                
                # Clasificación de la macroestructura base
                estado_censor = ""
                if precio_actual < (poc_promedio - umbral_paciencia):
                    estado_censor = "Camino de Desgastamiento"
                elif abs(precio_actual - poc_promedio) <= umbral_paciencia:
                    estado_censor = "Camino de la Paciencia"
                else:
                    estado_censor = "Ignición Latente"
                
                st.markdown("---")
                st.markdown(f"### 📊 Veredicto de Estructura para **{ticker}**")
                
                # 2. EVALUACIÓN COGNITIVA DE RANGOS DE DISTANCIA AL POC
                if estado_censor == "Camino de Desgastamiento":
                    st.markdown(f"""
                    <div class="report-box" style="background-color: rgba(255, 0, 0, 0.1); border: 2px solid #FF3333;">
                        <h3 style="color: #FF3333; margin-top:0;">❌ CAMINO DE DESGASTAMIENTO (Descartar Inversión)</h3>
                        <p><b>Diagnóstico:</b> El precio actual (<b>${precio_actual:.2f}</b>) ha quebrado a la baja el muro de volumen institucional (POC) situado en <b>${poc_promedio:.2f}</b>.</p>
                        <p><b>Riesgo:</b> Las manos fuertes que acumularon este año están bajo pérdida o distribuyendo material. Entrada prohibida.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                else:
                    # Renderizado según la nueva taxonomía optimizada de riesgo pactada
                    if distancia_al_poc < 5.0:
                        st.markdown(f"""
                        <div class="report-box" style="background-color: rgba(0, 255, 170, 0.1); border: 2px solid #00FFAA;">
                            <h3 style="color: #00FFAA; margin-top:0;">🟢 ENTRADA CONSERVADORA (Zona de Acumulación)</h3>
                            <p><b>Diagnóstico:</b> El precio actual (<b>${precio_actual:.2f}</b>) está a solo <b>{distancia_al_poc:.2f}%</b> del POC institucional (<b>${poc_promedio:.2f}</b>).</p>
                            <p><b>Ventaja:</b> Estás comprando dentro del núcleo de alta liquidez. El soporte es masivo y el riesgo de reversión media es mínimo.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif 5.0 <= distancia_al_poc < 8.0:
                        st.markdown(f"""
                        <div class="report-box" style="background-color: rgba(255, 234, 0, 0.1); border: 2px solid #FFEA00;">
                            <h3 style="color: #FFEA00; margin-top:0;">🟡 ENTRADA MODERADA (Zona de Transición)</h3>
                            <p><b>Diagnóstico:</b> El precio actual (<b>${precio_actual:.2f}</b>) se sitúa a <b>{distancia_al_poc:.2f}%</b> del POC institucional (<b>${poc_promedio:.2f}</b>).</p>
                            <p><b>Ventaja:</b> El precio muestra fuerza expansiva saliendo del Área de Valor. Riesgo moderado de re-testeo del bloque de volumen.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    elif 8.0 <= distancia_al_poc <= 12.0:
                        st.markdown(f"""
                        <div class="report-box" style="background-color: rgba(255, 136, 0, 0.1); border: 2px solid #FF8800;">
                            <h3 style="color: #FF8800; margin-top:0;">🟠 ENTRADA AGRESIVA (Zona de Escape)</h3>
                            <p><b>Diagnóstico:</b> Distancia considerable del precio (<b>${precio_actual:.2f}</b>) respecto al POC (<b>{distancia_al_poc:.2f}%</b>).</p>
                            <p><b>Alerta:</b> El activo está en modo descubrimiento. El soporte institucional queda lejos. Exigir FPC excepcional para validar la operación.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="report-box" style="background-color: rgba(255, 0, 0, 0.1); border: 2px solid #FF3333;">
                            <h3 style="color: #FF3333; margin-top:0;">🔴 ZONA DE EXCLUSIÓN CRÍTICA (Inhibición Automática)</h3>
                            <p><b>Diagnóstico:</b> El precio (<b>${precio_actual:.2f}</b>) está sobreextendido a un <b>{distancia_al_poc:.2f}%</b> del POC (<b>${poc_promedio:.2f}</b>).</p>
                            <p><b>Veredicto:</b> Entrada vetada por el Censor de Volumen. Riesgo de retroceso técnico severo e inaceptable.</p>
                        </div>
                        """, unsafe_allow_html=True)

                # --- ⚡ NUEVA MATRIZ DE DECISIONES SINCRO-ESTADOS CON RANGOS DINÁMICOS ---
                st.markdown("### ⚡ MATRIZ DE EJECUCIÓN COMBINADA")
                
                # 1. 🔥 CRUCE DE URANO
                if estado_maestro == "🔥 CRUCE DE URANO":
                    if estado_censor == "Ignición Latente":
                        if distancia_al_poc < 5.0:
                            st.success("🎯 **VEREDICTO: ENTRADA ÓPTIMA DE MOMENTUM BAJO RIESGO**")
                            st.info(f"🧠 *Instrucción:* Ignición confirmada en el Panel Maestro y el precio está apenas un {distancia_al_poc:.1f}% por encima del POC (Zona Conservadora). Ejecutar orden limitada directa.")
                        elif 5.0 <= distancia_al_poc < 8.0:
                            st.success("🎯 **VEREDICTO: ENTRADA DE MOMENTUM MODERADO**")
                            st.info(f"🧠 *Instrucción:* Expansión activa en zona de transición ({distancia_al_poc:.1f}% del POC). Dividir la entrada en dos partes para absorber un posible re-testeo.")
                        elif 8.0 <= distancia_al_poc <= 12.0:
                            st.warning("⚠️ **VEREDICTO: EJECUCIÓN AGRESIVA BAJO CONDICIÓN**")
                            st.info(f"🧠 *Instrucción:* El precio está en zona de escape ({distancia_al_poc:.1f}% del POC). Ejecutar únicamente si el FPC es extraordinario y utilizando una orden Stop-Limit por encima de máximos locales.")
                        else:
                            st.error("🛑 **VEREDICTO: ACCIÓN INHIBIDA (Exclusión por Distancia)**")
                            st.info(f"🧠 *Instrucción:* El cohete se alejó un {distancia_al_poc:.1f}% de la acumulación institucional. El Censor bloquea la compra. Esperar micro-retroceso estructural.")
                    elif estado_censor == "Camino de la Paciencia":
                        st.success("🎯 **VEREDICTO: ACUMULACIÓN EN SQUEEZE DE VOLUMEN**")
                        st.info("🧠 *Instrucción:* Transición explosiva ocurriendo exactamente sobre el bloque principal de volumen anual (Distancia < 5%). Compra autorizada con riesgo controlado.")
                    elif estado_censor == "Camino de Desgastamiento":
                        st.error("🛑 **VEREDICTO: FALSO QUIPU / SEÑAL DE LIQUIDACIÓN**")
                        st.info("🧠 *Instrucción:* El cruce de precio amaga alza, pero está por debajo del POC. El movimiento es artificial y carece de soporte institucional.")

                # 2. 💎 SOBERANO
                elif estado_maestro == "💎 SOBERANO":
                    if estado_censor == "Ignición Latente":
                        if distancia_al_poc < 5.0:
                            st.success("🎯 **VEREDICTO: COMPRA DE CONTINUACIÓN SOBERANA ÓPTIMA**")
                            st.info(f"🧠 *Instrucción:* Consolidación ideal en Zona Conservadora ({distancia_al_poc:.1f}% del POC). Flujo institucional robusto. Asignación directa de capital.")
                        elif 5.0 <= distancia_al_poc < 8.0:
                            st.success("🎯 **VEREDICTO: CONTINUACIÓN SOBERANA MODERADA**")
                            st.info(f"🧠 *Instrucción:* El activo defiende la estructura a un {distancia_al_poc:.1f}% del POC. Construir la posición de forma escalonada (DCA).")
                        elif 8.0 <= distancia_al_poc <= 12.0:
                            st.warning("⚠️ **VEREDICTO: SOBERANO EN EXTENSIÓN (Riesgo Agresivo)**")
                            st.info(f"🧠 *Instrucción:* Estructura macro sólida pero el precio a corto plazo está estirado ({distancia_al_poc:.1f}% del POC). Disminuir el tamaño del lote inicial a la mitad.")
                        else:
                            st.error("🛑 **VEREDICTO: VETO POR EXTENSIÓN DE PRECIO**")
                            st.info(f"🧠 *Instrucción:* La distancia al POC ({distancia_al_poc:.1f}%) invalida la disciplina del Cuadrante de Hierro. Esperar el re-testeo del Área de Valor.")
                    elif estado_censor == "Camino de la Paciencia":
                        st.success("🎯 **VEREDICTO: COMPRA ESTRATÉGICA DE LARGO PLAZO**")
                        st.info("🧠 *Instrucción:* Fuerza macro en el Panel Maestro combinada con cotización exacta sobre el punto de equilibrio de los fondos. Compra de alta fidelidad.")
                    elif estado_censor == "Camino de Desgastamiento":
                        st.error("🛑 **VEREDICTO: DISTRIBUCIÓN SOBERANA EN CURSO**")
                        st.info("🧠 *Instrucción:* Alerta. A pesar de su historial robusto, las instituciones están perforando el soporte del POC anual. Distribución encubierta detectada.")

                # 3. ⚡ OLLA DE PRESIÓN
                elif estado_maestro == "⚡ OLLA DE PRESIÓN":
                    if estado_censor == "Ignición Latente" or estado_censor == "Camino de la Paciencia":
                        if distancia_al_poc <= 8.0:
                            st.success("🎯 **VEREDICTO: INFILTRACIÓN ANTICIPATIVA DE ALTA FIDELIDAD**")
                            st.info(f"🧠 *Instrucción:* Compresión extrema inmóvil en zona segura (distancia: {distancia_al_poc:.1f}%). Relación riesgo/beneficio imbatible. Acumular en silencio antes de la ruptura.")
                        else:
                            st.warning("⚠️ **VEREDICTO: COMPRESIÓN EXTENDIDA (Monitoreo Estricto)**")
                            st.info(f"🧠 *Instrucción:* Olla de presión cotizando a un {distancia_al_poc:.1f}% de su base. No perseguir si no rompe con volumen confirmado.")
                    elif estado_censor == "Camino de Desgastamiento":
                        st.warning("⚠️ **VEREDICTO: OLLA AGUJERADA (Esperar Confirmación)**")
                        st.info("🧠 *Instrucción:* Hay interés teórico, pero el mercado cotiza por debajo del POC. Esperar la recuperación de la línea de control institucional.")

                # 4. 🚀 MOMENTUM TEMPRANO
                elif estado_maestro == "🚀 MOMENTUM TEMPRANO":
                    if estado_censor == "Ignición Latente":
                        if distancia_al_poc < 5.0:
                            st.success("🎯 **VEREDICTO: VELOCIDAD ÓPTIMA EN RANGO CONSERVADOR**")
                            st.info(f"🧠 *Instrucción:* Rotación rápida de capital. Saliendo de la base técnica a solo {distancia_al_poc:.1f}% del POC. Alta probabilidad de expansión vertical inmediata.")
                        elif 5.0 <= distancia_al_poc < 8.0:
                            st.success("🎯 **VEREDICTO: MOMENTUM EN ZONA MODERADA**")
                            st.info(f"🧠 *Instrucción:* Velocidad activa a un {distancia_al_poc:.1f}% del POC. Entrar con un lote inicial y agregar el lote secundario ante la confirmación de la siguiente vela diaria.")
                        elif 8.0 <= distancia_al_poc <= 12.0:
                            st.warning("⚠️ **VEREDICTO: VELOCIDAD AGRESIVA (Riesgo de Persecución)**")
                            st.info(f"🧠 *Instrucción:* El precio corre con prisa y se aleja de su base ({distancia_al_poc:.1f}% del POC). Reducir exposición o esperar micro-retroceso.")
                        else:
                            st.error("🛑 **VEREDICTO: COMPRA INHIBIDA POR SOBRECOMPRA**")
                            st.info(f"🧠 *Instrucción:* Momentum tardío. El precio cotiza a un {distancia_al_poc:.1f}% del POC. El Censor prohíbe el ingreso para evitar atrapamiento.")
                    elif estado_censor == "Camino de la Paciencia":
                        st.success("🎯 **VEREDICTO: ENTRADA PILOTO (Velocidad en Base)**")
                        st.info("🧠 *Instrucción:* Momentum incubando directamente sobre la línea de control de volumen anual (Distancia < 5%). Añadir lote inicial.")
                    elif estado_censor == "Camino de Desgastamiento":
                        st.error("🛑 **VEREDICTO: FALSO DESPEGUE (Trampa de Momentum)**")
                        st.info("🧠 *Instrucción:* Falsa prisa compradora. Las instituciones no están respaldando el movimiento del precio detrás del libro de órdenes.")

                # 5. 🛡️ ACUMULACIÓN / SACUDIDA INSTITUCIONAL
                elif estado_maestro == "🛡️ SACUDIDA INSTITUCIONAL":
                    if estado_censor == "Camino de la Paciencia" or estado_censor == "Ignición Latente":
                        st.success("🎯 **VEREDICTO: COMPRA DE PÁNICO (Suelo Confirmado)**")
                        st.info(f"🧠 *Instrucción:* Caza de liquidez. El precio barrió soportes pero las instituciones defienden firmemente el POC anual (Distancia actual: {distancia_al_poc:.1f}%). Compra de alta convicción con stop-loss ajustado.")
                    elif estado_censor == "Camino de Desgastamiento":
                        st.error("🛑 **VEREDICTO: SACUDIDA FALLIDA (Cuchillo Cayendo)**")
                        st.info("🧠 *Instrucción:* El pánico quebró el POC institucional de largo plazo. No hay red debajo de este nivel. Mantener liquidez a salvo.")

                # 6. 📡 RADAR (Neutralidad)
                elif estado_maestro == "📡 RADAR":
                    st.warning("⏳ **VEREDICTO: NEUTRALIDAD / OBSERVACIÓN PASIVA**")
                    st.info("🧠 *Instrucción:* Sin anomalías estructurales o de momentum. Cero asignación de capital bajo las reglas estrictas del Cuadrante de Hierro.")
                
                # --- 3. GRÁFICO VISUAL DEL PERFIL DE VOLUMEN HORIZONTAL ---
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    y=[(bin_edges[i] + bin_edges[i+1])/2 for i in range(len(counts))],
                    x=counts,
                    orientation='h',
                    name='Volumen Transaccionado',
                    marker=dict(color='rgba(0, 255, 170, 0.2)', line=dict(color='#00FFAA', width=1))
                ))
                
                fig.add_trace(go.Scatter(
                    x=[0, max(counts)],
                    y=[precio_actual, precio_actual],
                    mode='lines',
                    name=f'Precio Actual (${precio_actual:.2f})',
                    line=dict(color='#FF3388', width=3)
                ))
                
                fig.add_trace(go.Scatter(
                    x=[0, max(counts)],
                    y=[poc_promedio, poc_promedio],
                    mode='lines',
                    name=f'POC Institucional (${poc_promedio:.2f})',
                    line=dict(color='#00FFAA', width=3, dash='dash')
                ))
                
                fig.update_layout(
                    title=f"Distribución del Perfil de Volumen (1 Año) - {ticker}",
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)',
                    font=dict(color="#e0e0e0"),
                    xaxis_title="Volumen Acumulado",
                    yaxis_title="Zonas de Precio ($)",
                    height=450,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
        except Exception as e:
            st.error(f"Error en la extracción de datos de mercado o procesamiento de volumen: {e}")

st.markdown("---")
st.caption("Filtro de volumen autónomo v4.0 - Sincronizado con la jerarquía de control de riesgo de gravedad del Cuadrante de Hierro.")
