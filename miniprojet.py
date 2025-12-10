# version python du projet 

# Importation des programmathèques nécessaires
import pandas as pd 
import matplotlib.pyplot as plt
import numpy as np 
from ydata_profiling import ProfileReport
import seaborn as sns
import calendar
import plotly.graph_objects as go
import plotly.express as px
# === FONCTIONS ===

# Diagnostic sur les données. Le fichier en entrée de la fonction contiendra le rapport.
def diagnostic(donnees, titre, fichier):
    rapport = ProfileReport(donnees, title=titre, explorative=True, correlations={"auto": {"calculate": False}})
    rapport.to_file(fichier)
    print("\nConsultez le fichier \"", fichier, "\" afin de visualiser le diagnostic.\n")

# Duplique les données d'un groupby en ne gardant qu'une catégorie par entrée.
# Affiche aussi la différence avant / après
def compte_avec_recoupages(donnees_entrantes):
    # Sépare les données en plusieurs colonnes
    donnees_separees = donnees_entrantes.str.split(pat=", ", expand=True)
    print("======= Étendage des données ========\n")    
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
    print("\n======= Recoupage et comptage des données ========\n")
    print(retour)    
    return retour
    
# Affiche les types de données dans un DataFrame.
def affiche_typedonnees(donnees): # On aura besoin de réutiliser.
    print("-----------------Types de données :")
    print(donnees.dtypes)
# === PROGRAMME PRINCIPAL ===
# (Séparé par des ---- afin de conserver, dans le fichier Python, la structure du notebook Jupyter.)
# ------------------------------------------------------------------------------
# Chargement des données
fichier = "netflix_titles.csv"
donnees = pd.read_csv(fichier, encoding='utf-8', encoding_errors='ignore')  # Chargement du fichier csv
print(f"Nombre de lignes : {donnees.shape[0]}; Nombre de colonnes : {donnees.shape[1]}")
print(f"Données chargées depuis le fichier \"{fichier}\".")
# 1 - Exploration des données
# ------------------------------------------------------------------------------
# Diagnostics
diagnostic(donnees, "Rapport de pré-nettoyage", "pré-nettoyage.html") # Diagnostic pré-nettoyage
affiche_typedonnees(donnees)
print("-----------------Types de données :")
print(donnees.head()) # Aperçu des données pour guider le nettoyage
# ------------------------------------------------------------------------------
# Attribution du type de données exact de chacune des colonnes
donnees = donnees.convert_dtypes()
affiche_typedonnees(donnees)
# ------------------------------------------------------------------------------
# Conversion des valeurs de date en format utile à l'analyse
donnees["date_added"] = pd.to_datetime(donnees["date_added"], format= '%B %d, %Y', errors='coerce')
print(donnees.head())
# 2 - Analyses de contenus
# ------------------------------------------------------------------------------
# 2a) Analyse de contenus: types de produit audiovisuel
print(" TYPES DE PRODUITS AUDIOVISUELS \n")
types = donnees.groupby("type")["type"].count()  # regroupement par type
print("====== Aperçu préliminaire =======")
print(types)
# Calcul et affichage des proportions
types_pourcentages = types / donnees.shape[0] * 100 # convertion en pourcentages 
print("\n======== Proportions (%) =========")
print(types_pourcentages.round(2))

# Recoupage des tendances
types_tendances = donnees.groupby(["release_year","type"])["type"].count() # regroupement par année de sortie puis type
types_tendances = types_tendances.unstack().fillna(0).astype("int64")
print("\n========== Tendances par année ========")
print(types_tendances)
# ------------------------------------------------------------------------------
# Étape 2 :  Longueur des produits audiovisuels
# D'après notre rapport d'analyse (HTML), il manque 3 valeurs. On commence par les nettoyer.
donnees_temp = donnees.copy()
donnees_temp = donnees_temp.dropna(subset=["duration"])
# Extraction des entiers de la valeur "duration"
donnees_temp["duration"] = donnees_temp["duration"].str.extract(r"(\d+)").astype(int)
# Sépare les données en films et séries
movies = donnees_temp[(donnees_temp["type"] == "Movie")]
shows = donnees_temp[(donnees_temp["type"] == "TV Show")]
# Affichage des maximum et des minimum
print("Durée minimum des films :", movies["duration"].min(),"minutes")
print("Durée maximum des films :", movies["duration"].max(),"minutes")
print("Nombre de saisons minimum des séries :", shows["duration"].min(), "saison(s)")
print("Nombre de saisons maximum des séries :", shows["duration"].max(), "saison(s)")
# ------------------------------------------------------------------------------
# 2b) Analyse de contenus: genres (listed_in)
print(" GENRES \n")
print("======= Apperçu préliminaire ========")
print(donnees.groupby("listed_in")["listed_in"].count())  # regroupement par genre
# ------------------------------------------------------------------------------
# Souvent plus d'une donnée présente par enregistrement.
genres = compte_avec_recoupages(donnees["listed_in"])
genres = genres.sort_values(ascending=False)
# ------------------------------------------------------------------------------
# 2c) Analyse de contenus: répartition géographique
print(" RÉPARTITION GÉOGRAPHIQUE \n")
# Les entrées manquantes seront premièrement marquées "Unkown".
donees_temp = donnees
donees_temp["country"] = donees_temp["country"].fillna("Unknown")
print("======= Apperçu préliminaire ========")
print(donees_temp.groupby("country")["country"].count()) # regroupement par pays
# ------------------------------------------------------------------------------
# Souvent plus d'une donnée présente par enregistrement.
pays = compte_avec_recoupages(donees_temp["country"])
pays = pays.sort_values(ascending=False)
# 2d1) Analyse de contenus: acteurs
print(" ACTEURS \n")
# Les entrées manquantes seront premièrement marquées "Unkown".
donees_temp = donnees
donees_temp["cast"] = donees_temp["cast"].fillna("Unknown")
print("======= Apperçu préliminaire ========")
print(donees_temp.groupby("cast")["cast"].count()) # regroupement par acteur
# ------------------------------------------------------------------------------
# Souvent plus d'une donnée présente par enregistrement.
acteurs = compte_avec_recoupages(donees_temp["cast"])
print("\n======= Les cinq acteurs les plus fréquents ========")
acteurs_frequents = acteurs.drop(index="Unknown").reset_index(name='count').sort_values(['count'], ascending=False).head(10)
print(acteurs_frequents)
# (P.S.: On remarque que "Jr". a mal été découpé, mais sa relative très faible fréquence ne donne pas lieu à coder spécialement pour rectifier.)
# 2d2) Analyse de contenus: réalisateurs
print(" RÉALISATEURS \n")
# Les entrées manquantes seront premièrement marquées "Unkown".
donees_temp = donnees 
donees_temp["director"] = donees_temp["director"].fillna("Unknown")
print("======= Apperçu préliminaire ========")
print(donees_temp.groupby("director")["director"].count()) # regroupement par réalisateur
# ------------------------------------------------------------------------------
# Souvent plus d'une donnée présente par enregistrement.
realisateurs = compte_avec_recoupages(donees_temp["director"])
realisateurs_frequents = realisateurs.drop(index="Unknown").reset_index(name='count').sort_values(['count'], ascending=False).head(10)
print("\n======= Les cinq réalisateurs les plus fréquents ========")
print(realisateurs_frequents)
# 3 - Analyses temporelles 
# ------------------------------------------------------------------------------
# 3a) Analyse temporelle: années de sortie
print(" ANNÉES DE SORTIE \n")
annees_sortie = donnees.dropna(subset=["release_year"]).groupby("release_year").size()  # Regroupe et compte toutes les données existantes
print ("=========== Aperçu =========== \n ")
print(annees_sortie.reset_index(name="count").sort_values("release_year"))
# ------------------------------------------------------------------------------
# 3b) Analyse temporelle: ajout aux données (tous types confondus)
# On se débarasse totu d'abord des données non disponibles
donnees_temp = donnees.dropna(subset=["date_added"])
# L'analyse se fera en 3 étapes : par année, par mois toutes années confondues, et par mois
# Étape 1: par année
ajout_par_annee = donnees_temp["date_added"].dt.year
donnees_temp = pd.concat([donnees_temp,ajout_par_annee.rename("year_added")], axis=1)  # On en aura besoin à l'étape 3
ajout_par_annee = donnees_temp.groupby("year_added")["year_added"].count()
print(" ANNÉES D'AJOUT \n")
print ("=========== Aperçu =========== \n ")
print(ajout_par_annee)
# Génération du graphique pour l'étape 4. 
ajout_par_annee_graph = ajout_par_annee.sort_index()
# ------------------------------------------------------------------------------
# Étape 2: par mois (toutes années confondues (tac))
ajout_par_mois_tac = donnees_temp["date_added"].dt.month
donnees_temp = pd.concat([donnees_temp,ajout_par_mois_tac.rename("month_added_ayc")], axis=1)  # On en aura besoin à l'étape 3
ajout_par_mois_tac = donnees_temp.groupby("month_added_ayc")["month_added_ayc"].count()
print(" MOIS D'AJOUT (TOUTES ANNÉES CONFONDUES) \n")
print ("=========== Aperçu =========== \n ")
print(ajout_par_mois_tac)
# Génération du graphique pour l'étape 4.
ajout_par_mois_tac_graph = ajout_par_mois_tac
ajout_par_mois_tac_graph.index = pd.to_datetime(ajout_par_mois_tac_graph.index, format="%m").month_name()
# ------------------------------------------------------------------------------
# Étape 3: par mois
ajout_par_mois = donnees_temp["year_added"].astype(str) + "-" + donnees_temp["month_added_ayc"].astype(str).str.zfill(2)
ajout_par_mois = pd.concat([donnees_temp,ajout_par_mois.rename("month_added")], axis=1)
ajout_par_mois = ajout_par_mois.groupby("month_added")["month_added"].count()
#ajout_par_mois = donnees_temp.groupby(["year_added","month_added"])["month_added"].count() # regroupement par année puis par mois
#ajout_par_mois = ajout_par_mois.unstack().fillna(0).astype("int64")
print(" MOIS D'AJOUT \n")
print ("=========== Aperçu =========== \n ")
print(ajout_par_mois)
# TODO, générer le graphique ici?
#tendance_mois = donnees_temp.groupby(donnees_temp["date_added"].dt.to_period("M")).size()
#tendance_mois.index = tendance_mois.index.to_timestamp()
# 4 - Visualisation graphique des analyses 
print("\n============= VISUALISATION GRAPHIQUE DES ANALYSES DE CONTENU ================")
# 1- proportions du contenu: 
# 1-a : Pourcentage de presence par types 
#Countplot des types de contenus
plt.figure(figsize=(8,6))
# definir les noms des axes, separer l'axe x avec seaborn methode des mediane sur chaque countplots 
ax = sns.countplot(data=donnees, x="type", palette="Set2")
plt.title("Répartition des types de contenus (Films vs Séries)")
plt.xlabel("Type de contenu")
plt.ylabel("Nombre de titres")
# reutilisation des antecedent de 2-a) dans le calcul des pourcentages 
movie_pct = float(types_pourcentages["Movie"])
tv_pct    = float(types_pourcentages["TV Show"])
labels = [f"Movie : {movie_pct:.1f}%",f"TV Show : {tv_pct:.1f}%"]
# faire une legende avec plt pour passer nos proportions en format legende 
plt.legend(
    handles=[plt.Line2D([], [], color="none")] * 2,
    labels=labels,
    title="Proportions",
    loc="upper right",
    frameon=True
)
plt.show()
# utilisation des countplots pour faire ces graphiques 
# 1-b : pourcentage par genre 
# utulisation de px pour faire un diagramme en bande horizontale pour afficher le contenu listed_in 
genres_df = genres.reset_index()
genres_df.columns = ["genre", "valeur_numerique"]
fig = px.bar(
    genres_df,
    x="valeur_numerique",
    y="genre",
    orientation="h",
    color="genre",
    title="Répartition des genres"
)
fig.update_layout(
    height=900,              
    margin=dict(l=200),
    plot_bgcolor="gray",    
    showlegend=False,
)
fig.update_yaxes(dtick=1, automargin=True,)
fig.show()
# 1-c: boxplot de comparatif des duree moyenne et max du contenu
# pour le films 
movies = donnees[(donnees["type"] == "Movie") & donnees["duration"].notna()].copy()
movies["minutes"] = movies["duration"].str.extract(r"(\d+)").astype(int)
plt.figure(figsize=(6,5))
sns.boxplot(data=movies, y="minutes")
plt.ylabel("Durée des films (minutes)")
plt.title("Distribution de la durée des films")
plt.show()
#2 pour les series 
shows = donnees[(donnees["type"] == "TV Show") & donnees["duration"].notna()].copy()
shows["seasons"] = shows["duration"].str.extract(r"(\d+)").astype(int)
plt.figure(figsize=(6,5))
sns.boxplot(data=shows, y="seasons")
plt.ylabel("Durée des séries (saisons)")
plt.title("Distribution de la durée des séries")
plt.show()
#1- d : repartition geogrpahique 
# meme logique que repartition par genre, code reutiliser et modifié
# prendre des pays dont la distribution est superieur ou egale a 10, pour avoir un beau chart 
# la consequence a ce choix: la valeur unknow est biaise car on lui retire des valeurs numerique qui sont attribue a ces pays 
#inconus dont la distribution ne depasse pas 10. 
pays_filtre = pays[pays >= 10]   # garde seulement les valeurs ≥ 10
pays_df = pays_filtre.reset_index()
pays_df.columns = ["pays", "valeur_numerique"]
fig = px.bar(
    pays_df,
    x="valeur_numerique",
    y="pays",
    orientation="h",
    color="pays",
    title="Répartition géographique des contenus (≥ 10 titres)"
)
fig.update_layout(
    height=900,
    margin=dict(l=200),
    plot_bgcolor="gray",
    showlegend=False,
)
fig.update_yaxes(dtick=1, automargin=True)
fig.show()
#1-e : realisateur les plus frequent, 10 noms 
plt.figure(figsize=(8,6))
realisateurs_frequents.columns = ["director", "count"]
ax = sns.barplot(
    data=realisateurs_frequents,
    x="count",
    y="director",
    palette="viridis"
)
plt.title("Les 10 réalisateurs les plus fréquents")
plt.xlabel("Nombre de contenus")
plt.ylabel("Réalisateur")
plt.show()
#1-f: acteurs 
acteurs_frequents.columns = ["actor", "count"]
plt.figure(figsize=(8,6))
ax = sns.barplot(
    data=acteurs_frequents,
    x="count",
    y="actor",
    palette="Set2"
)
plt.title("Les 10 acteurs les plus fréquents")
plt.xlabel("Nombre de titres")
plt.ylabel("Acteur")
plt.tight_layout()
plt.show()
print("\n============= VISUALISATION GRAPHIQUE DES ANALYSES TEMPORELLE ================")
# comparaison des courbes de tendances des films et des series
# utilisation de l'objet go 
# types_tendances : index = release_year, colonnes = ["Movie", "TV Show"]
fig = go.Figure() # l'objet fiure go 
fig.add_trace(go.Scatter(
    x=types_tendances.index,
    y=types_tendances["Movie"],
    mode="lines+markers",
    name="Movies",
    line=dict(color="red", width=3)
)) # courbe de films 
fig.add_trace(go.Scatter(
    x=types_tendances.index,
    y=types_tendances["TV Show"],
    mode="lines+markers",
    name="TV Shows",
    line=dict(color="green", width=3, dash="dash")
)) # courbe de series
fig.update_layout(
    title="Tendance par année des dates de sortie : Films vs Séries",
    xaxis_title="Année de sortie",
    yaxis_title="Nombre de contenus",
    plot_bgcolor="black",
    paper_bgcolor="white",
    legend_title="Type de contenu"
) # modification du layout des courbes 
fig.update_xaxes(showgrid=True, gridcolor="white")
fig.update_yaxes(showgrid=True, gridcolor="white", type="linear") # modification du background 
fig.show()
# barre plot du nombre de sortie par annee de facon confondu
#utilisation de px. 
annees_sortie = donnees_temp.groupby("release_year").size().reset_index(name="nombre_de_titres")
fig = px.bar(
    annees_sortie,
    x="release_year",
    y="nombre_de_titres",
    color="nombre_de_titres",
    color_continuous_scale="Cividis",  # ou "Blues", "Plasma", etc.
)
fig.update_layout(
    title="Nombre de sortie par année, type confondu(release_date)",
    xaxis_title="Année de sortie",
    yaxis_title="Nombre de titres",
    plot_bgcolor="black",
    paper_bgcolor="white",
)
fig.show()
# graphique des ajouts de contenue sur netflix par annee/ en fonction de la periode de temps
#les mois sont pris en compte 
ajout_par_annee = (
    donnees_temp
    .groupby(donnees_temp["date_added"].dt.year)
    .size()
    .reset_index(name="nombre_de_titres")
    .rename(columns={"date_added": "annee_ajout"})
    .sort_values("annee_ajout")
)

fig = px.bar(
    ajout_par_annee,
    x="annee_ajout",
    y="nombre_de_titres",
    color="nombre_de_titres",
    color_continuous_scale="Cividis",
    title="Nombre de titres ajoutés par année",
)

fig.update_layout(
    xaxis_title="Année d'ajout",
    yaxis_title="Nombre de titres",
    plot_bgcolor="black",
    paper_bgcolor="white",
)
#graphique des dates par mois 
ajout_par_mois = (
    donnees_temp
    .groupby(donnees_temp["date_added"].dt.month)
    .size()
    .reset_index(name="nombre_de_titres")
    .rename(columns={"date_added": "mois_num"})
)
# rendre les dates en int 
ajout_par_mois["mois_num"] = ajout_par_mois["mois_num"].astype(int)
ajout_par_mois["mois"] = ajout_par_mois["mois_num"].apply(lambda m: calendar.month_name[m])
ajout_par_mois = ajout_par_mois.sort_values("mois_num")

fig = px.bar(
    ajout_par_mois,
    x="mois",
    y="nombre_de_titres",
    color="nombre_de_titres",
    color_continuous_scale="Cividis",
    title="Nombre de titres ajoutés par mois (toutes années confondues)",
)
fig.update_layout(
    xaxis_title="Mois", 
    yaxis_title="Nombre de titres",
    plot_bgcolor="black",
    paper_bgcolor="white",)
fig.show()

# ===== Tendance annuelle =====
fig_annee = px.line(
    ajout_par_annee,
    x="annee_ajout",
    y="nombre_de_titres",
    title="Tendance annuelle des ajouts",
)
fig_annee.update_traces(
    name="Ajouts annuels",         
    showlegend=True,
    line=dict(color="orange", width=3, dash="dash"),
)
fig_annee.update_layout(
    legend_title_text="Série temporelle",  
    legend=dict(
        x=0.02,
        y=0.98,
        bgcolor="rgba(255,255,255,0.7)",
        bordercolor="black",
        borderwidth=1,
    ),
)
# ===== Tendance mensuelle =====
fig_mois = ajout_par_mois_tac.plot.line(backend="plotly")
fig_mois.update_traces(
    name="Ajouts mensuels",   # texte de légende
    line=dict(color="red", width=3, dash="solid")
)
fig_mois.update_layout(
    title="Tendance mensuelle des ajouts",
    xaxis_title="Date (mois)",
    yaxis_title="Nombre de titres",
    legend_title_text="Type de courbe",
    legend=dict(
        x=0.02,
        y=0.98,
        bgcolor="rgba(255,255,255,0.7)",
        bordercolor="black",
        borderwidth=1,
    ),
)
fig_annee.show()
fig_mois.show()