import streamlit as st
import pandas as pd
import plotly.express as px

# ────────────── CONFIG ──────────────
st.set_page_config(
    page_title="Référentiel Industriel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────── HEADER ──────────────
st.markdown("""
<style>
.header {
    background: linear-gradient(90deg, #0d47a1, #1976d2);
    padding: 1rem 2rem;
    border-radius: 0.5rem;
    color: white;
    font-size: 1.5rem;
}
</style>
<div class="header">⚙️ REFINOR – Tableau de bord interactif des pièces industrielles</div>
""", unsafe_allow_html=True)

# ────────────── DESCRIPTION ──────────────
st.markdown("""
Bienvenue sur **REFINOR** – votre **tableau de bord interactif** pour le référentiel industriel des pièces de rechange.  
Cet outil vous permet de **charger votre base Gpairo**, de **visualiser instantanément le fichier nettoyé et classifié**  
et d’analyser vos données par **sous-familles**, **agrégats** et **produits** grâce à des graphes modernes et interactifs.  
""")

# ────────────── UPLOAD GP AIRO ──────────────
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

    # ────────────── FILTRES ──────────────
    sous_familles = sorted(df['SOUS_FAMILLE'].dropna().unique())
    selected_sous_famille = st.selectbox("🔎 Choisir une sous-famille :", ["(Toutes)"] + sous_familles)

    if selected_sous_famille != "(Toutes)":
        df_filtered = df[df['SOUS_FAMILLE'] == selected_sous_famille]
    else:
        df_filtered = df.copy()

    # Agrégats disponibles
    agregats = sorted(df_filtered['AGREGAT'].dropna().unique())
    selected_agregat = st.selectbox("Choisir un agrégat :", ["(Tous)"] + agregats)

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
        color='AGREGAT',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    # Graph 2 : Top produits
    produits_counts = df_agregat['NOM PRODUIT'].value_counts().head(20).reset_index()
    produits_counts.columns = ['NOM PRODUIT', 'Nombre']

    fig_treemap = px.treemap(
        produits_counts,
        path=['NOM PRODUIT'],
        values='Nombre',
        title="Top 20 produits de l’agrégat sélectionné"
    )
    st.plotly_chart(fig_treemap, use_container_width=True)

    # Aperçu des données filtrées
    st.markdown("### 📝 Aperçu des données filtrées")
    st.dataframe(df_agregat.head(30), use_container_width=True)

else:
    st.info("Importez d'abord votre fichier Gpairo dans le menu latéral pour afficher le tableau de bord.")
