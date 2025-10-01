import streamlit as st
import pandas as pd
import plotly.express as px

# ────────────── CONFIG ──────────────
st.set_page_config(
    page_title="Référentiel Installations Fixes",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ────────────── CSS GLOBAL ──────────────
st.markdown("""
<style>
thead tr th { background-color:#8ecae6 !important; color:#023047 !important; font-weight:bold !important; text-align:center !important; }
[data-testid="stDataFrame"] table { background-color:#fffdf6 !important; border-radius:10px; }
div.stDownloadButton > button { background-color:#ffb703 !important; color:#023047 !important; font-weight:bold !important; border:none; border-radius:8px !important; }
.subfam-box { border: 1px solid #8ecae6; border-radius: 5px; padding: 8px; margin-bottom: 15px; }
.subfam-title { font-weight: bold; font-size: 17px; color: #023047; margin-bottom: 5px; }
</style>
""", unsafe_allow_html=True)

# ────────────── IMAGE HEADER ──────────────
st.image("header.png", use_container_width=True)

# ────────────── SIDEBAR NAVIGATION ──────────────
st.sidebar.image("logo.png", width=140)

if st.sidebar.button("🛠️ Pièces de rechange (Gpairo)"):
    st.experimental_set_query_params(page="gpairo")
if st.sidebar.button("🏭 Installations fixes (WebPDRMIF)"):
    st.experimental_set_query_params(page="webpdrmif")

# ────────────── LECTURE FICHIERS ──────────────
try:
    df_dataset = pd.read_csv("dataset_webpdrmif.csv", encoding="utf-8-sig")
except Exception as e:
    st.error(f"Erreur lecture dataset_webpdrmif.csv : {e}")
    st.stop()

try:
    df = pd.read_csv("Ref_Installations fixes_Mif.csv", encoding="utf-8-sig")
except Exception as e:
    st.error(f"Erreur lecture Ref_Installations fixes_Mif.csv : {e}")
    st.stop()

# Normalisation colonnes
df.columns = df.columns.str.strip()
df_dataset.columns = df_dataset.columns.str.strip()

# filtrer sous-familles != Non identifiable
if "SOUS_FAMILLE" in df.columns:
    df = df[df["SOUS_FAMILLE"] != "Non identifiable"]

# ────────────── STATISTIQUES GLOBALES ──────────────
total_lignes = len(df)
nb_sous_familles = df['SOUS_FAMILLE'].nunique() if 'SOUS_FAMILLE' in df.columns else 0
nb_agregats = df['AGREGAT'].nunique() if 'AGREGAT' in df.columns else 0
nb_produits = df['NOM PRODUIT'].nunique() if 'NOM PRODUIT' in df.columns else 0

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
    file_name="resultat_installations_fixes.csv",
    mime="text/csv"
)

# ────────────── FILTRES & DASHBOARD ──────────────
if 'SOUS_FAMILLE' in df.columns:
    col1, col2 = st.columns(2)
    sous_familles = sorted(df['SOUS_FAMILLE'].dropna().unique())
    selected_sous_famille = col1.selectbox("🔎 Choisir une sous-famille :", ["(Toutes)"] + sous_familles)

    if selected_sous_famille != "(Toutes)":
        df_filtered = df[df['SOUS_FAMILLE'] == selected_sous_famille]
    else:
        df_filtered = df.copy()

    agregats = sorted(df_filtered['AGREGAT'].dropna().unique())
    selected_agregat = col2.selectbox("Choisir un agrégat :", ["(Tous)"] + agregats)

    if selected_agregat != "(Tous)":
        df_agregat = df_filtered[df_filtered['AGREGAT'] == selected_agregat]
    else:
        df_agregat = df_filtered.copy()

    # Graphiques
    agg_counts = df_filtered['AGREGAT'].value_counts().reset_index()
    agg_counts.columns = ['AGREGAT', 'Nombre']
    fig_bar = px.bar(agg_counts, x='AGREGAT', y='Nombre', text='Nombre', title="Répartition des agrégats", color='AGREGAT')
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    produits_counts = df_agregat['NOM PRODUIT'].value_counts().head(20).reset_index()
    produits_counts.columns = ['NOM PRODUIT', 'Nombre']
    if not produits_counts.empty:
        fig_treemap = px.treemap(produits_counts, path=['NOM PRODUIT'], values='Nombre', title="Top produits")
        st.plotly_chart(fig_treemap, use_container_width=True)
    else:
        st.info("Aucun produit disponible pour l'agrégat sélectionné.")

    st.markdown("### 📝 Aperçu des données filtrées")
    st.dataframe(df_agregat.head(30), use_container_width=True)

    # Exploration visuelle
    st.markdown("---")
    st.subheader("🗂️ Exploration des produits")
    grouped = df.groupby('SOUS_FAMILLE')['AGREGAT'].unique().reset_index()

    for i in range(0, len(grouped), 2):
        colA, colB = st.columns(2)

        for j, col in enumerate([colA, colB]):
            if i + j < len(grouped):
                sousfam = grouped.iloc[i + j]['SOUS_FAMILLE']
                if sousfam != "Non identifiable":
                    with col:
                        ags = grouped.iloc[i + j]['AGREGAT']
                        st.markdown(f"""<div style="border:1px solid #ccc; border-radius:8px; padding:10px; margin-bottom:15px;">
                                         <div style="font-weight:bold; color:blue; font-size:16px; margin-bottom:8px;">{sousfam}</div>""",
                                    unsafe_allow_html=True)
                        for agr in ags:
                            produits = df[df['AGREGAT'] == agr]['NOM PRODUIT'].dropna().tolist()
                            produits = list(dict.fromkeys(produits))
                            with st.expander(f"{agr}"):
                                if len(produits) <= 5:
                                    for p in produits: st.markdown(f"- {p}")
                                else:
                                    show_all = st.checkbox("Voir tout", key=f"chk_{sousfam}_{agr}")
                                    if show_all:
                                        for p in produits: st.markdown(f"- {p}")
                                    else:
                                        for p in produits[:5]: st.markdown(f"- {p}")
                        st.markdown("</div>", unsafe_allow_html=True)
