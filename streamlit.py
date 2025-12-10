import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import calendar


st.set_page_config(page_title="Netflix Analyzer", layout="wide")


# fonction qui traitent les donnees du jupiter et qui permet de renvoyer les statistique sur streamli
#aussi accessible par le chatbot via des mot cles
def compte_avec_recoupages(donnees_entrantes):
    donnees_separees = donnees_entrantes.str.split(pat=", ", expand=True)
    nb_colonnes_add = donnees_separees.shape[1] - 1
    retour = donnees_separees.replace("", np.nan).groupby(0)[0].count()
    for index in range(1, nb_colonnes_add):
        retour = retour.add(
            donnees_separees.replace("", np.nan).groupby(index)[index].count(),
            fill_value=0,
        )
    retour = retour.astype("int64")
    return retour # fonction data 

@st.cache_data # donnee de fonction du chatbot 
def load_and_prepare():
    fichier = "netflix_titles.csv"
    donnees = pd.read_csv(fichier, encoding="utf-8", encoding_errors="ignore")
    # Types + les proportions, 
    types = donnees.groupby("type")["type"].count()
    types_pourcentages = types / donnees.shape[0] * 100 
    # fonction des genres, colonne listed_in exploitée 
    genres = compte_avec_recoupages(donnees["listed_in"]).sort_values(ascending=False) 
    # Durées : même logique que ton notebook, mais formatée pour Plotly
    donnees_temp = donnees.copy()
    donnees_temp = donnees_temp.dropna(subset=["duration"])
    donnees_temp["duration_num"] = (
        donnees_temp["duration"]
        .astype(str)
        .str.extract(r"(\d+)")
        .astype(int)
    )
    movies = donnees_temp[donnees_temp["type"] == "Movie"].copy()
    shows = donnees_temp[donnees_temp["type"] == "TV Show"].copy()
    # ACTEURS
    tmp = donnees.copy()
    tmp["cast"] = tmp["cast"].fillna("Unknown")
    acteurs = compte_avec_recoupages(tmp["cast"])
    acteurs_frequents = (
        acteurs
        .drop(index="Unknown", errors="ignore")
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(10)
    )
    # REALISATEURS
    tmp = donnees.copy()
    tmp["director"] = tmp["director"].fillna("Unknown")
    realisateurs = compte_avec_recoupages(tmp["director"])
    realisateurs_frequents = (
        realisateurs
        .drop(index="Unknown", errors="ignore")
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(10)
    )
    # repartition geographique 
    tmp = donnees.copy() 
    tmp["country"] = tmp["country"].fillna("Unknown")
    pays = compte_avec_recoupages(tmp["country"]).sort_values(ascending=False)
    pays_filtre = pays[pays >= 10]
    #dates pour les tendances 
    donnees["date_added"] = pd.to_datetime(
        donnees["date_added"], format="%B %d, %Y", errors="coerce"
    )
    donnees_temp = donnees.dropna(subset=["date_added"]).copy()
    # Tendance films vs séries (par année de sortie)
    types_tendances = (
        donnees.groupby(["release_year", "type"])["type"]
        .count()
        .unstack()
        .fillna(0)
        .astype("int64")
    )
    # Nombre de sorties par année release_year
    annees_sortie = (
        donnees.dropna(subset=["release_year"])
        .groupby("release_year")
        .size()
        .reset_index(name="nombre_de_titres")
    )
    # Graphique par année d'ajouts 
    ajout_par_annee = (
        donnees_temp.groupby(donnees_temp["date_added"].dt.year)
        .size()
        .reset_index(name="nombre_de_titres")
        .rename(columns={"date_added": "annee_ajout"})
        .sort_values("annee_ajout")
    )
    # Graphique des mois, tous confondu selon les annnees
    ajout_par_mois_tac = (
        donnees_temp.groupby(donnees_temp["date_added"].dt.month)
        .size()
        .reset_index(name="nombre_de_titres")
        .rename(columns={"date_added": "mois_num"})
    )
    ajout_par_mois_tac["mois_num"] = ajout_par_mois_tac["mois_num"].astype(int)
    return (
        donnees,
        types,
        types_pourcentages,
        genres,
        pays_filtre,
        movies,
        shows,
        acteurs_frequents,
        realisateurs_frequents,
        types_tendances,
        annees_sortie,
        ajout_par_annee,
        ajout_par_mois_tac,
    ) # <--- fonction a retourne dans le chatbot 
(
    donnees,
    types,
    types_pourcentages,
    genres,
    pays_filtre,
    movies,
    shows,
    acteurs_frequents,
    realisateurs_frequents,
    types_tendances,
    annees_sortie,
    ajout_par_annee,
    ajout_par_mois_tac,
) = load_and_prepare()

# disponibilite des donnees dans le chatbot, statisque de temps 
def afficher_analyse_duree():
    st.markdown("### Analyse de la durée des contenus")
    # Texte min / max (reprend ton notebook)
    duree_min_film  = movies["duration_num"].min()
    duree_max_film  = movies["duration_num"].max()
    duree_min_show  = shows["duration_num"].min()
    duree_max_show  = shows["duration_num"].max()
    st.write(f"Durée minimum des films : {duree_min_film} minutes")
    st.write(f"Durée maximum des films : {duree_max_film} minutes")
    st.write(f"Nombre de saisons minimum des séries : {duree_min_show} saison(s)")
    st.write(f"Nombre de saisons maximum des séries : {duree_max_show} saison(s)")
    # Boxplot films
    fig_movies = px.box(
        movies,
        y="duration_num",
        points="outliers",
        title="Distribution de la durée des films (minutes)",
        labels={"duration_num": "Durée (minutes)"},
    )
    st.plotly_chart(fig_movies, use_container_width=True)
    # Boxplot séries
    fig_shows = px.box(
        shows,
        y="duration_num",
        points="outliers",
        title="Distribution du nombre de saisons (séries)",
        labels={"duration_num": "Nombre de saisons"},
    )
    st.plotly_chart(fig_shows, use_container_width=True)
    # Petite explication
    st.markdown(
        "Ces boxplots montrent la répartition des durées : "
        "la boîte correspond au cœur des valeurs (quartiles), "
        "les moustaches aux valeurs plus extrêmes, et les points aux outliers."
    )
# realisateurs et acteurs 
def afficher_acteurs_realisateurs():
    st.markdown("### Acteurs et réalisateurs les plus fréquents")
    # Acteurs fréquents (top 10) – mêmes données que dans ton notebook
    acteurs_frequents_df = acteurs_frequents.copy()
    acteurs_frequents_df.columns = ["actor", "count"]

    fig_acteurs = px.bar(
        acteurs_frequents_df,
        x="count",
        y="actor",
        orientation="h",
        title="Top 10 acteurs les plus fréquents",
        labels={"count": "Nombre de titres", "actor": "Acteur"},
    )
    fig_acteurs.update_layout(height=400, margin=dict(l=100, r=20, t=40, b=40))
    st.plotly_chart(fig_acteurs, use_container_width=True)

    # Réalisateurs fréquents- top 10 
    realisateurs_frequents_df = realisateurs_frequents.copy()
    realisateurs_frequents_df.columns = ["director", "count"]

    fig_realisateurs = px.bar(
        realisateurs_frequents_df,
        x="count",
        y="director",
        orientation="h",
        title="Top 10 réalisateurs les plus fréquents",
        labels={"count": "Nombre de contenus", "director": "Réalisateur"},
    )
    fig_realisateurs.update_layout(height=400, margin=dict(l=100, r=20, t=40, b=40))
    st.plotly_chart(fig_realisateurs, use_container_width=True)
    # Texte de sortie 
    st.markdown(
        "Ces deux graphique represente," \
        "les acteurs les plus presents" \
        "sur des set donc sur des realisation" \
        "ainsi que les realisateur qui ont le plus de " \
        "contenu sur la plateforme netflix"
    )
# fonction de sorties des graphique d'analyse de contenue 
def afficher_analyse_contenu(): # commencer le debugage ici si probleme 
    st.markdown("ANALYSE DE CONTENU")
    # 1) Répartition des types (proportions)
    st.markdown("Proportions des types de contenus")
    types_df = types_pourcentages.round(2).to_frame(name="pourcentage").reset_index()
    types_df.columns = ["type", "pourcentage"]
    fig_types = px.bar(
        types_df,
        x="type",
        y="pourcentage",
        title="Proportions des types de contenus (Films vs Séries)",
        labels={"type": "Type de contenu", "pourcentage": "Pourcentage (%)"},
        text="pourcentage",
        color="type",
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_types.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_types.update_layout(yaxis_range=[0, types_df["pourcentage"].max() * 1.2])
    st.plotly_chart(fig_types, use_container_width=True)
    # 2) Répartition des genres
    st.markdown("Répartition des genres")
    genres_df = genres.reset_index()
    genres_df.columns = ["genre", "valeur_numerique"]
    fig_genres = px.bar( 
        genres_df,
        x="valeur_numerique",
        y="genre",
        orientation="h",
        title="Répartition des genres",
        labels={"valeur_numerique": "Nombre de titres", "genre": "Genre"},
    )
    fig_genres.update_layout(
        height=900,
        margin=dict(l=200, r=20, t=40, b=40),
        showlegend=False,
    )
    fig_genres.update_yaxes(dtick=1, automargin=True)
    st.plotly_chart(fig_genres, use_container_width=True)
    # 3) Répartition géographique
    st.markdown("Répartition géographique (≥ 10 titres)")
    pays_df = pays_filtre.reset_index()
    pays_df.columns = ["pays", "valeur_numerique"]

    fig_geo = px.bar(
        pays_df,
        x="valeur_numerique",
        y="pays",
        orientation="h",
        title="Répartition géographique des contenus (≥ 10 titres)",
        labels={"valeur_numerique": "Nombre de titres", "pays": "Pays"},
        color="pays",
    )
    fig_geo.update_layout(
        height=900,
        margin=dict(l=200, r=20, t=40, b=40),
        showlegend=False,
    )
    fig_geo.update_yaxes(dtick=1, automargin=True)
    st.plotly_chart(fig_geo, use_container_width=True)
    import calendar

def afficher_tendances():
    st.markdown("## Analyses de tendances")

    # 1) Courbes films vs séries (release_year)
    st.markdown("### Tendance des sorties : Films vs Séries")
    types_t_df = types_tendances.reset_index().melt(
        id_vars="release_year", value_vars=["Movie", "TV Show"],
        var_name="type", value_name="nombre"
    )
    fig_vs = px.line(
        types_t_df,
        x="release_year",
        y="nombre",
        color="type",
        markers=True,
        title="Tendance par année des dates de sortie : Films vs Séries",
        labels={"release_year": "Année de sortie", "nombre": "Nombre de contenus"},
    )
    st.plotly_chart(fig_vs, use_container_width=True)
    # 2) Nombre de sorties par année (release_year, type confondu)
    st.markdown("### Nombre de sorties par année (release_year)")
    fig_sorties = px.bar(
        annees_sortie,
        x="release_year",
        y="nombre_de_titres",
        color="nombre_de_titres",
        color_continuous_scale="Cividis",
        title="Nombre de sorties par année (type confondu)",
        labels={"release_year": "Année de sortie", "nombre_de_titres": "Nombre de titres"},
    )
    st.plotly_chart(fig_sorties, use_container_width=True)

    # 3) Tendance annuelle des ajouts (date_added)
    st.markdown("### Tendance annuelle des ajouts (date_added)")
    fig_annee = px.line(
        ajout_par_annee,
        x="annee_ajout",
        y="nombre_de_titres",
        markers=True,
        title="Tendance annuelle des ajouts",
        labels={"annee_ajout": "Année d'ajout", "nombre_de_titres": "Nombre de titres"},
    )
    st.plotly_chart(fig_annee, use_container_width=True)

    # 4) Ajouts par mois toutes années confondues
    st.markdown("### Ajouts par mois (toutes années confondues)")
    apm = ajout_par_mois_tac.copy()
    apm["mois"] = apm["mois_num"].apply(lambda m: calendar.month_name[m])
    apm = apm.sort_values("mois_num")

    fig_mois_bar = px.bar(
        apm,
        x="mois",
        y="nombre_de_titres",
        color="nombre_de_titres",
        color_continuous_scale="Cividis",
        title="Nombre de titres ajoutés par mois (toutes années confondues)",
        labels={"mois": "Mois", "nombre_de_titres": "Nombre de titres"},
    )
    st.plotly_chart(fig_mois_bar, use_container_width=True)

    # 5) Tendance mensuelle (même données, version ligne simple)
    st.markdown("### Tendance mensuelle des ajouts (index mois)")
    fig_mois_line = px.line(
        apm,
        x="mois",
        y="nombre_de_titres",
        markers=True,
        title="Tendance mensuelle des ajouts",
        labels={"mois": "Mois", "nombre_de_titres": "Nombre de titres"},
    )
    st.plotly_chart(fig_mois_line, use_container_width=True)
# apparence de l'interface 
st.title("Analyse du dataset Netflix")
col_left, col_right = st.columns([1, 2]) # separer l'interface en deux colonnes, 


# Colonne gauche, qui represente une esquisse 
with col_left:
    st.subheader("Statistiques minimales ")
    # 1) Donut types (Movie / TV Show)
    type_counts = types.to_frame(name="nombre").reset_index()
    type_counts.columns = ["type", "nombre"]
    fig_type = px.pie(
        type_counts,
        names="type",
        values="nombre",
        title="Répartition des types de contenus",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig_type.update_traces(textposition="inside", textinfo="percent+label")
    fig_type.update_layout(
        width=350,
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False,
    )
    st.plotly_chart(fig_type, use_container_width=False)
    # 2) Donut Top 10 genres (toujours à partir de TON 'genres')
    genres_df = genres.reset_index()
    genres_df.columns = ["genre", "valeur_numerique"]
    top10_genres = genres_df.head(10)
    fig_genres = px.pie(
        top10_genres,
        names="genre",
        values="valeur_numerique",
        title="Top 10 genres (en nombre de titres)",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Pastel,
    )
    fig_genres.update_traces(textposition="inside", textinfo="percent+label")
    fig_genres.update_layout(
        width=350,
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
        showlegend=False,
    )
    st.plotly_chart(fig_genres, use_container_width=False)
    st.subheader("Distribution de la durée")
    # 3) Boxplot Plotly : durée des films
    fig_movies = px.box(
        movies,
        y="duration_num",
        points="outliers",
        title="Distribution de la durée des films (minutes)",
        labels={"duration_num": "Durée (minutes)"},
    )
    fig_movies.update_layout(
        width=350,
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig_movies, use_container_width=False)
    # 4) Boxplot Plotly : durée des séries (saisons)
    fig_shows = px.box(
        shows,
        y="duration_num",
        points="outliers",
        title="Distribution du nombre de saisons (séries)",
        labels={"duration_num": "Nombre de saisons"},
    )
    fig_shows.update_layout(
        width=350,
        height=350,
        margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig_shows, use_container_width=False)


#  Colonne droite : Chatbot 
with col_right:
    st.subheader("Chatbot Netflix") # initialisation des cles 
    if "messages" not in st.session_state:
        st.session_state["messages"] = []
    if "last_action" not in st.session_state:
        st.session_state["last_action"] = None

    user_input = st.chat_input("Pose une question sur les données Netflix :")
    # 1) Traiter la nouvelle question AVANT d'afficher
    if user_input:
        question = user_input.lower()
        st.session_state["messages"].append(f"Utilisateur : {user_input}")
        if "durée" in question or "duree" in question: 
            st.session_state["messages"].append(
                f"Chatbot : Voici la reponse a votre consultation sur : {question} ."
            )
            st.session_state["last_action"] = "analyse_duree"  # dureee 
        elif "acteur" in question or "réalisateur" in question or "realisateur" in question:
            st.session_state["messages"].append(
               f"Chatbot : Voici la reponse a votre consultation sur : {question} ."
            )
            st.session_state["last_action"] = "acteurs_realisateurs"
        elif "contenu" in question:
            st.session_state["messages"].append(
                f"Chatbot : Voici la reponse a votre consultation sur : {question} ."
            )
            st.session_state["last_action"] = "analyse_contenu"
        elif "tendance" in question or "tendances" in question:
            st.session_state["messages"].append(
                f"Chatbot : Voici la reponse a votre consultation sur : {question} ."
            )
            st.session_state["last_action"] = "tendances"
        else:
            st.session_state["messages"].append(
                "Chatbot : Pour l’instant, je comprends surtout les questions sur la durée."
            )
            st.session_state["last_action"] = None
    # 2) garder l'historique lors d'affichage de la sortie
    for msg in st.session_state["messages"]:
        st.write(msg)
    # 3) Afficher l’analyse demandée 
    if st.session_state["last_action"] == "analyse_duree":
        afficher_analyse_duree()
    elif st.session_state["last_action"] == "acteurs_realisateurs": 
        afficher_acteurs_realisateurs()
    elif st.session_state["last_action"] == "analyse_contenu": 
        afficher_analyse_contenu()
    elif st.session_state["last_action"] == "tendances":
        afficher_tendances()


