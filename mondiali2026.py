import streamlit as st
import math
import pandas as pd
from collections import defaultdict
from fpdf import FPDF
import matplotlib.pyplot as plt
import tempfile
import urllib.request
import datetime
import os

# --- 1. CONFIGURAZIONE PAGINA (Deve essere il primissimo comando Streamlit) ---
st.set_page_config(page_title="WC 2026 Predictor Live", page_icon="⚽", layout="wide")

# --- 2. INIZIALIZZAZIONE CALENDARIO DA CSV E SESSION STATE ---
@st.cache_data
def carica_calendario_csv():
    """Carica il file CSV esterno con tutto il calendario del mondiale"""
    try:
        df = pd.read_csv("calendario_mondiali.csv")
        # Forziamo il cast a stringa per evitare problemi di formattazione dati
        df['Data'] = df['Data'].astype(str)
        df['Ora'] = df['Ora'].astype(str)
        df['Girone'] = df['Girone'].astype(str)
        df['Casa'] = df['Casa'].astype(str)
        df['Ospite'] = df['Ospite'].astype(str)
        return df
    except Exception as e:
        # Fallback di sicurezza se il file CSV non viene trovato
        st.error(f"Errore nel caricamento del file 'calendario_mondiali.csv': {e}")
        return pd.DataFrame(columns=["Data", "Ora", "Girone", "Casa", "Ospite"])

df_calendario_raw = carica_calendario_csv()

# Inizializziamo il registro dei risultati nello session_state leggendo direttamente dal CSV
if 'df_risultati' not in st.session_state:
    init_data = []
    if not df_calendario_raw.empty:
        for _, row in df_calendario_raw.iterrows():
            init_data.append({
                "Match": f"{row['Data']} - {row['Ora']} - {row['Girone']} | {row['Casa']} vs {row['Ospite']}",
                "Casa": row['Casa'], 
                "Ospite": row['Ospite'],
                "Gol Casa": 0, 
                "Gol Ospite": 0, 
                "Giocata": False
            })
    st.session_state.df_risultati = pd.DataFrame(init_data)

# --- 3. INTERFACCIA PRINCIPALE & BANNER ---
st.image("banner1.png", use_container_width=True)
st.write("Inserisci i risultati reali nel pannello per aggiornare lo stato di forma delle squadre in tempo reale.")

# --- 4. DATASET STATICI (Scout Ratings & Mappe ISO) ---
scout_ratings_base = {
    'Argentina': {'attacco': 1.85, 'difesa': 0.60, 'flag': '🇦🇷'}, 'Francia': {'attacco': 1.90, 'difesa': 0.65, 'flag': '🇫🇷'},
    'Brasile': {'attacco': 1.75, 'difesa': 0.70, 'flag': '🇧🇷'}, 'Inghilterra': {'attacco': 1.80, 'difesa': 0.65, 'flag': '🇬🇧'},
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
    'Scozia': {'attacco': 1.00, 'difesa': 1.05, 'flag': '🇬🇧'}, 'Iran': {'attacco': 0.95, 'difesa': 1.00, 'flag': '🇮🇷'}
}

iso_map = {
    'Argentina': 'ar', 'Francia': 'fr', 'Brasile': 'br', 'Inghilterra': 'gb-eng',
    'Spagna': 'es', 'Portogallo': 'pt', 'Olanda': 'nl', 'Germania': 'de',
    'Belgio': 'be', 'Croazia': 'hr', 'Uruguay': 'uy', 'Marocco': 'ma',
    'USA': 'us', 'Paraguay': 'py', 'Messico': 'mx', 'Canada': 'ca',
    'Giappone': 'jp', 'Corea del Sud': 'kr', 'Svizzera': 'ch', 'Svezia': 'se',
    'Ecuador': 'ec', 'Colombia': 'co', 'Senegal': 'sn', 'Costa d Avorio': 'ci',
    'Egitto': 'eg', 'Turchia': 'tr', 'Cechia': 'cz', 'Austria': 'at',
    'Norvegia': 'no', 'Bosnia': 'ba', 'Australia': 'au', 'Algeria': 'dz',
    'Ghana': 'gh', 'Tunisia': 'tn', 'Arabia Saudita': 'sa', 'Qatar': 'qa',
    'Iraq': 'iq', 'Sudafrica': 'za', 'Uzbekistan': 'uz', 'DR Congo': 'cd',
    'Curacao': 'cw', 'Capo Verde': 'cv', 'Giordania': 'jo', 'Haiti': 'ht',
    'Nuova Zelanda': 'nz', 'Panama': 'pa', 'Scozia': 'gb-sct', 'Iran': 'ir'
}

MEDIA_GOL_TORNEO = 1.35

# --- 5. REGISTRO RISULTATI REALI (DATA EDITOR) ---
st.header("📝 Registro Risultati Reali (Fase a Gironi)")
with st.expander("Apri il pannello per inserire i gol delle partite terminate", expanded=False):
    if not st.session_state.df_risultati.empty:
        edited_df = st.data_editor(
            st.session_state.df_risultati,
            column_config={
                "Match": st.column_config.TextColumn("Incontro Programmato", disabled=True),
                "Gol Casa": st.column_config.NumberColumn("Gol Casa", min_value=0, max_value=10, step=1),
                "Gol Ospite": st.column_config.NumberColumn("Gol Ospite", min_value=0, max_value=10, step=1),
                "Giocata": st.column_config.CheckboxColumn("Partita Terminata?")
            },
            disabled=["Match", "Casa", "Ospite"],
            hide_index=True,
            key="editor_gironi_v2"
        )
        st.session_state.df_risultati = edited_df
    else:
        st.warning("Nessun match caricato. Verifica che il file 'calendario_mondiali.csv' sia presente.")

# --- 6. CALCOLO RANKING MOBILE DINAMICO (POISSON LIVE) ---
scout_ratings = {k: v.copy() for k, v in scout_ratings_base.items()}
stats_torneo = defaultdict(lambda: {'gf': 0, 'gs': 0, 'p': 0})

if not st.session_state.df_risultati.empty:
    for _, row in st.session_state.df_risultati.iterrows():
        if row['Giocata']:
            c, o = row['Casa'], row['Ospite']
            gc, go = int(row['Gol Casa']), int(row['Gol Ospite'])
            
            stats_torneo[c]['gf'] += gc
            stats_torneo[c]['gs'] += go
            stats_torneo[c]['p'] += 1
            
            stats_torneo[o]['gf'] += go
            stats_torneo[o]['gs'] += gc
            stats_torneo[o]['p'] += 1

for team, s in stats_torneo.items():
    if s['p'] > 0 and team in scout_ratings:
        alpha = min(s['p'] * 0.15, 0.45)  # Peso forma attuale massimo 45%
        perf_att = s['gf'] / (s['p'] * MEDIA_GOL_TORNEO)
        perf_def = s['gs'] / (s['p'] * MEDIA_GOL_TORNEO)
        
        scout_ratings[team]['attacco'] = max(0.5, (alpha * perf_att) + ((1 - alpha) * scout_ratings_base[team]['attacco']))
        scout_ratings[team]['difesa'] = max(0.3, (alpha * perf_def) + ((1 - alpha) * scout_ratings_base[team]['difesa']))

# --- 7. SIDEBAR: PANNELLO DI SELEZIONE E STRATEGIA ---
st.sidebar.header("🗓️ Seleziona Match")
fase = st.sidebar.radio("Fase del Torneo:", ["Fase a Gironi", "Fasi Finali (Eliminazione)"])

# Dichiarazione variabili di tempo e contesto di default
data_partita, ora_partita, girone_partita = "", "", ""

if fase == "Fase a Gironi" and not st.session_state.df_risultati.empty:
    lista_match_sidebar = [f"{row['Match']}" for _, row in st.session_state.df_risultati.iterrows()]
    match_scelto = st.sidebar.selectbox("Partite del girone", lista_match_sidebar)
    
    # Estrazione variabili temporali e squadre basate sul formato CSV salvato nello session_state
    parte_sinistra, parte_destra = match_scelto.split(" | ")
    dati_tempo_girone = parte_sinistra.split(" - ")
    data_partita = dati_tempo_girone[0].strip()
    ora_partita = dati_tempo_girone[1].strip()
    girone_partita = dati_tempo_girone[2].strip()
    
    squadre = parte_destra.split(" vs ")
    casa = squadre[0].strip()
    ospite = squadre[1].strip()
    titolo_match = match_scelto
else:
    tabellone = ["Sedicesimi | 1° Gruppo A vs 2° Gruppo B", "Sedicesimi | 1° Gruppo C vs 2° Gruppo D", "Ottavi | Vincente S1 vs Vincente S2", "Finale | Finalista 1 vs Finalista 2"]
    slot = st.sidebar.selectbox("Slot Tabellone", tabellone)
    st.sidebar.caption("Componi la sfida inserendo le squadre qualificate:")
    t_list = sorted(list(scout_ratings.keys()))
    casa = st.sidebar.selectbox("Squadra Casa", t_list, index=t_list.index("Argentina"))
    ospite = st.sidebar.selectbox("Squadra Ospite", t_list, index=t_list.index("Francia"))
    titolo_match = f"{slot.split(' | ')[0]} | {casa} vs {ospite}"
    girone_partita = slot.split(' | ')[0]

# Sidebar Modificatori Strategici
st.sidebar.subheader("Strategia & Infermeria")
mod_motivazione_casa = st.sidebar.slider(f"Motivazione {casa}", 0.8, 1.2, 1.0, step=0.1)
mod_motivazione_ospite = st.sidebar.slider(f"Motivazione {ospite}", 0.8, 1.2, 1.0, step=0.1)

# --- 8. ELABORAZIONE STATISTICA POISSON MALUS/BONUS ---
r_casa = scout_ratings[casa]
r_ospite = scout_ratings[ospite]

lambda_casa = MEDIA_GOL_TORNEO * (r_casa['attacco'] * mod_motivazione_casa) * r_ospite['difesa']
lambda_ospite = MEDIA_GOL_TORNEO * (r_ospite['attacco'] * mod_motivazione_ospite) * r_casa['difesa']

# --- 9. VISUALIZZAZIONE DATI SULL'APP ---
st.write("---")
st.subheader(f"🏟️ Pronostico: {r_casa['flag']} {casa} vs {ospite} {r_ospite['flag']}")

if stats_torneo[casa]['p'] > 0 or stats_torneo[ospite]['p'] > 0:
    st.info("📈 Nota dello Scout: Questo calcolo include il modificatore sullo stato di forma aggiornato dai risultati reali precedenti!")

c1, c2 = st.columns(2)
with c1: st.metric(label=f"Gol Attesi {casa} (λ)", value=f"{lambda_casa:.2f}")
with c2: st.metric(label=f"Gol Attesi {ospite} (λ)", value=f"{lambda_ospite:.2f}")

# Calcolo Matrice di Probabilità dei Risultati Esatti
match_counts = {}
for gc in range(6):
    for go in range(6):
        prob = ((lambda_casa**gc * math.exp(-lambda_casa)) / math.factorial(gc)) * \
               ((lambda_ospite**go * math.exp(-lambda_ospite)) / math.factorial(go)) * 100
        match_counts[f"{gc} - {go}"] = prob

top_5 = sorted(match_counts.items(), key=lambda x: x[1], reverse=True)[:5]

# Renderizzazione Orizzontale dei 5 Pronostici Top su 5 Colonne
st.divider()
colonne = st.columns(5)
for i, (res, pr) in enumerate(top_5):
    colonne[i].metric(label=f"{i+1}° Opzione", value=res, delta=f"{pr:.2f}%")

st.divider()
st.bar_chart(pd.DataFrame(top_5, columns=["Risultato", "Probabilità (%)"]), x="Risultato", y="Probabilità (%)")

# --- 10. GENERAZIONE REPORT PDF PROFESSIONALE ---
st.write("---")
st.subheader("📄 Esporta Scheda Partita")

def genera_pdf():
    pdf = FPDF()
    pdf.add_page()

    # --- 1. INTESTAZIONE E LOGHI (FASCIA BLU) ---
    pdf.set_fill_color(0, 96, 156) 
    pdf.rect(0, 0, 210, 32, 'F') 
        
    try:
        url_casa = f"https://flagcdn.com/w80/{iso_map.get(casa, 'un')}.png"
        url_ospite = f"https://flagcdn.com/w80/{iso_map.get(ospite, 'un')}.png"
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f_casa:
            urllib.request.urlretrieve(url_casa, f_casa.name)
            pdf.image(f_casa.name, 12, 9, 22)
            
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f_ospite:
            urllib.request.urlretrieve(url_ospite, f_ospite.name)
            pdf.image(f_ospite.name, 176, 9, 22)
    except Exception:
        pass # Fallback silenzioso in assenza di rete internet
    
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", 'B', 20)
    pdf.cell(190, 10, "WORLD CUP - MATCH REPORT", ln=True, align='C')
    
    data_analisi = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(190, 7, f"Analisi effettuata il: {data_analisi}", ln=True, align='C')

    # --- 2. TITOLO MATCH E DATA/ORA PRELEVATI DAL MENU ---
    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(190, 10, f"MATCH: {casa} vs {ospite}", ln=True, align='C')
    
    if fase == "Fase a Gironi":
        testo_data_ora = f"Data programmata: {data_partita} alle ore {ora_partita} ({girone_partita})"
    else:
        testo_data_ora = f"Fase del torneo: {girone_partita}"
        
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(190, 8, testo_data_ora, ln=True, align='C')
    pdf.ln(5)
    
    # --- 3. PARAMETRI E RISULTATI ---
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 8, "PARAMETRI DI ANALISI APPLICATI:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(95, 8, f"Fattore Motivazione {casa}: x{mod_motivazione_casa}")
    pdf.cell(95, 8, f"Fattore Motivazione {ospite}: x{mod_motivazione_ospite}", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 8, "GOL ATTESI DALLE SQUADRE:", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.cell(95, 10, f"Gol Attesi {casa}: {lambda_casa:.2f}")
    pdf.cell(95, 10, f"Gol Attesi {ospite}: {lambda_ospite:.2f}", ln=True)
    pdf.ln(10)
    
    # --- 4. CREAZIONE GRAFICO PER IL PDF (Titolo in grassetto) ---
    fig, ax = plt.subplots(figsize=(4, 3))
    res_labels = [x[0] for x in top_5]
    res_probs = [x[1] for x in top_5]
    ax.bar(res_labels, res_probs, color='#00609c')
    ax.set_title('Distribuzione Risultati', fontweight='bold')
    plt.tight_layout()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as f_chart:
        plt.savefig(f_chart.name, format="png")
        chart_path = f_chart.name
    plt.close(fig)

    # --- 5. TOP 5 (Titolo in grassetto, risultati normali) EFFETTO AFFIANCATO ---
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(190, 8, "TOP 5 RISULTATI ESATTI:", ln=True)
    
    y_start = pdf.get_y()
    
    pdf.set_font("Arial", '', 11)
    for pos, (res, pr) in enumerate(top_5, 1):
        pdf.cell(95, 10, f" {pos}. Risultato {res} -> {pr:.2f}%", ln=False)
        pdf.ln(10)
        
    pdf.image(chart_path, x=110, y=y_start, w=90)
    
    return pdf.output(dest="S").encode("latin1")

# Pulsante di Download del PDF generato
st.download_button(
    label="⬇️ Scarica PDF",
    data=genera_pdf(),
    file_name=f"Pronostico_{casa}_{ospite}.pdf",
    mime="application/pdf"
)
