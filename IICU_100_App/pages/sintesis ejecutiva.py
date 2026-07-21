def generar_reporte_sintetizado_v5(datos_panel, datos_censor):
    """
    Motor Unificado IICU-100 v5.1
    Combina la precisión de estados de microestructura (Motor 2) 
    con la riqueza analítica de salida ejecutiva (Motor 1).
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

    # --- ÁRBOLES DE DECISIÓN EXHAUSTIVOS ---
    if precio > poc_200:
        if delta_poc200 > 12.0 and rvol < 1.20:
            veredicto = "🟡 TRAMPA DE AIRE / SOBREEXTENSIÓN SANGUÍNEA"
            nivel_riesgo = "ALTO"
            accion = "NO COMPRAR. Tomar beneficios parciales si se está dentro."
            tesis = f"Sobreextensión del {delta_poc200:.2f}% respecto al POC Anual (${poc_200:.2f}) sin respaldo de volumen ({rvol:.2f}x). Elevado riesgo de regresión a la media."
        
        elif rvol >= 1.20 and obv_creciente:
            veredicto = "🔥 IGNICIÓN Y ESCAPE CONFIRMADO"
            nivel_riesgo = "MEDIO (Por velocidad)"
            accion = "COMPRA DE MOMENTUM. Entrar con órdenes límite. No perseguir si supera el 12% de distancia al POC."
            tesis = f"Volumen de confirmación ({rvol:.2f}x) e impulso de flujo (OBV) respaldan la ruptura sobre los ${poc_200:.2f}. Descartada trampa de mercado."
            
        elif delta_poc200 <= 5.0 and sma200_ok and fpc >= 65.0:
            veredicto = "🟢 COMPRESIÓN EN ZONA DE ACUMULACIÓN SEGURA"
            nivel_riesgo = "BAJO"
            accion = f"COMPRA TÁCTICA AUTORIZADA. Entrada directa con Stop rígido en ${stop_invalidacion}."
            tesis = f"El activo cotiza a {delta_poc200:.2f}% de su centro de gravedad (${poc_200:.2f}). Respaldado por SMA200 y FPC de {fpc:.1f}."
            
        else:
            veredicto = "📡 CONSOLIDACIÓN POR ENCIMA DE SOPORTE"
            nivel_riesgo = "MEDIO"
            accion = "MANTENER O MONITOREAR. Aguardar anomalía de volumen o compresión adicional."
            tesis = f"El activo oscila sobre su zona de valor (${poc_200:.2f}) sin flujo institucional agresivo actual."

    else: # precio <= poc_200
        if precio > poc_20:
            if not sma200_ok and rvol < 1.20:
                veredicto = "⏳ SANDWICH DE GRAVEDAD / REBOTE DE INERCIA"
                nivel_riesgo = "MEDIO-ALTO"
                accion = f"VENTA EN REBOTE. Tomar ganancias de corto plazo conforme se acerque a ${poc_200:.2f}."
                tesis = f"El activo está atrapado entre el piso local (${poc_20:.2f}) y la resistencia anual (${poc_200:.2f}). Rebote sin volumen suficiente para romper el techo."
            else:
                veredicto = "🛠️ RECUPERACIÓN EN DESARROLLO"
                nivel_riesgo = "MEDIO"
                accion = "COMPRA ESCALONADA TÁCTICA. Iniciar posición pequeña con objetivo en POC Anual."
                tesis = f"El precio ha superado el POC local (${poc_20:.2f}) intentando cerrar la brecha con el POC Anual (${poc_200:.2f})."
        else:
            if rvol >= 1.20 and not obv_creciente:
                veredicto = "🛑 CASCADA DE LIQUIDEZ / DISTRIBUCIÓN AGRESIVA"
                nivel_riesgo = "CRÍTICO"
                accion = "PROHIBIDA LA ENTRADA. Salir de posiciones o ejecutar stop de inmediato."
                tesis = f"Venta institucional activa. Perforación bajo el POC anual con volumen inusualmente alto ({rvol:.2f}x) y OBV decreciente."
                
            elif rvol >= 1.20 and obv_creciente:
                veredicto = "🛠️ GIRO INSTITUCIONAL DETECTADO (OLLA RECONSTRUIDA)"
                nivel_riesgo = "BAJO (Asimetría Positiva Favorable)"
                accion = f"COMPRA ESCALONADA AUTORIZADA. 50% en ${precio:.2f} y 50% al romper ${poc_200:.2f}."
                tesis = f"Absorción activa bajo el precio medio anual. RVOL de {rvol:.2f}x con OBV creciente confirma que el capital fuerte está frenando la caída sobre el POC local (${poc_20:.2f})."
                
            else:
                veredicto = "⏳ INERCIA BAJISTA PASIVA"
                nivel_riesgo = "MEDIO-ALTO"
                accion = "PERMANECER EN RADAR. No colocar capital aún."
                tesis = "Goteo bajista por falta de compradores (desinterés), no por pánico. Sin RVOL > 1.2x no hay resorte comprador."

    return {
        "veredicto": veredicto,
        "riesgo": nivel_riesgo,
        "accion": accion,
        "tesis": tesis,
        "stop": stop_invalidacion,
        "gap_pocs": round(gap_pocs, 2)
    }
