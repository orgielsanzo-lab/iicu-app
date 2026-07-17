import math
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf

# --- [I. CONFIGURACIÓN DE IDENTIDAD Y MANIFIESTO] ---
PILARES = {
    "1. La Mente": [
        "MSFT", "NVDA", "GOOGL", "AMZN", "TSM", "AVGO", "ASML", "AMD", "QCOM", "META",
        "SNOW", "PLTR", "MSTR", "INTC", "ARM", "KLAC", "AMAT", "CDNS", "PSTG", "ADBE"
    ],
    "2. El Corazón": [
        "CEG", "VST", "CCJ", "BWXT", "SMR", "OKLO", "UUUU", "ETN", "GE", "VRT",
        "HUBB", "POWL", "NEE", "FSLR", "ENPH", "SEDG", "BE", "DUK", "SO", "AES"
    ],
    "3. Biología": [
        "CRSP", "BEAM", "EDIT", "NTLA", "LLY", "NVO", "VRTX", "AMGN", "REGN", "TMO",
        "DHR", "ILMN", "A", "IQV", "RXRX", "SDGR", "DNA", "GNKX", "MRNA", "BIIB"
    ],
    "4. Base Física": [
        "MP", "ALB", "SQM", "LAC", "LTHM", "FCX", "BHP", "RIO", "VALE", "TECK",
        "AA", "NEM", "CF", "MOS", "CAT", "DE", "JCI", "URI", "SCCO", "STLD"
    ],
    "5. Expansión Orbital": [
        "RKLB", "MDA.TO", "PL", "SPIR", "BKSY", "LMT", "NOC", "RTX", "LHX", "BA",
        "HWM", "TDG", "JOBY", "ACHR", "TSP", "GSAT", "ASTS", "IRDM", "VSAT", "SPCE", "SPCX"
    ],
}

# Diccionario de Estados Actualizado (Inclusión de Olla Reconstruida)
DICCIONARIO_ESTADOS = {
    "🔥 CRUCE DE URANO": {
        "Definición": "Ignición por volumen vertical y ruptura inminente de rango.",
        "Métrica": "RSI sobrecomprado con volumen relativo masivo (>1.8x)."
    },
    "💎 SOBERANO": {
        "Definición": "Estructura alcista madura en fase de enfriamiento temporal.",
        "Métrica": "Precio > SMA 200, SMA 50 > SMA 200 con RSI frío (<35) y OBV alcista."
    },
    "🛠️ OLLA RECONSTRUIDA": {
        "Definición": "Giro institucional en mínimos detectado. Absorción masiva antes del retorno al control.",
        "Métrica": "Precio < POC Anual pero > POC Local (20d), volumen local > 1.2x media, OBV ascendente."
    },
    "⚡ OLLA DE PRESIÓN": {
        "Definición": "Compresión extrema de volatilidad antes del despegue estructural.",
        "Métrica": "FPC extraordinario (>95), RSI en zona muerta (35-48) y acumulación silenciosa."
    },
    "🚀 MOMENTUM TEMPRANO": {
        "Definición": "Fase inicial de aceleración alcista y salida rápida de base.",
        "Métrica": "Precio > SMA 200, FPC > 90, RSI activo (60-68) con flujo positivo."
    },
    "🛡️ SACUDIDA INSTITUCIONAL": {
        "Definición": "Limpieza extrema de stop-loss minoristas antes del giro alcista.",
        "Métrica": "Precio > SMA 200, FPC > 85, RSI extremadamente deprimido (<36)."
    },
    "📡 RADAR": {
        "Definición": "Activo sin anomalías de acumulación o momentum detectadas.",
        "Métrica": "Estructura neutral. No apto para asignación de capital."
    }
}

def calcular_fpc(ticker):
    try:
        asset = yf.Ticker(ticker)
        info = asset.info
        rd = info.get("researchDevelopment")
        if rd is None or rd == 0:
            rd = info.get("totalOperatingExpenses", 0) * 0.2
        rev = info.get("totalRevenue", 1)
        if rev <= 0:
            rev = 1
        intensity = abs(rd / rev)
        growth = abs(info.get("revenueGrowth", 0.1))
        raw_score = (intensity * 70) + (growth * 30)
        fpc_final = 100 * (1 - math.exp(-raw_score / 2))
        return round(fpc_final, 2)
    except:
        return 0.0

def calcular_rendimiento_y_alpha(df_pilar, ticker_benchmark="SPY"):
    try:
        benchmark = yf.Ticker(ticker_benchmark).history(period="1y")["Close"]
        if benchmark.empty:
            return None, 0, 0
        bench_norm = (benchmark / benchmark.iloc[0]) * 100

        pilares_data = []
        for t in df_pilar["Sigla"]:
            h = yf.Ticker(t).history(period="1y")["Close"]
            if not h.empty:
                pilares_data.append((h / h.iloc[0]) * 100)

        iicu_norm = pd.concat(pilares_data, axis=1).mean(axis=1)

        ret_iicu = round(iicu_norm.iloc[-1] - 100, 2)
        ret_spy = round(bench_norm.iloc[-1] - 100, 2)
        alpha = round(ret_iicu - ret_spy, 2)

        fig = go.Figure()
        fig.add_trace(go.Scatter(x=bench_norm.index, y=bench_norm, name="S&P 500", line=dict(color="#888888", dash="dot")))
        fig.add_trace(go.Scatter(x=iicu_norm.index, y=iicu_norm, name="IICU-100", line=dict(color="#00FFAA", width=4)))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e0e0e0"),
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig, alpha, ret_iicu
    except:
        return None, 0, 0


# --- [II. MOTOR DE AUDITORÍA CUÁNTICA - CAPAS 2, 3 Y MÓDULO DE ROTACIÓN] ---
def auditoria_tecnica(ticker):
    try:
        asset = yf.Ticker(ticker)
        hist = asset.history(period="1y")
        if len(hist) < 200:
            return None

        # 1. Indicadores Base
        close = hist["Close"]
        sma200 = close.rolling(200).mean().iloc[-1]
        sma50 = close.rolling(50).mean().iloc[-1]
        actual = close.iloc[-1]

        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]

        # OBV base
        hist["OBV"] = (np.sign(close.diff()) * hist["Volume"]).fillna(0).cumsum()
        obv_trend = hist["OBV"].iloc[-1] > hist["OBV"].rolling(10).mean().iloc[-1]

        fpc_valor = calcular_fpc(ticker)
        sma200_ok = actual > sma200

        # 2. CÁLCULO DE PERFILES DE VOLUMEN (POC ANUAL VS POC LOCAL)
        # POC Anual (200 días)
        hist_200 = hist.tail(200).copy()
        bins_200 = 20
        hist_200['price_bin'] = pd.cut(hist_200['Close'], bins=bins_200)
        vol_profile_200 = hist_200.groupby('price_bin', observed=False)['Volume'].sum()
        poc_anual = vol_profile_200.idxmax().mid

        # POC Local (últimos 20 días para detectar consolidaciones en base)
        hist_20 = hist.tail(20).copy()
        bins_20 = 10
        hist_20['price_bin'] = pd.cut(hist_20['Close'], bins=bins_20)
        vol_profile_20 = hist_20.groupby('price_bin', observed=False)['Volume'].sum()
        poc_local = vol_profile_20.idxmax().mid

        # 3. Métricas de Soporte de Volumen
        volumen_media_100 = hist['Volume'].rolling(100).mean().iloc[-1]
        volumen_media_local = hist_20['Volume'].mean()
        rvol_local = volumen_media_local / volumen_media_100 if volumen_media_100 > 0 else 1.0
        
        obv_local_ascendente = hist['OBV'].iloc[-1] > hist['OBV'].iloc[-5]

        # 4. Evaluación de Giro Institucional Bajo el Muro ("Olla Reconstruida")
        # El precio está por debajo del POC anual principal pero consolidando con volumen en mínimos
        giro_en_base = (
            actual < (poc_anual * 0.98) and        # Cotizando bajo el muro anual
            actual >= (poc_local * 0.98) and       # Sosteniendo la base local negociada
            rvol_local > 1.15 and                  # Anomalía de volumen local de acumulación
            obv_local_ascendente                   # Flujo monetario acumulándose localmente
        )

        # 5. ASIGNACIÓN JERÁRQUICA DE ESTADOS
        es_soberano = (sma200_ok and (sma50 > sma200) and (rsi < 35) and obv_trend)
        
        ignicion = False
        if es_soberano:
            vol_rel = hist["Volume"].iloc[-1] / hist["Volume"].rolling(20).mean().iloc[-1]
            div_rsi = rsi > 100 - (100 / (1 + (gain / loss)).iloc[-3])
            div_prc = actual < close.iloc[-3]
            if vol_rel > 1.8 or (div_rsi and div_prc):
                ignicion = True

        if ignicion:
            estado = "🔥 CRUCE DE URANO"
        elif es_soberano:
            estado = "💎 SOBERANO"
        elif giro_en_base:
            estado = "🛠️ OLLA RECONSTRUIDA"
        else:
            if obv_trend:
                if fpc_valor > 95.0000 and 35.00 <= rsi <= 48.00:
                    estado = "⚡ OLLA DE PRESIÓN"
                elif (sma200_ok and fpc_valor > 90.0000 and 60.00 <= rsi <= 68.00):
                    estado = "🚀 MOMENTUM TEMPRANO"
                elif (sma200_ok and fpc_valor > 85.0000 and rsi < 36.00):
                    estado = "🛡️ SACUDIDA INSTITUCIONAL"
                else:
                    estado = "📡 RADAR"
            else:
                estado = "📡 RADAR"

        definicion = DICCIONARIO_ESTADOS[estado]["Definición"]
        metrica_critica = DICCIONARIO_ESTADOS[estado]["Métrica"]

        return {
            "Sigla": ticker,
            "Precio": round(actual, 2),
            "RSI": round(rsi, 1),
            "FPC (Peso)": fpc_valor,
            "SMA 200": "✅" if sma200_ok else "❌",
            "Flujo": "💹" if obv_trend else "📉",
            "Estado": estado,
            "Diagnóstico": definicion,
            "Criterio": metrica_critica
        }
    except:
        return None


# --- [III. INTERFAZ IICU-100 v4.2.0] ---
st.set_page_config(page_title="IICU-100 Soberanía", layout="wide")

st.markdown(
    """
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .glass { background: rgba(255, 255, 255, 0.03); border: 1px solid #00FFAA; border-radius: 10px; padding: 15px; }
    h1, h2 { color: #00FFAA; text-shadow: 0px 0px 10px #00FFAA; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🏛️ IICU-100: ENGINE DE SOBERANÍA TÉCNICA")
st.sidebar.header("ESTADO DEL SISTEMA")
st.sidebar.info("Panel Maestro v4.2.0. Integrada detección temprana de rotación institucional en base.")

nodo_seleccionado = st.selectbox(
    "Seleccionar Nodo de Poder", list(PILARES.keys())
)

if st.button("EJECUTAR AUDITORÍA DE NODO"):
    res_list = []
    with st.spinner("Escaneando Cuadrante de Hierro..."):
        for t in PILARES[nodo_seleccionado]:
            inf = auditoria_tecnica(t)
            if inf:
                res_list.append(inf)

    df = pd.DataFrame(res_list)
    st.session_state["audit_data"] = df
    st.session_state["pilar_activo"] = nodo_seleccionado

if "audit_data" in st.session_state:
    df = st.session_state["audit_data"]
    st.markdown("### 🛰️ MAPA DE PODER ACTUAL")
    
    st.dataframe(
        df[[
            "Sigla", "Precio", "RSI", "FPC (Peso)", "SMA 200", "Flujo", 
            "Estado", "Diagnóstico", "Criterio"
        ]], 
        use_container_width=True
    )

    st.markdown("---")
    st.subheader("📊 Diagnóstico de Divergencia (Alpha de Urano)")

    with st.spinner("Sincronizando con el S&P 500..."):
        fig_comp, val_alpha, ret_iicu = calcular_rendimiento_y_alpha(df)

        if fig_comp:
            c1, c2 = st.columns(2)
            c1.metric("RENDIMIENTO IICU (1Y)", f"{ret_iicu}%")
            c2.metric(
                "ALFA DE SOBERANÍA",
                f"{val_alpha}%",
                delta=f"{val_alpha}% vs SPY",
                delta_color="normal",
            )
            st.plotly_chart(fig_comp, use_container_width=True)

    st.markdown("---")
