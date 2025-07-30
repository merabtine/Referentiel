import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Référentiel Industriel",
    layout="wide"
)

# 🔁 Gestion de la réinitialisation (avant le layout principal)
if st.session_state.get("reset_flag"):
    st.session_state.clear()
    st.session_state["reset_flag"] = False
    st.experimental_rerun()

# ─────────────────────────────────────────────
# Logo + Titre alignés + bouton reset
col_logo, col_title, col_button = st.columns([1, 4, 1])
with col_logo:
    st.image("logo.png", width=130)
with col_title:
    st.markdown("## **Référentiel Industriel : Données des pièces de rechange**")
with col_button:
    if st.button("🔄 Réinitialiser l'application"):
        st.session_state["reset_flag"] = True
        st.experimental_rerun()

st.markdown("---")

# ─────────────────────────────────────────────
# Zone centrale à deux colonnes
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

        side.success(f"Fichier {title} chargé avec succès ✅")

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

            # Diagramme en camembert (couleurs personnalisées)
            stats_df = pd.DataFrame({
                "Type": ["Produits uniques", "Duplications"],
                "Valeur": [produits_uniques, duplications]
            })

            fig_pie = px.pie(
                stats_df,
                values="Valeur",
                names="Type",
                title=f"📊 Répartition des désignations - {title}",
                color_discrete_sequence=["#EEEE0E", "#4430DE"],  # Jaune et Bleu
                hole=0.4
            )
            side.plotly_chart(fig_pie, use_container_width=True)

            # 🔶 Bloc HTML stylisé : Statistiques Générales
            side.markdown(f"""
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 6px solid #1f77b4; margin-top: 10px;">
                    <h4 style="color: #1f77b4;">📌 Statistiques Générales</h4>
                    <ul style="list-style-type: none; padding-left: 0;">
                        <li><b>Lignes totales :</b> <span style="color: #333;">{total_lignes:,}</span></li>
                        <li><b>Produits uniques :</b> <span style="color: #2ca02c;">{produits_uniques:,}</span></li>
                        <li><b>Duplications détectées :</b> <span style="color: #d62728;">{duplications:,}</span></li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

            # 🔵 Barre de progression (volume de désignations)
            side.markdown("#### 📏 Volume de données")
            progress_value = min(total_lignes / 10000, 1.0)
            side.progress(progress_value, text=f"{total_lignes:,} désignations brutes")
        else:
            side.warning("⚠️ La colonne 'DESI_ARTI' est introuvable dans ce fichier.")

# ─────────────────────────────────────────────
# Section gauche : Gpairo
show_file_section("Gpairo", left)

# Section droite : Webpdrmif
show_file_section("Webpdrmif", right)

st.markdown("---")
st.info("🔧 D'autres rubriques seront intégrées prochainement sur cette même page.")
