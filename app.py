import streamlit as st
import pandas as pd
import plotly.express as px
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
            produits_uniques = df['DESI_ARTI'].dropna().str.strip().str.lower().nunique()

            stats_df = pd.DataFrame({
                "Type": ["Lignes totales", "Produits uniques"],
                "Valeur": [total_lignes, produits_uniques]
            })

            fig = px.pie(
                stats_df,
                values="Valeur",
                names="Type",
                title=f"📊 Statistiques - {title}",
                color_discrete_sequence=px.colors.sequential.RdBu,
                hole=0.4
            )
            side.plotly_chart(fig, use_container_width=True)
        else:
            side.warning("La colonne 'DESI_ARTI' est introuvable dans ce fichier.")

# Section gauche : Gpairo
show_file_section("Gpairo", left)

# Section droite : Xebpdrmif
show_file_section("Webpdrmif", right)

st.markdown("---")
st.info("🔧 D'autres rubriques seront intégrées prochainement sur cette même page.")
