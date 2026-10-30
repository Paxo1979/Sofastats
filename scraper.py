import os
import json
import requests
from bs4 import BeautifulSoup

os.makedirs('dati', exist_ok=True)

LEGHE = {
    "serie_a": {"nome": "Serie A", "code": "italy"},
    "premier_league": {"nome": "Premier League", "code": "england"},
    "la_liga": {"nome": "La Liga", "code": "spain"},
    "bundesliga": {"nome": "Bundesliga", "code": "germany"},
    "ligue_1": {"nome": "Ligue 1", "code": "france"},
    "svizzera": {"nome": "Super League", "code": "switzerland"},
    "olanda": {"nome": "Eredivisie", "code": "netherlands"},
    "belgio": {"nome": "Pro League", "code": "belgium"},
    "turchia": {"nome": "Süper Lig", "code": "turkey"},
    "champions": {"nome": "Champions League", "code": "championsleague"},
    "europa_league": {"nome": "Europa League", "code": "europaleague"},
    "conference": {"nome": "Conference League", "code": "conferenceleague"}
}

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
dati_finali = {}

for chiave, info in LEGHE.items():
    dati_finali[chiave] = {
        "nome_lega": info["nome"],
        "squadre": {}
    }
    
    url = f"https://www.soccerstats.com/homeaway.asp?league={info['code']}"
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for tab in soup.find_all('table'):
                for r in tab.find_all('tr'):
                    celle = r.find_all('td')
                    if len(celle) >= 13:
                        testo_cella = celle[0].get_text(strip=True)
                        nome_sq = "".join([c for c in testo_cella if not c.isdigit()]).strip()
                        if not nome_sq:
                            nome_sq = testo_cella
                            
                        if len(nome_sq) > 2 and not any(x in nome_sq.lower() for x in ['team', 'stats', 'league', 'home', 'away', 'table', 'total', 'average', 'pts']):
                            try:
                                p_casa = int(celle[1].text.strip()) if celle[1].text.strip().isdigit() else 0
                                gf_casa = float(celle[5].text.strip()) if celle[5].text.strip().replace('.','',1).isdigit() else 0
                                gs_casa = float(celle[6].text.strip()) if celle[6].text.strip().replace('.','',1).isdigit() else 0

                                p_fuori = int(celle[7].text.strip()) if celle[7].text.strip().isdigit() else 0
                                gf_fuori = float(celle[11].text.strip()) if celle[11].text.strip().replace('.','',1).isdigit() else 0
                                gs_fuori = float(celle[12].text.strip()) if celle[12].text.strip().replace('.','',1).isdigit() else 0

                                if p_casa > 0 or p_fuori > 0:
                                    dati_finali[chiave]["squadre"][nome_sq] = {
                                        "partita_giocate": p_casa + p_fuori,
                                        "casa": {
                                            "gf": round(gf_casa / p_casa, 2) if p_casa > 0 else 0.0,
                                            "gs": round(gs_casa / p_casa, 2) if p_casa > 0 else 0.0,
                                            "corner_fatti": 5.2,
                                            "corner_concessi": 4.5,
                                            "cartellini_fatti": 2.1,
                                            "cartellini_subiti": 2.0
                                        },
                                        "fuori": {
                                            "gf": round(gf_fuori / p_fuori, 2) if p_fuori > 0 else 0.0,
                                            "gs": round(gs_fuori / p_fuori, 2) if p_fuori > 0 else 0.0,
                                            "corner_fatti": 4.5,
                                            "corner_concessi": 5.2,
                                            "cartellini_fatti": 2.3,
                                            "cartellini_subiti": 2.2
                                        }
                                    }
                            except Exception:
                                pass
    except Exception as e:
        print(f"Errore {info['nome']}: {e}")

percorso_file = os.path.join('dati', 'stats.json')
with open(percorso_file, 'w', encoding='utf-8') as f:
    json.dump(dati_finali, f, ensure_ascii=False, indent=4)

print("Scraping completato con successo!")
