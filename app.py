import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import base64
import os

st.set_page_config(page_title="Refinor", layout="centered")

# Affichage du logo
def show_logo(png_file):
    if os.path.exists(png_file):
        with open(png_file, "rb") as image_file:
            encoded = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"<div style='text-align: center'><img src='data:image/png;base64,{encoded}' width='200'/></div>",
            unsafe_allow_html=True
        )
    else:
        st.warning("Logo non trouvé.")

show_logo("logo.png")  # <-- place ton fichier logo ici

# Reset de l'application (nettoyage total)
if st.button("🔄 Réinitialiser"):
    st.experimental_rerun()

st.title("Analyse des fichiers Refinor")

# Chargement des deux fichiers
file1 = st.file_uploader("📁 Charger le fichier GPairo", type=["csv"])
file2 = st.file_uploader("📁 Charger le fichier Webpdrmif", type=["csv"])

# Traitement si les deux fichiers sont chargés
if file1 and file2:
    df1 = pd.read_csv(file1, sep=";", encoding="utf-8", on_bad_lines="skip")
    df2 = pd.read_csv(file2, sep=";", encoding="utf-8", on_bad_lines="skip")

    st.subheader("Aperçu du fichier GPairo")
    st.dataframe(df1.head(10))

    st.subheader("Aperçu du fichier Webpdrmif")
    st.dataframe(df2.head(10))

    # Statistiques dynamiques
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🧾 Lignes GPairo", f"{df1.shape[0]}")
        st.metric("🧾 Colonnes GPairo", f"{df1.shape[1]}")
    with col2:
        st.metric("🧾 Lignes Webpdrmif", f"{df2.shape[0]}")
        st.metric("🧾 Colonnes Webpdrmif", f"{df2.shape[1]}")

    # Détection des colonnes numériques communes
    numeric_cols = list(set(df1.select_dtypes(include='number').columns) & set(df2.select_dtypes(include='number').columns))

    if len(numeric_cols) >= 1:
        st.subheader("📊 Comparaison des valeurs numériques (histogramme)")
        selected_col = st.selectbox("Choisir une colonne numérique à comparer", numeric_cols)
        fig, ax = plt.subplots()
        ax.hist(df1[selected_col].dropna(), bins=20, alpha=0.5, label='GPairo')
        ax.hist(df2[selected_col].dropna(), bins=20, alpha=0.5, label='Webpdrmif')
        ax.set_title(f"Distribution des valeurs - {selected_col}")
        ax.legend()
        st.pyplot(fig)
    else:
        st.info("Pas assez de colonnes numériques communes pour tracer un graphique.")
