import streamlit as st

def generar_reporte_sintetizado_v5(datos_panel, datos_censor):
    """
    Motor Unificado IICU-100 v5.1 (Limpio y Optimizado)
    """
    precio = datos_panel["Precio"]
    rsi = datos_panel.get("RSI", 50.0)
    sma200_ok = datos_panel["SMA200_OK"]
    obv_creciente = datos_panel["OBV_Creciente"]
    fpc = datos_panel.get("FPC", 50.0)

    poc_200 = datos_censor["POC_200"]
    poc_20 = datos_censor["POC_20"]
    rvol = datos_censor["RVOL"]

    delta_poc200 = ((precio - poc_200) / poc_200) * 100
    gap_pocs = abs((poc_200 - poc_20) / poc_200) * 100
    stop_invalidacion = round(min(poc_200, poc_20) * 0.985, 2)

    if precio > poc_200:
        if delta_poc200 > 12.0 and rvol < 1.20:
            veredicto = "🟡 TRAMPA DE AIRE / SOBREEXTENSIÓN SANGUÍNEA"
            nivel_riesgo = "ALTO"
            accion = "NO COMPRAR. Tomar beneficios parciales si se está dentro."
            tesis = f"Sobreextensión del {delta_poc200:.2f}% respecto al POC Anual (${poc_200:.2f}) sin respaldo de volumen ({rvol:.2f}x)."
        elif rvol >= 1.20 and obv_creciente:
            veredicto = "🔥 IGNICIÓN Y ESCAPE CONFIRMADO"
            nivel_riesgo = "MEDIO (Por velocidad)"
            accion = "COMPRA DE MOMENTUM. Entrar con órdenes límite."
            tesis = f"Volumen de confirmación ({rvol:.2f}x) e impulso de flujo (OBV) respaldan la ruptura sobre los ${poc_200:.2f}."
        elif delta_poc200 <= 5.0 and sma200_ok and fpc >= 65.0:
            veredicto = "🟢 COMPRESIÓN EN ZONA DE ACUMULACIÓN SEGURA"
            nivel_riesgo = "BAJO"
            accion = f"COMPRA TÁCTICA AUTORIZADA. Entrada directa con Stop rígido en ${stop_invalidacion}."
            tesis = f"El activo cotiza a {delta_poc200:.2f}% de su centro de gravedad (${poc_200:.2f})."
        else:
            veredicto = "📡 CONSOLIDACIÓN POR ENCIMA DE SOPORTE"
            nivel_riesgo = "MEDIO"
            accion = "MANTENER O MONITOREAR."
            tesis = f"El activo oscila sobre su zona de valor (${poc_200:.2f}) sin flujo institucional agresivo actual."
    else:
        if precio > poc_20:
            if not sma200_ok and rvol < 1.20:
                veredicto = "⏳ SANDWICH DE GRAVEDAD / REBOTE DE INERCIA"
                nivel_riesgo = "MEDIO-ALTO"
                accion = f"VENTA EN REBOTE. Tomar ganancias conforme se acerque a ${poc_200:.2f}."
                tesis = f"El activo está atrapado entre el piso local (${poc_20:.2f}) y la resistencia anual (${poc_200:.2f})."
            else:
                veredicto = "🛠️ RECUPERACIÓN EN DESARROLLO"
                nivel_riesgo = "MEDIO"
                accion = "COMPRA ESCALONADA TÁCTICA."
                tesis = f"El precio ha superado el POC local (${poc_20:.2f}) intentando cerrar la brecha con el POC Anual (${poc_200:.2f})."
        else:
            if rvol >= 1.20 and not obv_creciente:
                veredicto = "🛑 CASCADA DE LIQUIDEZ / DISTRIBUCIÓN AGRESIVA"
                nivel_riesgo = "CRÍTICO"
                accion = "PROHIBIDA LA ENTRADA. Salir de posiciones de inmediato."
                tesis = f"Venta institucional activa. Perforación bajo el POC anual con volumen alto ({rvol:.2f}x)."
            elif rvol >= 1.20 and obv_creciente:
                veredicto = "🛠️ GIRO INSTITUCIONAL DETECTADO (OLLA RECONSTRUIDA)"
                nivel_riesgo = "BAJO (Asimetría Positiva)"
                accion = f"COMPRA ESCALONADA AUTORIZADA. 50% en ${precio:.2f} y 50% al romper ${poc_200:.2f}."
                tesis = f"Absorción activa. RVOL de {rvol:.2f}x con OBV creciente frena la caída sobre el POC local (${poc_20:.2f})."
            else:
                veredicto = "⏳ INERCIA BAJISTA PASIVA"
                nivel_riesgo = "MEDIO-ALTO"
                accion = "PERMANECER EN RADAR."
                tesis = "Goteo bajista por falta de compradores. Sin RVOL > 1.2x no hay resorte comprador."

    return {
        "veredicto": veredicto,
        "riesgo": nivel_riesgo,
        "accion": accion,
        "tesis": tesis,
        "stop": stop_invalidacion,
        "gap_pocs": round(gap_pocs, 2)
    }

# --- RENDERIZADO PRINCIPAL DE STREAMLIT ---
def render_sintesis_ejecutiva(datos_panel, datos_censor):
    """
    Función de renderizado para conectar directamente con la UI.
    """
    res = generar_reporte_sintetizado_v5(datos_panel, datos_censor)

    st.title("Síntesis Ejecutiva IICU-100")
    st.subheader(res["veredicto"])
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Nivel de Riesgo:** {res['riesgo']}")
        st.write(f"**Acción Sugerida:** {res['accion']}")
    with col2:
        st.warning(f"**Stop de Invalidación:** ${res['stop']}")
        st.caption(f"Brecha entre POCs (Gap): {res['gap_pocs']}%")
        
    st.info(f"**Tesis Técnica:** {res['tesis']}")

# Bloque de ejecución local autónoma (Si corres el archivo directo)
if __name__ == "__main__":
    datos_panel_test = {"Precio": 105.0, "RSI": 45.0, "SMA200_OK": True, "OBV_Creciente": True, "FPC": 70.0}
    datos_censor_test = {"POC_200": 100.0, "POC_20": 98.0, "RVOL": 1.35}
    render_sintesis_ejecutiva(datos_panel_test, datos_censor_test)
