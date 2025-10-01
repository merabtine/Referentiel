import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ────────────── CONFIG ──────────────
st.set_page_config(page_title="Référentiel Industriel", layout="wide", initial_sidebar_state="expanded")

# ────────────── CSS GLOBAL ──────────────
st.markdown("""
<style>
/* Onglets stylés */
.tab-button {
    background-color: #023047;
    color: white;
    border-radius: 8px;
    padding: 8px 16px;
    margin-right: 5px;
    cursor: pointer;
    display: inline-block;
    font-weight: bold;
}
.tab-button:hover {
    background-color: #219ebc;
}
.active-tab {
    background-color: #ffb703 !important;
    color: #023047 !important;
}

/* tableaux */
thead tr th { background-color:#8ecae6 !important; color:#023047 !important; font-weight:bold !important; text-align:center !important; }
[data-testid="stDataFrame"] table { background-color:#fffdf6 !important; border-radius:10px; }

/* boutons download */
div.stDownloadButton > button { background-color:#ffb703 !important; color:#023047 !important; font-weight:bold !important; border:none; border-radius:8px !important; }

.subfam-box { border: 1px solid #8ecae6; border-radius: 5px; padding: 8px; margin-bottom: 15px; }
.subfam-title { font-weight: bold; font-size: 17px; color: #023047; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# ────────────── HEADER COMMUN ──────────────
st.image("header.png", use_container_width=True)

# ────────────── ONGLET STYLE MODERNE ──────────────
tabs = ["Accueil", "Pièces de rechange", "Installations fixes"]
selected_tab = st.radio("", tabs, horizontal=True)

# ────────────── LECTURE DES FICHIERS ──────────────
df_central = pd.read_csv("Referentiel Central.csv")
df_pieces = pd.read_csv("Ref_Pieces de rechange_Gpairo.csv")
df_install = pd.read_csv("Ref_Installations fixes_Mif.csv")
df_corresp = pd.read_csv("Table de correspondance.csv")

# ────────────── FONCTION UTILE : PIE CIRCLE DESI_ARTI ──────────────
def plot_donut_desiarit(df):
    counts = df.groupby('BASE')['DESI_ARTI'].nunique().reset_index()
    counts['Autres'] = counts['DESI_ARTI'].sum() - counts['DESI_ARTI']
    fig = go.Figure(data=[go.Pie(
        labels=counts['BASE'],
        values=counts['DESI_ARTI'],
        hole=0.5,
        textinfo='label+percent',
        marker=dict(colors=['#023047', '#ffb703'])
    )])
    fig.update_layout(title=f"Total DESI_ARTI uniques : {df['DESI_ARTI'].nunique():,}", title_x=0.5)
    return fig

# ────────────── ACCUEIL ──────────────
if selected_tab == "Accueil":
    st.header("🏠 Référentiel Central")

    # Cercle DESI_ARTI par base
    st.plotly_chart(plot_donut_desiarit(df_central), use_container_width=True)

    # Statistiques post-normalisation
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("📂 Familles", df_central['FAMILLE'].nunique())
    col2.metric("🔹 Sous-familles", df_central['SOUS_FAMILLE'].nunique())
    col3.metric("⚙ Agrégats", df_central['AGREGAT'].nunique())
    col4.metric("🛒 Produits uniques", df_central['NOM PRODUIT'].nunique())

    # Graphiques interactifs supplémentaires
    st.markdown("### Répartition des Agrégats")
    fig_agg = px.bar(df_central['AGREGAT'].value_counts().reset_index().rename(columns={'index':'AGREGAT','AGREGAT':'Nombre'}),
                     x='AGREGAT', y='Nombre', text='Nombre', color='AGREGAT')
    fig_agg.update_traces(textposition='outside')
    st.plotly_chart(fig_agg, use_container_width=True)

    st.markdown("### Répartition des Familles")
    fig_fam = px.pie(df_central['FAMILLE'].value_counts().reset_index().rename(columns={'index':'FAMILLE','FAMILLE':'Nombre'}),
                     names='FAMILLE', values='Nombre', color_discrete_sequence=px.colors.sequential.Teal)
    st.plotly_chart(fig_fam, use_container_width=True)

    st.markdown("### Top 10 Sous-familles par nombre de produits")
    top_sousfam = df_central.groupby('SOUS_FAMILLE')['NOM PRODUIT'].nunique().sort_values(ascending=False).head(10)
    fig_top = px.bar(top_sousfam.reset_index().rename(columns={'NOM PRODUIT':'Nombre'}),
                     x='SOUS_FAMILLE', y='Nombre', text='Nombre', color='Nombre')
    st.plotly_chart(fig_top, use_container_width=True)

    st.markdown("---")
    with st.expander("📑 Aperçu du Référentiel Central"):
        st.dataframe(df_central.head(50), use_container_width=True)
        st.download_button("💾 Télécharger CSV", data=df_central.to_csv(index=False).encode('utf-8-sig'),
                           file_name="Referentiel Central.csv", mime="text/csv")

    st.markdown("---")
    st.subheader("🔗 Table de correspondance")
    st.dataframe(df_corresp, use_container_width=True)

# ────────────── PIÈCES DE RECHANGE ──────────────
elif selected_tab == "Pièces de rechange":
    st.header("🔧 Pièces de rechange")
    st.dataframe(df_pieces.head(50), use_container_width=True)
    st.download_button("💾 Télécharger CSV",
                       data=df_pieces.to_csv(index=False).encode('utf-8-sig'),
                       file_name="Ref_Pieces_de_rechange_Gpairo.csv", mime="text/csv")

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

# ────────────── INSTALLATIONS FIXES ──────────────
elif selected_tab == "Installations fixes":
    st.header("🏗 Installations fixes")
    st.dataframe(df_install.head(50), use_container_width=True)
    st.download_button("💾 Télécharger CSV",
                       data=df_install.to_csv(index=False).encode('utf-8-sig'),
                       file_name="Ref_Installations fixes_Mif.csv", mime="text/csv")

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
