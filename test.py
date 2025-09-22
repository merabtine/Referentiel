import pandas as pd

df = pd.read_excel('produits_normalises.xlsx')

df_subset = df[['NOM_CLEAN', 'CLE_NORMALISEE']]

df_uniques = df_subset.drop_duplicates(subset='NOM_CLEAN')

df_uniques.to_csv('produits_gpairo.csv', index=False)

print("Extraction terminée : produits et clés sauvegardés.")
