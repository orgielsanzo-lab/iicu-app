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
    "🔥 CRUCE DE URANO": {"Definición": "Ignición por volumen vertical.", "Métrica": "Volumen > 1.8x."},
    "💎 SOBERANO": {"Definición": "Estructura alcista madura.", "Métrica": "RSI < 35, OBV alcista."},
    "🛠️ OLLA RECONSTRUIDA": {"Definición": "Giro institucional en mínimos.", "Métrica": "RVOL > 1.2x, OBV ascendente."},
    "⚡ OLLA DE PRESIÓN": {"Definición": "Compresión de volatilidad.", "Métrica": "FPC > 95, RSI 35-48."},
    "🚀 MOMENTUM TEMPRANO": {"Definición": "Aceleración inicial.", "Métrica": "FPC > 90, RSI 60-68."},
    "🛡️ SACUDIDA INSTITUCIONAL": {"Definición": "Limpieza de stop-loss.", "Métrica": "FPC > 85, RSI < 36."},
    "⏳ ESPERA ESTÉRIL": {"Definición": "Inercia bajista pasiva (sin volumen).", "Métrica": "RVOL < 1.0, OBV plano/descendente."},
    "🛑 OLLA AGUJERADA": {"Definición": "Ruptura crítica con volumen institucional.", "Métrica": "RVOL > 1.2x, OBV descendente."},
    "📡 RADAR": {"Definición": "Estado neutral.", "Métrica": "Sin anomalías."}
}

# --- [II. LÓGICA DE CÁLCULO] ---
def calcular_fpc(ticker):
    try:
        asset = yf.Ticker(ticker)
        info = asset.info
        rd = info.get("researchDevelopment") or info.get("totalOperatingExpenses", 0) * 0.2
        rev = info.get("totalRevenue") or 1
        intensity = abs(rd / rev)
        growth = abs(info.get("revenueGrowth", 0.1))
        fpc_final = 100 * (1 - math.exp(-((intensity * 70) + (growth * 30)) / 2))
        return round(fpc_final, 2)
    except: return 0.0

def auditoria_tecnica(ticker):
    try:
        asset = yf.Ticker(ticker)
        hist = asset.history(period="1y")
        if len(hist) < 200: return None
        
        close = hist["Close"]
        actual = close.iloc[-1]
        
        # Volatilidad Relativa
        vol_med_100 = hist['Volume'].rolling(100).mean().iloc[-1]
        vol_loc_20 = hist['Volume'].tail(20).mean()
        rvol = vol_loc_20 / vol_med_100 if vol_med_100 > 0 else 1.0
        
        # Lógica de Giro/Espera
        hist_200 = hist.tail(200)
        poc_anual = (hist_200['High'] + hist_200['Low'] + hist_200['Close']).mean() / 3
        
        if actual < poc_anual:
            estado = "🛑 OLLA AGUJERADA" if rvol > 1.2 else "⏳ ESPERA ESTÉRIL"
        else:
            estado = "📡 RADAR" # Mantener tu lógica de estados superiores aquí
            
        return {"Sigla": ticker, "Precio": round(actual, 2), "Estado": estado, "Diagnóstico": DICCIONARIO_ESTADOS[estado]["Definición"]}
    except: return None

# --- [III. INTERFAZ] ---
st.set_page_config(page_title="IICU-100 Soberanía", layout="wide")

nodo = st.selectbox("Seleccionar Nodo", list(PILARES.keys()))
if st.button("EJECUTAR AUDITORÍA"):
    res = [auditoria_tecnica(t) for t in PILARES[nodo]]
    df = pd.DataFrame([r for r in res if r])
    st.dataframe(df, use_container_width=True)
    
    # Renderizado condicional del Panel Maestro
    for _, row in df.iterrows():
        if row["Estado"] == "⏳ ESPERA ESTÉRIL":
            st.markdown(f"**{row['Sigla']}**: [NEUTRAL] - Inercia pasiva. Sin acción.")
