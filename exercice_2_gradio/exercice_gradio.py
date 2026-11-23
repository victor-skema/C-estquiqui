# =====================================================================
# Session 2 - Exercice 2 : Gradio, « L'annuaire de la coloc »
# Victor DESENCLOS
# =====================================================================

import gradio as gr
import pandas as pd

# Les données sont lues une seule fois, au lancement du programme.
# Les noms en MAJUSCULES rappellent que ces tableaux ne changent pas.
AFFAIRES = pd.read_csv("data/affaires.csv", sep=";", encoding="utf-8-sig")
# fillna("") : les innocents n'ont ni faille ni excuse, on évite les cases vides
SUSPECTS = pd.read_csv("data/suspects.csv", sep=";", encoding="utf-8-sig").fillna("")
PARTIES = pd.read_csv("data/parties_exemple.csv", sep=";", encoding="utf-8-sig")

NB_QUESTIONS = 5


# =====================================================================
# Les fonctions Python (aucune ne touche à l'écran directement :
# elles reçoivent des valeurs et en renvoient)
# =====================================================================

# Étape 1 - message d'accueil
def saluer(prenom):
    if prenom.strip() == "":
        return "Dis-moi d'abord comment tu t'appelles."
    return f"Bienvenue dans la coloc, **{prenom}** !"


# Étape 2 + 4 - on choisit une affaire
# Deux outputs (description, choix_coloc) -> on renvoie deux valeurs.
def choisir_affaire(titre):
    if titre is None:
        return "", gr.update(choices=[], value=None)
    affaire = AFFAIRES[AFFAIRES["titre"] == titre].iloc[0]
    colocs = SUSPECTS[SUSPECTS["affaire_id"] == affaire["affaire_id"]]
    noms = colocs["nom"].tolist()
    # gr.update change les choix du Radio et sélectionne le premier coloc
    return affaire["description"], gr.update(choices=noms, value=noms[0])


# Transforme le compteur en texte affichable
def texte_compteur(restantes):
    return f"Questions restantes : {restantes}"


# Étapes 4 + 6 - on choisit un coloc
# Renvoie : la fiche, la conversation vide, l'historique vide,
# le compteur remis à 5 et son texte.
def choisir_coloc(nom):
    if nom is None:
        return "", [], [], NB_QUESTIONS, texte_compteur(NB_QUESTIONS)
    coloc = SUSPECTS[SUSPECTS["nom"] == nom].iloc[0]
    # Défi 2 : voix féminine ou masculine
    if coloc["voix"] == "female-french":
        voix = "Voix féminine"
    else:
        voix = "Voix masculine"
    fiche = f"### {nom}\n{coloc['caractere']}\n\n*{voix}*"
    return fiche, [], [], NB_QUESTIONS, texte_compteur(NB_QUESTIONS)


# Étape 6 - le « robot » cherche des mots dans la question
def trouver_reponse(fiche, question):
    question = question.lower()
    if "soir" in question or "faisais" in question or "étais" in question:
        return fiche["alibi"]
    elif "vu" in question or "entendu" in question or "remarqué" in question:
        return fiche["indice"]
    else:
        return fiche["defense"]


# Étapes 5 + 6 - on envoie une question
# 4 inputs (nom, question, historique, restantes)
# 5 outputs (conversation, historique, question, restantes, compteur)
def envoyer(nom, question, historique, restantes):
    # Question vide : on ne change rien
    if question.strip() == "":
        return historique, historique, question, restantes, texte_compteur(restantes)
    if nom is None:
        raise gr.Error("Choisis d'abord un coloc.")
    if restantes == 0:
        raise gr.Error("Tu n'as plus de questions.")

    fiche = SUSPECTS[SUSPECTS["nom"] == nom].iloc[0].to_dict()
    reponse = trouver_reponse(fiche, question)

    # On crée une nouvelle liste avec les deux messages ajoutés
    historique = historique + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": reponse},
    ]
    restantes = restantes - 1
    return historique, historique, "", restantes, texte_compteur(restantes)


# Défi 1 - bouton Recommencer
def recommencer():
    return [], [], NB_QUESTIONS, texte_compteur(NB_QUESTIONS)


# Étape 7 - classement de l'exercice 1 (question E4)
def classement():
    tableau = PARTIES.groupby("pseudo").agg(
        points=("score", "sum"),
        parties=("score", "count"),
        meilleur=("score", "max"),
    )
    return tableau.sort_values("points", ascending=False).reset_index()


# Défi 3 - n'afficher que les parties d'une affaire
def filtrer_parties(titre):
    if titre is None or titre == "Toutes les affaires":
        return classement()
    parties_affaire = PARTIES[PARTIES["affaire"] == titre]
    parties_affaire = parties_affaire.sort_values("score", ascending=False)
    return parties_affaire[["date", "pseudo", "accuse", "score"]]


# =====================================================================
# L'écran : les composants, la mise en page et les événements
# =====================================================================

with gr.Blocks(title="L'annuaire de la coloc") as demo:
    # Étape 5 - valeurs gardées en mémoire, invisibles
    restantes = gr.State(NB_QUESTIONS)
    historique = gr.State([])

    gr.Markdown("# L'annuaire de la coloc")

    # Étape 7 - premier onglet
    with gr.Tab("Les colocs"):
        # Étape 3 - prénom et bouton sur la même ligne
        with gr.Row():
            prenom = gr.Textbox(label="Ton prénom", scale=3)
            bouton_saluer = gr.Button("Entrer", scale=1)
        accueil = gr.Markdown()

        # Étape 2 - liste des affaires
        choix_affaire = gr.Dropdown(AFFAIRES["titre"].tolist(), label="L'affaire", value=None)
        description = gr.Markdown()

        # Étape 3 - deux colonnes, la droite deux fois plus large
        with gr.Row():
            with gr.Column(scale=1):
                # Étape 4
                choix_coloc = gr.Radio([], label="Le coloc")
                fiche = gr.Markdown()
                # Étape 5
                question = gr.Textbox(label="Ta question")
                bouton_envoyer = gr.Button("Envoyer")
                compteur = gr.Markdown(texte_compteur(NB_QUESTIONS))
                # Défi 1
                bouton_recommencer = gr.Button("Recommencer")
            with gr.Column(scale=2):
                # Étape 6
                conversation = gr.Chatbot(label="La conversation")

    # Étape 7 - second onglet
    with gr.Tab("Classement") as onglet_classement:
        # Défi 3
        filtre_affaire = gr.Dropdown(
            ["Toutes les affaires"] + AFFAIRES["titre"].tolist(),
            label="Filtrer par affaire",
            value="Toutes les affaires",
        )
        tableau = gr.Dataframe(label="Classement des joueurs", interactive=False)

    # ----- Les événements -----
    # Règle d'or : autant de valeurs reçues que d'inputs,
    # autant de valeurs renvoyées que d'outputs, dans le même ordre.
    bouton_saluer.click(saluer, inputs=prenom, outputs=accueil)

    choix_affaire.change(choisir_affaire, inputs=choix_affaire,
                         outputs=[description, choix_coloc])

    choix_coloc.change(choisir_coloc, inputs=choix_coloc,
                       outputs=[fiche, conversation, historique, restantes, compteur])

    # Même fonction pour le clic et pour la touche Entrée
    bouton_envoyer.click(envoyer,
                         inputs=[choix_coloc, question, historique, restantes],
                         outputs=[conversation, historique, question, restantes, compteur])
    question.submit(envoyer,
                    inputs=[choix_coloc, question, historique, restantes],
                    outputs=[conversation, historique, question, restantes, compteur])

    bouton_recommencer.click(recommencer,
                             outputs=[conversation, historique, restantes, compteur])

    onglet_classement.select(filtrer_parties, inputs=filtre_affaire, outputs=tableau)
    filtre_affaire.change(filtrer_parties, inputs=filtre_affaire, outputs=tableau)

demo.launch()