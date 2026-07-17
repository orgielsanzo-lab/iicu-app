import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import linregress

# --- CONFIGURACIÓN DE LA INTERFAZ ---
st.set_page_config(page_title="Censor de Volumen - IICU-100", layout="centered")

# Estilos personalizados para interfaz oscura "Cuadrante de Hierro"
st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    h1, h2, h3 { color: #00FFAA; text-shadow: 0px 0px 8px rgba(0, 255, 170, 0.4); }
    .report-box { padding: 20px; border-radius: 10px; margin: 15px 0px; }
    div[data-testid="stMetricValue"] { color: #00FFAA !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ CENSOR DE VOLUMEN E HISTOGRAMA INSTITUCIONAL")
st.subheader("Filtro de Segunda Línea con Control de Gravedad POC (2026)")
st.write("Inserta el ticker detectado por el IICU-100 para diagnosticar su estructura de acumulación y su rango de riesgo de ejecución.")

# --- PERSISTENCIA Y OPTIMIZACIÓN DE DATOS (CACHÉ) ---
@st.cache_data(ttl=600)  # Conserva los datos en caché por 10 minutos
def obtener_datos_mercado(ticker_symbol):
    try:
        asset = yf.Ticker(ticker_symbol)
        # Extraemos 2 años de datos para asegurar el cálculo limpio de las métricas de 200 días
        df = asset.history(period="2y")
        if df.empty:
            return None
        df = df.dropna(subset=['Close', 'Volume'])
        return df
    except Exception:
        return None

# Función matemática auxiliar para calcular el POC ponderado por volumen en un segmento
def calcular_poc_segmento(df_slice, bins=50):
    if df_slice.empty:
        return np.nan
    
    price_min = df_slice['Low'].min()
    price_max = df_slice['High'].max()
    
    if price_min == price_max:
        return price_min
        
    counts, bin_edges = np.histogram(
        df_slice['Close'], 
        bins=bins, 
        range=(price_min, price_max), 
        weights=df_slice['Volume']
    )
    
    # El bin con mayor volumen acumulado es el POC
    max_idx = np.argmax(counts)
    poc = (bin_edges[max_idx] + bin_edges[max_idx + 1]) / 2
    return poc

# --- ENTRADA DE DATOS SINCRO-ESTADOS ---
col_ticker, col_maestro = st.columns(2)

with col_ticker:
    ticker = st.text_input("INGRESA EL TICKER:", "").upper().strip()

with col_maestro:
    estado_maestro = st.selectbox(
        "ESTADO DEL PANEL MAESTRO:", 
        [
            "🔥 CRUCE DE URANO", 
            "💎 SOBERANO", 
            "⚡ OLLA DE PRESIÓN", 
            "🚀 MOMENTUM TEMPRANO", 
            "🛡️ SACUDIDA INSTITUCIONAL",
            "📡 RADAR"
        ]
    )

if ticker:
    with st.spinner(f"Analizando perfil de volumen para {ticker}..."):
        df_completo = obtener_datos_mercado(ticker)
        
        if df_completo is None or len(df_completo) < 200:
            st.error("❌ Datos insuficientes o incorrectos. Se requieren al menos 200 días de historial de cotización.")
        else:
            # Rebanadas temporales estrictas para el análisis
            df_200 = df_completo.iloc[-200:]
            df_100 = df_completo.iloc[-100:]
            df_20 = df_completo.iloc[-20:]
            
            precio_actual = float(df_completo['Close'].iloc[-1])
            
            # 1. CÁLCULO DE PUNTOS DE CONTROL (POC) BASADO EN BINS REALES DE PRECIO/VOLUMEN
            poc_anual = float(calcular_poc_segmento(df_200, bins=50))   # POC_200 (Muro institucional)
            poc_local = float(calcular_poc_segmento(df_20, bins=50))    # POC_20 (Ventana de acumulación local)
            
            # 2. CÁLCULO DE RATIO DE VOLUMEN RELATIVO (RVOL)
            vol_prom_20 = df_20['Volume'].mean()
            vol_prom_100 = df_100['Volume'].mean()
            rvol = float(vol_prom_20 / vol_prom_100) if vol_prom_100 > 0 else 1.0
            
            # 3. CÁLCULO DEL ON-BALANCE VOLUME (OBV) Y SU TENDENCIA CON REGRESIÓN LINEAL (SCIPY)
            df_completo['OBV'] = (np.sign(df_completo['Close'].diff()) * df_completo['Volume']).fillna(0).cumsum()
            obv_local = df_completo['OBV'].iloc[-20:].values
            
            # Usamos Scipy Linregress para calcular la pendiente exacta del OBV local de 20 días
            x_range = np.arange(len(obv_local))
            slope, _, _, _, _ = linregress(x_range, obv_local)
            obv_ascendente = slope > 0
            
            # 4. CONDICIONALES DE CONFLUENCIA DE LA FISICA DE LA OLLA (MICROESTRUCTURA)
            bajo_poc_anual = precio_actual < poc_anual
            sostiene_poc_local = precio_actual >= (poc_local * 0.985)  # Tolerancia del 1.5%
            rvol_alto = rvol >= 1.2
            
            # Clasificación matemática e inequívoca de estados del Censor
            if bajo_poc_anual:
                if sostiene_poc_local and rvol_alto and obv_ascendente:
                    estado_censor = "Giro Detectado / Olla Reconstruida"
                elif not sostiene_poc_local and rvol_alto:
                    estado_censor = "Camino de Desgastamiento / Olla Agujerada"
                else:
                    estado_censor = "Camino de Desgastamiento / Olla Agujerada"  # Fallback si no hay soporte ni volumen acumulativo
            else:
                # Estructuras por encima de la zona de gravedad institucional
                distancia_poc_anual = ((precio_actual - poc_anual) / poc_anual) * 100
                if distancia_poc_anual <= 5.0:
                    estado_censor = "Zona de Acumulación Segura"
                elif 5.0 < distancia_poc_anual <= 12.0:
                    estado_censor = "Ignición Latente / Escape"
                else:
                    estado_censor = "Exclusión por Sobreextensión"

            # Renderizado de métricas en la interfaz
            m1, m2, m3, m4 = st.columns(4)
            m1.metric("Precio Actual", f"${precio_actual:.2f}")
            m2.metric("POC Anual (200d)", f"${poc_anual:.2f}")
            m3.metric("POC Local (20d)", f"${poc_local:.2f}")
            m4.metric("RVOL (20d/100d)", f"{rvol:.2f}x")
            
            st.markdown("---")
            st.markdown(f"### 📊 Diagnóstico Físico de Flujo para **{ticker}**")
            
            # --- RENDERIZADO DEL DIAGNÓSTICO DE GRAVEDAD ---
            if estado_censor == "Camino de Desgastamiento / Olla Agujerada":
                st.markdown(f"""
                <div class="report-box" style="background-color: rgba(255, 0, 0, 0.1); border: 2px solid #FF3333;">
                    <h3 style="color: #FF3333; margin-top:0;">❌ OLLA AGUJERADA / CAMINO DE DESGASTAMIENTO</h3>
                    <p><b>Diagnóstico (Foco en Pánico):</b> El precio (<b>${precio_actual:.2f}</b>) cotiza en zona de pánico, por debajo del POC Anual (<b>${poc_anual:.2f}</b>).</p>
                    <p><b>Microestructura:</b> El soporte del POC Local de 20 días (<b>${poc_local:.2f}</b>) ha sido perforado o carece de la acumulación necesaria (RVOL: <b>{rvol:.2f}x</b>, Pendiente OBV: {'Positiva' if obv_ascendente else 'Negativa'}).</p>
                    <p><b>Riesgo:</b> Las instituciones no están absorbiendo la oferta en estos niveles. Distribución o liquidación activa. <b>Entrada Estrictamente Prohibida</b>.</p>
                </div>
                """, unsafe_allow_html=True)
                
            elif estado_censor == "Giro Detectado / Olla Reconstruida":
                st.markdown(f"""
                <div class="report-box" style="background-color: rgba(0, 255, 170, 0.1); border: 2px solid #00FFAA;">
                    <h3 style="color: #00FFAA; margin-top:0;">🛠️ GIRO DETECTADO / OLLA RECONSTRUIDA</h3>
                    <p><b>Diagnóstico (Foco en Absorción):</b> El precio cotiza bajo el POC Anual de 200 días (<b>${poc_anual:.2f}</b>) en zona de pánico controlado.</p>
                    <p><b>Microestructura:</b> El precio se sostiene firmemente sobre el POC Local de 20 días (<b>${poc_local:.2f}</b>) con un RVOL institucional inusual de <b>{rvol:.2f}x</b> (superior a 1.2x) y flujo monetario OBV acumulativo (pendiente de regresión positiva).</p>
                    <p><b>Oportunidad:</b> Fase de acumulación agresiva oculta (esfuerzo de absorción institucional). Se autorizan <b>compras escalonadas en la base</b>.</p>
                </div>
                """, unsafe_allow_html=True)
                
            elif estado_censor == "Zona de Acumulación Segura":
                st.markdown(f"""
                <div class="report-box" style="background-color: rgba(0, 255, 170, 0.1); border: 2px solid #00FFAA;">
                    <h3 style="color: #00FFAA; margin-top:0;">🟢 ZONA DE ACUMULACIÓN SEGURA (Soporte Institucional)</h3>
                    <p><b>Diagnóstico:</b> El precio está por encima del POC Anual a una distancia conservadora. El núcleo de liquidez principal actúa como un colchón gravitacional.</p>
                </div>
                """, unsafe_allow_html=True)
                
            elif estado_censor == "Ignición Latente / Escape":
                st.markdown(f"""
                <div class="report-box" style="background-color: rgba(255, 234, 0, 0.1); border: 2px solid #FFEA00;">
                    <h3 style="color: #FFEA00; margin-top:0;">🟡 IGNICIÓN LATENTE / ZONA DE ESCAPE</h3>
                    <p><b>Diagnóstico:</b> El precio muestra fuerza expansiva. El soporte principal queda atrás. Requiere confirmación de aceleración institucional.</p>
                </div>
                """, unsafe_allow_html=True)
                
            else:
                st.markdown(f"""
                <div class="report-box" style="background-color: rgba(255, 0, 0, 0.1); border: 2px solid #FF3333;">
                    <h3 style="color: #FF3333; margin-top:0;">🔴 EXCLUSIÓN POR SOBREEXTENSIÓN CRÍTICA</h3>
                    <p><b>Diagnóstico:</b> El precio se encuentra demasiado alejado de sus puntos de control institucionales. El riesgo de reversión matemática a la media es extremo.</p>
                </div>
                """, unsafe_allow_html=True)

            # --- ⚡ MATRIZ DE DECISIONES COMBINADA DE CONFLUENCIA ---
            st.markdown("### ⚡ MATRIZ DE EJECUCIÓN COMBINADA")
            
            # [1] 🔥 CRUCE DE URANO
            if estado_maestro == "🔥 CRUCE DE URANO":
                if estado_censor == "Giro Detectado / Olla Reconstruida":
                    st.success("🎯 **VEREDICTO: ENTRADA ANTICIPATIVA DE ALTA CONVICCIÓN**")
                    st.info("🧠 *Instrucción:* El Cruce de Urano en el Panel se acopla perfectamente con una Olla Reconstruida en la base. Las ballenas están absorbiendo la oferta por debajo del precio promedio anual. Iniciar acumulación táctica.")
                elif estado_censor == "Camino de Desgastamiento / Olla Agujerada":
                    st.error("🛑 **VEREDICTO: SEÑAL TRAP / DESCARTE INMEDIATO**")
                    st.info("🧠 *Instrucción:* El indicador del Panel amaga fuerza, pero el censor de volumen detecta una Olla Agujerada. Sin volumen ni soporte local, la gravedad romperá la estructura.")
                else:
                    st.success("🎯 **VEREDICTO: ENTRADA DE MOMENTUM TRADICIONAL**")
                    st.info("🧠 *Instrucción:* Estructura por encima del POC anual consolidada. Ejecutar orden de continuación estándar.")

            # [2] 💎 SOBERANO
            elif estado_maestro == "💎 SOBERANO":
                if estado_censor == "Giro Detectado / Olla Reconstruida":
                    st.success("🎯 **VEREDICTO: COMPRA SOBERANA BAJO RADAR**")
                    st.info("🧠 *Instrucción:* El activo mantiene el rango soberano a nivel macro, y localmente ha reconstruido la olla de acumulación. Alta probabilidad de expansión de largo plazo.")
                elif estado_censor == "Camino de Desgastamiento / Olla Agujerada":
                    st.error("🛑 **VEREDICTO: DISTRIBUCIÓN SOBERANA / ESCAPE DE CAPITAL**")
                    st.info("🧠 *Instrucción:* Alerta grave. Un activo catalogado como Soberano que perfora el POC de 200 días sin volumen de absorción local está en fase de distribución institucional masiva.")
                else:
                    st.info("🧠 *Instrucción:* Estructura soberana clásica sobre el soporte del POC. Continuar con DCA automatizado.")

            # [3] ⚡ OLLA DE PRESIÓN
            elif estado_maestro == "⚡ OLLA DE PRESIÓN":
                if estado_censor == "Giro Detectado / Olla Reconstruida":
                    st.success("🎯 **VEREDICTO: COMPRESIÓN SQUEEZE DETECTADA**")
                    st.info(f"🧠 *Instrucción:* Olla de presión con volumen local activo ({rvol:.2f}x) en la base de la acumulación. La ruptura alcista inminente tiene el respaldo del dinero inteligente.")
                elif estado_censor == "Camino de Desgastamiento / Olla Agujerada":
                    st.error("🛑 **VEREDICTO: OLLA AGUJERADA (Falsa Compresión)**")
                    st.info("🧠 *Instrucción:* El activo muestra baja volatilidad pero el volumen local está muerto y debajo del POC anual. El escape será bajista por liquidación silenciosa.")
                else:
                    st.warning("⚠️ **VEREDICTO: COMPRESIÓN EN ZONAS ALTAS**")
                    st.info("🧠 *Instrucción:* Olla de presión acumulando energía por encima del POC anual. No entrar hasta ruptura física del límite superior del rango de consolidación.")

            # [4] 🚀 MOMENTUM TEMPRANO
            elif estado_maestro == "🚀 MOMENTUM TEMPRANO":
                if estado_censor == "Giro Detectado / Olla Reconstruida":
                    st.success("🎯 **VEREDICTO: VELOCIDAD CON RESPALDO INSTITUCIONAL**")
                    st.info("🧠 *Instrucción:* Giro local verificado con aceleración de volumen y momentum técnico inicial. Esta combinación suele marcar el inicio de una tendencia vertical masiva.")
                elif estado_censor == "Camino de Desgastamiento / Olla Agujerada":
                    st.error("🛑 **VEREDICTO: TRAMPA DE MOMENTUM (Falso Rebote)**")
                    st.info("🧠 *Instrucción:* Rebote sin volumen ni soporte de POC local. Movimiento impulsado por minoristas atrapados. El Censor bloquea la compra.")
                else:
                    st.warning("⚠️ **VEREDICTO: MOMENTUM EN ESCAPE**")
                    st.info("🧠 *Instrucción:* Impulso alcista en desarrollo. Ejecutar únicamente con órdenes stop por encima de máximos locales para evitar retrocesos agresivos.")

            # [5] 🛡️ SACUDIDA INSTITUCIONAL
            elif estado_maestro == "🛡️ SACUDIDA INSTITUCIONAL":
                if estado_censor == "Giro Detectado / Olla Reconstruida":
                    st.success("🎯 **VEREDICTO: LIMPIEZA DE STOP-LOSS / COMPRA DE SUELO**")
                    st.info(f"🧠 *Instrucción:* Barrido de liquidez ejecutado con éxito. El precio violó el soporte anual pero las instituciones mantuvieron el POC local con volumen (RVOL: {rvol:.2f}x). Entrada óptima.")
                elif estado_censor == "Camino de Desgastamiento / Olla Agujerada":
                    st.error("🛑 **VEREDICTO: PERFORACIÓN REAL / NO COMPRAR**")
                    st.info("🧠 *Instrucción:* No es una sacudida, es una pérdida real del soporte institucional sin interés de compra a precios de descuento.")

            # [6] 📡 RADAR (Neutralidad)
            elif estado_maestro == "📡 RADAR":
                st.warning("⏳ **VEREDICTO: OBSERVACIÓN Y SEGUIMIENTO**")
                st.info("🧠 *Instrucción:* Ticker bajo monitoreo. Guardar parámetros y esperar anomalías en el volumen relativo para disparar alertas.")

            # --- 📈 GRÁFICO VISUAL DEL PERFIL DE VOLUMEN MULTI-POC ---
            fig = go.Figure()
            
            # Histograma del perfil anual de volumen (200 días)
            price_min_200 = df_200['Low'].min()
            price_max_200 = df_200['High'].max()
            counts_200, bin_edges_200 = np.histogram(
                df_200['Close'].values, 
                bins=50, 
                range=(price_min_200, price_max_200), 
                weights=df_200['Volume'].values
            )
            
            fig.add_trace(go.Bar(
                y=[(bin_edges_200[i] + bin_edges_200[i+1])/2 for i in range(len(counts_200))],
                x=counts_200,
                orientation='h',
                name='Perfil de Volumen Anual (200d)',
                marker=dict(color='rgba(0, 255, 170, 0.12)', line=dict(color='#00FFAA', width=1))
            ))
            
            # Línea de precio actual
            fig.add_trace(go.Scatter(
                x=[0, max(counts_200)],
                y=[precio_actual, precio_actual],
                mode='lines',
                name=f'Precio Actual (${precio_actual:.2f})',
                line=dict(color='#FF3388', width=3)
            ))
            
            # Línea POC Anual
            fig.add_trace(go.Scatter(
                x=[0, max(counts_200)],
                y=[poc_anual, poc_anual],
                mode='lines',
                name=f'POC Anual (${poc_anual:.2f})',
                line=dict(color='#00FFAA', width=3, dash='dash')
            ))
            
            # Línea POC Local
            fig.add_trace(go.Scatter(
                x=[0, max(counts_200)],
                y=[poc_local, poc_local],
                mode='lines',
                name=f'POC Local 20d (${poc_local:.2f})',
                line=dict(color='#FFEA00', width=2, dash='dot')
            ))
            
            fig.update_layout(
                title=f"Distribución Física del Perfil de Volumen (POC 200 vs 20) - {ticker}",
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color="#e0e0e0"),
                xaxis_title="Volumen Acumulado Ponderado",
                yaxis_title="Zonas de Precio ($)",
                height=450,
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
            )
            
            st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption("Filtro de volumen autónomo v4.3.0 - Motor de confluencia física 'Olla de Presión & Reconstruida' diseñado por téchnē.")
