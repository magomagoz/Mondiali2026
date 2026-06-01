import streamlit as st
import math
import pandas as pd
from fpdf import FPDF
import base64

st.set_page_config(page_title="Scout Predictor 2026", page_icon="⚽", layout="wide")

st.title("🏆 WC 2026 - Advanced Delphi Predictor")
st.write("Generatore di probabilità e Report PDF per la direzione sportiva.")

# 1. Database Squadre, Rating e Bandiere
scout_ratings = {
    'Argentina': {'attacco': 1.85, 'difesa': 0.60, 'flag': '🇦🇷'}, 'Francia': {'attacco': 1.90, 'difesa': 0.65, 'flag': '🇫🇷'},
    'Brasile': {'attacco': 1.75, 'difesa': 0.70, 'flag': '🇧🇷'}, 'Inghilterra': {'attacco': 1.80, 'difesa': 0.65, 'flag': '🏴󠁧󠁢󠁥󠁮󠁧󠁿'},
    'Spagna': {'attacco': 1.70, 'difesa': 0.70, 'flag': '🇪🇸'}, 'Portogallo': {'attacco': 1.65, 'difesa': 0.75, 'flag': '🇵🇹'},
    'Olanda': {'attacco': 1.45, 'difesa': 0.80, 'flag': '🇳🇱'}, 'Germania': {'attacco': 1.50, 'difesa': 0.85, 'flag': '🇩🇪'},
    'Belgio': {'attacco': 1.40, 'difesa': 0.90, 'flag': '🇧🇪'}, 'Croazia': {'attacco': 1.30, 'difesa': 0.85, 'flag': '🇭🇷'},
    'Uruguay': {'attacco': 1.40, 'difesa': 0.80, 'flag': '🇺🇾'}, 'Marocco': {'attacco': 1.25, 'difesa': 0.75, 'flag': '🇲🇦'},
    'USA': {'attacco': 1.30, 'difesa': 0.95, 'flag': '🇺🇸'}, 'Paraguay': {'attacco': 0.95, 'difesa': 0.85, 'flag': '🇵🇾'},
    'Messico': {'attacco': 1.20, 'difesa': 0.90, 'flag': '🇲🇽'}, 'Canada': {'attacco': 1.25, 'difesa': 1.05, 'flag': '🇨🇦'},
    'Giappone': {'attacco': 1.35, 'difesa': 0.90, 'flag': '🇯🇵'}, 'Corea del Sud': {'attacco': 1.20, 'difesa': 1.00, 'flag': '🇰🇷'},
    'Svizzera': {'attacco': 1.15, 'difesa': 0.85, 'flag': '🇨🇭'}, 'Svezia': {'attacco': 1.25, 'difesa': 0.90, 'flag': '🇸🇪'},
    'Ecuador': {'attacco': 1.10, 'difesa': 0.85, 'flag': '🇪🇨'}, 'Colombia': {'attacco': 1.30, 'difesa': 0.85, 'flag': '🇨🇴'},
    'Senegal': {'attacco': 1.20, 'difesa': 0.90, 'flag': '🇸🇳'}, 'Costa d Avorio': {'attacco': 1.15, 'difesa': 0.95, 'flag': '🇨🇮'},
    'Egitto': {'attacco': 1.20, 'difesa': 1.00, 'flag': '🇪🇬'}, 'Turchia': {'attacco': 1.25, 'difesa': 0.95, 'flag': '🇹🇷'},
    'Cechia': {'attacco': 1.15, 'difesa': 0.95, 'flag': '🇨🇿'}, 'Austria': {'attacco': 1.20, 'difesa': 0.90, 'flag': '🇦🇹'},
    'Norvegia': {'attacco': 1.40, 'difesa': 1.10, 'flag': '🇳🇴'}, 'Bosnia': {'attacco': 1.05, 'difesa': 1.05, 'flag': '🇧🇦'},
    'Australia': {'attacco': 1.00, 'difesa': 1.00, 'flag': '🇦🇺'}, 'Algeria': {'attacco': 1.10, 'difesa': 1.00, 'flag': '🇩🇿'},
    'Ghana': {'attacco': 1.10, 'difesa': 1.05, 'flag': '🇬🇭'}, 'Tunisia': {'attacco': 0.90, 'difesa': 0.95, 'flag': '🇹🇳'},
    'Arabia Saudita': {'attacco': 0.90, 'difesa': 1.15, 'flag': '🇸🇦'}, 'Qatar': {'attacco': 0.95, 'difesa': 1.20, 'flag': '🇶🇦'},
    'Iraq': {'attacco': 0.85, 'difesa': 1.15, 'flag': '🇮🇶'}, 'Sudafrica': {'attacco': 0.90, 'difesa': 1.10, 'flag': '🇿🇦'},
    'Uzbekistan': {'attacco': 0.90, 'difesa': 1.10, 'flag': '🇺🇿'}, 'DR Congo': {'attacco': 0.95, 'difesa': 1.15, 'flag': '🇨🇩'},
    'Curacao': {'attacco': 0.75, 'difesa': 1.45, 'flag': '🇨🇼'}, 'Capo Verde': {'attacco': 0.80, 'difesa': 1.30, 'flag': '🇨🇻'},
    'Giordania': {'attacco': 0.80, 'difesa': 1.35, 'flag': '🇯🇴'}, 'Haiti': {'attacco': 0.75, 'difesa': 1.40, 'flag': '🇭🇹'},
    'Nuova Zelanda': {'attacco': 0.80, 'difesa': 1.25, 'flag': '🇳🇿'}, 'Panama': {'attacco': 0.85, 'difesa': 1.20, 'flag': '🇵🇦'},
    'Scozia': {'attacco': 1.00, 'difesa': 1.05, 'flag': '🏴󠁧󠁢󠁳󠁣󠁴󠁿'}, 'Iran': {'attacco': 0.95, 'difesa': 1.00, 'flag': '🇮🇷'}
}

MEDIA_GOL_TORNEO = 1.35

# 2. Calendari divisi per fasi
calendario_gironi = [
    "11 Giu | Messico vs Sudafrica", "12 Giu | Corea del Sud vs Cechia",
    "12 Giu | Canada vs Bosnia", "13 Giu | USA vs Paraguay",
    "14 Giu | Brasile vs Marocco", "16 Giu | Francia vs Senegal",
    "17 Giu | Argentina vs Algeria", "17 Giu | Inghilterra vs Croazia"
]

# Tabellone Eliminazione Diretta (Placeholders per quando finiranno i gironi)
calendario_eliminazione = [
    "Sedicesimi | 1° Gruppo A vs 2° Gruppo B",
    "Sedicesimi | 1° Gruppo C vs 2° Gruppo D",
    "Ottavi | Vincitrice S1 vs Vincitrice S2",
    "Quarti | Quarto Q1 vs Quarto Q2",
    "Semifinale | Semifinalista 1 vs Semifinalista 2",
    "Finale | Finalista 1 vs Finalista 2"
]

def calcola_poisson(k, lamb):
    if lamb <= 0: return 0.0
    return (lamb**k * math.exp(-lamb)) / math.factorial(k)

def crea_pdf_delphi(casa, ospite, top_5, lambda_c, lambda_o):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    
    # Intestazione stile Delphi
    pdf.cell(200, 10, txt="DELPHI PREDICTOR - SCOUTING REPORT", ln=True, align='C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(200, 10, txt="FIFA World Cup 2026 - Analisi Predittiva Avanzata", ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(200, 10, txt=f"MATCH: {casa} vs {ospite}", ln=True, align='C')
    
    pdf.ln(5)
    pdf.set_font("Arial", '', 12)
    pdf.cell(100, 10, txt=f"xG Attesi {casa}: {lambda_c:.2f}", align='L')
    pdf.cell(100, 10, txt=f"xG Attesi {ospite}: {lambda_o:.2f}", ln=True, align='R')
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="TOP 5 RISULTATI ESATTI (Modello di Poisson):", ln=True, align='L')
    
    pdf.set_font("Arial", '', 12)
    for pos, (risultato, prob) in enumerate(top_5, 1):
        pdf.cell(200, 10, txt=f"{pos}. Risultato {risultato} -> Probabilita': {prob:.2f}%", ln=True, align='L')
        
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 9)
    pdf.cell(200, 10, txt="Nota: Analisi generata incrociando i rating offensivi e difensivi dei 26 convocati.", ln=True, align='L')
    
    return pdf.output(dest="S").encode("latin1")

# 3. Sidebar Interattiva
st.sidebar.header("⚙️ Fase del Torneo")
fase = st.sidebar.radio("Seleziona la fase:", ["Fase a Gironi", "Eliminazione Diretta"])

if fase == "Fase a Gironi":
    match_selezionato = st.sidebar.selectbox("Partite in programma", calendario_gironi)
    data_match, squadre = match_selezionato.split(" | ")
    casa, ospite = squadre.split(" vs ")
else:
    match_selezionato = st.sidebar.selectbox("Tabellone", calendario_eliminazione)
    turno, squadre = match_selezionato.split(" | ")
    casa_placeholder, ospite_placeholder = squadre.split(" vs ")
    st.sidebar.info("Sostituisci i placeholder con le squadre reali man mano che si qualificano:")
    lista_squadre = sorted(list(scout_ratings.keys()))
    casa = st.sidebar.selectbox("Imposta Squadra 1", lista_squadre, index=0)
    ospite = st.sidebar.selectbox("Imposta Squadra 2", lista_squadre, index=1)
    data_match = turno

# Estrazione Rating
r_casa = scout_ratings.get(casa, {'attacco': 1.0, 'difesa': 1.0, 'flag': '🏴'})
r_ospite = scout_ratings.get(ospite, {'attacco': 1.0, 'difesa': 1.0, 'flag': '🏴'})

lambda_casa = MEDIA_GOL_TORNEO * r_casa['attacco'] * r_ospite['difesa']
lambda_ospite = MEDIA_GOL_TORNEO * r_ospite['attacco'] * r_casa['difesa']

# 4. Dashboard Visuale
st.subheader(f"🏟️ {data_match}: {r_casa['flag']} {casa} - {ospite} {r_ospite['flag']}")
c1, c2 = st.columns(2)
with c1:
    st.metric(label=f"xG {casa}", value=f"{lambda_casa:.2f}")
with c2:
    st.metric(label=f"xG {ospite}", value=f"{lambda_ospite:.2f}")
    
st.write("---")

match_counts = {}
for gol_c in range(6):
    for gol_o in range(6):
        prob_risultato = calcola_poisson(gol_c, lambda_casa) * calcola_poisson(gol_o, lambda_ospite) * 100
        match_counts[f"{gol_c} - {gol_o}"] = prob_risultato
        
top_5 = sorted(match_counts.items(), key=lambda x: x[1], reverse=True)[:5]

st.subheader("🎯 Top 5 Risultati Previsti")
col_sinistra, col_destra = st.columns([1, 1])

with col_sinistra:
    for pos, (risultato, prob) in enumerate(top_5, 1):
        st.metric(label=f"{pos}° Opzione", value=risultato, delta=f"{prob:.2f}%")
        
with col_destra:
    df_chart = pd.DataFrame(top_5, columns=["Risultato", "Probabilità (%)"])
    st.bar_chart(data=df_chart, x="Risultato", y="Probabilità (%)", color="#1f77b4")

# 5. Generazione PDF Delphi
st.write("---")
st.subheader("📄 Esporta Scouting Report")
st.write("Scarica la scheda tecnica in PDF pronta per la stampa o l'invio via mail.")

pdf_bytes = crea_pdf_delphi(casa, ospite, top_5, lambda_casa, lambda_ospite)
st.download_button(
    label="⬇️ Scarica Report Delphi Predictor (PDF)",
    data=pdf_bytes,
    file_name=f"Delphi_Report_{casa}_{ospite}.pdf",
    mime="application/pdf"
)
