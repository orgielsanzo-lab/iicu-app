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

# --- LÓGICA DE OPTIMIZACIÓN (CORRECCIONES APLICADAS) ---

def obtener_bins_dinamicos(precio_actual):
    """Ajuste de resolución según magnitud del activo."""
    if precio_actual > 500: return 250
    if precio_actual > 100: return 150
    return 80

def calcular_rvol_preciso(df_20, df_100):
    """RVOL filtrado por percentil para evitar sesgos de bajo volumen."""
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
    max_idx = np.argmax(counts)
    return (bin_edges[max_idx] + bin_edges[max_idx + 1]) / 2

# --- INTERFAZ Y EJECUCIÓN ---
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
            
            # Aplicación de Bins Dinámicos
            bins_ajustados = obtener_bins_dinamicos(precio_actual)
            poc_anual = float(calcular_poc_segmento(df_200, bins=bins_ajustados))
            poc_local = float(calcular_poc_segmento(df_20, bins=bins_ajustados))
            
            # Cálculo de RVOL Preciso
            rvol = calcular_rvol_preciso(df_20, df_100)
            
            # Lógica de Tendencia OBV
            df_completo['OBV'] = (np.sign(df_completo['Close'].diff()) * df_completo['Volume']).fillna(0).cumsum()
            slope, _, _, _, _ = linregress(np.arange(20), df_completo['OBV'].iloc[-20:].values)
            
            # Clasificación de Estado
            bajo_poc_anual = precio_actual < poc_anual
            sostiene_poc_local = precio_actual >= (poc_local * 0.985)
            rvol_alto = rvol >= 1.2
            
            if bajo_poc_anual:
                estado_censor = "Giro Detectado / Olla Reconstruida" if (sostiene_poc_local and rvol_alto and slope > 0) else \
                                "Olla Agujerada / Ruptura de Liquidez" if (not sostiene_poc_local and rvol_alto) else "Inercia Bajista Pasiva (Sin Volumen)"
            else:
                distancia = ((precio_actual - poc_anual) / poc_anual) * 100
                estado_censor = "Zona de Acumulación Segura" if distancia <= 5.0 else "Ignición Latente / Escape" if distancia <= 12.0 else "Exclusión por Sobreextensión"

            # Renderizado
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Precio", f"${precio_actual:.2f}")
            m2.metric("POC 200d", f"${poc_anual:.2f}")
            m3.metric("POC 20d", f"${poc_local:.2f}")
            m4.metric("RVOL", f"{rvol:.2f}x")
            
            st.markdown("---")
            # [Lógica de renderizado de estados omitida por brevedad, se mantiene igual]
            # ... (Aquí el resto de la lógica de renderizado y el gráfico plotly actualizado con bins_ajustados)
            st.info(f"Diagnóstico actual: **{estado_censor}**. Resolución de análisis: {bins_ajustados} bins.")
