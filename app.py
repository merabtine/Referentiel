import streamlit as st
import pandas as pd
import plotly.express as px

# ────────────── CONFIG ──────────────
st.set_page_config(
    page_title="Référentiel Industriel",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS pour colorer tableaux et boutons
st.markdown("""
<style>
/* style dataframe */
[data-testid="stDataFrame"] table {
    background-color:#fff3c2 !important;
    border-radius:10px;
}
thead tr th {
    background-color:#c2dcff !important;
    color:#023047 !important;
    font-weight:bold !important;
    text-align:center !important;
}

/* style bouton télécharger */
div.stDownloadButton > button {
    background-color:#c2dcff !important;
    color:#023047 !important;
    font-weight:bold !important;
    border-radius:8px !important;
}

/* style boutons filtres */
.stButton>button {
    background-color:#fff3c2 !important;
    color:#023047 !important;
    font-weight:bold !important;
    border-radius:8px !important;
    margin-bottom:0.3rem;
}
</style>
""", unsafe_allow_html=True)

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

    # ────────────── FILTRES ──────────────
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

    # ────────────── GRAPHIQUES ──────────────
    # Graph 1
    agg_counts = df_filtered['AGREGAT'].value_counts().reset_index()
    agg_counts.columns = ['AGREGAT', 'Nombre']

    fig_bar = px.bar(
        agg_counts,
        x='AGREGAT',
        y='Nombre',
        text='Nombre',
        title="Répartition des agrégats",
        color='AGREGAT'
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)

    # Graph 2
    produits_counts = (
        df_agregat['NOM PRODUIT']
        .value_counts()
        .head(20)
        .reset_index()
    )
    produits_counts.columns = ['NOM PRODUIT', 'Nombre']

    if not produits_counts.empty:
        fig_treemap = px.treemap(
            produits_counts,
            path=['NOM PRODUIT'],
            values='Nombre',
            title="Top produits"
        )
        st.plotly_chart(fig_treemap, use_container_width=True)
    else:
        st.info("Aucun produit disponible pour l’agrégat sélectionné.")

    st.markdown("### 📝 Aperçu des données filtrées")
    st.dataframe(df_agregat.head(30), use_container_width=True)

    # --- Exploration visuelle ---
    st.markdown("---")
    st.subheader("🗂️ Exploration des produits")

    grouped = df.groupby('SOUS_FAMILLE')['AGREGAT'].unique().reset_index()

    if 'open_agregats' not in st.session_state:
        st.session_state.open_agregats = {}

    for i in range(0, len(grouped), 2):  # 2 sous-familles par ligne
        cols = st.columns(2)
        for j in range(2):
            if i + j >= len(grouped):
                break
            sousfam = grouped.iloc[i + j]['SOUS_FAMILLE']
            ags = grouped.iloc[i + j]['AGREGAT']

            with cols[j]:
                st.markdown(
                    f"""
                    <div style='background-color:#c2dcff;
                                border-radius:10px;
                                padding:1rem;
                                box-shadow:0 4px 6px rgba(0,0,0,0.1);'>
                        <h4 style='color:#023047;margin-top:0'>{sousfam}</h4>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                for agr in ags:
                    if st.button(f"🔹 {agr}", key=f"{sousfam}_{agr}"):
                        st.session_state.open_agregats[agr] = not st.session_state.open_agregats.get(agr, False)

                    if st.session_state.open_agregats.get(agr, False):
                        produits = (
                            df[df['AGREGAT'] == agr]['NOM PRODUIT']
                            .dropna()
                            .value_counts()
                            .index.tolist()
                        )
                        max_items = st.session_state.open_agregats.get(f"max_{agr}", 5)
                        for p in produits[:max_items]:
                            st.markdown(f"- {p}")

                        if len(produits) > 5:
                            label = "Voir plus" if max_items == 5 else "Voir moins"
                            if st.button(label, key=f"voirplus_{agr}"):
                                if max_items == 5:
                                    st.session_state.open_agregats[f"max_{agr}"] = len(produits)
                                else:
                                    st.session_state.open_agregats[f"max_{agr}"] = 5
                        st.markdown("")
else:
    st.info("Importez d'abord votre fichier Gpairo dans le menu latéral pour afficher le tableau de bord.")
