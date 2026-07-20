import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import linregress

# --- CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="Censor de Volumen - IICU-100", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, h2, h3 { color: #00FFAA; text-shadow: 0px 0px 8px rgba(0, 255, 170, 0.4); }
    .report-box { padding: 20px; border-radius: 10px; margin: 15px 0px; }
    div[data-testid="stMetricValue"] { color: #00FFAA !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ CENSOR DE VOLUMEN E HISTOGRAMA INSTITUCIONAL")
st.subheader("Filtro v4.4.1 - Motor con Bins Dinámicos y RVOL Ponderado")

# --- LÓGICA DE OPTIMIZACIÓN ---
def obtener_bins_dinamicos(precio_actual):
    if precio_actual > 500: return 250
    if precio_actual > 100: return 150
    return 80

def calcular_rvol_preciso(df_20, df_100):
    vol_filtro = df_100['Volume'].quantile(0.1) 
    df_100_limpio = df_100[df_100['Volume'] > vol_filtro]
    vol_prom_20 = df_20['Volume'].mean()
    vol_prom_100 = df_100_limpio['Volume'].mean()
    return float(vol_prom_20 / vol_prom_100) if vol_prom_100 > 0 else 1.0

@st.cache_data(ttl=600)
def obtener_datos_mercado(ticker_symbol):
    try:
        asset = yf.Ticker(ticker_symbol)
        df = asset.history(period="2y")
        if df.empty or len(df) < 200: return None
        return df.dropna(subset=['Close', 'Volume', 'High', 'Low'])
    except Exception:
        return None

def calcular_poc_segmento(df_slice, bins=50):
    if df_slice.empty: return np.nan
    price_min, price_max = df_slice['Low'].min(), df_slice['High'].max()
    if price_min == price_max: return price_min
    typical_price = (df_slice['High'] + df_slice['Low'] + df_slice['Close']) / 3
    counts, bin_edges = np.histogram(typical_price, bins=bins, range=(price_min, price_max), weights=df_slice['Volume'])
    return (bin_edges[np.argmax(counts)] + bin_edges[np.argmax(counts) + 1]) / 2

# --- INTERFAZ ---
col_ticker, col_maestro = st.columns(2)
with col_ticker: ticker = st.text_input("INGRESA EL TICKER:", "").upper().strip()
with col_maestro: estado_maestro = st.selectbox("ESTADO DEL PANEL MAESTRO:", 
    ["🔥 CRUCE DE URANO", "💎 SOBERANO", "⚡ OLLA DE PRESIÓN", "🛠️ OLLA RECONSTRUIDA", "🚀 MOMENTUM TEMPRANO", "🛡️ SACUDIDA INSTITUCIONAL", "📡 RADAR"])

if ticker:
    with st.spinner(f"Analizando microestructura de {ticker}..."):
        df_completo = obtener_datos_mercado(ticker)
        if df_completo is None:
            st.error("❌ Datos insuficientes.")
        else:
            df_200, df_100, df_20 = df_completo.iloc[-200:], df_completo.iloc[-100:], df_completo.iloc[-20:]
            precio_actual = float(df_completo['Close'].iloc[-1])
            bins = obtener_bins_dinamicos(precio_actual)
            
            poc_anual = float(calcular_poc_segmento(df_200, bins=bins))
            poc_local = float(calcular_poc_segmento(df_20, bins=bins))
            rvol = calcular_rvol_preciso(df_20, df_100)
            
            df_completo['OBV'] = (np.sign(df_completo['Close'].diff()) * df_completo['Volume']).fillna(0).cumsum()
            slope, _, _, _, _ = linregress(np.arange(20), df_completo['OBV'].iloc[-20:].values)
            
            # Clasificación
            bajo_poc_anual = precio_actual < poc_anual
            sostiene_poc_local = precio_actual >= (poc_local * 0.985)
            rvol_alto = rvol >= 1.2
            
            if bajo_poc_anual:
                estado_censor = "Giro Detectado / Olla Reconstruida" if (sostiene_poc_local and rvol_alto and slope > 0) else \
                                "Olla Agujerada / Ruptura de Liquidez" if (not sostiene_poc_local and rvol_alto) else "Inercia Bajista Pasiva (Sin Volumen)"
            else:
                distancia = ((precio_actual - poc_anual) / poc_anual) * 100
                estado_censor = "Zona de Acumulación Segura" if distancia <= 5.0 else "Ignición Latente / Escape" if distancia <= 12.0 else "Exclusión por Sobreextensión"

            # Renderizado de métricas
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Precio", f"${precio_actual:.2f}")
            m2.metric("POC 200d", f"${poc_anual:.2f}")
            m3.metric("POC 20d", f"${poc_local:.2f}")
            m4.metric("RVOL", f"{rvol:.2f}x")
            
            st.markdown("---")
            st.markdown(f"### 📊 Diagnóstico Físico de Flujo para **{ticker}**")
            
            # Bloques de estados
            if estado_censor == "Olla Agujerada / Ruptura de Liquidez":
                st.markdown(f'<div class="report-box" style="background-color: rgba(255, 0, 0, 0.1); border: 2px solid #FF3333;"><h3>🛑 OLLA AGUJERADA</h3><p>Precio (<b>${precio_actual:.2f}</b>) bajo soporte con RVOL de <b>{rvol:.2f}x</b>. Salida de capital.</p></div>', unsafe_allow_html=True)
            elif estado_censor == "Giro Detectado / Olla Reconstruida":
                st.markdown(f'<div class="report-box" style="background-color: rgba(0, 255, 170, 0.1); border: 2px solid #00FFAA;"><h3>🛠️ OLLA RECONSTRUIDA</h3><p>Absorción institucional confirmada. RVOL: <b>{rvol:.2f}x</b>. Compras escalonadas.</p></div>', unsafe_allow_html=True)
            elif estado_censor == "Inercia Bajista Pasiva (Sin Volumen)":
                st.markdown(f'<div class="report-box" style="background-color: rgba(150, 150, 150, 0.1); border: 2px solid #888888;"><h3>⏳ INERCIA BAJISTA PASIVA</h3><p>Goteo sin volumen. Esperar anomalía.</p></div>', unsafe_allow_html=True)
            elif estado_censor == "Zona de Acumulación Segura":
                st.markdown(f'<div class="report-box" style="background-color: rgba(0, 255, 170, 0.1); border: 2px solid #00FFAA;"><h3>🟢 ZONA DE ACUMULACIÓN</h3><p>El precio actúa sobre el colchón gravitacional.</p></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="report-box" style="border: 2px solid #FFEA00;"><h3>⚠️ {estado_censor}</h3></div>', unsafe_allow_html=True)

           # --- GRÁFICO ---
            fig = go.Figure()
            
            # Histograma del perfil de volumen (200d)
            typical_price_200 = (df_200['High'] + df_200['Low'] + df_200['Close']) / 3
            counts_200, bin_edges_200 = np.histogram(typical_price_200.values, bins=bins, weights=df_200['Volume'].values)
            
            fig.add_trace(go.Bar(
                y=[(bin_edges_200[i] + bin_edges_200[i+1])/2 for i in range(len(counts_200))], 
                x=counts_200, 
                orientation='h', 
                name='Perfil 200d', 
                marker=dict(color='rgba(0, 255, 170, 0.12)')
            ))
            
            # Línea de Precio Actual
            fig.add_trace(go.Scatter(
                x=[0, max(counts_200)], y=[precio_actual, precio_actual], 
                mode='lines', name=f'Precio (${precio_actual:.2f})', 
                line=dict(color='#FF3388', width=2)
            ))
            
            # Línea de POC Anual (200d)
            fig.add_trace(go.Scatter(
                x=[0, max(counts_200)], y=[poc_anual, poc_anual], 
                mode='lines', name=f'POC Anual (${poc_anual:.2f})', 
                line=dict(color='#00FFAA', width=2, dash='dash')
            ))
            
            # --- NUEVA LÍNEA: POC LOCAL (20d) ---
            fig.add_trace(go.Scatter(
                x=[0, max(counts_200)], y=[poc_local, poc_local], 
                mode='lines', name=f'POC Local 20d (${poc_local:.2f})', 
                line=dict(color='#FFEA00', width=2, dash='dot')
            ))
            
            fig.update_layout(
                title=f"Distribución con {bins} Bins - {ticker}", 
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)', 
                font=dict(color="#e0e0e0"), 
                height=450,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            st.plotly_chart(fig, use_container_width=True)
