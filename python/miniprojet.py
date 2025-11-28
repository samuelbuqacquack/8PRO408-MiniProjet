import pandas as pd

# Chargement des données
fichier = "netflix_titles.csv"
donnees = pd.read_csv(fichier, encoding='utf-8', encoding_errors='ignore')  # Chargement du fichier csv
print(f"Nombre de lignes : {donnees.shape[0]}; Nombre de colonnes : {donnees.shape[1]}")
print(f"Données chargées depuis le fichier \"{fichier}\".")
