import streamlit as st
import feedparser
import re
import yfinance as yf
import pandas as pd
import numpy as np
import math

# --- [1. CONFIGURACIÓN DE IDENTIDAD Y MANIFIESTO] ---
st.set_page_config(page_title="IICU-100: Explorador Satélite", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #030712; color: #f3f4f6; }
    h1, h2, h3 { color: #00E5FF; text-shadow: 0px 0px 8px #00E5FF; }
    .card { background: rgba(255, 255, 255, 0.02); border: 1px solid #00E5FF; border-radius: 8px; padding: 15px; }
    </style>
    """, unsafe_allow_html=True)

st.title("🛰️ EXPLORADOR DE URANO: CAPTURA DE MATERIA PRIMA")
st.subheader("Módulo Satélite Autónomo de Detección de Disrupción")

# Base de datos actual del IICU-100 para exclusión automática (101 tickers en total)
PILARES_ACTUALES = {
    "1. La Mente": ["MSFT", "NVDA", "GOOGL", "AMZN", "TSM", "AVGO", "ASML", "AMD", "QCOM", "META", "SNOW", "PLTR", "MSTR", "INTC", "ARM", "KLAC", "AMAT", "CDNS", "PSTG", "ADBE"],
    "2. El Corazón": ["CEG", "VST", "CCJ", "BWXT", "SMR", "OKLO", "UUUU", "ETN", "GE", "VRT", "HUBB", "POWL", "NEE", "FSLR", "ENPH", "SEDG", "BE", "DUK", "SO", "AES"],
    "3. Biología": ["CRSP", "BEAM", "EDIT", "NTLA", "LLY", "NVO", "VRTX", "AMGN", "REGN", "TMO", "DHR", "ILMN", "A", "IQV", "RXRX", "SDGR", "DNA", "GNKX", "MRNA", "BIIB"],
    "4. Base Física": ["MP", "ALB", "SQM", "LAC", "LTHM", "FCX", "BHP", "RIO", "VALE", "TECK", "AA", "NEM", "CF", "MOS", "CAT", "DE", "JCI", "URI", "SCCO", "STLD"],
    "5. Expansión Orbital": ["RKLB", "MDA.TO", "PL", "SPIR", "BKSY", "LMT", "NOC", "RTX", "LHX", "BA", "HWM", "TDG", "JOBY", "ACHR", "TSP", "GSAT", "ASTS", "IRDM", "VSAT", "SPCE", "SPCX"]
}

# Creamos una lista aplanada para búsquedas ultrarápidas de exclusión
TICKERS_PROPIOS = set([ticker for lista in PILARES_ACTUALES.values() for ticker in lista])

# --- [2. DICCIONARIO MAESTRO DE PALABRAS CLAVE (5 PILARES)] ---
MATRIZ_SEMANTERA = {
    "1. La Mente (IA & Cuántica)": ["ai", "artificial intelligence", "quantum", "llm", "gpu", "semiconductor", "foundry", "supercomputing", "nvidia", "openai"],
    "2. El Corazón (Energía e Infraestructura)": ["nuclear", "smr", "reactor", "fusion", "grid", "electrification", "uranium", "thorium", "hydrogen"],
    "3. Biología (Ciencia de la Vida)": ["crispr", "genomics", "biotech", "mrna", "therapeutics", "dna", "longevity", "gene editing"],
    "4. Base Física (Materias Primas & Logística)": ["lithium", "cobalt", "copper", "rare earths", "commodities", "mining", "materials", "nickel", "titanium"],
    "5. Expansión Orbital (Defensa & Espacio)": ["space", "satellite", "orbit", "rocket", "payload", "defense", "hypersonic", "aerospace", "spacex"]
}

# Canales RSS públicos de alta fidelidad tecnológica e industrial
FEEDS_OBJETIVO = [
    "https://www.space.com/feeds/all",
    "https://feeds.feedburner.com/TechCrunch/",
    "https://www.defenseone.com/rss/all/",
    "https://www.technologyreview.com/feed/",
    "https://www.mining.com/feed/"
]

# --- [3. FUNCIONES DE INTELIGENCIA MATEMÁTICA Y SEMÁNTICA] ---

def calcular_fpc(ticker):
    """Motor de Poder de Ciencia: Relación I+D frente a Ingresos"""
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
        fpc_final = 100 * (1 - math.exp(-raw_score / 2)) # Función de saturación
        
        return round(fpc_final, 2)
    except:
        return 0.0

def extraer_tickers(texto):
    """Filtro Semántico: Extrae combinaciones de 3 a 5 letras en mayúsculas"""
    candidatos = re.findall(r'\b[A-Z]{3,5}\b', texto)
    falsos_positivos = ["USA", "CEO", "NEW", "FOR", "THE", "APP", "GDP", "FED", "BIT", "AI", "IPO", "NYSE", "AMER", "TECH", "RSS", "AND", "EST"]
    return [t for t in list(set(candidatos)) if t not in falsos_positivos]

def auditar_viabilidad_financiera(ticker):
    """Filtro de Viabilidad Financiera: Purga penny stocks e iliquidez"""
    try:
        asset = yf.Ticker(ticker)
        hist = asset.history(period="5d")
        if hist.empty or len(hist) < 3:
            return None
        
        precio = hist['Close'].iloc[-1]
        volumen_medio = hist['Volume'].mean()
        
        if precio < 1.0 or volumen_medio < 10000:
            return None
            
        return {"Precio": round(precio, 2), "Volumen_Medio": int(volumen_medio)}
    except:
        return None

# --- [4. INTERFAZ VISUAL DEL ARQUITECTO] ---

st.sidebar.header("CONTROLES ORBITALES")
if st.sidebar.button("INICIAR ESCANEO DE RED"):
    res_encontrados = []
    progreso = st.progress(0, text="Sincronizando sensores RSS...")
    
    # Ingesta de datos
    for idx, url in enumerate(FEEDS_OBJETIVO):
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                # El texto completo se pasa en minúsculas solo para buscar las palabras clave
                contenido_noticia_lower = f"{entry.title} {getattr(entry, 'summary', '')}".lower()
                
                # Filtrado Semántico por Pilares
                for pilar, palabras in MATRIZ_SEMANTERA.items():
                    if any(p in contenido_noticia_lower for p in palabras):
                        # SOLUCIÓN AL BUG: Extraemos tickers de título Y resumen preservando mayúsculas
                        texto_completo_original = f"{entry.title} {getattr(entry, 'summary', '')}"
                        tickers_potenciales = extraer_tickers(texto_completo_original)
                        
                        for ticker in tickers_potenciales:
                            # EXCLUSIÓN AUTOMÁTICA: Si ya es parte del IICU-100, se ignora
                            if ticker in TICKERS_PROPIOS:
                                continue
                                
                            # Evitamos duplicar candidatos dentro del mismo escaneo
                            if not any(item['Ticker'] == ticker for item in res_encontrados):
                                datos_mercado = auditar_viabilidad_financiera(ticker)
                                if datos_mercado:
                                    # CALCULO DE FPC INTEGRADO
                                    fpc_score = calcular_fpc(ticker)
                                    
                                    res_encontrados.append({
                                        "Ticker": ticker,
                                        "Pilar Detectado": pilar,
                                        "FPC (Innovación)": fpc_score,
                                        "Precio Actual": datos_mercado["Precio"],
                                        "Volumen 5D": datos_mercado["Volumen_Medio"],
                                        "Noticia de Origen": entry.title
                                    })
        except:
            continue
        progreso.progress((idx + 1) / len(FEEDS_OBJETIVO), text=f"Escaneando canal {idx+1}...")
        
    progreso.empty()
    
    if res_encontrados:
        # Ordenamos los descubrimientos de mayor a menor FPC
        df_ordenado = pd.DataFrame(res_encontrados).sort_values(by="FPC (Innovación)", ascending=False)
        st.session_state['lista_descubrimientos'] = df_ordenado
    else:
        st.info("El entorno macro está en calma. No se detectan anomalías tecnológicas viables en este ciclo.")

# Despliegue de Resultados para la Decisión del Arquitecto
if 'lista_descubrimientos' in st.session_state:
    df_descubrimientos = st.session_state['lista_descubrimientos']
    
    st.markdown("### 🛰️ VECTORES TECNOLÓGICOS DETECTADOS (Externos al IICU-100)")
    st.markdown("El satélite ha aislado estos activos alternativos. Ordenados prioritariamente por su **Factor de Poder de Ciencia (FPC)**:")
    
    # Presentar tabla interactiva
    st.dataframe(df_descubrimientos, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### 🏛️ SENTENCIA AUTOMATIZADA DEL CENSOR")
    st.info("💡 **Uso Estratégico:** Si el Censor de Urano de tu aplicación principal te sugiere sacar una empresa por *Atrofia Estructural*, toma la que tenga mayor **FPC (Innovación)** de esta tabla que pertenezca al mismo pilar e intégrala en tu código maestro.")