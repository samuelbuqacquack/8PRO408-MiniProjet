import pandas as pd
from ydata_profiling import ProfileReport
import numpy as np

# Diagnostic sur les données. Le fichier en entrée est où sauvegarder le rapport.
def diagnostic(donnees, titre, fichier):
    rapport = ProfileReport(donnees, title=titre, explorative=True, correlations={"auto": {"calculate": False}})
    rapport.to_file(fichier)

# Duplique les données d'un groupby en ne gardant qu'une catégorie par entrée.
# Affiche aussi la différence avant / après
def compte_avec_recoupages(donnees_entrantes):
    # Sépare les données en plusieurs colonnes
    donnees_separees = donnees_entrantes.str.split(pat=", ", expand=True)
    print(donnees_separees)

    # On a obtenu un maximum de x genre par entrée.
    nb_colonnes_add = donnees_separees.shape[1] -1 # Nombre de colonnes additionnelles
    # Il nous suffit de comptabiliser par chacune des colonnes et des les aditionner
    # On prend soin de remplacer les chaînes vides par NaN (ex: ", genre2"  commence par une virgule et crée ainsi une chaîne vide au début)
    # Lors de l'addition des colonnes, les genres non comptabilisés dans une colonne donnée seront replacées par 0.
    retour = donnees_separees.replace("", np.nan).groupby(0)[0].count()
    for index in range(1,nb_colonnes_add): # Commence à 1 car on n'a pas besoin d'ajouter 0 à 0...
        retour = retour.add(donnees_separees.replace("", np.nan).groupby(index)[index].count(), fill_value=0)
    retour = retour.astype("int64")
   
    print(retour)    
    return retour

# ------------------------------------------------------------------------------
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
def affiche_typedonnees(donnees): # On aura besoin de réutiliser.
    print("-----------------Types de données :")
    print(donnees.dtypes)
affiche_typedonnees(donnees)
# --------------------------------------------------------------------------------------------------------------------------------------
# À part release_year, tous sont identifiés comme "object", donc il faudra normaliser.
# Affichage d'un aperçu des données
print(donnees.head())
# --------------------------------------------------------------------------------------------------------------------------------------
# À la vue des données, seules date_aded peuvent être stockées dans une valeur qui n'est pas une string.
# On essaie avec convert_dtypes()
donnees = donnees.convert_dtypes()
affiche_typedonnees(donnees)
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
# (La liste d'année est abrégée mais on peut confirmer l'absence de valeurs aberrantes en la triant)
types = donnees.groupby("type")["type"].count()
annees_sortie = donnees.groupby("release_year")["release_year"].count()
print(types)
print(annees_sortie.sort_values())
# --------------------------------------------------------------------------------------------------------------------------------------
# Proportions.
# Concaténation d'une colonne de pourcentage pour les types, puis affichage
types_pourcentages = types / donnees.shape[0] * 100
types = pd.concat([types.rename("count"),types_pourcentages.rename("percent")], axis=1)
print(types)
# --------------------------------------------------------------------------------------------------------------------------------------
# Tendances par année.
# Génère un dataframe à deux index (année, type).
types_tendances = donnees.groupby(["release_year","type"])["type"].count()
print(types_tendances)
print("----------------")
# Reforme ce dataframe en transformant les types en colonnes
# (Utilise fillna pour transformer en 0 le compte des années où un type est absent)
types_tendances = types_tendances.unstack().fillna(0).astype("int64")
print(types_tendances)
types_tendances.plot(backend="plotly")
# --------------------------------------------------------------------------------------------------------------------------------------
# 2b) Genres principaux
# Pour cette colonne, aucune valeur manquante n'est reportée, donc aucun pré-traitement n'est nécessaire.
# Aperçu afin de s'assurer qu'ils ne sont pas dupliqués (majuscules-minuscules)
print(donnees.groupby("listed_in")["listed_in"].count())
# --------------------------------------------------------------------------------------------------------------------------------------
# On note la présence de recoupages (plus d'un genre par entrée).
genres = compte_avec_recoupages(donnees["listed_in"])
genres.sort_values().plot.bar(backend="plotly") # Affiche un graphique en barres
# --------------------------------------------------------------------------------------------------------------------------------------
# 2c) Répartition géographique
# Les entrées manquantes seront premièrement marquées "Unkown".
donnees_pays = donnees
donnees_pays["country"] = donnees_pays["country"].fillna("Unknown")
# Aperçu afin de s'assurer qu'ils ne sont pas dupliqués (majuscules-minuscules)
print(donnees.groupby("listed_in")["listed_in"].count())
# --------------------------------------------------------------------------------------------------------------------------------------
# On note la présence de recoupages (plus d'un genre par entrée).
pays = compte_avec_recoupages(donnees_pays["country"])
pays.sort_values().plot.bar(backend="plotly") # Affiche un graphique en barres  TODO afficher en formet de tarte plutôt
