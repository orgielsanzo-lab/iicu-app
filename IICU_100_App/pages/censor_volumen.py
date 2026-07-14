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

# --- ENTRADA DE DATOS ---
col_ticker, col_maestro = st.columns(2)

with col_ticker:
    ticker = st.text_input("INGRESA EL TICKER:", "").upper().strip()

with col_maestro:
    estado_maestro = st.selectbox("ESTADO DEL PANEL MAESTRO:", ["Soberano", "Radar", "Cruce de Urano"])

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

                # --- ⚡ MATRIZ DE DECISIONES CUÁNTICAS IICU-100 ---
                st.markdown("### ⚡ MATRIZ DE EJECUCIÓN COMBINADA")
                
                # Cálculo de la distancia porcentual al POC para el filtro de riesgo
                distancia_al_poc = ((precio_actual - poc_promedio) / poc_promedio) * 100
                
                # LÓGICA DE CRUCE MATRICIAL CON FILTRO DE DISTANCIA CRÍTICA
                if estado_maestro == "Soberano":
                    if estado_censor == "Ignición Latente":
                        if distancia_al_poc <= 7.0:
                            st.success("🎯 **VEREDICTO: COMPRA DE CONTINUACIÓN**")
                            st.info(f"🧠 *Lectura:* El precio está en máximos pero descansando cerca del soporte (a un {distancia_al_poc:.1f}% del POC). Consolidación sana en la parte alta. Añadir con Stop Loss ajustado.")
                        else:
                            st.warning("⚠️ **VEREDICTO: SOBERANO EXTENDIDO (No Perseguir)**")
                            st.info(f"🧠 *Lectura:* Aunque mantiene la inercia alcista, el precio cotiza un {distancia_al_poc:.1f}% por encima de su POC anual (${poc_promedio:.2f}). Riesgo de corrección alto. Esperar un retroceso para optimizar ratio riesgo/beneficio.")
                    elif estado_censor == "Camino de la Paciencia":
                        st.warning("⚠️ **VEREDICTO: ESPERAR CONFIRMACIÓN**")
                        st.info("🧠 *Lectura:* Fuerza en el maestro pero el precio regresó al promedio de los fondos. El precio podría estancarse un tiempo antes de volver a arrancar.")
                    elif estado_censor == "Camino de Desgastamiento":
                        st.error("🛑 **VEREDICTO: TRAMPA DE MERCADO / DISTRIBUCIÓN**")
                        st.info("🧠 *Lectura:* Alerta máxima. El maestro registra euforia pero las instituciones están vaciando inventario rompiendo el POC hacia abajo. ¡No tocar!")

                elif estado_maestro == "Radar":
                    if estado_censor == "Ignición Latente":
                        if distancia_al_poc <= 7.0:
                            st.success("🎯 **VEREDICTO: ¡COMPRA ÓPTIMA! (Máxima Eficiencia)**")
                            st.info(f"🧠 *Lectura:* El precio cayó cerca del soporte del POC anual (distancia segura del {distancia_al_poc:.1f}%) y los vendedores desaparecieron. Asimetría matemática inmejorable. Stop Loss milimétrico bajo el POC.")
                        else:
                            st.warning("⚠️ **VEREDICTO: ESTRUCTURA EXTENDIDA (No Perseguir)**")
                            st.info(f"🧠 *Lectura:* Aunque la estructura de fondo es alcista, el precio cotiza un {distancia_al_poc:.1f}% por encima del POC anual (${poc_promedio:.2f}). El riesgo de caída técnica es muy profundo para una compra segura. Monitorear y esperar.")
                    elif estado_censor == "Camino de la Paciencia":
                        st.warning("⏳ **VEREDICTO: ACUMULACIÓN LENTA**")
                        st.info("🧠 *Lectura:* Estás comprando al mismo costo que el dinero inteligente. Riesgo bajísimo, pero el capital puede quedarse lateralizado semanas. Paciencia.")
                    elif estado_censor == "Camino de Desgastamiento":
                        st.error("🛑 **VEREDICTO: EVITAR / ALERTA DE DESPLOME**")
                        st.info("🧠 *Lectura:* Las instituciones abandonaron el activo en la zona fría. Si estás dentro y rompe el POC, ejecuta la salida de emergencia de inmediato.")

                elif estado_maestro == "Cruce de Urano":
                    if estado_censor == "Ignición Latente":
                        if distancia_al_poc <= 7.0:
                            st.success("🛰️ **VEREDICTO: ENTRADA PILOTO**")
                            st.info(f"🧠 *Lectura:* El cruce de tendencia inicia sin volumen de venta en contra y cerca del soporte de volumen. Entrar con posición pequeña (ej. 25%).")
                        else:
                            st.warning("⚠️ **VEREDICTO: GIRO EXTENDIDO (Esperar Testeo)**")
                            st.info(f"🧠 *Lectura:* Hay intenciones de cambio de tendencia, pero el precio se disparó un {distancia_al_poc:.1f}% lejos del POC de acumulación. Esperar el 'throwback' (regreso) a la zona de valor.")
                    elif estado_censor == "Camino de la Paciencia":
                        st.success("🛰️ **VEREDICTO: ENTRADA DE GIRO DE ALTA CONVICCIÓN**")
                        st.info("🧠 *Lectura:* El cambio de ciclo ocurre exactamente encima del bloque de volumen anual. Confirmación del piso definitivo de mercado.")
                    elif estado_censor == "Camino de Desgastamiento":
                        st.error("🛑 **VEREDICTO: FALSO CRUCE (Trampa para Toros)**")
                        st.info("🧠 *Lectura:* El precio amaga con cambiar de tendencia arriba pero los bloques reales muestran que se encuentra por debajo del interés mayoritario. Quedarse en liquidez.")
                
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
st.caption("Filtro de volumen autónomo v2.1 - Algoritmo refinado con evaluación de Distancia Crítica de Riesgo.")
