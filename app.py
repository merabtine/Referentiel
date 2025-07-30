import streamlit as st
import pandas as pd
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Gpairo Visualizer", layout="wide")

st.title("📊 Gpairo Visualizer – Analyse des jeux de données")

# Session state pour gérer le reset
if "reset" not in st.session_state:
    st.session_state.reset = False

def reset_app():
    st.session_state.reset = True

# Onglet d'import
tab1, tab2 = st.tabs(["📂 Importer les jeux de données", "📈 Explorer les données"])

with tab1:
    st.subheader("📤 Importer les fichiers CSV")
    col1, col2 = st.columns(2)
    with col1:
        fichier_avant = st.file_uploader("📝 Fichier Gpairo (avant traitement)", type=["csv"], key="avant")
    with col2:
        fichier_apres = st.file_uploader("✅ Fichier Webpdrmif (après traitement)", type=["csv"], key="apres")

    if fichier_avant and fichier_apres:
        df_avant = pd.read_csv(fichier_avant, encoding="utf-8-sig")
        df_apres = pd.read_csv(fichier_apres, encoding="utf-8-sig")
        st.success("✅ Fichiers chargés avec succès. Passez à l'onglet suivant.")
        st.button("🔁 Réinitialiser les fichiers", on_click=reset_app)

# Affichage dynamique si fichiers chargés
if not st.session_state.reset and "df_avant" in locals() and "df_apres" in locals():
    with tab2:
        st.subheader("📌 Choisissez la base à explorer")
        choix_base = st.radio("Base de données :", ["Gpairo (AVANT)", "Webpdrmif (APRÈS)"], horizontal=True)

        df = df_avant if "Gpairo" in choix_base else df_apres

        st.markdown("### 👀 Aperçu du fichier")
        st.dataframe(df.head())

        st.markdown("### 📊 Statistiques principales")
        nb_total = len(df)
        nb_uniques = df["DESI_ARTI"].nunique() if "DESI_ARTI" in df else df["nom"].nunique()
        st.metric("📦 Total de produits", nb_total)
        st.metric("🧾 Désignations uniques", nb_uniques)

        # Familles, sous-familles et agrégats si base après traitement
        if "famille" in df.columns:
            col1, col2, col3 = st.columns(3)
            col1.metric("📂 Familles uniques", df["famille"].nunique())
            col2.metric("📁 Sous-familles uniques", df["sous_famille"].nunique())
            col3.metric("🧩 Agrégats uniques", df["agregat"].nunique())

        st.markdown("### 📉 Répartition des familles (si dispo)")
        if "famille" in df.columns:
            familles_counts = df["famille"].value_counts().reset_index()
            familles_counts.columns = ["famille", "nb_produits"]
            chart = alt.Chart(familles_counts).mark_bar().encode(
                x=alt.X('nb_produits:Q', title="Nombre de produits"),
                y=alt.Y('famille:N', sort='-x', title="Famille"),
                tooltip=['famille', 'nb_produits']
            ).properties(width=700, height=400)
            st.altair_chart(chart, use_container_width=True)

        st.markdown("### 🧪 Matrice de corrélation (si applicable)")
        num_cols = df.select_dtypes(include='number')
        if not num_cols.empty and num_cols.shape[1] > 1:
            fig, ax = plt.subplots()
            sns.heatmap(num_cols.corr(), annot=True, cmap="coolwarm", ax=ax)
            st.pyplot(fig)
        else:
            st.info("Pas assez de colonnes numériques pour une matrice de corrélation.")

        st.markdown("### 💾 Télécharger le fichier affiché")
        buffer = io.StringIO()
        df.to_csv(buffer, index=False, encoding="utf-8-sig")
        st.download_button("📥 Télécharger le fichier CSV", buffer.getvalue(), file_name="base_selectionnee.csv", mime="text/csv")
else:
    if st.session_state.reset:
        st.warning("⚠️ Application réinitialisée. Veuillez recharger les fichiers.")
