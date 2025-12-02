import pandas as pd
from ydata_profiling import ProfileReport

# Diagnostic sur les données. Le fichier en entrée est où sauvegarder le rapport.
def diagnostic(donnees, titre, fichier):
    rapport = ProfileReport(donnees, title=titre, explorative=True, correlations={"auto": {"calculate": False}})
    rapport.to_file(fichier)

# Chargement des données
fichier = "netflix_titles.csv"
donnees = pd.read_csv(fichier, encoding='utf-8', encoding_errors='ignore')  # Chargement du fichier csv
print(f"Nombre de lignes : {donnees.shape[0]}; Nombre de colonnes : {donnees.shape[1]}")
print(f"Données chargées depuis le fichier \"{fichier}\".")

# Diagnostic sous format HTML
diagnostic(donnees, "Rapport de pré-nettoyage", "pré-nettoyage.html") # Diagnostic pré-nettoyage
# --------------------------------------------------------------------------------------------------------------------------------------
# Après analyse du fichier HTML:
# Valeurs manquantes:
#   director (29.9%) (2634): impossible à imputer
#   cast (9.4%) (825): impossible à imputer
#   country (9.4%) (831): impossible à imputer
#   date_added (0.1%) (10): impossible à imputer
#   rating: (< 0.1%) (4): impossible à imputer
#   duration (<0.1%) (3): impossible à imputer (mais pour ce nombre on peut chercher sur Wikipedia...)
#    ---> Les valeurs manquantes pour chacune de ces colonnes seront nettoyées selon l'analyse nécessaire. 
# Duplicats: aucun
# Affichage du type de données
def affiche_typedonnees(): # On aura besoin de réutiliser.
    print("-----------------Types de données :")
    print(donnees.dtypes)
affiche_typedonnees()
# --------------------------------------------------------------------------------------------------------------------------------------
# À part release_year, tous sont identifiés comme "object", donc il faudra normaliser.
# Affichage d'un aperçu des données
print(donnees.head())
# --------------------------------------------------------------------------------------------------------------------------------------
# À la vue des données, seules date_aded peuvent être stockées dans une valeur qui n'est pas une string.
# On essaie avec convert_dtypes()
donnees = donnees.convert_dtypes()
affiche_typedonnees()
# --------------------------------------------------------------------------------------------------------------------------------------
# Convertit la date en un format utilisable.
# Référence: https://docs.python.org/3/library/datetime.html#strftime-and-strptime-behavior
donnees["date_added"] = pd.to_datetime(donnees["date_added"], format='%B %d, %Y', errors='coerce')
print(donnees.head())
# --------------------------------------------------------------------------------------------------------------------------------------
# 2a) Films vs séries : proportions, tendances par année.
# Pour ces colonnes, aucune valeur manquante n'est reportée, donc aucun pré-traitement n'est nécessaire.
# Aperçu des types afin de s'assurer qu'ils ne sont pas dupliqués (majuscules-minuscules)
# Aperçu également des dates de sortie, afin de s'assurer que les années sont plausibles.
types = donnees.groupby("type")["type"].count()
annees_sortie = donnees.groupby("release_year")["release_year"].count()
print(types)
print(annees_sortie)
# --------------------------------------------------------------------------------------------------------------------------------------
# Concaténation d'une colonne de pourcentage pour les types, puis affichage
pourcentages = types / donnees.shape[0] * 100
types = pd.concat([types.rename("count"),pourcentages.rename("percent")], axis=1)
print(types)
# --------------------------------------------------------------------------------------------------------------------------------------
# Tendances par année
#tendances = donnees.groupby("release_year")["type"].agg({"type":"sum"})
tendances = donnees.groupby(["release_year","type"])["type"].count()
print(tendances)
# TODO, faire un tableau plus compréhensible...
