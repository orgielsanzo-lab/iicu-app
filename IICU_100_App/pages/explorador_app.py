import streamlit as st
import feedparser
import re
import yfinance as yf
import pandas as pd
import numpy as np
import math
from datetime import datetime, timezone
import time
from email.utils import parsedate_to_datetime

# --- [1. CONFIGURACIÓN DE IDENTIDAD Y MANIFIESTO] ---
st.set_page_config(page_title="IICU-100: Explorador Satélite v3.9.5", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #030712; color: #f3f4f6; }
    h1, h2, h3 { color: #00E5FF; text-shadow: 0px 0px 8px #00E5FF; }
    .card { background: rgba(255, 255, 255, 0.02); border: 1px solid #00E5FF; border-radius: 8px; padding: 15px; }
    .report-box { padding: 20px; border-radius: 10px; margin: 15px 0px; background-color: rgba(0, 229, 255, 0.05); border: 1px solid #00E5FF; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ EXPLORADOR DE URANO: CAPTURA DE MATERIA PRIMA")
st.subheader("Módulo Satélite Autónomo con Blindaje Temporal Anti-Latencia (Año Actual: 2026)")

# AÑO CRÍTICO DE OPERACIÓN
ANIO_ACTUAL = 2026

# Base de datos actual del IICU-100 para exclusión automática (101 tickers en total)
PILARES_ACTUALES = {
    "1. La Mente (IA & Cuántica)": ["MSFT", "NVDA", "GOOGL", "AMZN", "TSM", "AVGO", "ASML", "AMD", "QCOM", "META", "SNOW", "PLTR", "MSTR", "INTC", "ARM", "KLAC", "AMAT", "CDNS", "PSTG", "ADBE"],
    "2. El Corazón (Energía e Infraestructura)": ["CEG", "VST", "CCJ", "BWXT", "SMR", "OKLO", "UUUU", "ETN", "GE", "VRT", "HUBB", "POWL", "NEE", "FSLR", "ENPH", "SEDG", "BE", "DUK", "SO", "AES"],
    "3. Biología (Ciencia de la Vida)": ["CRSP", "BEAM", "EDIT", "NTLA", "LLY", "NVO", "VRTX", "AMGN", "REGN", "TMO", "DHR", "ILMN", "A", "IQV", "RXRX", "SDGR", "DNA", "GNKX", "MRNA", "BIIB"],
    "4. Base Física (Materias Primas & Logística)": ["MP", "ALB", "SQM", "LAC", "LTHM", "FCX", "BHP", "RIO", "VALE", "TECK", "AA", "NEM", "CF", "MOS", "CAT", "DE", "JCI", "URI", "SCCO", "STLD"],
    "5. Expansión Orbital (Defensa & Espacio)": ["RKLB", "MDA.TO", "PL", "SPIR", "BKSY", "LMT", "NOC", "RTX", "LHX", "BA", "HWM", "TDG", "JOBY", "ACHR", "TSP", "GSAT", "ASTS", "IRDM", "VSAT", "SPCE", "SPCX"]
}

TICKERS_PROPIOS = set([ticker for lista in PILARES_ACTUALES.values() for ticker in lista])

MATRIZ_SEMANTERA = {
    "1. La Mente (IA & Cuántica)": ["ai", "artificial intelligence", "quantum", "llm", "gpu", "semiconductor", "foundry", "supercomputing", "nvidia", "openai"],
    "2. El Corazón (Energía e Infraestructura)": ["nuclear", "smr", "reactor", "fusion", "grid", "electrification", "uranium", "thorium", "hydrogen"],
    "3. Biología (Ciencia de la Vida)": ["crispr", "genomics", "biotech", "mrna", "therapeutics", "dna", "longevity", "gene editing"],
    "4. Base Física (Materias Primas & Logística)": ["lithium", "cobalt", "copper", "rare earths", "commodities", "mining", "materials", "nickel", "titanium"],
    "5. Expansión Orbital (Defensa & Espacio)": ["space", "satellite", "orbit", "rocket", "payload", "defense", "hypersonic", "aerospace", "spacex"]
}

FEEDS_OBJETIVO = [
    "https://www.space.com/feeds/all",
    "https://feeds.feedburner.com/TechCrunch/",
    "https://www.defenseone.com/rss/all/",
    "https://www.technologyreview.com/feed/",
    "https://www.mining.com/feed/"
]

# --- [2. FUNCIONES DE INTELIGENCIA TÉCNICA Y MATEMÁTICA] ---

def calcular_fpc(ticker):
    """Motor de Poder de Ciencia"""
    try:
        asset = yf.Ticker(ticker)
        info = asset.info
        rd = info.get('researchDevelopment')
        if rd is None or rd == 0:
            rd = info.get('totalOperatingExpenses', 0) * 0.2 
        rev = info.get('totalRevenue', 1)
        if rev <= 0: rev = 1
        intensity = abs(rd / rev)
        growth = abs(info.get('revenueGrowth', 0.1))
        raw_score = (intensity * 70) + (growth * 30)
        return round(100 * (1 - math.exp(-raw_score / 2)), 2)
    except:
        return 0.0

def calcular_rsi(prices, period=14):
    """RSI Matemático"""
    deltas = np.diff(prices)
    seed = deltas[:period+1]
    up = seed[seed >= 0].sum() / period
    down = -seed[seed < 0].sum() / period
    rs = up / down if down != 0 else 0
    rsi = np.zeros_like(prices)
    rsi[:period] = 100. - 100. / (1. + rs)
    for i in range(period, len(prices)):
        delta = deltas[i - 1]
        upval = delta if delta > 0 else 0.
        downval = -delta if delta < 0 else 0.
        up = (up * (period - 1) + upval) / period
        down = (down * (period - 1) + downval) / period
        rs = up / down if down != 0 else 0
        rsi[i] = 100. - 100. / (1. + rs)
    return rsi[-1]

def pre_clasificar_estado(ticker, fpc_score):
    """Mapeo a los 5 Estados de Poder del Cuadrante de Hierro"""
    try:
        asset = yf.Ticker(ticker)
        hist = asset.history(period="1y")
        if len(hist) < 200:
            return "📡 RADAR", "Historial insuficiente para Cuadrante de Hierro."

        close_prices = hist['Close'].values
        volumes = hist['Volume'].values
        precio_actual = close_prices[-1]
        sma_200 = np.mean(close_prices[-200:])
        sma_50 = np.mean(close_prices[-50:])
        rsi_14 = calcular_rsi(close_prices, 14)
        
        ratio_vol = volumes[-1] / np.mean(volumes[-20:]) if np.mean(volumes[-20:]) > 0 else 1.0
        obv_creciente = close_prices[-1] > close_prices[-5]

        # Condicionales estrictas por Tabla de Estados
        if precio_actual > sma_200 and (ratio_vol >= 1.8 or rsi_14 > 70):
            return "🔥 CRUCE DE URANO", f"Ignición inminente ({ratio_vol:.1f}x volumen, RSI: {rsi_14:.1f})."
        if precio_actual > sma_200 and rsi_14 < 36 and fpc_score > 85:
            return "🛡️ SACUDIDA INSTITUCIONAL", f"Caza de liquidez en soporte macro. RSI: {rsi_14:.1f}."
        if precio_actual > sma_200 and sma_50 > sma_200 and rsi_14 < 35 and obv_creciente:
            return "💎 SOBERANO", f"Fuerza estructural óptima. RSI frío ({rsi_14:.1f})."
        if fpc_score > 95 and (35 <= rsi_14 <= 48) and abs(precio_actual - sma_50)/sma_50 < 0.05:
            return "⚡ OLLA DE PRESIÓN", f"Acumulación silenciosa activa. RSI: {rsi_14:.1f}."
        if precio_actual > sma_200 and fpc_score > 90 and (60 <= rsi_14 <= 68):
            return "🚀 MOMENTUM TEMPRANO", f"Saliendo de base técnica rápida. RSI: {rsi_14:.1f}."

        return "📡 RADAR", f"Latencia estándar de mercado. RSI: {rsi_14:.1f}."
    except:
        return "📡 RADAR", "Falla de diagnóstico en API de mercado."

def extraer_tickers(texto):
    candidatos = re.findall(r'\b[A-Z]{3,5}\b', texto)
    falsos_positivos = ["USA", "CEO", "NEW", "FOR", "THE", "APP", "GDP", "FED", "BIT", "AI", "IPO", "NYSE", "AMER", "TECH", "RSS", "AND", "EST"]
    return [t for t in list(set(candidatos)) if t not in falsos_positivos]

def auditar_viabilidad_financiera(ticker):
    try:
        asset = yf.Ticker(ticker)
        hist = asset.history(period="5d")
        if hist.empty or len(hist) < 3: return None
        precio = hist['Close'].iloc[-1]
        volumen_medio = hist['Volume'].mean()
        if precio < 1.0 or volumen_medio < 10000: return None
        return {"Precio": round(precio, 2), "Volumen_Medio": int(volumen_medio)}
    except:
        return None

# --- [3. EXTRAER Y FILTRAR POR FECHA (MÉTRICA DE RECHAZO ANTI-LATENCIA)] ---

def validar_fecha_noticia(entry, max_dias_antiguedad):
    """
    Filtro Temporal Soberano: Garantiza que la noticia pertenezca estrictamente al
    año 2026 y cumpla con la ventana de frescura algorítmica.
    """
    dt_noticia = None
    
    if hasattr(entry, 'published_parsed') and entry.published_parsed:
        dt_noticia = datetime.fromtimestamp(time.mktime(entry.published_parsed), tz=timezone.utc)
    elif hasattr(entry, 'published'):
        try:
            dt_noticia = parsedate_to_datetime(entry.published)
            if dt_noticia.tzinfo is None:
                dt_noticia = dt_noticia.replace(tzinfo=timezone.utc)
        except:
            return False, None

    if dt_noticia is None:
        return False, None

    if dt_noticia.year != ANIO_ACTUAL:
        return False, dt_noticia

    dt_actual = datetime.now(timezone.utc)
    diferencia_dias = (dt_actual - dt_noticia).days
    
    if diferencia_dias > max_dias_antiguedad:
        return False, dt_noticia

    return True, dt_noticia

# --- [4. INTERFAZ VISUAL DEL ARQUITECTO] ---

st.sidebar.header("🛡️ FILTROS TEMPORALES (ANTI-LATENCIA)")
max_dias = st.sidebar.slider("Días máximos de antigüedad (dentro de 2026):", min_value=1, max_value=60, value=14)

if st.sidebar.button("INICIAR ESCANEO DE RED 2026"):
    res_encontrados = []
    noticias_descartadas_anio = 0
    noticias_descartadas_antiguedad = 0
    
    progreso = st.progress(0, text="Inicializando satélite...")
    
    for idx, url in enumerate(FEEDS_OBJETIVO):
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                
                fecha_valida, dt_noticia = validar_fecha_noticia(entry, max_dias)
                
                if not fecha_valida:
                    if dt_noticia and dt_noticia.year != ANIO_ACTUAL:
                        noticias_descartadas_anio += 1
                    else:
                        noticias_descartadas_antiguedad += 1
                    continue
                
                contenido_noticia_lower = f"{entry.title} {getattr(entry, 'summary', '')}".lower()
                
                for pilar, palabras in MATRIZ_SEMANTERA.items():
                    if any(p in contenido_noticia_lower for p in palabras):
                        texto_completo_original = f"{entry.title} {getattr(entry, 'summary', '')}"
                        tickers_potenciales = extraer_tickers(texto_completo_original)
                        
                        for ticker in tickers_potenciales:
                            if ticker in TICKERS_PROPIOS:
                                continue
                                
                            if not any(item['Ticker'] == ticker for item in res_encontrados):
                                datos_mercado = auditar_viabilidad_financiera(ticker)
                                if datos_mercado:
                                    fpc_score = calcular_fpc(ticker)
                                    estado_pre, diagnostico_pre = pre_clasificar_estado(ticker, fpc_score)
                                    
                                    res_encontrados.append({
                                        "Ticker": ticker,
                                        "Pilar Detectado": pilar,
                                        "Estado Diagnosticado": estado_pre,
                                        "FPC (Innovación)": fpc_score,
                                        "Precio Actual": datos_mercado["Precio"],
                                        "Volumen 5D": datos_mercado["Volumen_Medio"],
                                        "Fecha Publicación": dt_noticia.strftime('%Y-%m-%d %H:%M'),
                                        "Diagnóstico Estructural": diagnostico_pre,
                                        "Noticia de Origen": entry.title
                                    })
        except Exception as e:
            continue
        progreso.progress((idx + 1) / len(FEEDS_OBJETIVO), text=f"Escaneando canal {idx+1}...")
        
    progreso.empty()
    
    st.session_state['descartadas_anio'] = noticias_descartadas_anio
    st.session_state['descartadas_antiguedad'] = noticias_descartadas_antiguedad
    
    if res_encontrados:
        st.session_state['lista_descubrimientos'] = pd.DataFrame(res_encontrados).sort_values(by="FPC (Innovación)", ascending=False)
    else:
        st.session_state['lista_descubrimientos'] = pd.DataFrame()

if 'lista_descubrimientos' in st.session_state:
    
    st.markdown("### 📊 AUDITORÍA DE PURGA TEMPORAL (Métricas Anti-Latencia)")
    col_m1, col_m2, col_m3 = st.columns(3)
    with col_m1:
        st.metric(label="Noticias del Presente Año (Procesadas)", value=len(st.session_state['lista_descubrimientos']))
    with col_m2:
        st.metric(label="Registros de Años Anteriores Eliminados", value=st.session_state.get('descartadas_anio', 0), delta="Fuera de Rango", delta_color="inverse")
    with col_m3:
        st.metric(label="Noticias de 2026 Fuera de Ventana de Días", value=st.session_state.get('descartadas_antiguedad', 0))

    df_descubrimientos = st.session_state['lista_descubrimientos']
    
    if not df_descubrimientos.empty:
        st.markdown("### 🛰️ VECTORES TECNOLÓGICOS DETECTADOS (2026)")
        st.dataframe(
            df_descubrimientos[[
                "Ticker", "Pilar Detectado", "Estado Diagnosticado", 
                "FPC (Innovación)", "Precio Actual", "Fecha Publicación", 
                "Diagnóstico Estructural", "Noticia de Origen"
            ]], 
            use_container_width=True
        )
        
        st.markdown("---")
        st.markdown("### 🏛️ SENTENCIA DEL CENSOR DE URANO")
        candidatos_validos = df_descubrimientos[df_descubrimientos["Estado Diagnosticado"] != "📡 RADAR"]
        
        if not candidatos_validos.empty:
            mejor_candidato = candidatos_validos.iloc[0]
            pilar_objetivo = mejor_candidato["Pilar Detectado"]
            
            st.success(f"🎯 **PROPUESTA ACTIVA DE ROTACIÓN:** El candidato **{mejor_candidato['Ticker']}** ({mejor_candidato['Estado Diagnosticado']}) tiene un FPC de **{mejor_candidato['FPC (Innovación)']}**.")
            st.info(f"Instrucción técnica: Verifica si en el pilar **{pilar_objetivo}** tu software reporta un activo con FPC inferior a 10.0 o con una diferencia del 20% en desmedro estructural para ejecutar la sustitución lineal inmediata.")
        else:
            st.info("No hay activos externos calificados para desplazar los componentes de los 5 estados en este momento.")
    else:
        st.info("Filtro temporal completado de forma estricta. Cero anomalías frescas detectadas en esta ventana de tiempo.")
