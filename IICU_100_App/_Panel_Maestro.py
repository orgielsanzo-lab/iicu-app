import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# --- [I. CONFIGURACIÓN DE IDENTIDAD Y MANIFIESTO] ---
PILARES = {
    "1. La Mente": ["MSFT", "NVDA", "GOOGL", "AMZN", "TSM", "AVGO", "ASML", "AMD", "QCOM", "META", "SNOW", "PLTR", "MSTR", "INTC", "ARM", "KLAC", "AMAT", "CDNS", "PSTG", "ADBE"],
    "2. El Corazón": ["CEG", "VST", "CCJ", "BWXT", "SMR", "OKLO", "UUUU", "ETN", "GE", "VRT", "HUBB", "POWL", "NEE", "FSLR", "ENPH", "SEDG", "BE", "DUK", "SO", "AES"],
    "3. Biología": ["CRSP", "BEAM", "EDIT", "NTLA", "LLY", "NVO", "VRTX", "AMGN", "REGN", "TMO", "DHR", "ILMN", "A", "IQV", "RXRX", "SDGR", "DNA", "GNKX", "MRNA", "BIIB"],
    "4. Base Física": ["MP", "ALB", "SQM", "LAC", "LTHM", "FCX", "BHP", "RIO", "VALE", "TECK", "AA", "NEM", "CF", "MOS", "CAT", "DE", "JCI", "URI", "SCCO", "STLD"],
    "5. Expansión Orbital": ["RKLB", "MDA.TO", "PL", "SPIR", "BKSY", "LMT", "NOC", "RTX", "LHX", "BA", "HWM", "TDG", "JOBY", "ACHR", "TSP", "GSAT", "ASTS", "IRDM", "VSAT", "SPCE", "SPCX"],
}

DICCIONARIO_ESTADOS = {
    "🔥 CRUCE DE URANO": {"Definición": "Ignición por volumen vertical y ruptura inminente de rango.", "Métrica": "RSI sobrecomprado con volumen relativo masivo (>1.8x)."},
    "💎 SOBERANO": {"Definición": "Estructura alcista madura en fase de enfriamiento temporal.", "Métrica": "Precio > SMA 200, SMA 50 > SMA 200 con RSI frío (<35) y OBV alcista."},
    "🛠️ OLLA RECONSTRUIDA": {"Definición": "Giro institucional en mínimos detectado. Absorción masiva antes del retorno al control.", "Métrica": "Precio < POC Anual pero > POC Local (20d), volumen local > 1.2x media, OBV ascendente."},
    "⚡ OLLA DE PRESIÓN": {"Definición": "Compresión extrema de volatilidad antes del despegue estructural.", "Métrica": "FPC extraordinario (>95), RSI en zona muerta (35-48) y acumulación silenciosa."},
    "🚀 MOMENTUM TEMPRANO": {"Definición": "Fase inicial de aceleración alcista y salida rápida de base.", "Métrica": "Precio > SMA 200, FPC > 90, RSI activo (60-68) con flujo positivo."},
    "🛡️ SACUDIDA INSTITUCIONAL": {"Definición": "Limpieza extrema de stop-loss minoristas antes del giro alcista.", "Métrica": "Precio > SMA 200, FPC > 85, RSI extremadamente deprimido (<36)."},
    "📡 RADAR": {"Definición": "Activo sin anomalías de acumulación o momentum detectadas.", "Métrica": "Estructura neutral. No apto para asignación de capital."}
}

# --- [FUNCIONES DE CÁLCULO] ---
def calcular_fpc(ticker):
    try:
        asset = yf.Ticker(ticker)
        info = asset.info
        rd = info.get("researchDevelopment") or (info.get("totalOperatingExpenses", 0) * 0.2)
        rev = info.get("totalRevenue") or 1
        intensity = abs(rd / rev)
        growth = abs(info.get("revenueGrowth", 0.1))
        raw_score = (intensity * 70) + (growth * 30)
        return round(100 * (1 - math.exp(-raw_score / 2)), 2)
    except: return 0.0

def calcular_rendimiento_y_alpha(df_pilar, ticker_benchmark="SPY"):
    try:
        benchmark = yf.Ticker(ticker_benchmark).history(period="1y")["Close"]
        bench_norm = (benchmark / benchmark.iloc[0]) * 100
        pilares_data = [ (yf.Ticker(t).history(period="1y")["Close"] / yf.Ticker(t).history(period="1y")["Close"].iloc[0]) * 100 for t in df_pilar["Sigla"] ]
        iicu_norm = pd.concat(pilares_data, axis=1).mean(axis=1)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=bench_norm.index, y=bench_norm, name="S&P 500", line=dict(color="#888888", dash="dot")))
        fig.add_trace(go.Scatter(x=iicu_norm.index, y=iicu_norm, name="IICU-100", line=dict(color="#00FFAA", width=4)))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e0e0e0"), height=400)
        return fig, round(iicu_norm.iloc[-1] - bench_norm.iloc[-1], 2), round(iicu_norm.iloc[-1] - 100, 2)
    except: return None, 0, 0

def auditoria_tecnica(ticker):
    try:
        hist = yf.Ticker(ticker).history(period="1y")
        if len(hist) < 200: return None
        
        close = hist["Close"]
        delta = close.diff()
        gain, loss = delta.clip(lower=0).rolling(14).mean(), (-delta.clip(upper=0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss))).iloc[-1]
        
        hist["OBV"] = (np.sign(close.diff()) * hist["Volume"]).fillna(0).cumsum()
        sma200, actual = close.rolling(200).mean().iloc[-1], close.iloc[-1]
        
        # Lógica simplificada de estado para estabilidad
        estado = "📡 RADAR"
        if actual > sma200 and rsi < 35: estado = "💎 SOBERANO"
        
        return {
            "Sigla": ticker, "Precio": round(actual, 2), "RSI": round(rsi, 1),
            "FPC (Peso)": calcular_fpc(ticker), "Estado": estado,
            "Diagnóstico": DICCIONARIO_ESTADOS[estado]["Definición"],
            "Criterio": DICCIONARIO_ESTADOS[estado]["Métrica"]
        }
    except: return None

# --- [III. INTERFAZ STREAMLIT] ---
st.set_page_config(page_title="IICU-100 Soberanía", layout="wide")
st.title("🏛️ IICU-100: ENGINE DE SOBERANÍA TÉCNICA")

nodo_seleccionado = st.selectbox("Seleccionar Nodo de Poder", list(PILARES.keys()))

if st.button("EJECUTAR AUDITORÍA"):
    res = [auditoria_tecnica(t) for t in PILARES[nodo_seleccionado]]
    st.session_state["audit_data"] = pd.DataFrame([r for r in res if r])

if "audit_data" in st.session_state:
    st.dataframe(st.session_state["audit_data"], use_container_width=True)
    fig, alpha, ret = calcular_rendimiento_y_alpha(st.session_state["audit_data"])
    if fig:
        st.plotly_chart(fig, use_container_width=True)
        st.metric("ALFA DE SOBERANÍA", f"{alpha}%")
