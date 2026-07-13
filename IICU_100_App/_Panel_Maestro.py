import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import google.generativeai as genai
from datetime import datetime, timedelta

st.set_page_config(app_title="IICU-100", page_icon="🛰️", layout="wide")

# --- [I. CONFIGURACIÓN DE IDENTIDAD Y MANIFIESTO] ---
PILARES = {
    "1. La Mente": ["MSFT", "NVDA", "GOOGL", "AMZN", "TSM", "AVGO", "ASML", "AMD", "QCOM", "META", "SNOW", "PLTR", "MSTR", "INTC", "ARM", "KLAC", "AMAT", "CDNS", "PSTG", "ADBE"],
    "2. El Corazón": ["CEG", "VST", "CCJ", "BWXT", "SMR", "OKLO", "UUUU", "ETN", "GE", "VRT", "HUBB", "POWL", "NEE", "FSLR", "ENPH", "SEDG", "BE", "DUK", "SO", "AES"],
    "3. Biología": ["CRSP", "BEAM", "EDIT", "NTLA", "LLY", "NVO", "VRTX", "AMGN", "REGN", "TMO", "DHR", "ILMN", "A", "IQV", "RXRX", "SDGR", "DNA", "GNKX", "MRNA", "BIIB"],
    "4. Base Física": ["MP", "ALB", "SQM", "LAC", "LTHM", "FCX", "BHP", "RIO", "VALE", "TECK", "AA", "NEM", "CF", "MOS", "CAT", "DE", "JCI", "URI", "SCCO", "STLD"],
    "5. Expansión Orbital": ["RKLB", "MDA.TO", "PL", "SPIR", "BKSY", "LMT", "NOC", "RTX", "LHX", "BA", "HWM", "TDG", "JOBY", "ACHR", "TSP", "GSAT", "ASTS", "IRDM", "VSAT", "SPCE", "SPCX"]
}

def calcular_fpc(ticker):
    try:
        asset = yf.Ticker(ticker)
        info = asset.info
        
        # 1. Captura Robusta de I+D (con respaldo)
        rd = info.get('researchDevelopment')
        if rd is None or rd == 0:
            # Si no hay I+D explícito, buscamos en gastos operativos como proxy
            rd = info.get('totalOperatingExpenses', 0) * 0.2 
        
        rev = info.get('totalRevenue', 1)
        if rev <= 0: rev = 1 # Evitar división por cero
        
        # 2. Ratio de Intensidad (Ciencia sobre Ingreso)
        # Usamos valor absoluto para que las pérdidas por investigar sumen, no resten
        intensity = abs(rd / rev)
        
        # 3. Factor de Crecimiento y Vigor
        growth = abs(info.get('revenueGrowth', 0.1))
        
        # 4. Cálculo Final Normalizado (Escala 0-100)
        # Aplicamos una función logarítmica para que las empresas "Ignición" 
        # no den valores de 100,000, sino que se estabilicen en el tope de la escala.
        import math
        raw_score = (intensity * 70) + (growth * 30)
        fpc_final = 100 * (1 - math.exp(-raw_score / 2)) # Función de saturación
        
        return round(fpc_final, 2)
    except:
        return 0.0

# --- [NUEVO: PROTOCOLO DE CENSOR] ---

def censor_de_urano(pilar_actual, candidatos_externos):
    propuestas_sustitucion = []
    
    # 1. Identificar al nodo más débil. 
    # Usamos 'FPC (Peso)' porque así lo nombras en auditoria_tecnica
    nodos_con_fpc = [n for n in pilar_actual if n.get('FPC (Peso)') is not None]
    if not nodos_con_fpc: return []
    
    peor_nodo = min(nodos_con_fpc, key=lambda x: x['FPC (Peso)'])
    
    for aspirante in candidatos_externos:
        # Evitar comparar contra sí mismo si el aspirante ya está en el pilar
        if aspirante in [n['Sigla'] for n in pilar_actual]: continue
        
        fpc_aspirante = calcular_fpc(aspirante)
        
        # 2. Umbral de Sustitución
        if fpc_aspirante > (peor_nodo['FPC (Peso)'] * 1.20) or peor_nodo['FPC (Peso)'] < 10.0:
            propuestas_sustitucion.append({
                "SALE": peor_nodo['Sigla'],
                "ENTRA": aspirante,
                "FPC_NUEVO": fpc_aspirante,
                "MOTIVO": "Superioridad de Innovación" if fpc_aspirante > peor_nodo['FPC (Peso)'] else "Atrofia Estructural"
            })
            break # Solo sugerimos el cambio más relevante para no saturar
            
    return propuestas_sustitucion

def calcular_rendimiento_y_alpha(df_pilar, ticker_benchmark="SPY"):
    try:
        # Descarga el benchmark (S&P 500)
        benchmark = yf.Ticker(ticker_benchmark).history(period="1y")['Close']
        if benchmark.empty: return None, 0, 0
        bench_norm = (benchmark / benchmark.iloc[0]) * 100

        # Calcula el promedio del pilar (Índice IICU)
        pilares_data = []
        for t in df_pilar['Sigla']:
            h = yf.Ticker(t).history(period="1y")['Close']
            if not h.empty:
                pilares_data.append((h / h.iloc[0]) * 100)
        
        iicu_norm = pd.concat(pilares_data, axis=1).mean(axis=1)

        # Cálculo de métricas
        ret_iicu = round(iicu_norm.iloc[-1] - 100, 2)
        ret_spy = round(bench_norm.iloc[-1] - 100, 2)
        alpha = round(ret_iicu - ret_spy, 2)

        # Construcción del Gráfico
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=bench_norm.index, y=bench_norm, name="S&P 500", line=dict(color='#888888', dash='dot')))
        fig.add_trace(go.Scatter(x=iicu_norm.index, y=iicu_norm, name="IICU-100", line=dict(color='#00FFAA', width=4)))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color="#e0e0e0"), height=400, margin=dict(l=0, r=0, t=30, b=0),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        return fig, alpha, ret_iicu
    except:
        return None, 0, 0

# --- [EJECUCIÓN EN LA AUDITORÍA] ---
# Al auditar el nodo, ahora calculamos su relevancia en el Índice
# Ejemplo: Si SMR (NuScale) gasta más en I+D proporcionalmente que un gigante,
# su FPC será mayor, dándole más protagonismo en la Sentencia de Urano.
# --- [II. MOTOR DE AUDITORÍA CUÁNTICA - CAPAS 2 Y 3] ---
def auditoria_tecnica(ticker):
    try:
        asset = yf.Ticker(ticker)
        hist = asset.history(period="1y")
        if len(hist) < 200: return None

        # CAPA 2: CUADRANTE DE HIERRO (Verdad Matemática)
        close = hist['Close']
        sma200 = close.rolling(200).mean().iloc[-1]
        sma50 = close.rolling(50).mean().iloc[-1]
        actual = close.iloc[-1]
        
        # RSI Estricto (Criterio de Fatiga < 35)
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs)).iloc[-1]
        
        # OBV (Flujo de Dinero Inteligente)
        obv = (np.sign(close.diff()) * hist['Volume']).fillna(0).cumsum()
        obv_trend = obv.iloc[-1] > obv.rolling(10).mean().iloc[-1]

        # Validación Capa 2
        es_soberano = (actual > sma200) and (sma50 > sma200) and (rsi < 35) and obv_trend

        # CAPA 3: SENSORES DE IGNICIÓN
        ignicion = False
        if es_soberano:
            vol_rel = hist['Volume'].iloc[-1] / hist['Volume'].rolling(20).mean().iloc[-1]
            # Divergencia: Precio baja, RSI sube (últimos 3 días)
            div_rsi = rsi > 100 - (100 / (1 + (gain / loss)).iloc[-3])
            div_prc = actual < close.iloc[-3]
            if vol_rel > 1.8 or (div_rsi and div_prc):
                ignicion = True

        estado = "🔥 CRUCE DE URANO" if ignicion else ("💎 SOBERANO" if es_soberano else "📡 RADAR")
        
        # ... (dentro de auditoria_tecnica, justo antes del return)
        
        fpc_valor = calcular_fpc(ticker) # Llamada al nuevo motor

        return {
            "Sigla": ticker,
            "Precio": round(actual, 2),
            "RSI": round(rsi, 1),
            "FPC (Peso)": fpc_valor, # <--- NUEVA COLUMNA
            "SMA 200": "✅" if actual > sma200 else "❌",
            "Flujo": "💹" if obv_trend else "📉",
            "Estado": estado
        }
    except: return None

# --- [III. CAPA 4: SENTENCIA DE URANO (RESILIENTE)] ---
def ejecutar_sentencia(row, prompt_manifiesto):
    # Intento de conexión con el Oráculo (Google AI)
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content(f"Analiza {row['Sigla']} basado en el manifiesto: {prompt_manifiesto}. Determina si hay Falla Estructural o Empresa Herida.")
        return response.text
    except Exception as e:
        # FALLBACK: Sentencia Algorítmica Local si hay Error 404
        if row['Estado'] == "🔥 CRUCE DE URANO":
            return f"⚠️ [Soberanía Local Activa - Error 404 Oráculo]\n\nAUDITORÍA: El activo {row['Sigla']} presenta una Divergencia Soberana con volumen de capitulación. No se detectan fallas estructurales matemáticas. DIAGNÓSTICO: EMPRESA HERIDA - OPORTUNIDAD ESTRATÉGICA."
        else:
            return f"⚠️ [Soberanía Local Activa]\n\nAUDITORÍA TÉCNICA: {row['Sigla']} cumple el Cuadrante de Hierro. RSI en {row['RSI']} indica capitulación de manos débiles. DIAGNÓSTICO: VALIDACIÓN TÉCNICA COMPLETADA."

# --- [IV. INTERFAZ IICU-100 v3.7.5] ---
st.set_page_config(page_title="IICU-100 Soberanía", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .glass { background: rgba(255, 255, 255, 0.03); border: 1px solid #00FFAA; border-radius: 10px; padding: 15px; }
    h1, h2 { color: #00FFAA; text-shadow: 0px 0px 10px #00FFAA; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏛️ IICU-100: INFRAESTRUCTURA DEL FUTURO")
st.sidebar.header("CONFIGURACIÓN MAESTRA")
api_key = st.sidebar.text_input("Clave Oráculo", type="password")

if api_key:
    genai.configure(api_key="key")

nodo_seleccionado = st.selectbox("Seleccionar Nodo de Poder", list(PILARES.keys()))

if st.button("EJECUTAR AUDITORÍA DE NODO"):
    res_list = []
    with st.spinner("Escaneando Cuadrante de Hierro..."):
        for t in PILARES[nodo_seleccionado]:
            inf = auditoria_tecnica(t)
            if inf: res_list.append(inf)

    df = pd.DataFrame(res_list)
    st.session_state['audit_data'] = df
    # Almacenamos el nombre del pilar para que el Censor sepa qué está auditando
    st.session_state['pilar_activo'] = nodo_seleccionado

if 'audit_data' in st.session_state:
    df = st.session_state['audit_data']
    st.markdown("### 🛰️ MAPA DE PODER ACTUAL")
    st.table(df)

if 'audit_data' in st.session_state:
    df = st.session_state['audit_data']
    st.markdown("### 🛰️ MAPA DE PODER ACTUAL")
    st.table(df) # <--- Tu tabla actual

    # --- [INSERCIÓN DE MÉTRICAS DE ALFA Y GRÁFICO] ---
    st.markdown("---")
    st.subheader("📊 Diagnóstico de Divergencia (Alpha de Urano)")
    
    with st.spinner("Sincronizando con el S&P 500..."):
        fig_comp, val_alpha, ret_iicu = calcular_rendimiento_y_alpha(df)
        
        if fig_comp:
            # Mostramos las métricas neón
            c1, c2 = st.columns(2)
            c1.metric("RENDIMIENTO IICU (1Y)", f"{ret_iicu}%")
            
            # El Delta muestra si el Alfa es positivo (verde) o negativo (rojo)
            c2.metric("ALFA DE SOBERANÍA", f"{val_alpha}%", 
                      delta=f"{val_alpha}% vs SPY", delta_color="normal")
            
            # Renderizamos el gráfico de divergencia
            st.plotly_chart(fig_comp, use_container_width=True)
    
    st.markdown("---")

    # --- [ INTEGRACIÓN DEL CENSOR DE URANO ] ---
    st.markdown("---")
    aspirantes_globales = ["OKLO", "ASTS", "RKLB", "VKTX", "VRT", "ARM", "PLTR"]
    
    # Convertimos el DataFrame a lista de diccionarios para que la función la entienda
    resultados_para_censor = df.to_dict('records')
    
    # LLAMADA CORREGIDA: Usamos el nombre 'censor_de_urano'
    propuestas = censor_de_urano(resultados_para_censor, aspirantes_globales)
    
    if propuestas:
        st.subheader("🛰️ Sentencia del Censor de Urano")
        for p in propuestas:
            st.warning(f"⚠️ **REBALANCEO SUGERIDO:** Sacar `{p['SALE']}` e integrar `{p['ENTRA']}`")
            st.info(f"**Razón:** {p['MOTIVO']} | **FPC del Aspirante:** {p['FPC_NUEVO']}")
    else:
        st.success("✅ El Censor no detecta anomalías. Estructura óptima.")
    st.markdown("---")

    soberanos = df[df['Estado'].isin(["💎 SOBERANO", "🔥 CRUCE DE URANO"])]

    if not soberanos.empty:
        st.markdown("### ⚖️ SENTENCIA DE URANO")
        for index, row in soberanos.iterrows():
            with st.expander(f"SENTENCIA: {row['Sigla']} ({row['Estado']})"):
                # Nota: Usamos una clave única para cada botón de Gemini
                if st.button(f"INVOCAR INTÉRPRETE: {row['Sigla']}", key=f"btn_{row['Sigla']}"):
                    veredicto = ejecutar_sentencia(row, "Pilar 2 es Corazón, Pilar 5 es Urano. Buscar Falla Estructural.")
                    st.write(veredicto)
    else:
        st.info("No se detectan activos en Zona de Soberanía (RSI > 35).")

