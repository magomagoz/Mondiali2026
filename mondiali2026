import math
from collections import defaultdict

# 1. Definizione dei 12 Gruppi Ufficiali della Coppa del Mondo 2026
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

# 2. Database del Talent Scout: Ranking di Forza basato sulle metriche dei calciatori
# attacco: > 1.0 (forte), < 1.0 (debole)
# difesa: < 1.0 (solida, subisce meno), > 1.0 (vulnerabile, subisce di piu)
scout_ratings = {
    # Top Favoriti (Valori dominanti nei club d'élite)
    'Argentina': {'attacco': 1.85, 'difesa': 0.60},
    'Francia': {'attacco': 1.90, 'difesa': 0.65},
    'Brasile': {'attacco': 1.75, 'difesa': 0.70},
    'Inghilterra': {'attacco': 1.80, 'difesa': 0.65},
    'Spagna': {'attacco': 1.70, 'difesa': 0.70},
    'Portogallo': {'attacco': 1.65, 'difesa': 0.75},
    # Fascia Media / Outsider
    'Olanda': {'attacco': 1.45, 'difesa': 0.80},
    'Germania': {'attacco': 1.50, 'difesa': 0.85},
    'Belgio': {'attacco': 1.40, 'difesa': 0.90},
    'Croazia': {'attacco': 1.30, 'difesa': 0.85},
    'Uruguay': {'attacco': 1.40, 'difesa': 0.80},
    'Marocco': {'attacco': 1.25, 'difesa': 0.75},
    'Stati Uniti': {'attacco': 1.30, 'difesa': 0.95},
    'Messico': {'attacco': 1.20, 'difesa': 0.90},
    'Canada': {'attacco': 1.25, 'difesa': 1.05},
    'Giappone': {'attacco': 1.35, 'difesa': 0.90},
    'Corea del Sud': {'attacco': 1.20, 'difesa': 1.00},
    'Svizzera': {'attacco': 1.15, 'difesa': 0.85},
    'Svezia': {'attacco': 1.25, 'difesa': 0.90},
    'Ecuador': {'attacco': 1.10, 'difesa': 0.85},
    'Colombia': {'attacco': 1.30, 'difesa': 0.85},
    'Senegal': {'attacco': 1.20, 'difesa': 0.90},
    'Costa d\'Avorio': {'attacco': 1.15, 'difesa': 0.95},
    'Egitto': {'attacco': 1.20, 'difesa': 1.00},
    'Turchia': {'attacco': 1.25, 'difesa': 0.95},
    'Cechia': {'attacco': 1.15, 'difesa': 0.95},
    'Austria': {'attacco': 1.20, 'difesa': 0.90},
    'Norvegia': {'attacco': 1.40, 'difesa': 1.10}, # Attacco trainato da Haaland
    'Bosnia': {'attacco': 1.05, 'difesa': 1.05},
    'Paraguay': {'attacco': 0.95, 'difesa': 0.85},
    'Australia': {'attacco': 1.00, 'difesa': 1.00},
    'Algeria': {'attacco': 1.10, 'difesa': 1.00},
    'Ghana': {'attacco': 1.10, 'difesa': 1.05},
    'Tunisia': {'attacco': 0.90, 'difesa': 0.95},
    'Arabia Saudita': {'attacco': 0.90, 'difesa': 1.15},
    'Qatar': {'attacco': 0.95, 'difesa': 1.20},
    'Iraq': {'attacco': 0.85, 'difesa': 1.15},
    'Sudafrica': {'attacco': 0.90, 'difesa': 1.10},
    'Uzbekistan': {'attacco': 0.90, 'difesa': 1.10},
    'DR Congo': {'attacco': 0.95, 'difesa': 1.15},
    # Debuttanti o Underdog con rose meno competitive nei massimi campionati
    'Curaçao': {'attacco': 0.75, 'difesa': 1.45},
    'Capo Verde': {'attacco': 0.80, 'difesa': 1.30},
    'Giordania': {'attacco': 0.80, 'difesa': 1.35},
    'Haiti': {'attacco': 0.75, 'difesa': 1.40},
    'Nuova Zelanda': {'attacco': 0.80, 'difesa': 1.25},
    'Panama': {'attacco': 0.85, 'difesa': 1.20},
    'Scozia': {'attacco': 1.00, 'difesa': 1.05},
    'Iran': {'attacco': 0.95, 'difesa': 1.00},
    'USA': {'attacco': 1.30, 'difesa': 0.95}
}

# Costante del modello: media gol storica per singola squadra a partita nei gironi
MEDIA_GOL_TORNEO = 1.35

def calcola_poisson(k, lamb):
    """Calcola la probabilità di Poisson per k eventi con media lamb."""
    if lamb == 0:
        return 1.0 if k == 0 else 0.0
    return (lamb**k * math.exp(-lamb)) / math.factorial(k)

def simula_torneo():
    # Dizionario globale per accumulare le probabilità aggregate di ogni risultato esatto
    probabilita_globali = defaultdict(float)
    totale_partite = 0
    
    # Generazione automatica del calendario della fase a gironi (Round Robin per ogni gruppo)
    for nome_gruppo, squadre in gruppi.items():
        n = len(squadre)
        for i in range(n):
            for j in range(i + 1, n):
                casa = squadre[i]
                ospite = squadre[j]
                totale_partite += 1
                
                # Estrazione dei rating dal database dello scout
                stats_casa = scout_ratings.get(casa, {'attacco': 1.0, 'difesa': 1.0})
                stats_ospite = scout_ratings.get(ospite, {'attacco': 1.0, 'difesa': 1.0})
                
                # Calcolo dei Lambda (Gol attesi)
                lambda_casa = MEDIA_GOL_TORNEO * stats_casa['attacco'] * stats_ospite['difesa']
                lambda_ospite = MEDIA_GOL_TORNEO * stats_ospite['attacco'] * stats_casa['difesa']
                
                # Matrice dei risultati esatti fino a un massimo logico di 5-5
                for gol_c in range(6):
                    for gol_o in range(6):
                        p_c = calcola_poisson(gol_c, lambda_casa)
                        p_o = calcola_poisson(gol_o, lambda_ospite)
                        p_match = p_c * p_o
                        
                        # Memorizziamo il risultato in modo standardizzato (Squadra Forte vs Squadra Debole o semplicemente i-j)
                        # Per avere i 5 risultati generici più probabili del torneo, aggreghiamo le combinazioni simmetriche?
                        # No, teniamo conto dell'ordine "Gol Casa - Gol Ospite" nelle partite come programmate.
                        probabilita_globali[(gol_c, gol_o)] += p_match

    # Normalizzazione delle probabilità sull'intero volume delle partite simulate
    risultati_finali = {}
    for score, prob_cumulata in probabilita_globali.items():
        risultati_finali[score] = (prob_cumulata / totale_partite) * 100
        
    # Ordinamento dei risultati dal più probabile al meno probabile
    risultati_ordinati = sorted(risultati_finali.items(), key=lambda x: x[1], reverse=True)
    
    return risultati_ordinati[:5], totale_partite

# Esecuzione del modello statistico
top_5, n_partite = simula_torneo()

print(f"=== ANALISI PREDITTIVA SUI GIRONI DI FIFA WORLD CUP 2026 ===")
print(f"Partite simulate in base al calendario ufficiale: {n_partite}\n")
print("I 5 Risultati Esatti con la maggiore probabilità statistica di verificarsi:")
print("-" * 65)
for posizione, (score, prob) in enumerate(top_5, 1):
    print(f"{posizione}° Posto ➡️  Risultato: {score[0]}-{score[1]} | Probabilità Media a Partita: {prob:.2f}%")
print("-" * 65)
print("Nota dello Scout: Il calcio è a basso punteggio. La convergenza matematica premia i risultati a scarto ridotto.")
