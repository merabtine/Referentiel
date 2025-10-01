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
thead tr th { background-color:#8ecae6 !important; color:#023047 !important; font-weight:bold !important; text-align:center !important; }
[data-testid="stDataFrame"] table { background-color:#fffdf6 !important; border-radius:10px; }
div.stDownloadButton > button { background-color:#ffb703 !important; color:#023047 !important; font-weight:bold !important; border:none; border-radius:8px !important; }
.agg-button, .toggle-button { color: #023047 !important; background: none !important; border: none !important; padding: 0 !important; margin: 0 5px 0 0 !important; cursor: pointer !important; font-size: 15px !important; text-decoration: none !important; }
.agg-button:hover, .toggle-button:hover { color: #219ebc !important; }
.subfam-box { border: 1px solid #8ecae6; border-radius: 5px; padding: 8px; margin-bottom: 15px; }
.subfam-title { font-weight: bold; font-size: 17px; color: #023047; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# ────────────── HEADER COMMUN ──────────────
st.image("header.png", use_container_width=True)

# ────────────── SIDEBAR ──────────────
st.sidebar.image("logo.png", width=140)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à :", ["Accueil", "Pièces de rechange", "Installations fixes"])

# ────────────── LECTURE DES FICHIERS ──────────────
# Chemins vers tes fichiers
FILE_REP_CENTRAL = "Referentiel_central.xlsx"
FILE_PIECES = "Ref_Pieces_de_rechange_Gpairo.xlsx"
FILE_INSTALL = "Ref_Installations_fixes_Mif.xlsx"
FILE_CORRESP = "Table_correspondance.xlsx"

# Lecture fichiers
df_central = pd.read_excel(FILE_REP_CENTRAL)
df_pieces = pd.read_excel(FILE_PIECES)
df_install = pd.read_excel(FILE_INSTALL)
df_corresp = pd.read_excel(FILE_CORRESP)

# ────────────── ONGLET ACCUEIL ──────────────
if page == "Accueil":
    st.header("🏠 Référentiel Central")

    # Statistiques globales
    total_produits = df_central['NOM PRODUIT'].nunique()
    total_familles = df_central['FAMILLE'].nunique()
    total_sousfam = df_central['SOUS_FAMILLE'].nunique()
    total_agregats = df_central['AGREGAT'].nunique()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🛒 Produits uniques", f"{total_produits:,}")
    c2.metric("📂 Familles", f"{total_familles:,}")
    c3.metric("🔹 Sous-familles", f"{total_sousfam:,}")
    c4.metric("⚙ Agrégats", f"{total_agregats:,}")

    st.markdown("---")
    st.subheader("📑 Aperçu du Référentiel Central")
    st.dataframe(df_central.head(50), use_container_width=True)

    st.download_button(
        "💾 Télécharger le Référentiel Central",
        data=df_central.to_csv(index=False).encode('utf-8-sig'),
        file_name="Referentiel_central.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("📊 Dashboard interactif")

    # Filtrage interactif
    col1, col2 = st.columns(2)
    sousfam = sorted(df_central['SOUS_FAMILLE'].dropna().unique())
    selected_sousfam = col1.selectbox("🔎 Choisir une sous-famille :", ["(Toutes)"] + sousfam)
    df_filtered = df_central if selected_sousfam == "(Toutes)" else df_central[df_central['SOUS_FAMILLE'] == selected_sousfam]

    agregats = sorted(df_filtered['AGREGAT'].dropna().unique())
    selected_agr = col2.selectbox("Choisir un agrégat :", ["(Tous)"] + agregats)
    df_agr = df_filtered if selected_agr == "(Tous)" else df_filtered[df_filtered['AGREGAT'] == selected_agr]

    # Graphiques
    fig_bar = px.bar(
        df_filtered['AGREGAT'].value_counts().reset_index().rename(columns={'index':'AGREGAT','AGREGAT':'Nombre'}),
        x='AGREGAT', y='Nombre', text='Nombre', title="Répartition des Agrégats", color='AGREGAT'
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    fig_pie = px.pie(
        df_filtered['FAMILLE'].value_counts().reset_index().rename(columns={'index':'FAMILLE','FAMILLE':'Nombre'}),
        names='FAMILLE', values='Nombre', title="Répartition des Familles"
    )
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.subheader("🔗 Table de correspondance")
    st.dataframe(df_corresp, use_container_width=True)

# ────────────── ONGLET PIECES DE RECHANGE ──────────────
elif page == "Pièces de rechange":
    st.header("🔧 Pièces de rechange")
    st.dataframe(df_pieces.head(50), use_container_width=True)
    st.download_button(
        "💾 Télécharger le fichier Pièces de rechange",
        data=df_pieces.to_csv(index=False).encode('utf-8-sig'),
        file_name="Ref_Pieces_de_rechange.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("🗂️ Exploration par Sous-famille")
    grouped = df_pieces.groupby('SOUS_FAMILLE')['AGREGAT'].unique().reset_index()
    for i in range(0, len(grouped), 2):
        colA, colB = st.columns(2)
        for j, col in enumerate([colA, colB]):
            if i+j < len(grouped):
                sousfam = grouped.iloc[i+j]['SOUS_FAMILLE']
                ags = grouped.iloc[i+j]['AGREGAT']
                with col:
                    st.markdown(f"**{sousfam}**")
                    for agr in ags:
                        with st.expander(agr):
                            produits = df_pieces[df_pieces['AGREGAT']==agr]['NOM PRODUIT'].unique().tolist()
                            for p in produits[:5]:
                                st.markdown(f"- {p}")

# ────────────── ONGLET INSTALLATIONS FIXES ──────────────
elif page == "Installations fixes":
    st.header("🏗 Installations fixes")
    st.dataframe(df_install.head(50), use_container_width=True)
    st.download_button(
        "💾 Télécharger le fichier Installations fixes",
        data=df_install.to_csv(index=False).encode('utf-8-sig'),
        file_name="Ref_Installations_fixes.csv",
        mime="text/csv"
    )

    st.markdown("---")
    st.subheader("🗂️ Exploration par Sous-famille")
    grouped = df_install.groupby('SOUS_FAMILLE')['AGREGAT'].unique().reset_index()
    for i in range(0, len(grouped), 2):
        colA, colB = st.columns(2)
        for j, col in enumerate([colA, colB]):
            if i+j < len(grouped):
                sousfam = grouped.iloc[i+j]['SOUS_FAMILLE']
                ags = grouped.iloc[i+j]['AGREGAT']
                with col:
                    st.markdown(f"**{sousfam}**")
                    for agr in ags:
                        with st.expander(agr):
                            produits = df_install[df_install['AGREGAT']==agr]['NOM PRODUIT'].unique().tolist()
                            for p in produits[:5]:
                                st.markdown(f"- {p}")
