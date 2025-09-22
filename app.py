import streamlit as st
import pandas as pd
import plotly.express as px

# ────────────── CONFIG ──────────────
st.set_page_config(
    page_title="Référentiel Industriel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────── TITRE & DESCRIPTION ──────────────
st.title("⚙️ Référentiel Industriel – Tableau des pièces de rechange")
st.markdown("""
Bienvenue sur **REFINOR** – votre tableau de bord interactif pour les **produits industriels et pièces de rechange**.  
Toutes les données affichées ci-dessous proviennent de votre **système backend** (fichier déjà nettoyé et classifié).  
""")

# ────────────── SIDEBAR MODERNE ──────────────
st.sidebar.image("logo.png", width=140)
st.sidebar.markdown("## Menu")
page = st.sidebar.selectbox(
    "Navigation",
    ["📊 Tableau & Statistiques", "📈 Analyses interactives"]
)

# ────────────── LECTURE FICHIER BACKEND ──────────────
# Ton fichier résultat déjà prêt :
fichier_resultat = "resultat_classification.xlsx"

try:
    df = pd.read_excel(fichier_resultat)
except Exception as e:
    st.error(f"Impossible de lire le fichier résultat : {e}")
    st.stop()

# ────────────── PAGE 1 : TABLEAU + STATS ──────────────
if page == "📊 Tableau & Statistiques":
    st.subheader("📑 Aperçu du fichier résultat classifié")
    st.dataframe(df.head(50), use_container_width=True)

    # Petit rappel des colonnes :
    colonnes = df.columns.tolist()
    st.caption(f"Colonnes disponibles : {', '.join(colonnes)}")

    # Statistiques globales
    total_lignes = len(df)
    nb_sous_familles = df['SOUS_FAMILLE'].nunique()
    nb_agregats = df['AGREGAT'].nunique()
    nb_produits = df['NOM PRODUIT'].nunique()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Lignes totales", f"{total_lignes:,}")
    col2.metric("Sous-familles uniques", f"{nb_sous_familles:,}")
    col3.metric("Agrégats uniques", f"{nb_agregats:,}")
    col4.metric("Produits uniques", f"{nb_produits:,}")

    # Téléchargement CSV
    csv = df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        "💾 Télécharger le fichier résultat (CSV)",
        data=csv,
        file_name="resultat_classification.csv",
        mime="text/csv"
    )

# ────────────── PAGE 2 : ANALYSES INTERACTIVES ──────────────
elif page == "📈 Analyses interactives":
    st.subheader("Analyses interactives par Sous-famille / Agrégat / Produits")

    # Choix sous-famille
    sous_familles = sorted(df['SOUS_FAMILLE'].dropna().unique())
    selected_sous_famille = st.selectbox("🔎 Choisir une sous-famille :", ["(Toutes)"] + sous_familles)

    if selected_sous_famille != "(Toutes)":
        df_filtered = df[df['SOUS_FAMILLE'] == selected_sous_famille]
    else:
        df_filtered = df.copy()

    # Graph 1 : Répartition des agrégats dans la sous-famille
    agg_counts = df_filtered['AGREGAT'].value_counts().reset_index()
    agg_counts.columns = ['AGREGAT', 'Nombre']

    fig_bar = px.bar(
        agg_counts,
        x='AGREGAT',
        y='Nombre',
        text='Nombre',
        title="Répartition des agrégats",
        color='AGREGAT',
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    # Graph 2 : Top produits de l’agrégat choisi
    agregats = sorted(df_filtered['AGREGAT'].dropna().unique())
    selected_agregat = st.selectbox("Choisir un agrégat :", ["(Tous)"] + agregats)

    if selected_agregat != "(Tous)":
        df_agregat = df_filtered[df_filtered['AGREGAT'] == selected_agregat]
    else:
        df_agregat = df_filtered.copy()

    produits_counts = df_agregat['NOM PRODUIT'].value_counts().head(20).reset_index()
    produits_counts.columns = ['NOM PRODUIT', 'Nombre']

    fig_treemap = px.treemap(
        produits_counts,
        path=['NOM PRODUIT'],
        values='Nombre',
        title="Top 20 produits"
    )
    st.plotly_chart(fig_treemap, use_container_width=True)

    st.dataframe(df_agregat.head(30), use_container_width=True)
