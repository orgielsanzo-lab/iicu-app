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

# --- [II. LÓGICA DE AUDITORÍA Y CÁLCULOS] ---
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
        pilares_data = []
        for t in df_pilar["Sigla"]:
            h = yf.Ticker(t).history(period="1y")["Close"]
            if not h.empty: pilares_data.append((h / h.iloc[0]) * 100)
        iicu_norm = pd.concat(pilares_data, axis=1).mean(axis=1)
        ret_iicu = round(iicu_norm.iloc[-1] - 100, 2)
        ret_spy = round(bench_norm.iloc[-1] - 100, 2)
        alpha = round(ret_iicu - ret_spy, 2)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=bench_norm.index, y=bench_norm, name="S&P 500", line=dict(color="#888888", dash="dot")))
        fig.add_trace(go.Scatter(x=iicu_norm.index, y=iicu_norm, name="IICU-100", line=dict(color="#00FFAA", width=4)))
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#e0e0e0"), height=400, margin=dict(l=0, r=0, t=30, b=0), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        return fig, alpha, ret_iicu
    except: return None, 0, 0

def auditoria_tecnica(ticker):
    try:
        asset = yf.Ticker(ticker)
        hist = asset.history(period="1y")
        if len(hist) < 200: return None
        close = hist["Close"]
        sma200, sma50, actual = close.rolling(200).mean().iloc[-1], close.rolling(50).mean().iloc[-1], close.iloc[-1]
        delta = close.diff()
        gain, loss = (delta.where(delta > 0, 0)).rolling(14).mean(), (-delta.where(delta < 0, 0)).rolling(14).mean()
        rsi = (100 - (100 / (1 + (gain / loss)))).iloc[-1]
        hist["OBV"] = (np.sign(close.diff()) * hist["Volume"]).fillna(0).cumsum()
        obv_trend = hist["OBV"].iloc[-1] > hist["OBV"].rolling(10).mean().iloc[-1]
        
        # Perfiles de Volumen
        poc_anual = pd.cut(hist.tail(200)['Close'], bins=20).value_counts().idxmax().mid
        poc_local = pd.cut(hist.tail(20)['Close'], bins=10).value_counts().idxmax().mid
        
        rvol_local = hist.tail(20)['Volume'].mean() / hist['Volume'].rolling(100).mean().iloc[-1]
        giro_en_base = (actual < (poc_anual * 0.98) and actual >= (poc_local * 0.98) and rvol_local > 1.15 and hist['OBV'].iloc[-1] > hist['OBV'].iloc[-5])
        
        es_soberano = (actual > sma200 and sma50 > sma200 and rsi < 35 and obv_trend)
        ignicion = False
        if es_soberano:
            div_rsi = rsi > (100 - (100 / (1 + (gain.iloc[-3] / loss.iloc[-3]))))
            if (hist["Volume"].iloc[-1] / hist["Volume"].rolling(20).mean().iloc[-1] > 1.8) or (div_rsi and actual < close.iloc[-3]):
                ignicion = True

        if ignicion: estado = "🔥 CRUCE DE URANO"
        elif es_soberano: estado = "💎 SOBERANO"
        elif giro_en_base: estado = "🛠️ OLLA RECONSTRUIDA"
        elif obv_trend:
            fpc = calcular_fpc(ticker)
            if fpc > 95 and 35 <= rsi <= 48: estado = "⚡ OLLA DE PRESIÓN"
            elif actual > sma200 and fpc > 90 and 60 <= rsi <= 68: estado = "🚀 MOMENTUM TEMPRANO"
            elif actual > sma200 and fpc > 85 and rsi < 36: estado = "🛡️ SACUDIDA INSTITUCIONAL"
            else: estado = "📡 RADAR"
        else: estado = "📡 RADAR"
        
        return {"Sigla": ticker, "Precio": round(actual, 2), "RSI": round(rsi, 1), "FPC (Peso)": calcular_fpc(ticker), "SMA 200": "✅" if actual > sma200 else "❌", "Flujo": "💹" if obv_trend else "📉", "Estado": estado, "Diagnóstico": DICCIONARIO_ESTADOS[estado]["Definición"], "Criterio": DICCIONARIO_ESTADOS[estado]["Métrica"]}
    except: return None

# --- [III. INTERFAZ] ---
st.set_page_config(page_title="IICU-100 Soberanía", layout="wide")
st.markdown("<style>.stApp { background-color: #050505; color: #e0e0e0; }</style>", unsafe_allow_html=True)
st.title("🏛️ IICU-100: ENGINE DE SOBERANÍA TÉCNICA")
nodo_seleccionado = st.sidebar.selectbox("Seleccionar Nodo de Poder", list(PILARES.keys()))

if st.button("EJECUTAR AUDITORÍA DE NODO"):
    res_list = [auditoria_tecnica(t) for t in PILARES[nodo_seleccionado]]
    st.session_state["audit_data"] = pd.DataFrame([r for r in res_list if r])

if "audit_data" in st.session_state:
    st.dataframe(st.session_state["audit_data"], use_container_width=True)
    fig, val_alpha, ret_iicu = calcular_rendimiento_y_alpha(st.session_state["audit_data"])
    if fig:
        st.metric("ALFA DE SOBERANÍA", f"{val_alpha}%")
        st.plotly_chart(fig, use_container_width=True)
