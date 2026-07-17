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
from scipy.stats import linregress

# --- [1. CONFIGURACIÓN DE IDENTIDAD Y MANIFIESTO] ---
st.set_page_config(page_title="IICU-100: Explorador Satélite v4.4.1", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #030712; color: #f3f4f6; }
    h1, h2, h3 { color: #00E5FF; text-shadow: 0px 0px 8px #00E5FF; }
    .card { background: rgba(255, 255, 255, 0.02); border: 1px solid #00E5FF; border-radius: 8px; padding: 15px; }
    .report-box { padding: 20px; border-radius: 10px; margin: 15px 0px; background-color: rgba(0, 229, 255, 0.05); border: 1px solid #00E5FF; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ EXPLORADOR DE URANO: CAPTURA DE MATERIA PRIMA")
st.subheader("Módulo Satélite Autónomo con Sincronización del Censor de Volumen y Redundancia FPC (v4.4.1)")

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
    """
    Motor de Poder de Ciencia Sincronizado v4.4.1.
    Posee doble redundancia (Balance Financiero Directo + Info API) para evitar colapsos a 0.0.
    """
    try:
        asset = yf.Ticker(ticker)
        
        # Redundancia principal: Acceder directamente al Estado de Resultados (.income_stmt)
        # Esto evita la consulta pesada a '.info' que suele bloquear Yahoo Finance.
        try:
            financials = asset.income_stmt
            rev = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials.index else None
            rd = financials.loc['Research And Development'].iloc[0] if 'Research And Development' in financials.index else None
            
            # Proxy matemático: Si no hay R&D declarado, usamos el 20% de Gastos Operativos
            if (rd is None or pd.isna(rd) or rd == 0) and 'Total Operating Expenses' in financials.index:
                rd = financials.loc['Total Operating Expenses'].iloc[0] * 0.2
        except:
            rev = None
            rd = None

        # Redundancia secundaria: Si el balance falló o devolvió vacío, intentamos con '.info'
        info = {}
        if rev is None or rd is None:
            try:
                info = asset.info
                if rd is None or pd.isna(rd):
                    rd = info.get('researchDevelopment')
                if rev is None or pd.isna(rev):
                    rev = info.get('totalRevenue', 1)
            except:
                pass

        # Fallbacks de seguridad para prevenir divisiones por cero o valores vacíos
        if rd is None or pd.isna(rd) or rd == 0:
            # Si no hay datos, asumimos un proxy conservador de innovación del 5% del Revenue estimado
            rd = (rev if rev and rev > 0 else 1000000) * 0.05
            
        if rev is None or pd.isna(rev) or rev <= 0: 
            rev = 1
            
        # Intensidad de Innovación
        intensity = abs(rd / rev)
        
        # Obtención del Crecimiento de Ingresos
        growth = 0.1
        try:
            growth = abs(info.get('revenueGrowth', 0.1)) if info else 0.1
        except:
            pass
            
        # Puntuación Bruta combinando Intensidad (70%) y Crecimiento (30%)
        raw_score = (intensity * 70) + (growth * 30)
        
        if raw_score <= 0.01:
            raw_score = 0.1  # Nivel de ruido técnico mínimo
            
        return round(100 * (1 - math.exp(-raw_score / 2)), 2)
    except:
        return 5.0  # Retorno residual controlado para evitar el colapso del flujo de datos a 0.0

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

def calcular_poc_segmento(df_slice, bins=50):
    """Calcula el Point of Control (POC) utilizando el Precio Típico (High+Low+Close)/3"""
    if df_slice.empty:
        return np.nan
    price_min = df_slice['Low'].min()
    price_max = df_slice['High'].max()
    if price_min == price_max:
        return price_min
    
    # [FASE A] Cálculo de Precio Típico para volumen microestructural
    typical_price = (df_slice['High'] + df_slice['Low'] + df_slice['Close']) / 3
    counts, bin_edges = np.histogram(
        typical_price, 
        bins=bins, 
        range=(price_min, price_max), 
        weights=df_slice['Volume']
    )
    max_idx = np.argmax(counts)
    return (bin_edges[max_idx] + bin_edges[max_idx + 1]) / 2

def pre_clasificar_estado(ticker, fpc_score):
    """
    Mapeo Sincronizado a Microestructura de 3 Vías bajo el POC Anual
    e Intervalos Superiores del Cuadrante de Hierro.
    """
    try:
        asset = yf.Ticker(ticker)
        hist = asset.history(period="2y")
        if len(hist) < 200:
            return "📡 RADAR", "Historial insuficiente para Cuadrante de Hierro."

        hist = hist.dropna(subset=['Close', 'Volume', 'High', 'Low'])
        
        df_200 = hist.iloc[-200:]
        df_20 = hist.iloc[-20:]
        
        precio_actual = float(hist['Close'].iloc[-1])
        
        # Calcular POCs usando el Precio Típico de la Fase A
        poc_anual = float(calcular_poc_segmento(df_200, bins=50))
        poc_local = float(calcular_poc_segmento(df_20, bins=50))
        
        # Relación de Volumen Relativo (RVOL)
        vol_prom_20 = df_20['Volume'].mean()
        vol_prom_100 = hist.iloc[-100:]['Volume'].mean()
        rvol = float(vol_prom_20 / vol_prom_100) if vol_prom_100 > 0 else 1.0
        
        # Cálculo de Tendencia OBV via Regresión Lineal
        hist['OBV'] = (np.sign(hist['Close'].diff()) * hist['Volume']).fillna(0).cumsum()
        obv_local = hist['OBV'].iloc[-20:].values
        x_range = np.arange(len(obv_local))
        slope, _, _, _, _ = linregress(x_range, obv_local)
        obv_ascendente = slope > 0
        
        bajo_poc_anual = precio_actual < poc_anual
        sostiene_poc_local = precio_actual >= (poc_local * 0.985)  # Tolerancia del 1.5%
        rvol_alto = rvol >= 1.2
        
        # --- [SITUACIÓN A: BAJO EL POC DE EQUILIBRIO ANUAL - TRES VÍAS] ---
        if bajo_poc_anual:
            if sostiene_poc_local and rvol_alto and obv_ascendente:
                return "🛠️ GIRO (Olla Reconstruida)", f"Giro / Absorción institucional. RVOL: {rvol:.2f}x, OBV Alcista."
            elif not sostiene_poc_local and rvol_alto:
                return "🛑 FUGA DE LIQUIDEZ (Agujerada)", f"Ruptura crítica de soporte. Liquidación activa con RVOL: {rvol:.2f}x."
            else:
                return "⏳ INERCIA PASIVA (Ignorar)", f"Goteo bajista sin volumen ni interés institucional. RVOL: {rvol:.2f}x."
                
        # --- [SITUACIÓN B: POR ENCIMA DEL POC ANUAL (ESTADOS SUPERIORES)] ---
        else:
            close_prices = hist['Close'].values
            rsi_14 = calcular_rsi(close_prices, 14)
            distancia_poc_anual = ((precio_actual - poc_anual) / poc_anual) * 100
            
            if distancia_poc_anual <= 5.0:
                return "🟢 ACUMULACIÓN SEGURA", f"En soporte de equilibrio macro. RSI: {rsi_14:.1f}."
            elif 5.0 < distancia_poc_anual <= 12.0:
                return "🚀 MOMENTUM / ESCAPE", f"Fuerza de escape alcista. RSI: {rsi_14:.1f}."
            else:
                return "⚠️ SOBREEXTENSIÓN", f"Fase distributiva lejana de soportes. RSI: {rsi_14:.1f}."
    except Exception as e:
        return "📡 RADAR", f"Falla de diagnóstico físico: {str(e)}"

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
        
        # Filtramos la inercia pasiva, sobreextensiones y fugas de liquidez para la propuesta de rotación lineal
        estados_excluidos = ["📡 RADAR", "⏳ INERCIA PASIVA (Ignorar)", "🛑 FUGA DE LIQUIDEZ (Agujerada)", "⚠️ SOBREEXTENSIÓN"]
        candidatos_validos = df_descubrimientos[~df_descubrimientos["Estado Diagnosticado"].isin(estados_excluidos)]
        
        if not candidatos_validos.empty:
            mejor_candidato = candidatos_validos.iloc[0]
            pilar_objetivo = mejor_candidato["Pilar Detectado"]
            
            st.success(f"🎯 **PROPUESTA ACTIVA DE ROTACIÓN:** El candidato **{mejor_candidato['Ticker']}** está clasificado en **{mejor_candidato['Estado Diagnosticado']}** con un FPC sólido de **{mejor_candidato['FPC (Innovación)']}**.")
            st.info(f"Instrucción técnica: Verifica si en el pilar **{pilar_objetivo}** tu software reporta un activo con FPC inferior a 10.0 o con una diferencia del 20% en desmedro estructural para ejecutar la sustitución lineal inmediata.")
        else:
            st.info("No hay activos externos calificados (Giro / Olla Reconstruida u Acumulación) para desplazar componentes en este ciclo.")
    else:
        st.info("Filtro temporal completado de forma estricta. Cero anomalías frescas detectadas en esta ventana de tiempo.")
