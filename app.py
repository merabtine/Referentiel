import streamlit as st
import pandas as pd
import altair as alt
import matplotlib.pyplot as plt
import numpy as np
import io

st.set_page_config(page_title="Refinor", layout="wide")

logo_path = "logo.png"  
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image(logo_path, width=80)
with col_title:
    st.title("Refinor – Analyse des jeux de données référentiels")

# Reset total via session state
if "fichier_1" not in st.session_state:
    st.session_state.fichier_1 = None
if "fichier_2" not in st.session_state:
    st.session_state.fichier_2 = None
if "restarted" not in st.session_state:
    st.session_state.restarted = False

def reset_app():
    st.session_state.fichier_1 = None
    st.session_state.fichier_2 = None
    st.session_state.restarted = True
    st.experimental_rerun()

tab1, tab2 = st.tabs(["Importer les fichiers", "Explorer les données"])

with tab1:
    st.subheader("Charger les fichiers de données")
    col1, col2 = st.columns(2)

    with col1:
        st.session_state.fichier_1 = st.file_uploader("Fichier 1", type=["csv"], key="file1")
    with col2:
        st.session_state.fichier_2 = st.file_uploader("Fichier 2", type=["csv"], key="file2")

    if st.session_state.fichier_1 and st.session_state.fichier_2:
        st.success("Fichiers chargés avec succès. Passez à l’onglet suivant.")
        st.button("Réinitialiser", on_click=reset_app)

# Onglet d’analyse
if st.session_state.fichier_1 and st.session_state.fichier_2:
    df1 = pd.read_csv(st.session_state.fichier_1, encoding="utf-8-sig")
    df2 = pd.read_csv(st.session_state.fichier_2, encoding="utf-8-sig")

    with tab2:
        st.subheader("Choix du jeu de données à explorer")

        base_choisie = st.radio("Sélectionnez une base :", ["Fichier 1", "Fichier 2"], horizontal=True)
        df = df1 if base_choisie == "Fichier 1" else df2

        st.markdown("### Aperçu du fichier")
        st.dataframe(df.head(10), use_container_width=True)

        st.markdown("### Statistiques générales")

        total_produits = len(df)
        if "DESI_ARTI" in df.columns:
            uniques = df["DESI_ARTI"].nunique()
        elif "nom" in df.columns:
            uniques = df["nom"].nunique()
        else:
            uniques = total_produits

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("Nombre total de lignes")
            st.progress(min(total_produits / 1000, 1.0))  # max 1000 pour l’animation
            st.metric(label="", value=f"{total_produits} lignes")
        with col2:
            st.markdown("Produits uniques")
            st.progress(min(uniques / 1000, 1.0))
            st.metric(label="", value=f"{uniques} produits")

        if "famille" in df.columns:
            st.markdown("### Répartition des familles")
            famille_counts = df["famille"].value_counts().reset_index()
            famille_counts.columns = ["famille", "nb_produits"]
            chart = alt.Chart(famille_counts).mark_bar().encode(
                x=alt.X('nb_produits:Q', title="Nombre de produits"),
                y=alt.Y('famille:N', sort='-x', title="Famille"),
                tooltip=['famille', 'nb_produits']
            ).properties(width=700, height=400)
            st.altair_chart(chart, use_container_width=True)

        st.markdown("### Télécharger le jeu de données sélectionné")
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, encoding="utf-8-sig")
        st.download_button("Télécharger en CSV", buffer.getvalue(), file_name="base_selectionnee.csv", mime="text/csv")
