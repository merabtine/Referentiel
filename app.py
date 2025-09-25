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
/* tableaux */
thead tr th {
    background-color:#8ecae6 !important;
    color:#023047 !important;
    font-weight:bold !important;
    text-align:center !important;
}


/* cellule */
[data-testid="stDataFrame"] table {
    background-color:#fffdf6 !important;
    border-radius:10px;
}


/* bouton télécharger */
div.stDownloadButton > button {
    background-color:#ffb703 !important;
    color:#023047 !important;
    font-weight:bold !important;
    border:none;
    border-radius:8px !important;
}


/* boutons style texte agrégats & voir plus/moins */
.agg-button, .toggle-button {
    color: #023047 !important;
    background: none !important;
    border: none !important;
    padding: 0 !important;
    margin: 0 5px 0 0 !important;
    cursor: pointer !important;
    font-size: 15px !important;
    text-decoration: none !important; /* pas de soulignement */
}
.agg-button:hover, .toggle-button:hover {
    color: #219ebc !important;
}


/* conteneur sous-famille */
.subfam-box {
    border: 1px solid #8ecae6;
    border-radius: 5px;
    padding: 8px;
    margin-bottom: 15px;
}
.subfam-title {
    font-weight: bold;
    font-size: 17px;
    color: #023047;
    margin-bottom: 5px;
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
    try:
        if uploaded_file.name.endswith(".csv"):
            df_input = pd.read_csv(uploaded_file)
        else:
            df_input = pd.read_excel(uploaded_file)
        st.sidebar.success("Fichier Gpairo chargé ✅")
    except Exception as e:
        st.error(f"Erreur de lecture du fichier : {e}")
        st.stop()


    # on lit ton résultat déjà produit en backend
    try:
        df = pd.read_excel("resultat_classification.xlsx")
    except Exception as e:
        st.error(f"Impossible de lire le fichier résultat : {e}")
        st.stop()


    # filtrer sous-familles != Non identifiable
    df = df[df["SOUS_FAMILLE"] != "Non identifiable"]


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
    agg_counts = df_filtered['AGREGAT'].value_counts().reset_index()
    agg_counts.columns = ['AGREGAT', 'Nombre']
    fig_bar = px.bar(
        agg_counts,
        x='AGREGAT', y='Nombre', text='Nombre',
        title="Répartition des agrégats", color='AGREGAT'
    )
    fig_bar.update_traces(textposition='outside')
    st.plotly_chart(fig_bar, use_container_width=True)


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

# on prépare un grouped propre : liste d’agrégats par sous-famille
grouped = (
    df.groupby('SOUS_FAMILLE')['AGREGAT']
    .unique()
    .reset_index()
)

# on parcourt 2 par 2 pour avoir 2 sous-familles par ligne
for i in range(0, len(grouped), 2):
    colA, colB = st.columns(2)

    # -------- Première sous-famille --------
    sousfam = grouped.iloc[i]['SOUS_FAMILLE']
    if sousfam != "Non identifiable":
        with colA:
            ags = grouped.iloc[i]['AGREGAT']
            # cadre englobant la sous-famille
            st.markdown(
                f"""
                <div style="border:1px solid #ccc; border-radius:8px; padding:10px; margin-bottom:15px;">
                  <div style="font-weight:bold; color:blue; font-size:16px; margin-bottom:8px;">{sousfam}</div>
                """,
                unsafe_allow_html=True
            )
            for agr in ags:
                # produits uniques
                produits = df[df['AGREGAT'] == agr]['NOM PRODUIT'].dropna().tolist()
                produits = list(dict.fromkeys(produits))  # supprime doublons en gardant l'ordre
                # expander sans soulignement ni cadre
                with st.expander(f"{agr}"):
                    if len(produits) <= 5:
                        for p in produits:
                            st.markdown(f"- {p}")
                    else:
                        # clé unique par sousfamille+agrégat
                        show_all = st.checkbox(
                            "Voir tout",
                            key=f"chk_{sousfam}_{agr}"
                        )
                        if show_all:
                            for p in produits:
                                st.markdown(f"- {p}")
                        else:
                            for p in produits[:5]:
                                st.markdown(f"- {p}")
            st.markdown("</div>", unsafe_allow_html=True)

    # -------- Deuxième sous-famille si elle existe --------
    if i + 1 < len(grouped):
        sousfam2 = grouped.iloc[i + 1]['SOUS_FAMILLE']
        if sousfam2 != "Non identifiable":
            with colB:
                ags2 = grouped.iloc[i + 1]['AGREGAT']
                st.markdown(
                    f"""
                    <div style="border:1px solid #ccc; border-radius:8px; padding:10px; margin-bottom:15px;">
                      <div style="font-weight:bold; color:blue; font-size:16px; margin-bottom:8px;">{sousfam2}</div>
                    """,
                    unsafe_allow_html=True
                )
                for agr in ags2:
                    produits = df[df['AGREGAT'] == agr]['NOM PRODUIT'].dropna().tolist()
                    produits = list(dict.fromkeys(produits))
                    with st.expander(f"{agr}"):
                        if len(produits) <= 5:
                            for p in produits:
                                st.markdown(f"- {p}")
                        else:
                            show_all = st.checkbox(
                                "Voir tout",
                                key=f"chk_{sousfam2}_{agr}"
                            )
                            if show_all:
                                for p in produits:
                                    st.markdown(f"- {p}")
                            else:
                                for p in produits[:5]:
                                    st.markdown(f"- {p}")
                st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("Importez d'abord votre fichier Gpairo dans le menu latéral pour afficher le tableau de bord.")