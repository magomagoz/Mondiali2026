import streamlit as st
import math
import pandas as pd

# 1. Configurazione della pagina
st.set_page_config(page_title="Scout Predictor 2026", page_icon="⚽", layout="wide")

st.title("banner.png")
#st.title("🗓️ WC 2026 - Match Predictor Ufficiale")
st.write("Seleziona una partita dal calendario ufficiale per simulare il risultato esatto tramite la Distribuzione di Poisson.")

# 2. Database Forza Squadre (Scout Ratings - Nomi puliti per iOS)
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

# 3. Calendario Ufficiale - Giornata 1 (Ordine Cronologico)
calendario = [
    "11 Giu | Messico vs Sudafrica",
    "12 Giu | Corea del Sud vs Cechia",
    "12 Giu | Canada vs Bosnia",
    "13 Giu | USA vs Paraguay",
    "13 Giu | Qatar vs Svizzera",
    "14 Giu | Brasile vs Marocco",
    "14 Giu | Haiti vs Scozia",
    "14 Giu | Australia vs Turchia",
    "14 Giu | Germania vs Curacao",
    "14 Giu | Olanda vs Giappone",
    "15 Giu | Costa d Avorio vs Ecuador",
    "15 Giu | Svezia vs Tunisia",
    "15 Giu | Spagna vs Capo Verde",
    "15 Giu | Belgio vs Egitto",
    "16 Giu | Arabia Saudita vs Uruguay",
    "16 Giu | Iran vs Nuova Zelanda",
    "16 Giu | Francia vs Senegal",
    "16 Giu | Iraq vs Norvegia",
    "17 Giu | Argentina vs Algeria",
    "17 Giu | Austria vs Giordania",
    "17 Giu | Portogallo vs DR Congo",
    "17 Giu | Inghilterra vs Croazia",
    "18 Giu | Uzbekistan vs Colombia",
    "18 Giu | Panama vs Ghana"
]

def calcola_poisson(k, lamb):
    if lamb <= 0: return 0.0
    return (lamb**k * math.exp(-lamb)) / math.factorial(k)

# 4. Interfaccia Sidebar: Scelta Partita dal Calendario
st.sidebar.header("📅 Calendario Partite")
match_selezionato = st.sidebar.selectbox("Prossime sfide in programma", calendario)

# Scomposizione stringa: "11 Giu | Messico vs Sudafrica" -> Casa="Messico", Ospite="Sudafrica"
data_match, squadre = match_selezionato.split(" | ")
casa, ospite = squadre.split(" vs ")

# 5. Estrazione Rating e Calcolo
r_casa = scout_ratings.get(casa, {'attacco': 1.0, 'difesa': 1.0})
r_ospite = scout_ratings.get(ospite, {'attacco': 1.0, 'difesa': 1.0})

lambda_casa = MEDIA_GOL_TORNEO * r_casa['attacco'] * r_ospite['difesa']
lambda_ospite = MEDIA_GOL_TORNEO * r_ospite['attacco'] * r_casa['difesa']

# Intestazione della dashboard
st.subheader(f"🏟️ Sfida del {data_match}: {casa} - {ospite}")
c1, c2 = st.columns(2)
with c1:
    st.metric(label=f"Gol Attesi {casa} (λ)", value=f"{lambda_casa:.2f}")
with c2:
    st.metric(label=f"Gol Attesi {ospite} (λ)", value=f"{lambda_ospite:.2f}")
    
st.write("---")

# 6. Simulazione dei Risultati Esatti
match_counts = {}
for gol_c in range(6):
    for gol_o in range(6):
        prob_risultato = calcola_poisson(gol_c, lambda_casa) * calcola_poisson(gol_o, lambda_ospite) * 100
        match_counts[f"{gol_c} - {gol_o}"] = prob_risultato
        
# Estrazione dei primi 5 risultati
top_5 = sorted(match_counts.items(), key=lambda x: x[1], reverse=True)[:5]

# 7. Output grafico
st.subheader(f"🎯 Top 5 Risultati Previsti per {casa} - {ospite}")

col_sinistra, col_destra = st.columns([1, 1])

with col_sinistra:
    for pos, (risultato, prob) in enumerate(top_5, 1):
        st.metric(label=f"{pos}° Opzione", value=risultato, delta=f"{prob:.2f}% di probabilità")
        
with col_destra:
    st.write("📈 **Distribuzione Probabilità (%)**")
    df_chart = pd.DataFrame(top_5, columns=["Risultato", "Probabilità (%)"])
    st.bar_chart(data=df_chart, x="Risultato", y="Probabilità (%)", color="#ff4b4b")
