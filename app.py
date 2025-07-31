import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Référentiel Industriel",
    layout="wide"
)

# ────────────── Header (logo + titre) ──────────────
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("logo.png", width=130)
with col_title:
    st.markdown("## **Référentiel Industriel : Données des pièces de rechange**")

# ────────────── Barre de navigation ──────────────
page = st.radio(
    "Navigation",
    options=["Accueil", "API Models Overview", "Autre rubrique"],
    horizontal=True
)

if page == "Accueil":
    # ────────────── Overview et description ──────────────
    st.markdown("---")
    st.header("Bienvenue dans REFINOR: Le Référentiel Industriel")

    st.markdown("""
    Cette application permet de **nettoyer**, **classer** et **analyser** des bases de données industrielles de pièces de rechange, 
    notamment pour des installations fixes et du matériel roulant.
    
    **Objectifs principaux :**
    
    1. **Nettoyage des désignations brutes**  
       - Correction orthographique et harmonisation des termes  
       - Normalisation pour garantir la cohérence des catégories  
       
    2. **Classification hiérarchique**  
       Chaque produit est classé selon quatre champs obligatoires :  
       - **Famille** (catégorie générale, ex: mécanique, électrique)  
       - **Sous-famille** (regroupement large, ex: outils, connecteurs)  
       - **Agrégat** (regroupement plus spécifique dérivé du nom du produit)  
       - **Nom** (désignation nettoyée, produit individuel)  
    """)

    st.markdown("---")
    
    # ────────────── Upload et traitement fichiers ──────────────
    st.subheader("Importer vos fichiers de données")
    left, right = st.columns(2)

    def show_file_section(title, side):
        uploaded_file = side.file_uploader(f"📂 Importer {title}", type=["csv", "xlsx"], key=title)
        if uploaded_file is None:
            st.session_state[f"{title}_uploaded"] = False
            return False

        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
        except Exception as e:
            side.error(f"Erreur de lecture du fichier : {e}")
            st.session_state[f"{title}_uploaded"] = False
            return False

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
                <div style="background-color: #f0f2f6; padding: 15px; border-radius: 10px; border-left: 6px solid #1f77b4; margin-top: 10px;">
                    <h4 style="color: #1f77b4;">📌 Statistiques Générales</h4>
                    <ul style="list-style-type: none; padding-left: 0;">
                        <li><b>Lignes totales :</b> {total_lignes:,}</li>
                        <li><b>Produits uniques :</b> <span style="color: #2ca02c;">{produits_uniques:,}</span></li>
                        <li><b>Duplications détectées :</b> <span style="color: #ff4d4d;">{duplications:,}</span></li>
                    </ul>
                </div>
            """, unsafe_allow_html=True)

            side.markdown("#### 📏 Volume de données")
            progress_value = min(total_lignes / 10000, 1.0)
            side.progress(progress_value, text=f"{total_lignes:,} désignations brutes")
        else:
            side.warning("⚠️ La colonne 'DESI_ARTI' est introuvable dans ce fichier.")

        st.session_state[f"{title}_uploaded"] = True
        return True

    gpairo_ok = show_file_section("Gpairo", left)
    webpdrmif_ok = show_file_section("Webpdrmif", right)

    # ────────────── Visualisation dataset global backend ──────────────
    if gpairo_ok and webpdrmif_ok:
        st.markdown("---")
        st.header("📊 Visualisation du résultat après classification")
        
        try:
            df_global = pd.read_excel("Ref_Gpairo_Webpdrmif.xlsx")
            st.subheader("🔍 Aperçu des premières lignes du résultat")
            st.dataframe(df_global.head(30), use_container_width=True)
            col1, col2 = st.columns(2)

            # ── Diagramme en anneau (à gauche)
            with col1:
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
                    annotations=[dict(
                        text=f'Total<br>{total_lignes:,}', 
                        x=0.5, y=0.5, font_size=20, showarrow=False
                    )]
                )
                st.plotly_chart(fig_donut, use_container_width=True)

            # ── Diagramme en barres (à droite)
            with col2:
                nb_familles = df_global['FAMILLE'].nunique()
                nb_sous_familles = df_global['SOUS_FAMILLE'].nunique()
                nb_agregats = df_global['AGREGAT'].nunique()
                nb_produits = df_global['NOM PRODUIT'].nunique()

                stats_cat = pd.DataFrame({
                    "Catégorie": ["Familles", "Sous-familles", "Agrégats", "Produits"],
                    "Nombre": [nb_familles, nb_sous_familles, nb_agregats, nb_produits]
                })

                fig_bar = px.bar(
                    stats_cat,
                    x="Catégorie",
                    y="Nombre",
                    color="Catégorie",
                    text="Nombre",
                    title="Nombre d’éléments distincts par catégorie",
                    color_discrete_sequence=["#fda558", "#7dec7d", "#61a4d4", "#ea7bef"]
                )
                fig_bar.update_layout(showlegend=False)
                fig_bar.update_traces(textposition="outside")
                st.plotly_chart(fig_bar, use_container_width=True)

            # ── Bouton de téléchargement
            csv = df_global.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Télécharger dataset global fusionné (CSV)",
                data=csv,
                file_name="dataset_gpairo_webpdrmif.csv",
                mime="text/csv"
            )

        except Exception as e:
            st.error(f"❌ Erreur lors du chargement du dataset global backend : {e}")
    else:
        st.info("⚠️ Importez les deux fichiers Gpairo et Webpdrmif pour visualiser le dataset global fusionné.")

elif page == "API Models Overview":
    st.header("Présentation des modèles AI et APIs")
    st.markdown("Contenu à venir (OpenRouter, Together AI, etc.)")

else:
    st.header("Autre rubrique")
    st.write("Contenu à définir")
