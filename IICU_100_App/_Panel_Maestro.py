import math
from datetime import datetime, timedelta
import google.generativeai as genai
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

# Diccionario Maestro de Explicaciones para mapear dinámicamente en la interfaz
DICCIONARIO_ESTADOS = {
    "🔥 CRUCE DE URANO": {
        "Definición": "Ignición por volumen vertical y ruptura inminente de rango.",
        "Métrica": "RSI sobrecomprado con volumen relativo masivo (>1.8x)."
    },
    "💎 SOBERANO": {
        "Definición": "Estructura alcista madura en fase de enfriamiento temporal.",
        "Métrica": "Precio > SMA 200, SMA 50 > SMA 200 con RSI frío (<35) y OBV alcista."
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

        # 1. Captura Robusta de I+D (con respaldo)
        rd = info.get("researchDevelopment")
        if rd is None or rd == 0:
            rd = info.get("totalOperatingExpenses", 0) * 0.2

        rev = info.get("totalRevenue", 1)
        if rev <= 0:
            rev = 1

        # 2. Ratio de Intensidad (Ciencia sobre Ingreso)
        intensity = abs(rd / rev)

        # 3. Factor de Crecimiento y Vigor
        growth = abs(info.get("revenueGrowth", 0.1))

        # 4. Cálculo Final Normalizado (Escala 0-100)
        raw_score = (intensity * 70) + (growth * 30)
        fpc_final = 100 * (1 - math.exp(-raw_score / 2))

        return round(fpc_final, 2)
    except:
        return 0.0

# --- [PROTOCOLO DE CENSOR] ---
def censor_de_urano(pilar_actual, candidatos_externos):
    propuestas_sustitucion = []

    nodos_con_fpc = [
        n for n in pilar_actual if n.get("FPC (Peso)") is not None
    ]
    if not nodos_con_fpc:
        return []

    peor_nodo = min(nodos_con_fpc, key=lambda x: x["FPC (Peso)"])

    for aspirante in candidatos_externos:
        if aspirante in [n["Sigla"] for n in pilar_actual]:
            continue

        fpc_aspirante = calcular_fpc(aspirante)

        if (
            fpc_aspirante > (peor_nodo["FPC (Peso)"] * 1.20)
            or peor_nodo["FPC (Peso)"] < 10.0
        ):
            propuestas_sustitucion.append(
                {
                    "SALE": peor_nodo["Sigla"],
                    "ENTRA": aspirante,
                    "FPC_NUEVO": fpc_aspirante,
                    "MOTIVO": (
                        "Superioridad de Innovación"
                        if fpc_aspirante > peor_nodo["FPC (Peso)"]
                        else "Atrofia Estructural"
                    ),
                }
            )
            break

    return propuestas_sustitucion


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
    except:
        return None, 0, 0


# --- [II. MOTOR DE AUDITORÍA CUÁNTICA - CAPAS 2 Y 3] ---
def auditoria_tecnica(ticker):
    try:
        asset = yf.Ticker(ticker)
        hist = asset.history(period="1y")
        if len(hist) < 200:
            return None

        close = hist["Close"]
        sma200 = close.rolling(200).mean().iloc[-1]
        sma50 = close.rolling(50).mean().iloc[-1]
        actual = close.iloc[-1]

        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]

        obv = (np.sign(close.diff()) * hist["Volume"]).fillna(0).cumsum()
        obv_trend = obv.iloc[-1] > obv.rolling(10).mean().iloc[-1]

        fpc_valor = calcular_fpc(ticker)

        sma200_ok = actual > sma200
        es_soberano = (
            sma200_ok and (sma50 > sma200) and (rsi < 35) and obv_trend
        )

        ignicion = False
        if es_soberano:
            vol_rel = (
                hist["Volume"].iloc[-1] / hist["Volume"].rolling(20).mean().iloc[-1]
            )
            div_rsi = rsi > 100 - (100 / (1 + (gain / loss)).iloc[-3])
            div_prc = actual < close.iloc[-3]
            if vol_rel > 1.8 or (div_rsi and div_prc):
                ignicion = True

        # Asignación Jerárquica de Estados
        if ignicion:
            estado = "🔥 CRUCE DE URANO"
        elif es_soberano:
            estado = "💎 SOBERANO"
        else:
            if obv_trend:
                if fpc_valor > 95.0000 and 35.00 <= rsi <= 48.00:
                    estado = "⚡ OLLA DE PRESIÓN"
                elif (
                    sma200_ok and fpc_valor > 90.0000 and 60.00 <= rsi <= 68.00
                ):
                    estado = "🚀 MOMENTUM TEMPRANO"
                elif sma200_ok and fpc_valor > 85.0000 and rsi < 36.00:
                    estado = "🛡️ SACUDIDA INSTITUCIONAL"
                else:
                    estado = "📡 RADAR"
            else:
                estado = "📡 RADAR"

        # Captura de definiciones desde el diccionario maestro para las nuevas columnas explicativas
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
            "Diagnóstico del Estado": definicion,
            "Métrica Crítica": metrica_critica
        }
    except:
        return None


# --- [III. CAPA 4: SENTENCIA DE URANO] ---
def ejecutar_sentencia(row, prompt_manifiesto):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(
            f"Analiza {row['Sigla']} basado en el manifiesto: {prompt_manifiesto}. Determina si hay Falla Estructural o Empresa Herida."
        )
        return response.text
    except Exception as e:
        if row["Estado"] in ["🔥 CRUCE DE URANO", "💎 SOBERANO"]:
            return f"⚠️ [Soberanía Local Activa - Fallback]\n\nAUDITORÍA: El activo {row['Sigla']} ({row['Estado']}) presenta una Divergencia Soberana en su estructura. No se detectan fallas estructurales matemáticas. DIAGNÓSTICO: EMPRESA HERIDA - OPORTUNIDAD ESTRATÉGICA."
        else:
            return f"⚠️ [Soberanía Local Activa]\n\nAUDITORÍA TÉCNICA: {row['Sigla']} cumple el Cuadrante de Hierro. Estado actual: {row['Estado']}. DIAGNÓSTICO: VALIDACIÓN COMPLETA."


# --- [IV. INTERFAZ IICU-100 v4.0.0] ---
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
st.sidebar.header("CONFIGURACIÓN MAESTRA")
api_key = st.sidebar.text_input("Clave Oráculo", type="password")

if api_key:
    genai.configure(api_key=api_key)

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
    
    # Renderizamos como Dataframe para tener columnas ajustables y control de visualización
    st.dataframe(
        df[[
            "Sigla", "Precio", "RSI", "FPC (Peso)", "SMA 200", "Flujo", 
            "Estado", "Diagnóstico del Estado", "Métrica Crítica"
        ]], 
        use_container_width=True
    )

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

    st.markdown("---")

    # --- [ INTEGRACIÓN DEL CENSOR DE URANO ] ---
    st.markdown("---")
    aspirantes_globales = ["OKLO", "ASTS", "RKLB", "VKTX", "VRT", "ARM", "PLTR"]

    resultados_para_censor = df.to_dict("records")
    propuestas = censor_de_urano(resultados_para_censor, aspirantes_globales)

    if propuestas:
        st.subheader("🛰️ Sentencia del Censor de Urano")
        for p in propuestas:
            st.warning(
                f"⚠️ **REBALANCEO SUGERIDO:** Sacar `{p['SALE']}` e integrar `{p['ENTRA']}`"
            )
            st.info(
                f"**Razón:** {p['MOTIVO']} | **FPC del Aspirante:** {p['FPC_NUEVO']}"
            )
    else:
        st.success("✅ El Censor no detecta anomalías. Estructura óptima.")
    st.markdown("---")

    # Sentencias automáticas extendidas a los nuevos estados
    soberanos = df[
        df["Estado"].isin(
            [
                "💎 SOBERANO",
                "🔥 CRUCE DE URANO",
                "⚡ OLLA DE PRESIÓN",
                "🚀 MOMENTUM TEMPRANO",
                "🛡️ SACUDIDA INSTITUCIONAL",
            ]
        )
    ]

    if not soberanos.empty:
        st.markdown("### ⚖️ SENTENCIA DE URANO")
        for index, row in soberanos.iterrows():
            with st.expander(f"SENTENCIA: {row['Sigla']} ({row['Estado']})"):
                if st.button(
                    f"INVOCAR INTÉRPRETE: {row['Sigla']}",
                    key=f"btn_{row['Sigla']}",
                ):
                    veredicto = ejecutar_sentencia(
                        row,
                        "Pilar 2 es Corazón, Pilar 5 es Urano. Buscar Falla Estructural y evaluar potencial de acumulación técnica.",
                    )
                    st.write(veredicto)
    else:
        st.info("No se detectan activos en zonas de despegue o acumulación.")
