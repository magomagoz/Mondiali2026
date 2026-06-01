import streamlit as st
import math
from collections import defaultdict

# Configurazione pagina iPad-friendly
st.set_page_config(page_title="World Cup 2026 Predictor", page_icon="⚽", layout="wide")

st.title("⚽ FIFA World Cup 2026 - Data Scout Predictor")
st.subheader("Modello di Poisson applicato al ranking delle 48 finaliste")

# Database dei gironi
gruppi = {
    'A': ['Messico', 'Sudafrica', 'Corea del Sud', 'Cechia'],
    'B': ['Canada', 'Bosnia', 'Qatar', 'Svizzera'],
    'C': ['Brasile', 'Marocco', 'Haiti', 'Scozia'],
    'D': ['USA', 'Paraguay', 'Australia', 'Turchia'],
    'E': ['Germania', 'Curaçao', 'Costa d\'Avorio', 'Ecuador'],
    'F': ['Olanda', 'Giappone', 'Svezia', 'Tunisia'],
    'G': ['Belgio', 'Egitto', 'Iran', 'Nuova Zelanda'],
    'H': ['Spagna', 'Capo Verde', 'Arabia Saudita', 'Uruguay'],
    'I': ['Francia', 'Senegal', 'Iraq', 'Norvegia'],
    'J': ['Argentina', 'Algeria', 'Austria', 'Giordania'],
    'K': ['Portogallo', 'DR Congo', 'Uzbekistan', 'Colombia'],
    'L': ['Inghilterra', 'Croazia', 'Ghana', 'Panama']
}

# Database Forza Squadre (Scout Ratings)
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
    'Senegal': {'attacco': 1.20, 'difesa': 0.90}, 'Costa d\'Avorio': {'attacco': 1.15, 'difesa': 0.95},
    'Egitto': {'attacco': 1.20, 'difesa': 1.00}, 'Turchia': {'attacco': 1.25, 'difesa': 0.95},
    'Cechia': {'attacco': 1.15, 'difesa': 0.95}, 'Austria': {'attacco': 1.20, 'difesa': 0.90},
    'Norvegia': {'attacco': 1.40, 'difesa': 1.10}, 'Bosnia': {'attacco': 1.05, 'difesa': 1.05},
    'Australia': {'attacco': 1.00, 'difesa': 1.00}, 'Algeria': {'attacco': 1.10, 'difesa': 1.00},
    'Ghana': {'attacco': 1.10, 'difesa': 1.05}, 'Tunisia': {'attacco': 0.90, 'difesa': 0.95},
    'Arabia Saudita': {'attacco': 0.90, 'difesa': 1.15}, 'Qatar': {'attacco': 0.95, 'difesa': 1.20},
    'Iraq': {'attacco': 0.85, 'difesa': 1.15}, 'Sudafrica': {'attacco': 0.90, 'difesa': 1.10},
    'Uzbekistan': {'attacco': 0.90, 'difesa': 1.10}, 'DR Congo': {'attacco': 0.95, 'difesa': 1.15},
    'Curaçao': {'attacco': 0.75, 'difesa': 1.45}, 'Capo Verde': {'attacco': 0.80, 'difesa': 1.30},
    'Giordania': {'attacco': 0.80, 'difesa': 1.35}, 'Haiti': {'attacco': 0.75, 'difesa': 1.40},
    'Nuova Zelanda': {'attacco': 0.80, 'difesa': 1.25}, 'Panama': {'attacco': 0.85, 'difesa': 1.20},
    'Scozia': {'attacco': 1.00, 'difesa': 1.05}, 'Iran': {'attacco': 0.95, 'difesa': 1.00}
}

MEDIA_GOL_TORNEO = 1.35

def calcola_poisson(k, lamb):
    return (lamb**k * math.exp(-lamb)) / math.factorial(k)

# Sidebar di controllo per l'iPad
st.sidebar.header("⚙️ Parametri Modello")
soglia_gol = st.sidebar.slider("Massimo numero gol simulati per squadra", 3, 5, 4)

if st.sidebar.button("🚀 Lancia Simulazione"):
    probabilita_globali = defaultdict(float)
    totale_partite = 0
    
    for nome_gruppo, squadre in gruppi.items():
        n = len(squadre)
        for i in range(n):
            for j in range(i + 1, n):
                casa, ospite = squadre[i], squadre[j]
                totale_partite += 1
                
                stats_casa = scout_ratings.get(casa, {'attacco': 1.0, 'difesa': 1.0})
                stats_ospite = scout_ratings.get(ospite, {'attacco': 1.0, 'difesa': 1.0})
                
                lambda_casa = MEDIA_GOL_TORNEO * stats_casa['attacco'] * stats_ospite['difesa']
                lambda_ospite = MEDIA_GOL_TORNEO * stats_ospite['attacco'] * stats_casa['difesa']
                
                for gol_c in range(soglia_gol + 1):
                    for gol_o in range(soglia_gol + 1):
                        p_match = calcola_poisson(gol_c, lambda_casa) * calcola_poisson(gol_o, lambda_ospite)
                        probabilita_globali[(gol_c, gol_o)] += p_match

    # Elaborazione risultati
    top_5 = sorted({f"{score[0]} - {score[1]}": (prob / totale_partite) * 100 
                    for score, prob in probabilita_globali.items()}.items(), 
                   key=lambda x: x[1], reverse=True)[:5]
    
    # Layout a colonne su iPad
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.success(f"Analisi Completata su {totale_partite} partite dei gironi!")
        for pos, (risultato, prob) in enumerate(top_5, 1):
            st.metric(label=f"{pos}° Risultato più probabile", value=risultato, delta=f"{prob:.2f}% di chance")
            
    with col2:
        st.write("📊 **Grafico delle probabilità aggregate**")
        chart_data = {res: pr for res, pr in top_5}
        st.bar_chart(chart_data)
else:
    st.info("Clicca sul pulsante nella barra laterale per generare i 5 risultati esatti più probabili.")
