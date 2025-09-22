import streamlit as st
import pandas as pd
import plotly.express as px

# ────────────── CONFIG ──────────────
st.set_page_config(
    page_title="Référentiel Industriel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────── CSS GLOBAL ──────────────
st.markdown("""
<style>
/* HEADER avec image */
.header {
    position: relative;
    background-image: url('pieces-de-rechange.jpg');
    background-size: cover;
    background-position: center;
    border-radius: 0.8rem;
    height: 260px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.header-overlay {
    background: rgba(2,48,71,0.6); /* overlay foncé */
    border-radius: 0.8rem;
    width: 100%;
    height: 100%;
    display:flex;
    align-items:center;
    justify-content:center;
}
.header-text {
    color: #fff;
    font-size: 2rem;
    font-weight: 700;
    text-align: center;
}

/* Stats animées */
.stat-card {
    background: linear-gradient(145deg, #8ecae6, #219ebc);
    color: white;
    border-radius: 50%;
    width: 120px;
    height: 120px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    margin: auto;
    transition: transform 0.3s ease-in-out;
    box-shadow: 0 4px 15px rgba(0,0,0,0.2);
}
.stat-card:hover {
    transform: scale(1.1);
}
.stat-number {
    font-size: 1.3rem;
    font-weight: bold;
}
.stat-label {
    font-size: 0.8rem;
}

/* Select sur une seule ligne */
.filter-container {
    display: flex;
    gap: 2rem;
}
</style>
""", unsafe_allow_html=True)

# ────────────── HEADER ──────────────
st.markdown("""
<div class="header">
  <div class="header-overlay">
    <div class="header-text"> 
    <h1> REFINOR – </h1>
    <p>Votre plateforme moderne pour charger, nettoyer et analyser vos données industrielles  
    </p>
    </div>
            
  </div>
</div>
""", unsafe_allow_html=True)

# ────────────── DESCRIPTION ──────────────
st.markdown("""
Dans un contexte marqué par la **transformation numérique** et la multiplication des solutions logicielles,  
les entreprises modernes s’appuient sur des systèmes d’information de plus en plus complexes pour piloter leurs activités.  

La capacité à **collecter**, **centraliser** et **analyser efficacement** les données constitue aujourd’hui un facteur stratégique de compétitivité.  
Les **référentiels produits** occupent une place essentielle car ils assurent la **cohérence** et la **fiabilité** des informations au sein des différentes applications et départements.  

**REFINOR** a pour objectif de mettre en place un mécanisme capable :  
- d’**assainir et normaliser** les désignations produits,  
- de **regrouper** les entrées similaires malgré les variations de saisie,  
- de **classifier** chaque produit selon une hiérarchie normalisée : **Famille → Sous-famille → Agrégat → Produit**.  

Grâce à ce tableau de bord, vous pouvez **visualiser instantanément** vos données et les **analyser de manière interactive**.
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
    with c1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{total_lignes:,}</div>
            <div class="stat-label">Lignes</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{nb_sous_familles:,}</div>
            <div class="stat-label">Sous-familles</div>
        </div>
        """, unsafe_allow_html=True)
    with c3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{nb_agregats:,}</div>
            <div class="stat-label">Agrégats</div>
        </div>
        """, unsafe_allow_html=True)
    with c4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-number">{nb_produits:,}</div>
            <div class="stat-label">Produits</div>
        </div>
        """, unsafe_allow_html=True)

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

    # ────────────── FILTRES SUR UNE LIGNE ──────────────
    sous_familles = sorted(df['SOUS_FAMILLE'].dropna().unique())
    agregats = sorted(df['AGREGAT'].dropna().unique())

    col1, col2 = st.columns(2)
    with col1:
        selected_sous_famille = st.selectbox("🔎 Choisir une sous-famille :", ["(Toutes)"] + sous_familles)
    with col2:
        selected_agregat = st.selectbox("Choisir un agrégat :", ["(Tous)"] + agregats)

    df_filtered = df.copy()
    if selected_sous_famille != "(Toutes)":
        df_filtered = df_filtered[df_filtered['SOUS_FAMILLE'] == selected_sous_famille]

    df_agregat = df_filtered.copy()
    if selected_agregat != "(Tous)":
        df_agregat = df_agregat[df_agregat['AGREGAT'] == selected_agregat]

    # ────────────── GRAPHIQUES ──────────────
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

    produits_counts = df_agregat['NOM PRODUIT'].value_counts().head(20).reset_index()
    produits_counts.columns = ['NOM PRODUIT', 'Nombre']

    fig_treemap = px.treemap(
        produits_counts,
        path=['NOM PRODUIT'],
        values='Nombre',
        title="Top 20 produits de l’agrégat sélectionné"
    )
    st.plotly_chart(fig_treemap, use_container_width=True)

    st.markdown("### 📝 Aperçu des données filtrées")
    st.dataframe(df_agregat.head(30), use_container_width=True)

else:
    st.info("Importez d'abord votre fichier Gpairo dans le menu latéral pour afficher le tableau de bord.")
