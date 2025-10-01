import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ────────────── CONFIG ──────────────
st.set_page_config(page_title="Référentiel Industriel", layout="wide", initial_sidebar_state="expanded")

# ────────────── CSS GLOBAL ──────────────
st.markdown("""
<style>
/* tableaux */
thead tr th { background-color:#8ecae6 !important; color:#023047 !important; font-weight:bold !important; text-align:center !important; }
[data-testid="stDataFrame"] table { background-color:#fffdf6 !important; border-radius:10px; }
div.stDownloadButton > button { background-color:#ffb703 !important; color:#023047 !important; font-weight:bold !important; border:none; border-radius:8px !important; }
.subfam-box { border: 1px solid #8ecae6; border-radius: 5px; padding: 8px; margin-bottom: 15px; }
.subfam-title { font-weight: bold; font-size: 17px; color: #023047; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# ────────────── HEADER ──────────────
st.image("header.png", use_container_width=True)

# ────────────── LECTURE DES FICHIERS ──────────────
df_gpairo = pd.read_csv("dataset_gpairo_webpdrmif.csv")  # Entrée avant traitement
df_referentiel = pd.read_csv("Referentiel Central.csv")  # Résultat après traitement
df_pieces = pd.read_csv("Ref_Pieces de rechange_Gpairo.csv")
df_install = pd.read_csv("Ref_Installations fixes_Mif.csv")
df_corresp = pd.read_csv("Table de correspondance.csv")

# ────────────── SIDEBAR NAVIGATION ──────────────
st.sidebar.image("logo.png", width=140)
page = st.sidebar.radio("Navigation", ["Accueil", "Pièces de rechange", "Installations fixes"])

# ────────────── FONCTION UTILE : DONUT DESI_ARTI ──────────────
def plot_donut_desiarit(df, col_label='BASE', col_value='DESI_ARTI', title="Répartition"):
    counts = df.groupby(col_label)[col_value].nunique().reset_index()
    fig = go.Figure(data=[go.Pie(
        labels=counts[col_label],
        values=counts[col_value],
        hole=0.5,
        textinfo='label+percent',
        marker=dict(colors=px.colors.qualitative.Dark24)
    )])
    fig.update_layout(title=f"{title} (Total uniques : {df[col_value].nunique():,})", title_x=0.5)
    return fig

# ────────────── PAGE : ACCUEIL ──────────────
if page == "Accueil":
    st.header("🏠 Référentiel Central")
    
    st.subheader("📊 Statistiques globales - avant traitement")
    total_lignes = len(df_gpairo)
    total_desiarit = df_gpairo['DESI_ARTI'].nunique()
    st.metric("📄 Total lignes", f"{total_lignes:,}")
    st.metric("🛒 Total DESI_ARTI uniques", f"{total_desiarit:,}")
    
    st.markdown("### Aperçu du dataset global (head)")
    st.dataframe(df_gpairo.head(50), use_container_width=True)
    
    st.markdown("---")
    st.subheader("📊 Dashboard après traitement")
    st.markdown("### Statistiques globales")
    total_produits = df_referentiel['NOM PRODUIT'].nunique()
    nb_familles = df_referentiel['FAMILLE'].nunique()
    nb_sousfamilles = df_referentiel['SOUS_FAMILLE'].nunique()
    nb_agregats = df_referentiel['AGREGAT'].nunique()
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📂 Familles", nb_familles)
    c2.metric("🔹 Sous-familles", nb_sousfamilles)
    c3.metric("⚙ Agrégats", nb_agregats)
    c4.metric("🛒 Produits uniques", total_produits)
    
    st.plotly_chart(plot_donut_desiarit(df_referentiel, col_label='BASE', col_value='DESI_ARTI', title="Répartition DESI_ARTI par Base"), use_container_width=True)
    
    st.markdown("### Top 10 Sous-familles par nombre de produits")
    top_sousfam = df_referentiel.groupby('SOUS_FAMILLE')['NOM PRODUIT'].nunique().sort_values(ascending=False).head(10)
    fig_top = px.bar(top_sousfam.reset_index().rename(columns={'NOM PRODUIT':'Nombre'}),
                     x='SOUS_FAMILLE', y='Nombre', text='Nombre', color='Nombre')
    st.plotly_chart(fig_top, use_container_width=True)
    
    st.markdown("---")
    st.subheader("📑 Aperçu du Référentiel Central")
    st.dataframe(df_referentiel.head(50), use_container_width=True)
    st.download_button("💾 Télécharger CSV", data=df_referentiel.to_csv(index=False).encode('utf-8-sig'),
                       file_name="Referentiel_central.csv", mime="text/csv")
    
    st.markdown("---")
    st.subheader("🔗 Table de correspondance")
    st.dataframe(df_corresp, use_container_width=True)

# ────────────── PAGE : PIÈCES DE RECHANGE ──────────────
elif page == "Pièces de rechange":
    st.header("🔧 Pièces de rechange")
    
    st.subheader("📊 Statistiques globales - avant traitement")
    st.metric("📄 Total lignes", len(df_gpairo))
    st.metric("🛒 Total DESI_ARTI uniques", df_gpairo['DESI_ARTI'].nunique())
    
    st.markdown("### Aperçu du dataset pièces de rechange")
    st.dataframe(df_pieces.head(50), use_container_width=True)
    st.download_button("💾 Télécharger CSV", data=df_pieces.to_csv(index=False).encode('utf-8-sig'),
                       file_name="Ref_Pieces_de_rechange_Gpairo.csv", mime="text/csv")
    
    st.markdown("---")
    st.subheader("🗂️ Exploration par Sous-famille")
    grouped = df_pieces.groupby('SOUS_FAMILLE')['AGREGAT'].unique().reset_index()
    for i in range(0, len(grouped), 2):
        colA, colB = st.columns(2)
        for j, col in enumerate([colA, colB]):
            if i+j < len(grouped):
                sousfam = grouped.iloc[i+j]['SOUS_FAMILLE']
                with col:
                    ags = grouped.iloc[i+j]['AGREGAT']
                    with st.expander(sousfam):
                        for agr in ags:
                            produits = df_pieces[df_pieces['AGREGAT']==agr]['NOM PRODUIT'].unique().tolist()
                            with st.expander(agr):
                                for p in produits[:10]:
                                    st.markdown(f"- {p}")

# ────────────── PAGE : INSTALLATIONS FIXES ──────────────
elif page == "Installations fixes":
    st.header("🏗 Installations fixes")
    
    st.subheader("📊 Statistiques globales - avant traitement")
    st.metric("📄 Total lignes", len(df_webpdrmif))
    st.metric("🛒 Total DESI_ARTI uniques", df_webpdrmif['DESI_ARTI'].nunique())
    
    st.markdown("### Aperçu du dataset installations fixes")
    st.dataframe(df_install.head(50), use_container_width=True)
    st.download_button("💾 Télécharger CSV", data=df_install.to_csv(index=False).encode('utf-8-sig'),
                       file_name="Ref_Installations_fixes_Mif.csv", mime="text/csv")
    
    st.markdown("---")
    st.subheader("🗂️ Exploration par Sous-famille")
    grouped = df_install.groupby('SOUS_FAMILLE')['AGREGAT'].unique().reset_index()
    for i in range(0, len(grouped), 2):
        colA, colB = st.columns(2)
        for j, col in enumerate([colA, colB]):
            if i+j < len(grouped):
                sousfam = grouped.iloc[i+j]['SOUS_FAMILLE']
                with col:
                    ags = grouped.iloc[i+j]['AGREGAT']
                    with st.expander(sousfam):
                        for agr in ags:
                            produits = df_install[df_install['AGREGAT']==agr]['NOM PRODUIT'].unique().tolist()
                            with st.expander(agr):
                                for p in produits[:10]:
                                    st.markdown(f"- {p}")
