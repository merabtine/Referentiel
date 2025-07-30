import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from io import StringIO

st.set_page_config(
    page_title="Référentiel Industriel",
    layout="wide"
)

# Logo et bouton réinitialisation dans un layout horizontal
col_logo, col_button = st.columns([3, 1])
with col_logo:
    st.image("logo.png", width=180)
with col_button:
    if st.button("🔄 Réinitialiser l'application"):
        st.experimental_rerun()

st.markdown("## Référentiel Industriel : Données des pièces de rechange")

st.markdown("---")

# Zone centrale avec deux colonnes
left, right = st.columns(2)

def show_file_section(title, side):
    uploaded_file = side.file_uploader(f"📂 Importer {title}", type=["csv", "xlsx"], key=title)

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            side.error(f"Erreur de lecture du fichier : {e}")
            return

        side.success(f"Fichier {title} chargé avec succès !")

        # Aperçu
        with side.expander("🧾 Aperçu des données", expanded=True):
            side.dataframe(df.head(20), use_container_width=True)

        # Statistiques
        if "DESI_ARTI" in df.columns:
            total_lignes = len(df)
            df_cleaned = df['DESI_ARTI'].dropna().str.strip().str.lower()
            produits_uniques = df_cleaned.nunique()
            duplications = total_lignes - produits_uniques
            taux_duplication = round((duplications / total_lignes) * 100, 2) if total_lignes > 0 else 0

            ## 1. Diagramme en camembert avec Plotly
            stats_df = pd.DataFrame({
                "Type": ["Produits uniques", "Duplications"],
                "Valeur": [produits_uniques, duplications]
            })

            fig_pie = px.pie(
                stats_df,
                values="Valeur",
                names="Type",
                title=f"📊 Répartition des désignations - {title}",
                color_discrete_sequence=px.colors.sequential.RdBu,
                hole=0.4
            )
            side.plotly_chart(fig_pie, use_container_width=True)

            ## 2. Affichage du nombre total + taux de duplication (figure matplotlib)
            fig_bar, ax = plt.subplots(figsize=(4, 2))
            ax.barh(["Taux de duplication"], [taux_duplication], color="#d62728")
            ax.set_xlim(0, 100)
            ax.set_xlabel("%")
            ax.set_title(f"Taux de duplication : {taux_duplication}%")
            for i, v in enumerate([taux_duplication]):
                ax.text(v + 1, i, f"{v}%", color='black', va='center')
            side.pyplot(fig_bar, use_container_width=True)

            # Info complémentaire
            side.markdown(f"📌 **Lignes totales :** `{total_lignes}`")
            side.markdown(f"📌 **Produits uniques :** `{produits_uniques}`")
            side.markdown(f"📌 **Duplications détectées :** `{duplications}`")

        else:
            side.warning("⚠️ La colonne 'DESI_ARTI' est introuvable dans ce fichier.")

# Section gauche : Gpairo
show_file_section("Gpairo", left)

# Section droite : Webpdrmif
show_file_section("Webpdrmif", right)

st.markdown("---")
st.info("🔧 D'autres rubriques seront intégrées prochainement sur cette même page.")
