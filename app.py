import streamlit as st
import pandas as pd
import plotly.express as px

# ────────────── CONFIG ──────────────
st.set_page_config(
    page_title="Référentiel Industriel",
    layout="wide",
    initial_sidebar_state="expanded"
)
# ────────────── IMAGE HEADER ──────────────
st.image("header.png", use_container_width=True)
# ────────────── UPLOAD GPAIRO ──────────────
st.sidebar.image("logo.png", width=140)
st.sidebar.markdown("## Importer votre base Gpairo")
uploaded_file = st.sidebar.file_uploader("📂 Importer le fichier Gpairo", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Lecture fichier Gpairo (pour l'exemple on lit directement le résultat backend)
    try:
        if uploaded_file.name.endswith(".csv"):
            df_input = pd.read_csv(uploaded_file)
        else:
            df_input = pd.read_excel(uploaded_file)
        st.sidebar.success("Fichier Gpairo chargé ✅")
    except Exception as e:
        st.error(f"Erreur de lecture du fichier : {e}")
        st.stop()

    # Ici tu peux appeler ton backend pour générer le résultat
    # Pour l'exemple, on suppose que resultat_classification.xlsx existe déjà :
    try:
        df = pd.read_excel("resultat_classification.xlsx")
    except Exception as e:
        st.error(f"Impossible de lire le fichier résultat : {e}")
        st.stop()

    # ────────────── STATISTIQUES GLOBALES ──────────────
    total_lignes = len(df)
    nb_sous_familles = df['SOUS_FAMILLE'].nunique()
    nb_agregats = df['AGREGAT'].nunique()
    nb_produits = df['NOM PRODUIT'].nunique()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📄 Lignes totales", f"{total_lignes:,}")
    c2.metric("📂 Sous-familles", f"{nb_sous_familles:,}")
    c3.metric("🔧 Agrégats", f"{nb_agregats:,}")
    c4.metric("🛒 Produits", f"{nb_produits:,}")

    st.markdown("---")
    st.subheader("📑 Aperçu du fichier résultat classifié")
    st.dataframe(df.head(50), use_container_width=True)

    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "💾 Télécharger le fichier résultat (CSV)",
        data=csv,
        file_name="resultat_classification.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("📊 Dashboard interactif")

    # ────────────── FILTRES SUR UNE MÊME LIGNE ──────────────
    col1, col2 = st.columns(2)

    sous_familles = sorted(df['SOUS_FAMILLE'].dropna().unique())
    selected_sous_famille = col1.selectbox("🔎 Choisir une sous-famille :", ["(Toutes)"] + sous_familles)

    if selected_sous_famille != "(Toutes)":
        df_filtered = df[df['SOUS_FAMILLE'] == selected_sous_famille]
    else:
        df_filtered = df.copy()

    # Agrégats disponibles
    agregats = sorted(df_filtered['AGREGAT'].dropna().unique())
    selected_agregat = col2.selectbox("Choisir un agrégat :", ["(Tous)"] + agregats)

    if selected_agregat != "(Tous)":
        df_agregat = df_filtered[df_filtered['AGREGAT'] == selected_agregat]
    else:
        df_agregat = df_filtered.copy()

    # ────────────── GRAPHIQUES ──────────────
    # Graph 1 : répartition agrégats
    agg_counts = df_filtered['AGREGAT'].value_counts().reset_index()
    agg_counts.columns = ['AGREGAT', 'Nombre']

    fig_bar = px.bar(
        agg_counts,
        x='AGREGAT',
        y='Nombre',
        text='Nombre',
        title="Répartition des agrégats dans la sous-famille sélectionnée",
        color='AGREGAT'
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    # Graph 2 : Top produits (limite 20 mais gère les cas <20)
    produits_counts = (
        df_agregat['NOM PRODUIT']
        .value_counts()
        .head(20)  # si <20, renvoie juste ce qu'il y a
        .reset_index()
    )
    produits_counts.columns = ['NOM PRODUIT', 'Nombre']

    if not produits_counts.empty:
        fig_treemap = px.treemap(
            produits_counts,
            path=['NOM PRODUIT'],
            values='Nombre',
            title="Top produits de l’agrégat sélectionné"
        )
        st.plotly_chart(fig_treemap, use_container_width=True)
    else:
        st.info("Aucun produit disponible pour l’agrégat sélectionné.")

    # Aperçu des données filtrées
    st.markdown("### 📝 Aperçu des données filtrées")
    st.dataframe(df_agregat.head(30), use_container_width=True)

else:
    st.info("Importez d'abord votre fichier Gpairo dans le menu latéral pour afficher le tableau de bord.")
