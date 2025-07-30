import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Référentiel Industriel",
    layout="wide"
)

# ────────────── CSS personnalisé pour la navigation et le style ──────────────
st.markdown("""
<style>
/* Masquer le radio button par défaut de Streamlit */
.stRadio > div {
    display: none;
}

/* Conteneur de la barre de navigation */
.nav-container {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 15px;
    padding: 10px;
    margin: 20px 0;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
}

/* Barre de navigation */
.nav-bar {
    display: flex;
    justify-content: center;
    gap: 0;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 12px;
    padding: 5px;
    backdrop-filter: blur(10px);
}

/* Boutons de navigation */
.nav-button {
    flex: 1;
    padding: 15px 25px;
    text-align: center;
    color: white;
    text-decoration: none;
    border-radius: 10px;
    transition: all 0.3s ease;
    cursor: pointer;
    font-weight: 500;
    font-size: 16px;
    border: none;
    background: transparent;
    position: relative;
    overflow: hidden;
}

.nav-button:hover {
    background: rgba(255, 255, 255, 0.2);
    transform: translateY(-2px);
}

.nav-button.active {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    color: white;
    box-shadow: 0 5px 15px rgba(79, 172, 254, 0.4);
    transform: translateY(-2px);
}

.nav-button.active::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.3) 50%, transparent 70%);
    animation: shine 2s infinite;
}

@keyframes shine {
    0% { transform: translateX(-100%); }
    100% { transform: translateX(100%); }
}

/* Section intro avec logo en arrière-plan */
.intro-section {
    background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200"><circle cx="100" cy="100" r="80" fill="rgba(102,126,234,0.1)" stroke="rgba(102,126,234,0.2)" stroke-width="2"/><text x="100" y="105" text-anchor="middle" font-family="Arial" font-size="16" fill="rgba(102,126,234,0.3)">LOGO</text></svg>');
    background-repeat: no-repeat;
    background-position: right center;
    background-size: 300px;
    padding: 40px;
    border-radius: 20px;
    background-color: rgba(102, 126, 234, 0.02);
    border: 1px solid rgba(102, 126, 234, 0.1);
    margin: 30px 0;
    position: relative;
}

/* Conteneur des cercles concentriques */
.circles-container {
    display: flex;
    justify-content: center;
    align-items: center;
    height: 300px;
    position: relative;
}

.circle {
    position: absolute;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-weight: bold;
    color: white;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
}

.circle-famille {
    width: 250px;
    height: 250px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    font-size: 18px;
}

.circle-sous-famille {
    width: 200px;
    height: 200px;
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    font-size: 16px;
}

.circle-agregat {
    width: 150px;
    height: 150px;
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    font-size: 14px;
}

.circle-nom {
    width: 100px;
    height: 100px;
    background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
    font-size: 12px;
}

/* Animation des cercles */
.circle {
    animation: pulse 3s ease-in-out infinite;
}

.circle-famille { animation-delay: 0s; }
.circle-sous-famille { animation-delay: 0.5s; }
.circle-agregat { animation-delay: 1s; }
.circle-nom { animation-delay: 1.5s; }

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.05); }
}
</style>
""", unsafe_allow_html=True)

# ────────────── Header (logo + titre) ──────────────
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("logo.png", width=130)
with col_title:
    st.markdown("## **Référentiel Industriel : Données des pièces de rechange**")

# ────────────── Barre de navigation améliorée ──────────────
st.markdown("""
<div class="nav-container">
    <div class="nav-bar">
        <button class="nav-button" onclick="setPage('Accueil')" id="btn-accueil">
            🏠 Accueil
        </button>
        <button class="nav-button" onclick="setPage('API Models Overview')" id="btn-api">
            🤖 API Models
        </button>
        <button class="nav-button" onclick="setPage('Autre rubrique')" id="btn-autre">
            📊 Autre rubrique
        </button>
    </div>
</div>

<script>
function setPage(pageName) {
    // Retirer la classe active de tous les boutons
    document.querySelectorAll('.nav-button').forEach(btn => btn.classList.remove('active'));
    
    // Ajouter la classe active au bouton cliqué
    if (pageName === 'Accueil') {
        document.getElementById('btn-accueil').classList.add('active');
    } else if (pageName === 'API Models Overview') {
        document.getElementById('btn-api').classList.add('active');
    } else if (pageName === 'Autre rubrique') {
        document.getElementById('btn-autre').classList.add('active');
    }
    
    // Simuler le clic sur le radio button correspondant (caché)
    const radioButtons = document.querySelectorAll('input[type="radio"]');
    radioButtons.forEach(radio => {
        if (radio.nextElementSibling.textContent.trim() === pageName) {
            radio.click();
        }
    });
}

// Initialiser la page active au chargement
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('btn-accueil').classList.add('active');
});
</script>
""", unsafe_allow_html=True)

# Radio button caché pour la logique Streamlit
page = st.radio(
    "Navigation",
    options=["Accueil", "API Models Overview", "Autre rubrique"],
    horizontal=True,
    key="hidden_nav"
)

if page == "Accueil":
    # ────────────── Section introductive avec logo en arrière-plan ──────────────
    st.markdown("""
    <div class="intro-section">
        <div style="max-width: 60%;">
            <h2 style="color: #667eea; margin-bottom: 20px;">🎯 Bienvenue dans REFINOR</h2>
            <h3 style="color: #764ba2; margin-bottom: 15px;">Le Référentiel Industriel Intelligent</h3>
            <p style="font-size: 18px; line-height: 1.6; color: #555;">
                Cette application permet de <strong>nettoyer</strong>, <strong>classer</strong> et <strong>analyser</strong> 
                des bases de données industrielles de pièces de rechange, notamment pour des installations fixes et du matériel roulant.
            </p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ────────────── Cercles concentriques de hiérarchie ──────────────
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.markdown("### 🎯 **Objectifs principaux**")
        st.markdown("""
        **1. Nettoyage des désignations brutes**  
        - Correction orthographique et harmonisation des termes  
        - Normalisation pour garantir la cohérence des catégories  
        
        **2. Classification hiérarchique**  
        Chaque produit est classé selon quatre champs obligatoires représentés 
        par les cercles concentriques ci-contre.
        """)

    with col_right:
        st.markdown("### 🔄 **Hiérarchie des catégories**")
        st.markdown("""
        <div class="circles-container">
            <div class="circle circle-famille">FAMILLE</div>
            <div class="circle circle-sous-famille">SOUS-FAMILLE</div>
            <div class="circle circle-agregat">AGRÉGAT</div>
            <div class="circle circle-nom">NOM</div>
        </div>
        
        <div style="margin-top: 20px; font-size: 14px; color: #666;">
            <p><span style="color: #667eea;">●</span> <strong>Famille</strong> : Catégorie générale (mécanique, électrique)</p>
            <p><span style="color: #4facfe;">●</span> <strong>Sous-famille</strong> : Regroupement large (outils, connecteurs)</p>
            <p><span style="color: #43e97b;">●</span> <strong>Agrégat</strong> : Regroupement spécifique</p>
            <p><span style="color: #fa709a;">●</span> <strong>Nom</strong> : Désignation nettoyée individuelle</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    
    # ────────────── Upload et traitement fichiers ──────────────
    st.subheader("📂 Importer vos fichiers de données")
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
                color_discrete_sequence=["#4facfe", "#667eea"],
                hole=0.4
            )
            side.plotly_chart(fig_pie, use_container_width=True)

            side.markdown(f"""
                <div style="background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(79,172,254,0.1) 100%); 
                           padding: 20px; border-radius: 15px; border-left: 6px solid #4facfe; margin-top: 10px;">
                    <h4 style="color: #667eea;">📌 Statistiques Générales</h4>
                    <ul style="list-style-type: none; padding-left: 0;">
                        <li style="padding: 5px 0;"><b>Lignes totales :</b> {total_lignes:,}</li>
                        <li style="padding: 5px 0;"><b>Produits uniques :</b> <span style="color: #43e97b;">{produits_uniques:,}</span></li>
                        <li style="padding: 5px 0;"><b>Duplications détectées :</b> <span style="color: #fa709a;">{duplications:,}</span></li>
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
        st.header("📊 Visualisation dataset global fusionné")

        try:
            df_global = pd.read_csv("dataset_gpairo_webpdrmif.csv", encoding="utf-8-sig")
            base_counts = df_global['BASE'].value_counts()
            total_lignes = len(df_global)
            
            fig_donut = px.pie(
                base_counts,
                names=base_counts.index,
                values=base_counts.values,
                color_discrete_sequence=["#4facfe", "#667eea"],
                hole=0.6,
                title="Répartition des lignes par BASE"
            )
            fig_donut.update_layout(
                annotations=[dict(text=f'Total<br>{total_lignes:,}', x=0.5, y=0.5, font_size=20, showarrow=False)]
            )
            st.plotly_chart(fig_donut, use_container_width=True)

            csv = df_global.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 Télécharger dataset global fusionné (CSV)",
                data=csv,
                file_name="dataset_gpairo_webpdrmif.csv",
                mime="text/csv"
            )
        except Exception as e:
            st.error(f"Erreur lors du chargement du dataset global backend : {e}")
    else:
        st.info("⚠️ Importez les deux fichiers Gpairo et Webpdrmif pour visualiser le dataset global fusionné.")

elif page == "API Models Overview":
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(79,172,254,0.1) 100%); 
               padding: 30px; border-radius: 20px; margin: 20px 0;">
        <h2 style="color: #667eea;">🤖 Présentation des modèles AI et APIs</h2>
        <p style="font-size: 18px; color: #555;">
            Ici, vous pouvez explorer différents modèles d'IA, leurs APIs et exemples d'utilisation 
            (ex: OpenRouter, Together AI, etc.).
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    ### 🔧 Modèles disponibles
    - **OpenRouter** : Interface unifiée pour multiple modèles
    - **Together AI** : Modèles open-source optimisés
    - **Custom Models** : Modèles personnalisés pour votre domaine
    
    *(Contenu à compléter selon vos besoins)*
    """)

else:
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(102,126,234,0.1) 0%, rgba(79,172,254,0.1) 100%); 
               padding: 30px; border-radius: 20px; margin: 20px 0;">
        <h2 style="color: #667eea;">📊 Autre rubrique</h2>
        <p style="font-size: 18px; color: #555;">
            Contenu à définir selon vos besoins spécifiques.
        </p>
    </div>
    """, unsafe_allow_html=True)