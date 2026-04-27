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
        r = requests.get(url, headers=headers, timeout=15)
        # On force l'encodage pour éviter les caractères bizarres (é, à, etc.)
        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')
        
        results = []
        
        # Sur Messes.info, les horaires sont souvent dans des balises <article> ou <li> 
        # avec des classes qui contiennent 'event'
        items = soup.find_all(['li', 'article', 'div'], class_=lambda x: x and 'event' in x)
        
        for item in items:
            # On extrait le texte et on nettoie les espaces en trop
            texte = item.get_text(separator=" ", strip=True)
            # On filtre pour garder les lignes qui ont l'air d'une messe (contient souvent ':' pour l'heure)
            if ":" in texte and len(texte) > 15:
                results.append(texte)
        
        # Suppression des doublons éventuels
        results = list(dict.fromkeys(results))
        
        return results[:10] # On affiche les 10 premières
    except Exception as e:
        return [f"Erreur : {e}"]

# Tes 3 paroisses
paroisses = {
    "St-François d'Assise": "https://messes.info/communaute/gr/38/saint-francois-d-assise",
    "St-Pierre (Couleurs)": "https://messes.info/communaute/gr/38/saint-pierre-du-pays-des-couleurs",
    "St-Martin (Isle Crémieu)": "https://messes.info/communaute/gr/38/saint-martin-de-l-isle-cremieu"
}

st.info("Recherche des horaires en cours sur Messes.info...")

for nom, url in paroisses.items():
    with st.expander(f"📍 {nom}", expanded=True):
        messes = get_messes(url)
        if messes:
            for m in messes:
                st.write(f"{m}")
        else:
            st.warning("Aucun horaire détecté. Vérifiez sur le site si le calendrier est rempli.")

st.caption("Données extraites en temps réel de Messes.info")
