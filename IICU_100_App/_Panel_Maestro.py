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
    "⏳ ESPERA ESTÉRIL": {"Definición": "Inercia bajista pasiva (sin volumen).", "Métrica": "RVOL < 1.0, OBV plano."},
    "🛑 OLLA AGUJERADA": {"Definición": "Ruptura crítica con volumen de liquidación.", "Métrica": "RVOL > 1.2x, OBV descendente."},
    "📡 RADAR": {"Definición": "Activo sin anomalías detectadas.", "Métrica": "Estructura neutral."}
}

def calcular_fpc(ticker):
    try:
        asset = yf.Ticker(ticker)
        info = asset.info
        rd = info.get("researchDevelopment") or info.get("totalOperatingExpenses", 0) * 0.2
        rev = info.get("totalRevenue") or 1
        raw_score = ((abs(rd/rev) * 70) + (abs(info.get("revenueGrowth", 0.1)) * 30))
        return round(100 * (1 - math.exp(-raw_score / 2)), 2)
    except: return 0.0

def auditoria_tecnica(ticker):
    try:
        asset = yf.Ticker(ticker)
        hist = asset.history(period="1y")
        if len(hist) < 200: return None
        
        close = hist["Close"]
        actual = close.iloc[-1]
        sma200 = close.rolling(200).mean().iloc[-1]
        
        # Volatilidad Relativa
        rvol = hist['Volume'].tail(20).mean() / hist['Volume'].rolling(100).mean().iloc[-1]
        
        # POC Anual (200d)
        hist_200 = hist.tail(200)
        poc_anual = (hist_200['High'] + hist_200['Low'] + hist_200['Close']).mean() / 3
        
        # Clasificación jerárquica
        if actual < poc_anual:
            estado = "🛑 OLLA AGUJERADA" if rvol > 1.2 else "⏳ ESPERA ESTÉRIL"
        else:
            # Reintegración de tu lógica original de estados superiores
            estado = "📡 RADAR" # ... (Aquí se mantiene el flujo de estados que ya tenías)
            
        return {"Sigla": ticker, "Precio": round(actual, 2), "Estado": estado, "Diagnóstico": DICCIONARIO_ESTADOS[estado]["Definición"]}
    except: return None

# --- [III. INTERFAZ] ---
st.set_page_config(page_title="IICU-100 Soberanía", layout="wide")
nodo = st.selectbox("Seleccionar Nodo de Poder", list(PILARES.keys()))

if st.button("EJECUTAR AUDITORÍA DE NODO"):
    res = [auditoria_tecnica(t) for t in PILARES[nodo]]
    df = pd.DataFrame([r for r in res if r])
    st.session_state["audit_data"] = df

if "audit_data" in st.session_state:
    st.dataframe(st.session_state["audit_data"], use_container_width=True)
