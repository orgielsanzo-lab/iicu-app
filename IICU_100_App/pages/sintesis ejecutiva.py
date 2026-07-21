import math
import numpy as np
import pandas as pd
from scipy.stats import linregress
import streamlit as st
import yfinance as yf

# ==========================================
# 1. MOTOR 3: LÓGICA CORE DE INTERPRETACIONAL
# ==========================================


def interpretar_fisica_movimiento_v3(
    precio: float,
    poc_anual: float,
    poc_local: float,
    rvol: float,
    obv_slope: float,
    sma200_ok: bool,
    fpc: float = 75.0,
    rsi: float = 50.0,
    ticker: str = "ASSET",
):
    """Motor Integrado de Decisión Cuantitativa - IICU-100 v6.0."""
    delta_poc200 = ((precio - poc_anual) / poc_anual) * 100.0
    delta_poc20 = ((precio - poc_local) / poc_local) * 100.0
    gap_pocs = abs((poc_anual - poc_local) / poc_anual) * 100.0
    obv_creciente = obv_slope > 0
    stop_invalidacion = round(min(poc_anual, poc_local) * 0.985, 2)

    veredicto = ""
    nivel_riesgo = ""
    accion_sugerida = ""
    tesis_tecnica = ""

    # ESCENARIO A: PRECIO BAJO EL EQUILIBRIO ANUAL
    if precio < poc_anual:
        if precio >= (poc_local * 0.985) and rvol >= 1.20 and obv_creciente:
            veredicto = "🛠️ GIRO INSTITUCIONAL DETECTADO (ABSORCIÓN EN BASE)"
            nivel_riesgo = "BAJO (Asimetría Positiva Favorable)"
            accion_sugerida = (
                f"COMPRA ESCALONADA. Entrar con 50% en ${precio:.2f}. "
                f"Añadir el 50% restante al confirmar ruptura de ${poc_anual:.2f}."
            )
            tesis_tecnica = (
                f"Absorción activa bajo el precio de equilibrio anual (${poc_anual:.2f}). "
                f"Un RVOL de {rvol:.2f}x con flujo monetario positivo confirma "
                f"acumulación sobre el POC local de 20d (${poc_local:.2f})."
            )
        elif rvol >= 1.20 and not obv_creciente:
            veredicto = "🛑 CASCADA DE LIQUIDEZ / DISTRIBUCIÓN AGRESIVA"
            nivel_riesgo = "CRÍTICO"
            accion_sugerida = (
                "PROHIBIDA LA ENTRADA. Si está dentro, liquidar posición o ejecutar stop "
                "inmediatamente."
            )
            tesis_tecnica = (
                f"Venta institucional activa. El activo perfora soportes bajo el POC Anual (${poc_anual:.2f}) "
                f"con volumen de presión ({rvol:.2f}x) sin demanda que absorba la oferta."
            )
        elif precio > poc_local and not sma200_ok:
            veredicto = "⏳ SANDWICH DE GRAVEDAD / REBOTE DE INERCIA"
            nivel_riesgo = "MEDIO-ALTO"
            accion_sugerida = (
                f"OPERACIÓN TÁCTICA DE CORTO PLAZO. Tomar ganancias parcialmente conforme "
                f"el precio se acerque al techo del POC Anual (${poc_anual:.2f})."
            )
            tesis_tecnica = (
                f"El precio está comprimido entre el soporte local (${poc_local:.2f}) "
                f"y la resistencia mayor de 200 días (${poc_anual:.2f}). Sin tendencia estructural."
            )
        else:
            veredicto = "⏳ INERCIA BAJISTA PASIVA"
            nivel_riesgo = "MEDIO-ALTO"
            accion_sugerida = (
                "MANTENER EN RADAR. No asignar capital hasta ver anomalía de volumen."
            )
            tesis_tecnica = (
                f"Caída por desinterés comprador (RVOL {rvol:.2f}x). "
                f"Sin volumen comprador no hay efecto resorte."
            )

    # ESCENARIO B: PRECIO SOBRE EL EQUILIBRIO ANUAL
    else:
        if delta_poc200 <= 5.0 and sma200_ok and fpc >= 60.0:
            veredicto = "🟢 COMPRESIÓN EN ZONA DE ACUMULACIÓN SEGURA"
            nivel_riesgo = "BAJO"
            accion_sugerida = (
                f"COMPRA TÁCTICA AUTORIZADA. Entrada directa en ${precio:.2f}. "
                f"Stop rígido en ${stop_invalidacion}."
            )
            tesis_tecnica = (
                f"El activo cotiza a solo {delta_poc200:.2f}% de su centro de gravedad (${poc_anual:.2f}). "
                f"Respaldado por tendencia SMA200 y métricas fundamentales sólidas (FPC {fpc:.1f})."
            )
        elif (
            5.0 < delta_poc200 <= 12.0
            and rvol >= 1.20
            and obv_creciente
            and rsi <= 68.0
        ):
            veredicto = "🔥 IGNICIÓN Y ESCAPE CONFIRMADO"
            nivel_riesgo = "MEDIO (Inercia Rápida)"
            accion_sugerida = (
                "COMPRA DE MOMENTUM. Acompañar con órdenes límite. "
                "No perseguir si la extensión supera el 12% respecto al POC Anual."
            )
            tesis_tecnica = (
                f"Inyección de liquidez confirmada con RVOL de {rvol:.2f}x y OBV en expansión. "
                f"La rotación valida la ruptura por encima del precio de equilibrio."
            )
        elif delta_poc200 > 12.0 or (delta_poc200 > 5.0 and rvol < 1.0):
            veredicto = "🟡 TRAMPA DE AIRE / SOBREEXTENSIÓN SANGUÍNEA"
            nivel_riesgo = "ALTO"
            accion_sugerida = (
                "NO COMPRAR. Prohibido abrir nuevas posiciones. "
                "Ajustar trailing stop o tomar beneficios parciales."
            )
            tesis_tecnica = (
                f"El precio está sobreextendido un +{delta_poc200:.2f}% de su valor justo (${poc_anual:.2f}) "
                f"con volumen insuficiente ({rvol:.2f}x). Elevado riesgo de reversión a la media."
            )
        else:
            veredicto = "📡 CONSOLIDACIÓN EN RANGO"
            nivel_riesgo = "MEDIO"
            accion_sugerida = (
                "PERMANECER NEUTRO. Monitorear compresión o catalizadores de volumen."
            )
            tesis_tecnica = (
                f"Movimiento dentro del rango dinámico sin anomalías operativas claras. "
                f"Separación de POCs en {gap_pocs:.2f}%."
            )

    return {
        "ticker": ticker,
        "precio": round(precio, 2),
        "veredicto": veredicto,
        "nivel_riesgo": nivel_riesgo,
        "accion_sugerida": accion_sugerida,
        "tesis_tecnica": tesis_tecnica,
        "stop_invalidacion": stop_invalidacion,
        "gap_pocs": round(gap_pocs, 2),
    }


# ==========================================
# 2. INTERFAZ STREAMLIT Y EXTRACCIÓN DE DATOS
# ==========================================

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
    "Motor de Decisión Cuantitativa - Análisis Integrado Panel Maestro + Censor (v6.0)"
)

ticker_input = st.text_input("INGRESAR TICKER PARA INFORME:", "META").upper()

if ticker_input:
    with st.spinner("Sintetizando vectores de mercado..."):
        asset = yf.Ticker(ticker_input)
        hist = asset.history(period="1y")

        if not hist.empty and len(hist) >= 200:
            precio_act = float(hist["Close"].iloc[-1])
            sma200_val = hist["Close"].rolling(200).mean().iloc[-1]

            typical = (hist["High"] + hist["Low"] + hist["Close"]) / 3

            # POC Anual (200d)
            c200, b200 = np.histogram(
                typical.iloc[-200:],
                weights=hist["Volume"].iloc[-200:],
                bins=150,
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
            rvol_calc = float(
                hist["Volume"].iloc[-20:].mean() / v100_limpio.mean()
            )

            # Tendencia OBV
            hist["OBV"] = (
                (np.sign(hist["Close"].diff()) * hist["Volume"])
                .fillna(0)
                .cumsum()
            )
            slope_obv, _, _, _, _ = linregress(
                np.arange(20), hist["OBV"].iloc[-20:].values
            )

            # Cálculo básico de RSI (14 periodos)
            delta = hist["Close"].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi_calc = float(100 - (100 / (1 + rs)).iloc[-1])

            # EJECUCIÓN DEL MOTOR 3
            rep = interpretar_fisica_movimiento_v3(
                precio=precio_act,
                poc_anual=poc_a,
                poc_local=poc_l,
                rvol=rvol_calc,
                obv_slope=slope_obv,
                sma200_ok=(precio_act > sma200_val),
                fpc=75.0,  # Valor por defecto
                rsi=rsi_calc,
                ticker=ticker_input,
            )

            # RENDERIZADO EN STREAMLIT
            card_class = (
                "warning-card"
                if "🛑" in rep["veredicto"] or "🟡" in rep["veredicto"]
                else "executive-card"
            )

            st.markdown(
                f"""
            <div class="{card_class}">
                <h2 style="margin-top:0; color:#00FFAA;">{rep['veredicto']}</h2>
                <p><b>ACTIVO:</b> {rep['ticker']} | <b>PRECIO ACTUAL:</b> ${rep['precio']:.2f}</p>
                <hr style="border-color: rgba(255,255,255,0.1);">
                <p><b>1. Tesis Física de Flujo:</b><br>{rep['tesis_tecnica']}</p>
                <p><b>2. Evaluación de Riesgo Estructural:</b> {rep['nivel_riesgo']}</p>
                <p><b>3. Confluencia de POCs:</b> Separación Anual vs Local de <b>{rep['gap_pocs']}%</b> {'(Comprimido / Acumulación)' if rep['gap_pocs'] <= 2.0 else '(Expandido)'}</p>
                <hr style="border-color: rgba(255,255,255,0.1);">
                <h4 style="color:#00FFAA; margin-bottom: 5px;">🎯 INSTRUCCIÓN OPERATIVA PUNTUAL:</h4>
                <p style="font-size: 1.1em; font-weight: bold;">{rep['accion_sugerida']}</p>
                <p style="color: #FF3333; margin-bottom: 0;"><b>Punto Rígido de Invalidación (Stop Loss Estructural):</b> ${rep['stop_invalidacion']}</p>
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.error(
                "No se pudieron obtener suficientes datos históricos para el activo solicitado."
            )
