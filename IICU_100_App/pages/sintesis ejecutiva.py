import math
import numpy as np
import pandas as pd
from scipy.stats import linregress
import streamlit as st
import yfinance as yf


# --- MOTOR DE INTERPRETACIÓN EJECUTIVA ---
def generar_reporte_alto_perfil(
    ticker, precio, rsi, fpc, sma200_ok, poc_anual, poc_local, rvol, obv_slope
):
    """Genera la síntesis analítica en lenguaje directo de Wall Street cruzando la física de ambos módulos."""

    delta_poc200 = ((precio - poc_anual) / poc_anual) * 100
    gap_pocs = abs((poc_anual - poc_local) / poc_anual) * 100
    obv_creciente = obv_slope > 0

    veredicto = ""
    nivel_riesgo = ""
    accion_sugerida = ""
    tesis_tecnica = ""
    stop_invalidacion = round(min(poc_anual, poc_local) * 0.985, 2)

    # --- ESCENARIO 1: ABSORCIÓN BAJO EL EQUILIBRIO (ZONA DE OLLA) ---
    if precio < poc_anual:
        if precio >= (poc_local * 0.985) and rvol >= 1.2 and obv_creciente:
            veredicto = "🛠️ GIRO INSTITUCIONAL DETECTADO (OLLA RECONSTRUIDA)"
            nivel_riesgo = "BAJO (Asimetría Positiva Favorable)"
            accion_sugerida = f"COMPRA ESCALONADA AUTORIZADA. Iniciar posición del 50% en ${precio:.2f}. Agregar el otro 50% al romper los ${poc_anual:.2f}."
            tesis_tecnica = (
                f"Existe absorción activa por debajo del precio promedio anual (${poc_anual:.2f}). "
                f"Un RVOL de {rvol:.2f}x combinado con acumulación en OBV confirma que manos fuertes están "
                f"frenando la caída y construyendo un suelo en torno al POC local de 20 días (${poc_local:.2f})."
            )

        elif not obv_creciente and rvol >= 1.2:
            veredicto = "🛑 CASCADA DE LIQUIDEZ / DISTRIBUCIÓN AGRESIVA"
            nivel_riesgo = "CRÍTICO"
            accion_sugerida = "PROHIBIDA LA ENTRADA. Si se está posicionado, reducir exposición o ejecutar stop."
            tesis_tecnica = (
                f"El precio perfora soportes bajo el POC anual (${poc_anual:.2f}) respaldado por volumen inusualmente alto ({rvol:.2f}x) "
                f"sin demanda que lo absorba (OBV decreciente). Es venta institucional activa."
            )

        else:
            veredicto = "⏳ INERCIA BAJISTA PASIVA"
            nivel_riesgo = "MEDIO-ALTO"
            accion_sugerida = "PERMANECER EN RADAR. No colocar capital aún."
            tesis_tecnica = (
                f"El activo gotea a la baja por simple desinterés del mercado. Sin un RVOL > 1.2x que señale "
                f"presencia institucional, cualquier rebote actual es de baja calidad."
            )

    # --- ESCENARIO 2: EXPANSION SOBRE EL EQUILIBRIO (SOBRE EL POC ANUAL) ---
    else:
        if delta_poc200 <= 5.0 and sma200_ok and fpc >= 65.0:
            veredicto = "🟢 COMPRESIÓN EN ZONA DE ACUMULACIÓN SEGURA"
            nivel_riesgo = "BAJO"
            accion_sugerida = f"COMPRA TÁCTICA AUTORIZADA. Entrada directa con precio objetivo de expansión. Stop técnico rígido en ${stop_invalidacion}."
            tesis_tecnica = (
                f"El activo cotiza apenas a un {delta_poc200:.2f}% de su centro de gravedad anual (${poc_anual:.2f}). "
                f"Con una base fundamental sólida (FPC de {fpc:.1f}) y tendencia por encima de la SMA 200, "
                f"el activo está apoyado sobre su colchón gravitacional."
            )

        elif (
            5.0 < delta_poc200 <= 12.0
            and rvol >= 1.20
            and obv_creciente
            and rsi <= 68.0
        ):
            veredicto = "🔥 IGNICIÓN Y ESCAPE CONFIRMADO"
            nivel_riesgo = "MEDIO (Por velocidad)"
            accion_sugerida = "COMPRA DE MOMENTUM. Acompañar el movimiento con órdenes límite. No perseguir si supera el 12% de distancia al POC."
            tesis_tecnica = (
                f"El volumen de confirmación ({rvol:.2f}x) valida la ruptura por encima del POC. "
                f"El flujo de dinero (OBV) respalda el movimiento, descartando una trampa de mercado."
            )

        elif delta_poc200 > 12.0 and rvol < 1.2:
            veredicto = "🟡 TRAMPA DE AIRE / SOBREEXTENSIÓN SANGUÍNEA"
            nivel_riesgo = "ALTO"
            accion_sugerida = "NO COMPRAR. Tomar beneficios parciales si se está dentro."
            tesis_tecnica = (
                f"El activo está sobreextendido un {delta_poc200:.2f}% respecto a su zona de valor real (${poc_anual:.2f}) "
                f"sin el respaldo de volumen necesario (RVOL {rvol:.2f}x). Riesgo elevado de reversión abrupta a la media."
            )

        else:
            veredicto = "📡 CONSOLIDACIÓN EN RANGO"
            nivel_riesgo = "MEDIO"
            accion_sugerida = (
                "MONITOREAR PUNTOS EXTREMOS. Aguardar compresión o catalizador."
            )
            tesis_tecnica = (
                f"El activo oscila sin una anomalía de volumen clara que justifique tomar riesgo. "
                f"Comprimir el seguimiento en el tablero."
            )

    return {
        "veredicto": veredicto,
        "riesgo": nivel_riesgo,
        "accion": accion_sugerida,
        "tesis": tesis_tecnica,
        "stop": stop_invalidacion,
        "gap_pocs": round(gap_pocs, 2),
    }


# --- INTERFAZ STREAMLIT DE ALTA ESCUELA ---
st.set_page_config(
    page_title="IICU-100: Diagnóstico Ejecutivo de Decisión", layout="centered"
)

st.markdown(
    """
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .executive-card {
        background: rgba(255, 255, 255, 0.02);
        border-left: 4px solid #00FFAA;
        border-radius: 4px;
        padding: 20px;
        margin-top: 15px;
    }
    .warning-card {
        background: rgba(255, 0, 0, 0.03);
        border-left: 4px solid #FF3333;
        border-radius: 4px;
        padding: 20px;
        margin-top: 15px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🏛️ INFORME DE DECISIÓN Y SÍNTESIS ESTRUCTURAL")
st.caption(
    "Motor de Decisión Cuantitativa - Análisis Integrado Panel Maestro + Censor"
)

ticker_input = st.text_input("INGRESAR TICKER PARA INFORME:", "META").upper()

if ticker_input:
    with st.spinner("Sintetizando vectores de mercado..."):
        # Simulación/Carga de variables unificadas (Conectar a tus funciones existentes)
        asset = yf.Ticker(ticker_input)
        hist = asset.history(period="1y")

        if not hist.empty and len(hist) >= 200:
            precio_act = float(hist["Close"].iloc[-1])
            sma200_val = hist["Close"].rolling(200).mean().iloc[-1]

            # Reutilización de cálculos del Censor y Panel
            p_min, p_max = hist["Low"].min(), hist["High"].max()
            typical = (hist["High"] + hist["Low"] + hist["Close"]) / 3

            # POC Anual (200d)
            c200, b200 = np.histogram(
                typical.iloc[-200:], weights=hist["Volume"].iloc[-200:], bins=150
            )
            poc_a = (b200[np.argmax(c200)] + b200[np.argmax(c200) + 1]) / 2

            # POC Local (20d)
            c20, b20 = np.histogram(
                typical.iloc[-20:], weights=hist["Volume"].iloc[-20:], bins=150
            )
            poc_l = (b20[np.argmax(c20)] + b20[np.argmax(c20) + 1]) / 2

            # RVOL Depurado
            v100_limpio = hist["Volume"].iloc[-100:][
                hist["Volume"].iloc[-100:]
                > hist["Volume"].iloc[-100:].quantile(0.1)
            ]
            rvol_calc = float(hist["Volume"].iloc[-20:].mean() / v100_limpio.mean())

            # Tendencia OBV
            hist["OBV"] = (
                (np.sign(hist["Close"].diff()) * hist["Volume"]).fillna(0).cumsum()
            )
            slope_obv, _, _, _, _ = linregress(
                np.arange(20), hist["OBV"].iloc[-20:].values
            )

            # FPC / RSI Estándar
            fpc_calc = 75.0  # Tomado de tu función calcular_fpc
            rsi_calc = 48.5  # Tomado de tu función calcular_rsi_wilder

            # GENERACIÓN DEL INFORME
            rep = generar_reporte_alto_perfil(
                ticker=ticker_input,
                precio=precio_act,
                rsi=rsi_calc,
                fpc=fpc_calc,
                sma200_ok=(precio_act > sma200_val),
                poc_anual=poc_a,
                poc_local=poc_l,
                rvol=rvol_calc,
                obv_slope=slope_obv,
            )

            # RENDERIZADO DEL INFORME DE ALTA ESCUELA
            card_class = (
                "warning-card" if "🛑" in rep["veredicto"] else "executive-card"
            )

            st.markdown(
                f"""
            <div class="{card_class}">
                <h2 style="margin-top:0; color:#00FFAA;">{rep['veredicto']}</h2>
                <p><b>ACTIVO:</b> {ticker_input} | <b>PRECIO ACTUAL:</b> ${precio_act:.2f}</p>
                <hr style="border-color: rgba(255,255,255,0.1);">
                <p><b>1. Tesis Física de Flujo:</b><br>{rep['tesis']}</p>
                <p><b>2. Evaluación de Riesgo Estructural:</b> {rep['riesgo']}</p>
                <p><b>3. Confluencia de POCs:</b> Separación Anual vs Local de <b>{rep['gap_pocs']}%</b> {'(Comprimido / Acumulación)' if rep['gap_pocs'] <= 2.0 else '(Expandido)'}</p>
                <hr style="border-color: rgba(255,255,255,0.1);">
                <h4 style="color:#00FFAA; margin-bottom: 5px;">🎯 INSTRUCCIÓN OPERATIVA PUNTUAL:</h4>
                <p style="font-size: 1.1em; font-weight: bold;">{rep['accion']}</p>
                <p style="color: #FF3333; margin-bottom: 0;"><b>Punto Rígido de Invalidación (Stop Loss Estructural):</b> ${rep['stop']}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )