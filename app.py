

import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="Gpairo Classifier", layout="wide")

st.title("🔧 Gpairo Classifier – Classification IA des Produits Industriels")

menu = st.sidebar.radio("Navigation", [
    "1️⃣ Nettoyage",
    "2️⃣ Groupement",
    "3️⃣ Classification IA",
    "4️⃣ Correction des Clés",
    "5️⃣ Export & Résultats"
])

def nettoyer_desi_arti(valeur):
    if pd.isna(valeur):
        return valeur
    texte = str(valeur).strip()
    texte = texte.lower()
    return texte

# Onglet 1 : Nettoyage
if menu == "1️⃣ Nettoyage":
    st.header("🧼 Nettoyage de la désignation (DESI_ARTI)")
    fichier = st.file_uploader("Charger un fichier CSV contenant une colonne 'DESI_ARTI'", type=["csv"])
    
    if fichier:
        df = pd.read_csv(fichier, encoding="latin1")
        
        if "DESI_ARTI" in df.columns:
            df["DESI_ARTI"] = df["DESI_ARTI"].apply(nettoyer_desi_arti)
            st.success("✅ Nettoyage effectué.")
            st.dataframe(df.head(20))
            
            csv_buffer = io.BytesIO()
            df.to_csv(csv_buffer, index=False, encoding="utf-8-sig")
            csv_buffer.seek(0)
            
            st.download_button(
                label="📥 Télécharger le fichier nettoyé",
                data=csv_buffer,
                file_name="designation_nettoyee.csv",
                mime="text/csv"
            )
        else:
            st.error("❌ La colonne 'DESI_ARTI' est introuvable dans le fichier.")

elif menu == "2️⃣ Groupement":
    st.header("🔗 Groupement à venir")
    st.info("Cette section est en cours d’intégration. Elle permettra de grouper les désignations similaires.")

elif menu == "3️⃣ Classification IA":
    st.header("🤖 Classification IA à venir")
    st.warning("Fonctionnalité à intégrer : appel à l’API Together avec prompts et traitement batch.")

elif menu == "4️⃣ Correction des Clés":
    st.header("🧩 Correction des clés")
    st.info("À venir : comparaison entre fichiers et ajout automatique des clés manquantes.")

elif menu == "5️⃣ Export & Résultats":
    st.header("📤 Téléchargement des fichiers finaux")
    st.info("Cette section vous permettra de télécharger les résultats finaux une fois le traitement complet.")

