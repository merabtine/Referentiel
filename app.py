import streamlit as st
import pandas as pd
import plotly.express as px

# ────────────── CONFIG ──────────────
st.set_page_config(
    page_title="Référentiel Industriel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────── STYLE GLOBAL ──────────────
st.markdown("""
<style>
/* Police et couleurs globales */
body, .stApp {
    font-family: 'Segoe UI', sans-serif;
    background-color: #f9f9f9;
}

/* HEADER */
.hero {
    background: linear-gradient(135deg, #002366 0%, #0b3a91 100%);
    color: white;
    padding: 2.5rem;
    text-align: center;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
}
.hero h1 {
    font-size: 2.4rem;
    margin-bottom: 0.5rem;
    font-weight: 700;
}
.hero p {
    font-size: 1.2rem;
    opacity: 0.95;
}

/* Boutons download */
.stDownloadButton button {
    background-color: #F0B518;
    color: black;
    border-radius: 8px;
    font-weight: 600;
}

/* Filtres alignés */
.filter-box {
    display: flex;
    gap: 2rem;
    justify-content: center;
    margin-bottom: 1.5rem;
}
.filter-box > div {
    flex: 1;
}
</style>
""", unsafe_allow_html=True)

# ────────────── HEADER ──────────────
st.markdown("""
<div class="hero">
  <h1>⚙️ REFINOR</h1>
  <p>Tableau de bord interactif du <b>référentiel industriel</b>  
  pour vos <b>pièces de rechange</b></p>
</div>
""", unsafe_allow_html=True)

# ────────────── SIDEBAR ──────────────
st.sidebar.image("logo.png", width=140)
st.sidebar.markdown("## Importer votre base Gpairo")
uploaded_file = st.sidebar.file_uploader("📂 Importer le fichier Gpairo", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Lecture du fichier importé
    try:
        if uploaded_file.name.endswith(".csv"):
            df_input = pd.read_csv(uploaded_file)
        else:
            df_input = pd.read_excel(uploaded_file)
        st.sidebar.success("Fichier Gpairo chargé ✅")
    except Exception as e:
        st.error(f"Erreur de lecture du fichier : {e}")
        st.stop()

    # Charger le résultat backend
    try:
        df = pd.read_excel("resultat_classification.xlsx")
    except Exception as e:
        st.error(f"Impossible de lire le fichier résultat : {e}")
        st.stop()

    # ────────────── STATISTIQUES ──────────────
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

    # ────────────── FILTRES MODERNES ──────────────
    sous_familles = sorted(df['SOUS_FAMILLE'].dropna().unique())
    agregats_total = sorted(df['AGREGAT'].dropna().unique())

    # deux selectbox côte à côte
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_sous_famille = st.selectbox("🔎 Sous-famille :", ["(Toutes)"] + sous_familles)
    with col_f2:
        selected_agregat = st.selectbox("🔧 Agrégat :", ["(Tous)"] + agregats_total)

    # filtre
    if selected_sous_famille != "(Toutes)":
        df_filtered = df[df['SOUS_FAMILLE'] == selected_sous_famille]
    else:
        df_filtered = df.copy()

    if selected_agregat != "(Tous)":
        df_agregat = df_filtered[df_filtered['AGREGAT'] == selected_agregat]
    else:
        df_agregat = df_filtered.copy()

    # ────────────── GRAPHIQUES ──────────────
    # Répartition des agrégats
    agg_counts = df_filtered['AGREGAT'].value_counts().reset_index()
    agg_counts.columns = ['AGREGAT', 'Nombre']

    fig_bar = px.bar(
        agg_counts,
        x='AGREGAT',
        y='Nombre',
        text='Nombre',
        title="Répartition des agrégats",
        color='AGREGAT',
        color_discrete_sequence=[ '#002366', '#F0B518', '#0b3a91', '#ffa500' ]
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    # Top produits
    produits_counts = df_agregat['NOM PRODUIT'].value_counts().head(20).reset_index()
    produits_counts.columns = ['NOM PRODUIT', 'Nombre']

    fig_treemap = px.treemap(
        produits_counts,
        path=['NOM PRODUIT'],
        values='Nombre',
        title="Top 20 produits"
    )
    fig_treemap.update_traces(root_color="#002366")
    st.plotly_chart(fig_treemap, use_container_width=True)

    st.markdown("### 📝 Aperçu des données filtrées")
    st.dataframe(df_agregat.head(30), use_container_width=True)

else:
    st.info("📂 Importez d'abord votre fichier Gpairo dans le menu latéral pour afficher le tableau de bord.")
