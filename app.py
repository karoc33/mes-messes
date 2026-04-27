import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Mes Messes", page_icon="⛪")
st.title("⛪ Horaires des Paroisses")

def get_messes(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # Tentative 1 : Recherche par classe standard Messes.info
        items = soup.find_all(['li', 'div'], class_='h-event')
        
        if not items:
            # Tentative 2 : Recherche par les balises de temps si la classe a changé
            items = soup.find_all('time')
            
        results = []
        for item in items[:8]: # On prend les 8 prochaines
            # On récupère le texte parent pour avoir la date et le lieu
            texte = item.get_text(separator=" ", strip=True)
            if len(texte) > 10: # Évite les lignes vides ou trop courtes
                results.append(texte)
        
        return results if results else ["Aucune messe trouvée pour le moment."]
    except Exception as e:
        return [f"Erreur de connexion : {e}"]

paroisses = {
    "St-François d'Assise": "https://messes.info/communaute/gr/38/saint-francois-d-assise",
    "St-Pierre (Couleurs)": "https://messes.info/communaute/gr/38/saint-pierre-du-pays-des-couleurs",
    "St-Martin (Isle Crémieu)": "https://messes.info/communaute/gr/38/saint-martin-de-l-isle-cremieu"
}

for nom, url in paroisses.items():
    with st.expander(nom, expanded=False):
        infos = get_messes(url)
        for info in infos:
            st.write(f"• {info}")
