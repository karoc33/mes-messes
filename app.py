import streamlit as st
import requests
from bs4 import BeautifulSoup

st.set_page_config(page_title="Mes Messes", page_icon="⛪")
st.title("⛪ Horaires des Paroisses")

# ✅ CORRECTION 3 : Cache de 30 minutes pour éviter les requêtes répétées
@st.cache_data(ttl=1800)
def get_messes(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        r = requests.get(url, headers=headers, timeout=15)
        # ✅ CORRECTION 4 : Déclenche une HTTPError si code 4xx/5xx
        r.raise_for_status()

        r.encoding = r.apparent_encoding
        soup = BeautifulSoup(r.text, 'html.parser')

        results = []

        # ✅ CORRECTION 2 : Sélecteur plus ciblé (à affiner selon l'HTML réel du site)
        items = soup.select("li.event, article.event, div.event-item")

        # Fallback : si aucun résultat, on tente le sélecteur large avec un avertissement
        if not items:
            items = soup.find_all(['li', 'article', 'div'], class_=lambda x: x and 'event' in x)
            if not items:
                return ["⚠️ Aucun horaire détecté — la structure du site a peut-être changé."]

        for item in items:
            texte = item.get_text(separator=" ", strip=True)
            if ":" in texte and len(texte) > 15:
                results.append(texte)

        results = list(dict.fromkeys(results))
        return results[:10]

    # ✅ CORRECTION 4 : Erreurs spécifiques et messages clairs
    except requests.exceptions.Timeout:
        return ["⏱️ Délai dépassé — le site met trop de temps à répondre."]
    except requests.exceptions.ConnectionError:
        return ["🌐 Impossible de se connecter — vérifiez votre connexion internet."]
    except requests.exceptions.HTTPError as e:
        return [f"🚫 Erreur HTTP {e.response.status_code} — accès refusé ou page introuvable."]
    except Exception as e:
        return [f"❓ Erreur inattendue : {e}"]


# Tes 3 paroisses
paroisses = {
    "St-François d'Assise": "https://messes.info/communaute/gr/38/saint-francois-d-assise",
    "St-Pierre (Couleurs)": "https://messes.info/communaute/gr/38/saint-pierre-du-pays-des-couleurs",
    "St-Martin (Isle Crémieu)": "https://messes.info/communaute/gr/38/saint-martin-de-l-isle-cremieu"
}

# ✅ CORRECTION 1 : st.info() sans lien Markdown
st.info("Recherche des horaires en cours sur messes.info...")

# ✅ CORRECTION 5 : Bouton de rafraîchissement manuel
if st.button("🔄 Rafraîchir les horaires"):
    st.cache_data.clear()
    st.rerun()

for nom, url in paroisses.items():
    with st.expander(f"📍 {nom}", expanded=True):
        messes = get_messes(url)
        if messes:
            for m in messes:
                st.write(f"• {m}")
        else:
            st.warning("Aucun horaire détecté. Vérifiez sur le site si le calendrier est rempli.")

# ✅ CORRECTION 1 : lien Markdown correct dans st.caption()
st.caption("Données extraites en temps réel de [messes.info](https://messes.info)")
