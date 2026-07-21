import math
from typing import Any, Dict
import numpy as np


def interpretar_fisica_movimiento_v3(
    precio: float,
    poc_anual: float,
    poc_local: float,
    rvol: float,
    obv_slope: float,
    sma200_ok: bool,
    fpc: float = 50.0,
    rsi: float = 50.0,
    ticker: str = "ASSET",
) -> Dict[str, Any]:
    """Motor Integrado de Decisión Cuantitativa - IICU-100 v6.0.

    Sintetiza la microestructura de mercado (Volumen/POCs) y el análisis de
    dinámica de precios en una instrucción operativa puntual.
    """
    # 1. Cálculos de Vectores de Gravedad
    delta_poc200 = ((precio - poc_anual) / poc_anual) * 100.0
    delta_poc20 = ((precio - poc_local) / poc_local) * 100.0
    gap_pocs = abs((poc_anual - poc_local) / poc_anual) * 100.0
    obv_creciente = obv_slope > 0

    # Punto Rígido de Invalidación (Soporte Estructural del 1.5% bajo el POC más bajo)
    stop_invalidacion = round(min(poc_anual, poc_local) * 0.985, 2)

    # Variables de Salida
    veredicto = ""
    nivel_riesgo = ""
    accion_sugerida = ""
    tesis_tecnica = ""

    # 2. Árbol Integrado de Decisión (Física del Flujo)

    # --- ESCENARIO A: PRECIO BAJO EL EQUILIBRIO ANUAL (ZONA DE DESCUENTO) ---
    if precio < poc_anual:
        # A1. Absorción Institucional / Giro en Base
        if precio >= (poc_local * 0.985) and rvol >= 1.20 and obv_creciente:
            veredicto = "🛠️ GIRO INSTITUCIONAL DETECTADO (ABSORCIÓN EN BASE)"
            nivel_riesgo = "BAJO (Asimetría Positiva Favorable)"
            accion_sugerida = (
                f"COMPRA ESCALONADA. Entrar con 50% en ${precio:.2f}. "
                f"Añadir el 50% restante al confirmar ruptura de ${poc_anual:.2f}."
            )
            tesis_tecnica = (
                f"Absorción activa bajo el precio de equilibrio anual (${poc_anual:.2f}). "
                f"Un RVOL de {rvol:.2f}x con flujo monetario positivo (OBV creciente) confirma "
                f"acumulación sobre el POC local de 20d (${poc_local:.2f})."
            )

        # A2. Distribución / Cascada de Liquidez
        elif rvol >= 1.20 and not obv_creciente:
            veredicto = "🛑 CASCADA DE LIQUIDEZ / DISTRIBUCIÓN AGRESIVA"
            nivel_riesgo = "CRÍTICO"
            accion_sugerida = (
                "PROHIBIDA LA ENTRADA. Si está dentro, liquidar posición o ejecutar stop "
                "inmediatamente."
            )
            tesis_tecnica = (
                f"Venta institucional activa. El activo perfora niveles clave bajo el POC Anual (${poc_anual:.2f}) "
                f"con volumen de presión ({rvol:.2f}x) sin demanda consumiendo la oferta."
            )

        # A3. Rebote de Inercia / Atrapado en Rango
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

        # A4. Inercia Bajista Pasiva
        else:
            veredicto = "⏳ INERCIA BAJISTA PASIVA"
            nivel_riesgo = "MEDIO-ALTO"
            accion_sugerida = (
                "MANTENER EN RADAR. No asignar capital hasta ver anomalía de volumen."
            )
            tesis_tecnica = (
                f"Desgastante caída por falta de compradores (RVOL {rvol:.2f}x insuficiente). "
                f"Sin volumen comprador no hay efecto resorte."
            )

    # --- ESCENARIO B: PRECIO SOBRE EL EQUILIBRIO ANUAL (ZONA DE EXPANSIÓN) ---
    else:
        # B1. Acumulación Comprimida / Zona Segura
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

        # B2. Ruptura y Momentum Confirmado
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

        # B3. Sobreextensión / Trampa de Aire
        elif delta_poc200 > 12.0 or (delta_poc200 > 5.0 and rvol < 1.0):
            veredicto = "🟡 TRAMPA DE AIRE / SOBREEXTENSIÓN SANGUÍNEA"
            nivel_riesgo = "ALTO"
            accion_sugerida = (
                "NO COMPRAR. Prohibido abrir nuevas posiciones. "
                "Ajustar trailing stop o tomar beneficios parciales."
            )
            tesis_tecnica = (
                f"El precio está sobreextendido un +{delta_poc200:.2f}% de su valor justo (${poc_anual:.2f}) "
                f"con volumen decreciente ({rvol:.2f}x). Elevado riesgo de regresión abrupta a la media."
            )

        # B4. Consolidación Genérica
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

    # 3. Estructuración del Output Unificado
    return {
        "ticker": ticker,
        "precio": round(precio, 2),
        "veredicto": veredicto,
        "nivel_riesgo": nivel_riesgo,
        "accion_sugerida": accion_sugerida,
        "tesis_tecnica": tesis_tecnica,
        "stop_invalidacion": stop_invalidacion,
        "metricas_clave": {
            "delta_poc_anual_pct": round(delta_poc200, 2),
            "delta_poc_local_pct": round(delta_poc20, 2),
            "gap_pocs_pct": round(gap_pocs, 2),
            "rvol": round(rvol, 2),
            "obv_creciente": obv_creciente,
        },
    }
