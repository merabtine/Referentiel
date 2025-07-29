import streamlit as st
import pandas as pd
import time
import datetime
import altair as alt

st.set_page_config(page_title="Gpairo Visualizer", layout="wide")

st.title("📊 Gpairo Visualizer – Analyse et Comparaison des Résultats de Classification IA")

tab1, tab2 = st.tabs(["📂 Chargement des fichiers", "📈 Visualisation & Statistiques"])

with tab1:
    st.subheader("📤 Importer les fichiers")

    col1, col2 = st.columns(2)
    with col1:
        fichier_avant = st.file_uploader("📝 Fichier AVANT traitement", type=["csv"], key="avant")
    with col2:
        fichier_apres = st.file_uploader("✅ Fichier APRÈS traitement", type=["csv"], key="apres")

    if fichier_avant and fichier_apres:
        df_avant = pd.read_csv(fichier_avant, encoding="utf-8-sig")
        df_apres = pd.read_csv(fichier_apres, encoding="utf-8-sig")

        st.success("✅ Fichiers chargés avec succès. Allez à l'onglet suivant.")

with tab2:
    if 'df_avant' in locals() and 'df_apres' in locals():
        st.subheader("📊 Statistiques générales")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### AVANT")
            nb_designations = df_avant["DESI_ARTI"].nunique() if "DESI_ARTI" in df_avant else len(df_avant)
            st.metric("🧾 Désignations uniques", nb_designations)

        with col2:
            st.markdown("### APRÈS")
            nb_noms = df_apres["nom"].nunique() if "nom" in df_apres else 0
            st.metric("📌 Noms de produits uniques", nb_noms)

        if nb_designations > 0 and nb_noms > 0:
            reduction = round(100 * (1 - nb_noms / nb_designations), 2)
            st.markdown(f"### 🔻 Réduction du bruit : `{reduction}%`")

        st.divider()

        st.subheader("📚 Répartition des catégories (après traitement)")

        col3, col4, col5 = st.columns(3)
        with col3:
            st.metric("📂 Familles uniques", df_apres["famille"].nunique())
        with col4:
            st.metric("📁 Sous-familles uniques", df_apres["sous_famille"].nunique())
        with col5:
            st.metric("🧩 Agrégats uniques", df_apres["agregat"].nunique())

        st.markdown("### 📉 Visualisation des familles")
        familles_counts = df_apres["famille"].value_counts().reset_index()
        familles_counts.columns = ["famille", "nb_produits"]

        chart = alt.Chart(familles_counts).mark_bar().encode(
            x=alt.X('nb_produits:Q', title="Nombre de produits"),
            y=alt.Y('famille:N', sort='-x', title="Famille"),
            tooltip=['famille', 'nb_produits']
        ).properties(width=700, height=400)

        st.altair_chart(chart, use_container_width=True)

        st.divider()

        st.subheader("⏱️ Temps d’exécution")

        if "timestamp" in df_apres.columns:
            try:
                start = pd.to_datetime(df_apres["timestamp"].min())
                end = pd.to_datetime(df_apres["timestamp"].max())
                duree = end - start
                st.write(f"🕒 Traitement effectué du `{start}` au `{end}`")
                st.success(f"⏱️ Durée : `{str(duree)}`")
            except:
                st.warning("🕒 Colonne 'timestamp' non exploitable.")
        else:
            st.info("ℹ️ Aucune colonne 'timestamp' trouvée dans le fichier.")

        st.download_button("📥 Télécharger le fichier traité", df_apres.to_csv(index=False).encode("utf-8-sig"), file_name="gpairo_resultat.csv")
    else:
        st.info("Veuillez d'abord charger les fichiers dans l'onglet précédent.")

