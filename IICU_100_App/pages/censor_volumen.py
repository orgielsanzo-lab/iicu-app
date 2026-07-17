import streamlit as set_page_config
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
st.subheader("Filtro de Segunda Línea para Activos SOBERANOS")
st.write("Inserta el ticker detectado por el IICU-100 para diagnosticar su estructura de acumulación real.")

# --- ENTRADA DE DATOS SINCRO-ESTADOS ---
col_ticker, col_maestro = st.columns(2)

with col_ticker:
    ticker = st.text_input("INGRESA EL TICKER:", "").upper().strip()

with col_maestro:
    # Actualización de estados en coherencia con la evolución del Panel Maestro
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
                
                umbral = poc_promedio * 0.015
                
                # Definimos el estado del censor para la matriz
                estado_censor = ""
                
                # 2. CLASIFICACIÓN DE CAMINOS Y RENDERIZADO DE RESULTADOS
                st.markdown("---")
                st.markdown(f"### 📊 Veredicto de Estructura para **{ticker}**")
                
                if precio_actual < (poc_promedio - umbral):
                    estado_censor = "Camino de Desgastamiento"
                    st.markdown(f"""
                    <div class="report-box" style="background-color: rgba(255, 0, 0, 0.1); border: 2px solid #FF3333;">
                        <h3 style="color: #FF3333; margin-top:0;">❌ CAMINO DE DESGASTAMIENTO (Descartar Inversión)</h3>
                        <p><b>Diagnóstico:</b> El precio actual (<b>${precio_actual:.2f}</b>) ha quebrado a la baja el muro de volumen institucional (POC) situado en <b>${poc_promedio:.2f}</b>.</p>
                        <p><b>Riesgo:</b> Las manos fuertes que acumularon este año están bajo pérdida o distribuyendo material. La probabilidad de que rompa la SMA 200 hacia abajo y regrese a RADAR es críticamente alta.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif abs(precio_actual - poc_promedio) <= umbral:
                    estado_censor = "Camino de la Paciencia"
                    st.markdown(f"""
                    <div class="report-box" style="background-color: rgba(255, 165, 0, 0.1); border: 2px solid #FFA500;">
                        <h3 style="color: #FFA500; margin-top:0;">⏳ CAMINO DE LA PACIENCIA (Acumulación Lenta)</h3>
                        <p><b>Diagnóstico:</b> El precio actual (<b>${precio_actual:.2f}</b>) se encuentra exactamente en la zona de equilibrio institucional (POC) de <b>${poc_promedio:.2f}</b>.</p>
                        <p><b>Estrategia:</b> Zona con riesgo de caída bajísimo porque estás comprando al precio promedio de los fondos de inversión. Sin embargo, el capital puede quedarse congelado semanas lateralizando antes de despertar.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    estado_censor = "Ignición Latente"
                    st.markdown(f"""
                    <div class="report-box" style="background-color: rgba(0, 255, 170, 0.1); border: 2px solid #00FFAA;">
                        <h3 style="color: #00FFAA; margin-top:0;">🚀 IGNICIÓN LATENTE (Fase Altamente Eficiente)</h3>
                        <p><b>Diagnóstico:</b> El activo defiende el precio actual (<b>${precio_actual:.2f}</b>) por encima del bloque de volumen anual (<b>${poc_promedio:.2f}</b>).</p>
                        <p><b>Estrategia:</b> Estructura óptima de continuación alcista. Las compras institucionales previas actúan como un trampolín sólido. Es la ventana de tiempo más eficiente para colocar capital.</p>
                    </div>
                    """, unsafe_allow_html=True)

                # --- ⚡ NUEVA MATRIZ DE DECISIONES CUÁNTICAS SINCRO-ESTADOS ---
                st.markdown("### ⚡ MATRIZ DE EJECUCIÓN COMBINADA")
                
                distancia_al_poc = ((precio_actual - poc_promedio) / poc_promedio) * 100
                
                # --- LÓGICA DE CRUCE MATRICIAL CON NUEVOS ESTADOS ---
                
                # 1. 🔥 CRUCE DE URANO
                if estado_maestro == "🔥 CRUCE DE URANO":
                    if estado_censor == "Ignición Latente":
                        if distancia_al_poc <= 7.0:
                            st.success("🎯 **VEREDICTO: ENTRADA DE MOMENTUM INMEDIATO**")
                            st.info(f"🧠 *Lectura:* Ignición confirmada y el precio está apenas un {distancia_al_poc:.1f}% por encima del POC. Añadir agresivamente en la ruptura actual.")
                        else:
                            st.warning("⚠️ **VEREDICTO: MOMENTUM EXTENDIDO (Esperar Micro-Retroceso)**")
                            st.info(f"🧠 *Lectura:* El cohete despegó, pero cotiza un {distancia_al_poc:.1f}% por encima de su POC anual. Esperar retroceso rápido de 15 minutos en soporte local para evitar comprar el extremo.")
                    elif estado_censor == "Camino de la Paciencia":
                        st.success("🎯 **VEREDICTO: ACUMULACIÓN EN SQUEEZE DE VOLUMEN**")
                        st.info("🧠 *Lectura:* Transición explosiva ocurriendo exactamente sobre el bloque principal de volumen anual. Compra con riesgo controlado.")
                    elif estado_censor == "Camino de Desgastamiento":
                        st.error("🛑 **VEREDICTO: FALSO QUIPU / SEÑAL DE LIQUIDACIÓN**")
                        st.info("🧠 *Lectura:* El cruce técnico de precio amaga alza, pero los bloques reales de volumen muestran que está por debajo del POC. El despegue es artificial.")

                # 2. 💎 SOBERANO
                elif estado_maestro == "💎 SOBERANO":
                    if estado_censor == "Ignición Latente":
                        if distancia_al_poc <= 7.0:
                            st.success("🎯 **VEREDICTO: COMPRA DE CONTINUACIÓN SOBERANA**")
                            st.info(f"🧠 *Lectura:* El activo es soberano y consolida cerca del soporte (distancia segura del {distancia_al_poc:.1f}% al POC). Flujo institucional creciente. Posición óptima.")
                        else:
                            st.warning("⚠️ **VEREDICTO: SOBERANO EXTENDIDO (No Perseguir)**")
                            st.info(f"🧠 *Lectura:* Sólido en la macro, pero el precio se alejó un {distancia_al_poc:.1f}% de la zona de control de los fondos. Esperar un respiro técnico.")
                    elif estado_censor == "Camino de la Paciencia":
                        st.success("🎯 **VEREDICTO: COMPRA ESTRATÉGICA (Largo Plazo)**")
                        st.info("🧠 *Lectura:* Fuerza estructural en el Panel Maestro combinada con precio exacto de equilibrio institucional. Compra ideal con marea macro a favor.")
                    elif estado_censor == "Camino de Desgastamiento":
                        st.error("🛑 **VEREDICTO: DISTRIBUCIÓN SOBERANA**")
                        st.info("🧠 *Lectura:* Alerta. A pesar del histórico robusto, las instituciones están rompiendo la base del POC anual. Distribución encubierta.")

                # 3. ⚡ OLLA DE PRESIÓN
                elif estado_maestro == "⚡ OLLA DE PRESIÓN":
                    if estado_censor == "Ignición Latente" or estado_censor == "Camino de la Paciencia":
                        st.success("🎯 **VEREDICTO: INFILTRACIÓN ANTICIPATIVA**")
                        st.info(f"🧠 *Lectura:* Acumulación extrema (FPC > 95) mientras el precio está frío e inmóvil sobre o muy cerca de su POC (distancia: {distancia_al_poc:.1f}%). Relación riesgo/beneficio inmejorable. Acumular en silencio.")
                    elif estado_censor == "Camino de Desgastamiento":
                        st.warning("⚠️ **VEREDICTO: OLLA AGUJERADA (Esperar Confirmación)**")
                        st.info("🧠 *Lectura:* Hay interés institucional, pero los precios cotizan por debajo del POC. Esperar a que recupere el nivel de control antes de colocar capital.")

                # 4. 🚀 MOMENTUM TEMPRANO
                elif estado_maestro == "🚀 MOMENTUM TEMPRANO":
                    if estado_censor == "Ignición Latente":
                        if distancia_al_poc <= 7.0:
                            st.success("🎯 **VEREDICTO: ENTRADA POR VELOCIDAD ÓPTIMA**")
                            st.info(f"🧠 *Lectura:* Rotación rápida de capital. El precio está saliendo de su base con fuerza pero aún en el rango de protección del POC ({distancia_al_poc:.1f}%). Alta probabilidad de expansión inmediata.")
                        else:
                            st.warning("⚠️ **VEREDICTO: MOMENTUM EXTENDIDO (No Perseguir)**")
                            st.info(f"🧠 *Lectura:* Los compradores tienen prisa y el precio cotiza un {distancia_al_poc:.1f}% sobre la acumulación. Esperar retroceso.")
                    elif estado_censor == "Camino de la Paciencia":
                        st.success("🎯 **VEREDICTO: ENTRADA PILOTO (Velocidad en Base)**")
                        st.info("🧠 *Lectura:* momentum temprano incubando justo sobre la línea de control anual. Añadir lote inicial.")
                    elif estado_censor == "Camino de Desgastamiento":
                        st.error("🛑 **VEREDICTO: FALSO DESPEGUE (Trampa de Momentum)**")
                        st.info("🧠 *Lectura:* Falsa prisa compradora. Las instituciones no están respaldando el movimiento del precio real detrás del volumen.")

                # 5. 🛡️ SACUDIDA INSTITUCIONAL
                elif estado_maestro == "🛡️ SACUDIDA INSTITUCIONAL":
                    if estado_censor == "Camino de la Paciencia" or estado_censor == "Ignición Latente":
                        st.success("🎯 **VEREDICTO: COMPRA DE PÁNICO (Suelo Confirmado)**")
                        st.info(f"🧠 *Lectura:* Caza de liquidez extrema. El precio colapsó a niveles de soporte pero las instituciones defienden firmemente el POC anual. Compra de alta convicción contra la masa, stop-loss ajustado.")
                    elif estado_censor == "Camino de Desgastamiento":
                        st.error("🛑 **VEREDICTO: SACUDIDA FALLIDA (Cuchillo Cayendo)**")
                        st.info("🧠 *Lectura:* El pánico quebró el POC institucional de largo plazo. No hay soporte debajo. Mantener liquidez.")

                # 6. 📡 RADAR (Neutralidad)
                elif estado_maestro == "📡 RADAR":
                    st.warning("⏳ **VEREDICTO: NEUTRALIDAD / OBSERVACIÓN PASIVA**")
                    st.info("🧠 *Lectura:* Sin anomalías en momentum, acumulación o estructura de volumen. No se destina capital bajo ninguna circunstancia en este nodo.")
                
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
            st.error(f"Error en la extracción de datos de mercado: {e}")

st.markdown("---")
st.caption("Filtro de volumen autónomo v3.0 - Sincronizado con la jerarquía de estados IICU-100 v3.8.0")
