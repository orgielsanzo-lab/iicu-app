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
        "MSFT",
        "NVDA",
        "GOOGL",
        "AMZN",
        "TSM",
        "AVGO",
        "ASML",
        "AMD",
        "QCOM",
        "META",
        "SNOW",
        "PLTR",
        "MSTR",
        "INTC",
        "ARM",
        "KLAC",
        "AMAT",
        "CDNS",
        "PSTG",
        "ADBE",
    ],
    "2. El Corazón": [
        "CEG",
        "VST",
        "CCJ",
        "BWXT",
        "SMR",
        "OKLO",
        "UUUU",
        "ETN",
        "GE",
        "VRT",
        "HUBB",
        "POWL",
        "NEE",
        "FSLR",
        "ENPH",
        "SEDG",
        "BE",
        "DUK",
        "SO",
        "AES",
    ],
    "3. Biología": [
        "CRSP",
        "BEAM",
        "EDIT",
        "NTLA",
        "LLY",
        "NVO",
        "VRTX",
        "AMGN",
        "REGN",
        "TMO",
        "DHR",
        "ILMN",
        "A",
        "IQV",
        "RXRX",
        "SDGR",
        "DNA",
        "GNKX",
        "MRNA",
        "BIIB",
    ],
    "4. Base Física": [
        "MP",
        "ALB",
        "SQM",
        "LAC",
        "LTHM",
        "FCX",
        "BHP",
        "RIO",
        "VALE",
        "TECK",
        "AA",
        "NEM",
        "CF",
        "MOS",
        "CAT",
        "DE",
        "JCI",
        "URI",
        "SCCO",
        "STLD",
    ],
    "5. Expansión Orbital": [
        "RKLB",
        "MDA.TO",
        "PL",
        "SPIR",
        "BKSY",
        "LMT",
        "NOC",
        "RTX",
        "LHX",
        "BA",
        "HWM",
        "TDG",
        "JOBY",
        "ACHR",
        "TSP",
        "GSAT",
        "ASTS",
        "IRDM",
        "VSAT",
        "SPCE",
        "SPCX",
    ],
}


def calcular_fpc(ticker):
    try:
        asset = yf.Ticker(ticker)

        # 1. Extracción de Datos Fundamentales Básicos vía .info
        info = asset.info
        rev = info.get("totalRevenue")
        growth = abs(info.get("revenueGrowth", 0.10))

        # 2. Extracción Robusta de I+D (Investigación y Desarrollo)
        rd = None

        # Intento A: Consulta directa en el Estado de Resultados (Financials)
        try:
            financials = asset.financials
            if not financials.empty:
                if "Research Development" in financials.index:
                    rd = financials.loc["Research Development"].iloc[0]
                elif "Operating Expense" in financials.index:
                    rd = financials.loc["Operating Expense"].iloc[0] * 0.25
        except Exception:
            pass

        # Intento B: Si falla el estado de resultados, consultar .info
        if rd is None or pd.isna(rd) or rd == 0:
            rd = info.get("researchDevelopment")

        # Intento C: Respaldo por estimación de gastos operativos en .info
        if rd is None or pd.isna(rd) or rd == 0:
            op_exp = info.get("operatingExpenses") or info.get(
                "totalOperatingExpenses", 0
            )
            rd = (
                op_exp * 0.20
                if op_exp > 0
                else (rev * 0.15 if rev else 50000000)
            )

        # 3. Normalización de Ingresos
        if rev is None or pd.isna(rev) or rev <= 0:
            rev = info.get("grossProfits", 100000000)

        # 4. Cálculo de Métricas Cuantitativas
        intensity = abs(rd / rev) if rev > 0 else 0.10

        # Normalización para evitar disparos por startups con ingresos cero
        if intensity > 2.0:
            intensity = 2.0

        # 5. Cálculo Final Normalizado (Escala IICU 0-100)
        raw_score = (intensity * 70) + (growth * 30)
        fpc_final = 100 * (1 - math.exp(-raw_score / 1.5))

        return round(fpc_final, 2)

    except Exception as e:
        # Retorno de seguridad no nulo basado en la existencia del ticker
        return 50.00


def calcular_rsi_wilder(close_series, window=14):
    """Calcula el RSI utilizando la suavización exponencial exacta de Wilder."""
    delta = close_series.diff()

    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    # Inicialización con EMA/Wilder (alpha = 1 / window)
    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()

    rs = avg_gain / avg_loss
    rsi = 100.0 - (100.0 / (1.0 + rs))

    return rsi, avg_gain, avg_loss


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
        fig.add_trace(
            go.Scatter(
                x=bench_norm.index,
                y=bench_norm,
                name="S&P 500",
                line=dict(color="#888888", dash="dot"),
            )
        )
        fig.add_trace(
            go.Scatter(
                x=iicu_norm.index,
                y=iicu_norm,
                name="IICU-100",
                line=dict(color="#00FFAA", width=4),
            )
        )
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e0e0e0"),
            height=400,
            margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )
        return fig, alpha, ret_iicu
    except Exception:
        return None, 0, 0


# --- [II. MOTOR DE AUDITORÍA CUÁNTICA - CAPAS 2 Y 3] ---


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

        # CÁLCULO RSI (Algoritmo Wilder)
        rsi_series, avg_gain, avg_loss = calcular_rsi_wilder(close, window=14)
        rsi = rsi_series.iloc[-1]

        # OBV base asignado al dataframe
        hist["OBV"] = (
            (np.sign(close.diff()) * hist["Volume"]).fillna(0).cumsum()
        )
        obv_trend = (
            hist["OBV"].iloc[-1] > hist["OBV"].rolling(10).mean().iloc[-1]
        )

        fpc_valor = calcular_fpc(ticker)
        sma200_ok = actual > sma200

        # Lógica de Clasificación Jerárquica
        es_soberano = (
            sma200_ok and (sma50 > sma200) and (rsi < 35) and obv_trend
        )

        ignicion = False
        if es_soberano:
            vol_rel = (
                hist["Volume"].iloc[-1]
                / hist["Volume"].rolling(20).mean().iloc[-1]
            )

            # Divergencia calculada sobre los vectores de Wilder
            rs_prev = avg_gain.iloc[-3] / avg_loss.iloc[-3]
            rsi_prev = 100 - (100 / (1 + rs_prev))

            div_rsi = rsi > rsi_prev
            div_prc = actual < close.iloc[-3]

            if vol_rel > 1.8 or (div_rsi and div_prc):
                ignicion = True

        # --- [RECALIBRACIÓN DINÁMICA DE ESTADOS] ---
        obv_acumulando = (
            hist["OBV"].iloc[-1] >= hist["OBV"].iloc[-5]
        )  # Tendencia de 5 días más reactiva

        if ignicion:
            estado = "🔥 CRUCE DE URANO"
        elif es_soberano:
            estado = "💎 SOBERANO"
        else:
            # Calibración FPC basada en la distribución real
            if fpc_valor >= 70.0 and 30.0 <= rsi <= 50.0:
                estado = "⚡ OLLA DE PRESIÓN"
            elif (
                sma200_ok
                and fpc_valor >= 65.0
                and 50.0 < rsi <= 68.0
                and obv_trend
            ):
                estado = "🚀 MOMENTUM TEMPRANO"
            elif sma200_ok and fpc_valor >= 60.0 and rsi < 35.0:
                estado = "🛡️ SACUDIDA INSTITUCIONAL"
            elif obv_acumulando and sma200_ok:
                estado = "🛠️ ACUMULACIÓN SILENCIOSA"
            else:
                estado = "📡 RADAR"

        return {
            "Sigla": ticker,
            "Precio": round(actual, 2),
            "RSI": round(rsi, 1),
            "FPC (Peso)": fpc_valor,
            "SMA 200": "✅" if sma200_ok else "❌",
            "Flujo": "💹" if obv_trend else "📉",
            "Estado": estado,
        }

    except Exception:
        return None


# --- [III. INTERFAZ IICU-100 v3.8.0] ---
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

st.title("🏛️ IICU-100: INFRAESTRUCTURA DEL FUTURO")

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
    st.table(df)

    # --- [INSERCIÓN DE MÉTRICAS DE ALFA Y GRÁFICO] ---
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
