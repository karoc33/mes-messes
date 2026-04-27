import streamlit as st
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Mes Messes", page_icon="⛪")
st.title("⛪ Horaires des Paroisses")

# ─────────────────────────────────────────────
# CONFIGURATION
# Demandez votre clé gratuite à : contact.messesinfo@cef.fr
# ─────────────────────────────────────────────
USER_KEY = st.secrets.get("MESSES_API_KEY", "")  # Mettez la clé dans .streamlit/secrets.toml

# IDs de communauté (partie après /communaute/ dans l'URL du site)
PAROISSES = {
    "St-François d'Assise":      "gr/38/saint-francois-d-assise",
    "St-Pierre (Couleurs)":      "gr/38/saint-pierre-du-pays-des-couleurs",
    "St-Martin (Isle Crémieu)":  "gr/38/saint-martin-de-l-isle-cremieu",
}

TYPE_LABELS = {
    "WEEKMASS":    "Messe en semaine",
    "SUNDAYMASS":  "Messe du dimanche",
    "LAUDS":       "Laudes",
    "VESPERS":     "Vêpres",
    "OTHER":       "Autre célébration",
}

BASE_URL = "https://messes.info/api/v2"

# ─────────────────────────────────────────────
# FONCTIONS
# ─────────────────────────────────────────────

@st.cache_data(ttl=1800)
def get_horaires(community_id: str, nb_jours: int = 7) -> list[dict]:
    """
    Récupère les horaires via l'API officielle messes.info pour les nb_jours prochains jours.
    Retourne une liste de dicts {date, time, type, lieu}.
    """
    if not USER_KEY:
        return [{"erreur": "Clé API manquante. Voir la section Configuration ci-dessous."}]

    resultats = []
    today = datetime.today()

    for i in range(nb_jours):
        date = (today + timedelta(days=i)).strftime("%d-%m-%Y")
        url = f"{BASE_URL}/horaires/{date} Community:{community_id}"
        params = {"userkey": USER_KEY, "format": "json"}

        try:
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            data = r.json()

            for item in data.get("listCelebrationTime", []):
                resultats.append({
                    "date":  item.get("date", date),
                    "heure": item.get("time", "?"),
                    "type":  TYPE_LABELS.get(item.get("timeType", ""), item.get("timeType", "")),
                    "lieu":  item.get("localityId", "").split("/")[-1].replace("-", " ").title(),
                })

        except requests.exceptions.Timeout:
            return [{"erreur": "⏱️ Délai dépassé — le serveur met trop de temps à répondre."}]
        except requests.exceptions.ConnectionError:
            return [{"erreur": "🌐 Impossible de se connecter — vérifiez votre connexion internet."}]
        except requests.exceptions.HTTPError as e:
            code = e.response.status_code
            if code == 401:
                return [{"erreur": "🔑 Clé API invalide ou expirée."}]
            elif code == 404:
                return [{"erreur": "🏛️ Paroisse introuvable — vérifiez l'identifiant."}]
            else:
                return [{"erreur": f"🚫 Erreur HTTP {code}."}]
        except Exception as e:
            return [{"erreur": f"❓ Erreur inattendue : {e}"}]

    return resultats


def afficher_horaires(horaires: list[dict]):
    """Affiche les horaires groupés par date dans l'interface Streamlit."""
    if not horaires:
        st.warning("Aucun horaire disponible sur les prochains jours.")
        return

    # Cas d'erreur
    if "erreur" in horaires[0]:
        st.error(horaires[0]["erreur"])
        return

    # Regroupement par date
    par_date: dict[str, list] = {}
    for h in horaires:
        par_date.setdefault(h["date"], []).append(h)

    for date_str, items in par_date.items():
        # Formatage de la date en français
        try:
            d = datetime.strptime(date_str, "%Y-%m-%d")
            jours_fr = ["Lun", "Mar", "Mer", "Jeu", "Ven", "Sam", "Dim"]
            mois_fr  = ["jan", "fév", "mar", "avr", "mai", "juin",
                        "juil", "août", "sep", "oct", "nov", "déc"]
            label_date = f"{jours_fr[d.weekday()]} {d.day} {mois_fr[d.month - 1]}"
        except ValueError:
            label_date = date_str

        st.markdown(f"**📅 {label_date}**")
        for h in sorted(items, key=lambda x: x["heure"]):
            st.markdown(f"&nbsp;&nbsp;&nbsp;🕐 `{h['heure']}` — {h['type']}"
                        + (f" *(à {h['lieu']})*" if h['lieu'] else ""),
                        unsafe_allow_html=True)
        st.markdown("---")


# ─────────────────────────────────────────────
# INTERFACE
# ─────────────────────────────────────────────

# Avertissement si pas de clé API
if not USER_KEY:
    st.warning(
        "**Clé API manquante.**  \n"
        "Demandez votre clé gratuite à `contact.messesinfo@cef.fr`  \n"
        "puis ajoutez-la dans `.streamlit/secrets.toml` :\n"
        "```toml\nMESSES_API_KEY = \"votre_cle_ici\"\n```"
    )
    st.stop()

# Sélecteur de période
nb_jours = st.slider("Afficher les horaires sur combien de jours ?", 1, 14, 7)

# Bouton de rafraîchissement
if st.button("🔄 Rafraîchir les horaires"):
    st.cache_data.clear()
    st.rerun()

st.info("Récupération des horaires via l'API officielle messes.info...")

# Affichage par paroisse
for nom, community_id in PAROISSES.items():
    with st.expander(f"📍 {nom}", expanded=True):
        horaires = get_horaires(community_id, nb_jours)
        afficher_horaires(horaires)

st.caption("Données fournies par [messes.info](https://messes.info) — Conférence des évêques de France")
