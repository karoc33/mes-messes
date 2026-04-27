import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Mes Messes", page_icon="⛪")
st.title("⛪ Horaires des Paroisses")

def get_messes(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, 'html.parser')
        # On cible les éléments de la liste des messes
        items = soup.select('li.h-event') 
        results = []
        for item in items[:5]: # On prend les 5 prochaines
            date = item.select_one('time').text.strip()
            lieu = item.select_one('.p-location').text.strip()
            results.append(f"**{date}** : {lieu}")
        return results
    except:
        return ["Erreur de lecture"]

paroisses = {
    "St-François d'Assise": "https://messes.info/communaute/gr/38/saint-francois-d-assise",
    "St-Pierre (Couleurs)": "https://messes.info/communaute/gr/38/saint-pierre-du-pays-des-couleurs",
    "St-Martin (Isle Crémieu)": "https://messes.info/communaute/gr/38/saint-martin-de-l-isle-cremieu"
}

for nom, url in paroisses.items():
    with st.expander(nom):
        infos = get_messes(url)
        for info in infos:
            st.write(info)