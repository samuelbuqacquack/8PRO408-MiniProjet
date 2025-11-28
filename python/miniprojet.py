import pandas as pd
from ydata_profiling import ProfileReport

class PipelineDeNettoyage:
    def __init__ (self):
        self.logs = []

    # Diagnostic sur les données. Le fichier en entrée est où sauvegarder le rapport.
    def diagnostic(self, donnees, titre, fichier):
        self.logs.append("Diagnostic: analyse de complétude et doublons.")
        rapport = ProfileReport(donnees, title=titre, explorative=True)
        rapport.to_file(fichier)
        self.logs.append(f"  Profil des données sauvegardé dans le fichier \"{fichier}\".")
        self.logs.append("")        

    # Nettoyage des données
    def nettoyage(self, donnees):
        self.logs.append("Nettoyage : suppression des données incomplètes et des doublons.")
        donnees_sansNA = donnees.dropna()
        self.logs.append(f"  {donnees.shape[0] - donnees_sansNA.shape[0]} lignes incomplètes supprimées.")
        donnees_sansNA_sansDUP = donnees_sansNA.drop_duplicates()
        self.logs.append(f"  {donnees_sansNA.shape[0] - donnees_sansNA_sansDUP.shape[0]} lignes doubles supprimées.")
        self.logs.append("")        
        return donnees_sansNA_sansDUP

    def validation(self, donnees):
        self.logs.append("Validation : vérification des types de données.")
        self.logs.append(donnees.dtypes)
        self.logs.append("")        

    def normalisation(self, donnees):
        self.logs.append("Nettoyage : normalisation des types de données.")        
        donnees = donnees.convert_dtypes()
        self.logs.append("")        
        return donnees

    def reporting(self):
        print("Résumé du pipeline : \n")
        for log in self.logs:
            print(log)

# Chargement des données
fichier = "netflix_titles.csv"
donnees = pd.read_csv(fichier, encoding='utf-8', encoding_errors='ignore')  # Chargement du fichier csv
print(f"Nombre de lignes : {donnees.shape[0]}; Nombre de colonnes : {donnees.shape[1]}")
print(f"Données chargées depuis le fichier \"{fichier}\".")

# Création du pipeline de nettoyage
superNettoyeur = PipelineDeNettoyage()

# Exécution du pipeline
superNettoyeur.diagnostic(donnees, "Rapport de pré-nettoyage", "pré-nettoyage.html") # Diagnostic pré-nettoyage
