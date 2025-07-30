import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Référentiel Industriel",
    layout="wide"
)



# ─────────────────────────────────────────────
# Logo + Titre alignés + bouton reset
col_logo, col_title, col_button = st.columns([1, 4, 1])
with col_logo:
    st.image("logo.png", width=130)
with col_title:
    st.markdown("## **Référentiel Industriel : Données des pièces de rechange**")


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

            side.markdown(f"""
    <style>
    /* Fond clair / sombre selon le mode */
    .stat-box {{
        padding: 15px; 
        border-radius: 10px; 
        border-left: 6px solid #1f77b4; 
        margin-top: 10px;
        background-color: var(--bg-color);
        color: var(--text-color);
    }}
    .stat-box h4 {{
        color: #1f77b4;
    }}
    .stat-box ul {{
        list-style-type: none; 
        padding-left: 0; 
    }}
    .stat-box .unique {{ color: #2ca02c; }}
    .stat-box .duplication {{ color: #ff4d4d; }}
    </style>

    <script>
    // Applique les variables CSS selon le mode Streamlit
    const root = document.documentElement;
    const darkModeMediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

    function setColors(e) {{
        if (e.matches) {{
            root.style.setProperty('--bg-color', '#222');
            root.style.setProperty('--text-color', '#eee');
        }} else {{
            root.style.setProperty('--bg-color', '#f0f2f6');
            root.style.setProperty('--text-color', '#333');
        }}
    }}

    setColors(darkModeMediaQuery);
    darkModeMediaQuery.addEventListener('change', setColors);
    </script>

    <div class="stat-box">
        <h4>📌 Statistiques Générales</h4>
        <ul>
            <li><b>Lignes totales :</b> {total_lignes:,}</li>
            <li><b>Produits uniques :</b> <span class="unique">{produits_uniques:,}</span></li>
            <li><b>Duplications détectées :</b> <span class="duplication">{duplications:,}</span></li>
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

#--------------------------------------------------------
def show_global_base_distribution(df_global):
    if 'BASE' not in df_global.columns:
        st.error("La colonne 'BASE' est introuvable dans le dataset global.")
        return
    
    base_counts = df_global['BASE'].value_counts()
    total_lignes = len(df_global)
    
    fig_donut = px.pie(
        base_counts,
        names=base_counts.index,
        values=base_counts.values,
        color_discrete_sequence=["#EEEE0E", "#4430DE"],  
        hole=0.6,
        title="Répartition des lignes par BASE"
    )
    fig_donut.update_layout(
        annotations=[dict(text=f'Total<br>{total_lignes:,}', x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    st.plotly_chart(fig_donut, use_container_width=True)

# Chargement backend automatique du dataset global fusionné
try:
    df_global = pd.read_csv("dataset_gpairo_webpdrmif.csv", encoding="utf-8-sig")
    st.markdown("---")
    st.header("📊 Visualisation dataset global fusionné")

    show_global_base_distribution(df_global)

    csv = df_global.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="Télécharger dataset global fusionné (CSV)",
        data=csv,
        file_name="dataset_gpairo_webpdrmif.csv",
        mime="text/csv"
    )
except Exception as e:
    st.error(f"Erreur lors du chargement du dataset global backend : {e}")