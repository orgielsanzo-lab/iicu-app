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
ticker = st.text_input("INGRESA EL TICKER (Ej: SMR, OKLO, MSFT):", "").upper().strip()

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
                # Dividimos el rango de precios del año en 20 zonas (bins)
                counts, bin_edges = np.histogram(valores_precio, bins=20, weights=volumenes)
                max_volume_bin_index = np.argmax(counts)
                poc_inferior = bin_edges[max_volume_bin_index]
                poc_superior = bin_edges[max_volume_bin_index + 1]
                poc_promedio = (poc_inferior + poc_superior) / 2
                
                # Umbral de tolerancia del 1.5% para la zona de equilibrio
                umbral = poc_promedio * 0.015
                
                # 2. CLASIFICACIÓN DE CAMINOS Y RENDERIZADO DE RESULTADOS
                st.markdown("---")
                st.markdown(f"### 📊 Veredicto de Estructura para **{ticker}**")
                
                if precio_actual < (poc_promedio - umbral):
                    # --- CAMINO DE DESGASTAMIENTO ---
                    st.markdown(f"""
                    <div class="report-box" style="background-color: rgba(255, 0, 0, 0.1); border: 2px solid #FF3333;">
                        <h3 style="color: #FF3333; margin-top:0;">❌ CAMINO DE DESGASTAMIENTO (Descartar Inversión)</h3>
                        <p><b>Diagnóstico:</b> El precio actual (<b>${precio_actual:.2f}</b>) ha quebrado a la baja el muro de volumen institucional (POC) situado en <b>${poc_promedio:.2f}</b>.</p>
                        <p><b>Riesgo:</b> Las manos fuertes que acumularon este año están bajo pérdida o distribuyendo material. La probabilidad de que rompa la SMA 200 hacia abajo y regrese a RADAR es críticamente alta.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                elif abs(precio_actual - poc_promedio) <= umbral:
                    # --- CAMINO DE LA PACIENCIA ---
                    st.markdown(f"""
                    <div class="report-box" style="background-color: rgba(255, 165, 0, 0.1); border: 2px solid #FFA500;">
                        <h3 style="color: #FFA500; margin-top:0;">⏳ CAMINO DE LA PACIENCIA (Acumulación Lenta)</h3>
                        <p><b>Diagnóstico:</b> El precio actual (<b>${precio_actual:.2f}</b>) se encuentra exactamente en la zona de equilibrio institucional (POC) de <b>${poc_promedio:.2f}</b>.</p>
                        <p><b>Estrategia:</b> Zona con riesgo de caída bajísimo porque estás comprando al precio promedio de los fondos de inversión. Sin embargo, el capital puede quedarse congelado semanas lateralizando antes de despertar.</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                else:
                    # --- CAMINO DE LA IGNICIÓN LATENTE ---
                    st.markdown(f"""
                    <div class="report-box" style="background-color: rgba(0, 255, 170, 0.1); border: 2px solid #00FFAA;">
                        <h3 style="color: #00FFAA; margin-top:0;">🚀 IGNICIÓN LATENTE (Fase Altamente Eficiente)</h3>
                        <p><b>Diagnóstico:</b> El activo defiende el precio actual (<b>${precio_actual:.2f}</b>) por encima del bloque de volumen anual (<b>${poc_promedio:.2f}</b>).</p>
                        <p><b>Estrategia:</b> Estructura óptima de continuación alcista. Las compras institucionales previas actúan como un trampolín sólido. Es la ventana de tiempo más eficiente para colocar capital.</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # --- 3. GRÁFICO VISUAL DEL PERFIL DE VOLUMEN HORIZONTAL ---
                # Creamos el histograma de volumen horizontal usando Plotly
                fig = go.Figure()
                
                # Histograma horizontal (Barras de Volumen por Precio)
                fig.add_trace(go.Bar(
                    y=[(bin_edges[i] + bin_edges[i+1])/2 for i in range(len(counts))],
                    x=counts,
                    orientation='h',
                    name='Volumen Transaccionado',
                    marker=dict(color='rgba(0, 255, 170, 0.2)', line=dict(color='#00FFAA', width=1))
                ))
                
                # Línea del Precio Actual
                fig.add_trace(go.Scatter(
                    x=[0, max(counts)],
                    y=[precio_actual, precio_actual],
                    mode='lines',
                    name=f'Precio Actual (${precio_actual:.2f})',
                    line=dict(color='#FF3388', width=3)
                ))
                
                # Línea del POC Institucional
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
st.caption("Filtro de volumen autónomo v1.0 - Basado en la segmentación de acumulación por densidad de ticks.")