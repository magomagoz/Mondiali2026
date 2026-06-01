import streamlit as st
import math
import pandas as pd

# 1. Configurazione della pagina touch-friendly per iPad
st.set_page_config(page_title="Scout Predictor 2026", page_icon="⚽", layout="wide")

st.title("🔮 WC 2026 - Match Predictor")
st.write("Seleziona due nazionali nella barra laterale per calcolare la matrice di Poisson basata sulle metriche dei calciatori.")

# 2. Database completo delle 48 squadre (Nomi puliti per iOS)
scout_ratings = {
    'Argentina': {'attacco': 1.85, 'difesa': 0.60}, 'Francia': {'attacco': 1.90, 'difesa': 0.65},
    'Brasile': {'attacco': 1.75, 'difesa': 0.70}, 'Inghilterra': {'attacco': 1.80, 'difesa': 0.65},
    'Spagna': {'attacco': 1.70, 'difesa': 0.70}, 'Portogallo': {'attacco': 1.65, 'difesa': 0.75},
    'Olanda': {'attacco': 1.45, 'difesa': 0.80}, 'Germania': {'attacco': 1.50, 'difesa': 0.85},
    'Belgio': {'attacco': 1.40, 'difesa': 0.90}, 'Croazia': {'attacco': 1.30, 'difesa': 0.85},
    'Uruguay': {'attacco': 1.40, 'difesa': 0.80}, 'Marocco': {'attacco': 1.25, 'difesa': 0.75},
    'USA': {'attacco': 1.30, 'difesa': 0.95}, 'Paraguay': {'attacco': 0.95, 'difesa': 0.85},
    'Messico': {'attacco': 1.20, 'difesa': 0.90}, 'Canada': {'attacco': 1.25, 'difesa': 1.05},
    'Giappone': {'attacco': 1.35, 'difesa': 0.90}, 'Corea del Sud': {'attacco': 1.20, 'difesa': 1.00},
    'Svizzera': {'attacco': 1.15, 'difesa': 0.85}, 'Svezia': {'attacco': 1.25, 'difesa': 0.90},
    'Ecuador': {'attacco': 1.10, 'difesa': 0.85}, 'Colombia': {'attacco': 1.30, 'difesa': 0.85},
    'Senegal': {'attacco': 1.20, 'difesa': 0.90}, 'Costa d Avorio': {'attacco': 1.15, 'difesa': 0.95},
    'Egitto': {'attacco': 1.20, 'difesa': 1.00}, 'Turchia': {'attacco': 1.25, 'difesa': 0.95},
    'Cechia': {'attacco': 1.15, 'difesa': 0.95}, 'Austria': {'attacco': 1.20, 'difesa': 0.90},
    'Norvegia': {'attacco': 1.40, 'difesa': 1.10}, 'Bosnia': {'attacco': 1.05, 'difesa': 1.05},
    'Australia': {'attacco': 1.00, 'difesa': 1.00}, 'Algeria': {'attacco': 1.10, 'difesa': 1.00},
    'Ghana': {'attacco': 1.10, 'difesa': 1.05}, 'Tunisia': {'attacco': 0.90, 'difesa': 0.95},
    'Arabia Saudita': {'attacco': 0.90, 'difesa': 1.15}, 'Qatar': {'attacco': 0.95, 'difesa': 1.20},
    'Iraq': {'attacco': 0.85, 'difesa': 1.15}, 'Sudafrica': {'attacco': 0.90, 'difesa': 1.10},
    'Uzbekistan': {'attacco': 0.90, 'difesa': 1.10}, 'DR Congo': {'attacco': 0.95, 'difesa': 1.15},
    'Curacao': {'attacco': 0.75, 'difesa': 1.45}, 'Capo Verde': {'attacco': 0.80, 'difesa': 1.30},
    'Giordania': {'attacco': 0.80, 'difesa': 1.35}, 'Haiti': {'attacco': 0.75, 'difesa': 1.40},
    'Nuova Zelanda': {'attacco': 0.80, 'difesa': 1.25}, 'Panama': {'attacco': 0.85, 'difesa': 1.20},
    'Scozia': {'attacco': 1.00, 'difesa': 1.05}, 'Iran': {'attacco': 0.95, 'difesa': 1.00}
}

MEDIA_GOL_TORNEO = 1.35

def calcola_poisson(k, lamb):
    if lamb <= 0: return 0.0
    return (lamb**k * math.exp(-lamb)) / math.factorial(k)

# 3. Interfaccia Sidebar
st.sidebar.header("🏃‍♂️ Seleziona il Match")
lista_squadre = sorted(list(scout_ratings.keys()))

# Default impostato su una classica sfida d'élite
casa = st.sidebar.selectbox("Squadra in Casa (Home)", lista_squadre, index=lista_squadre.index("Francia"))
ospite = st.sidebar.selectbox("Squadra Ospite (Away)", lista_squadre, index=lista_squadre.index("Italia") if "Italia" in lista_squadre else 0)

if casa == ospite:
    st.sidebar.error("🚨 Errore: Seleziona due squadre diverse!")
else:
    # 4. Estrazione Rating e Calcolo dei Gol Attesi (Lambda)
    r_casa = scout_ratings[casa]
    r_ospite = scout_ratings[ospite]
    
    lambda_casa = MEDIA_GOL_TORNEO * r_casa['attacco'] * r_ospite['difesa']
    lambda_ospite = MEDIA_GOL_TORNEO * r_ospite['attacco'] * r_casa['difesa']
    
    # Visualizzazione dei dati dello Scout
    st.subheader(f"📊 Analisi Forze in Campo: {casa} vs {ospite}")
    c1, c2 = st.columns(2)
    with c1:
        st.metric(label=f"Gol Attesi {casa} (λ)", value=f"{lambda_casa:.2f}")
        st.caption(f"Potenza d'attacco: {r_casa['attacco']} | Vulnerabilità difesa avversaria: {r_ospite['difesa']}")
    with c2:
        st.metric(label=f"Gol Attesi {ospite} (λ)", value=f"{lambda_ospite:.2f}")
        st.caption(f"Potenza d'attacco: {r_ospite['attacco']} | Vulnerabilità difesa avversaria: {r_casa['difesa']}")
        
    st.write("---")
    
    # 5. Simulazione dei Risultati Esatti
    match_counts = {}
    for gol_c in range(6):  # Da 0 a 5 gol
        for gol_o in range(6):
            p_c = calcola_poisson(gol_c, lambda_casa)
            p_o = calcola_poisson(gol_o, lambda_ospite)
            prob_risultato = p_c * p_o * 100
            match_counts[f"{gol_c} - {gol_o}"] = prob_risultato
            
    # Estrazione dei primi 5 risultati
    top_5 = sorted(match_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # 6. Output grafico e metriche
    st.subheader("🎯 I 5 Risultati Esatti più Probabili")
    
    col_sinistra, col_destra = st.columns([1, 1])
    
    with col_sinistra:
        for pos, (risultato, prob) in enumerate(top_5, 1):
            st.metric(label=f"{pos}° Opzione di Risultato", value=risultato, delta=f"{prob:.2f}% di probabilità")
            
    with col_destra:
        st.write("📈 **Distribuzione delle Probabilità Top 5**")
        # Convertiamo in DataFrame per un grafico pulito in Streamlit
        df_chart = pd.DataFrame(top_5, columns=["Risultato", "Probabilità (%)"])
        st.bar_chart(data=df_chart, x="Risultato", y="Probabilità (%)", color="#1f77b4")
