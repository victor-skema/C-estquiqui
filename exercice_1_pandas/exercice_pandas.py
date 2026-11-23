# =====================================================================
# Session 2 - Exercice 1 : pandas avec les données de « C'est Qui Qui ? »
# =====================================================================

# pandas est la bibliothèque qui sert à manipuler des tableaux de données.
# On l'importe sous le surnom "pd" : c'est une convention, tout le monde
# l'écrit comme ça, et ça évite de taper "pandas." à chaque fois.
import pandas as pd

# Path sert à manipuler des chemins de fichiers (utile en F2 pour savoir
# si un fichier existe déjà).
from pathlib import Path


# =====================================================================
# Partie A — Lire et explorer
# =====================================================================

# A1. Lire les deux fichiers CSV.
# pd.read_csv transforme un fichier CSV en "DataFrame", c'est-à-dire un
# tableau avec des lignes et des colonnes nommées.
#  - sep=";" : dans ces fichiers, les colonnes sont séparées par des
#    points-virgules (et pas par des virgules, le réglage par défaut).
#  - encoding="utf-8-sig" : lit correctement les accents (é, è, à...) et
#    ignore le petit caractère invisible qu'Excel ajoute parfois au début.
affaires = pd.read_csv("data/affaires.csv", sep=";", encoding="utf-8-sig")
suspects = pd.read_csv("data/suspects.csv", sep=";", encoding="utf-8-sig")

# A2. La taille des tableaux.
# .shape donne (nombre de lignes, nombre de colonnes).
# On vérifie ainsi que le fichier a été lu en entier et bien découpé.
print("A2 - taille des affaires :", affaires.shape)   # (5, 6)
print("A2 - taille des colocs :", suspects.shape)     # (15, 10)

# A3. Le nom des colonnes.
# .columns liste les en-têtes. On en a besoin pour savoir quoi écrire
# entre les crochets dans la suite.
print("A3 - colonnes des affaires :", affaires.columns.tolist())
print("A3 - colonnes des colocs :", suspects.columns.tolist())
# Réponse : la colonne commune est "affaire_id". C'est elle qui relie
# chaque coloc à son affaire (elle servira en partie D).

# A4. Les 3 premières lignes, avec seulement 3 colonnes.
# Doubles crochets [[ ... ]] = on donne une LISTE de colonnes à garder.
# .head(3) = on garde les 3 premières lignes.
print("A4 :")
print(suspects[["affaire_id", "nom", "caractere"]].head(3))


# =====================================================================
# Partie B — Sélectionner
# =====================================================================

# B1. Une seule colonne : crochets simples avec son nom.
print("B1 :")
print(affaires["titre"])

# B2. Deux colonnes (doubles crochets) et les 5 premières lignes.
print("B2 :")
print(suspects[["nom", "voix"]].head(5))

# B3. Les colocs de l'affaire 3.
# suspects["affaire_id"] == 3 crée une colonne de True/False :
# True pour les lignes de l'affaire 3, False pour les autres.
# En la mettant entre crochets, on ne garde que les lignes True.
# Puis on prend la colonne "nom" et .tolist() la transforme en liste Python.
colocs_affaire_3 = suspects[suspects["affaire_id"] == 3]
print("B3 :", colocs_affaire_3["nom"].tolist())   # ['Margaux', 'Nina', 'Théo']

# B4. Tous les coupables.
# Attention : la colonne "coupable" contient le TEXTE "oui" ou "non",
# donc on compare avec "oui" entre guillemets.
coupables = suspects[suspects["coupable"] == "oui"]
print("B4 :")
print(coupables[["affaire_id", "nom"]])   # Léa, Camille, Théo, Anaïs, Sacha

# B5. Deux conditions à la fois : innocente ET voix féminine.
# - chaque condition est entre parenthèses (sinon Python se trompe
#   dans l'ordre des calculs et renvoie une erreur) ;
# - & veut dire "et" (on n'écrit pas "and" avec pandas).
innocentes = suspects[(suspects["coupable"] == "non") & (suspects["voix"] == "female-french")]
print("B5 :", innocentes["nom"].tolist())   # ['Inès', 'Margaux', 'Nina', 'Clara']

# B6. La fiche de Jules en dictionnaire.
# 1. On filtre la ligne de Jules (comme en B3).
# 2. .iloc[0] prend la première (et seule) ligne de ce résultat.
# 3. .to_dict() la transforme en dictionnaire : {"nom": "Jules", "alibi": ...}
# Ensuite on lit une valeur avec sa clé, comme pour tout dictionnaire.
# Dans le jeu, c'est ce dictionnaire qui servira à construire les
# consignes du personnage.
jules = suspects[suspects["nom"] == "Jules"].iloc[0].to_dict()
print("B6 :", jules["alibi"])


# =====================================================================
# Partie C — Transformer
# =====================================================================

# C1. Nouvelle colonne est_coupable (True/False).
# On écrit simplement le résultat de la comparaison dans une nouvelle
# colonne. Ensuite .sum() additionne : True compte pour 1, False pour 0,
# donc la somme = le nombre de True = le nombre de coupables.
suspects["est_coupable"] = suspects["coupable"] == "oui"
print("C1 - nombre de coupables :", suspects["est_coupable"].sum())   # 5

# C2. Compter chaque valeur de la colonne "voix".
# .value_counts() compte combien de fois apparaît chaque valeur.
print("C2 :")
print(suspects["voix"].value_counts())   # 8 male-french, 7 female-french

# C3. Longueur de l'alibi.
# .str donne accès aux outils de texte sur toute une colonne ;
# .str.len() calcule le nombre de caractères de chaque alibi.
# Puis on trie du plus long au plus court (ascending=False = décroissant)
# et on garde les 3 premiers.
suspects["longueur_alibi"] = suspects["alibi"].str.len()
plus_longs = suspects.sort_values("longueur_alibi", ascending=False)
print("C3 :")
print(plus_longs[["nom", "longueur_alibi"]].head(3))   # Camille 156, puis 154, 154

# C4. Le coloc dont l'indice contient "20h".
# .str.contains("20h") donne True si le texte contient "20h".
# On s'en sert comme filtre, exactement comme une condition ==.
print("C4 :")
print(suspects[suspects["indice"].str.contains("20h")][["affaire_id", "nom"]])   # Bastien, affaire 1

# C5. Les cases vides.
# Une case vide dans le CSV devient NaN ("Not a Number") dans pandas.
# .isna() met True sur chaque case vide, .sum() les compte.
print("C5 - cases vides avant :", suspects["faille"].isna().sum())   # 10
# .fillna("") remplace TOUTES les cases vides du tableau par un texte vide.
# Il faut réaffecter le résultat à suspects, sinon le tableau ne change pas.
suspects = suspects.fillna("")
print("C5 - cases vides après :", suspects["faille"].isna().sum())   # 0
# Réponse : 10 = 5 affaires x 2 innocents. Seul le coupable a une faille
# (et une excuse), les innocents n'en ont pas.


# =====================================================================
# Partie D — Croiser deux tableaux
# =====================================================================

# D1. Titre de chaque affaire + nom de son coupable.
# Le titre est dans "affaires", le nom du coupable dans "suspects".
# 1. On garde seulement les coupables (une ligne par affaire).
# 2. pd.merge colle les deux tableaux côte à côte en alignant les lignes
#    qui ont le même affaire_id (la colonne commune trouvée en A3).
coupables = suspects[suspects["est_coupable"]]
affaires_et_coupables = pd.merge(affaires, coupables, on="affaire_id")
print("D1 :")
print(affaires_et_coupables[["titre", "nom"]])

# D2. Vérifier qu'il y a 3 colocs par affaire.
# .groupby("affaire_id") range les lignes en paquets, un par affaire ;
# ["nom"].count() compte combien de noms il y a dans chaque paquet.
print("D2 :")
print(suspects.groupby("affaire_id")["nom"].count())   # 3 partout


# =====================================================================
# Partie E — Regrouper et classer
# =====================================================================

# E1. Lire les parties et compter les lignes.
# .shape[0] = le premier nombre de .shape = le nombre de lignes.
parties = pd.read_csv("data/parties_exemple.csv", sep=";", encoding="utf-8-sig")
print("E1 - nombre de parties :", parties.shape[0])   # 32

# E2. Score moyen (arrondi à 1 chiffre) et meilleur score.
# .mean() = moyenne, .max() = maximum, round(x, 1) = arrondi à 1 décimale.
print("E2 - moyenne :", round(parties["score"].mean(), 1))   # 61.3
print("E2 - maximum :", parties["score"].max())              # 98

# E3. La meilleure partie.
# On trie par score décroissant : la meilleure partie arrive en premier,
# et .iloc[0] la récupère. La colonne "affaire" contient déjà le titre.
meilleure = parties.sort_values("score", ascending=False).iloc[0]
print("E3 :", meilleure["pseudo"], "-", meilleure["affaire"], "-", meilleure["score"])

# E4. Le classement des joueurs.
# groupby("pseudo") fait un paquet de parties par joueur.
# .agg calcule plusieurs choses d'un coup ; chaque ligne se lit
#   nom_de_la_nouvelle_colonne=("colonne_de_départ", "calcul")
#   - points   : somme des scores
#   - parties  : nombre de parties jouées
#   - meilleur : score le plus haut
# Puis on trie par points décroissants.
# .reset_index() remet "pseudo" en colonne normale (après un groupby, il
# sert de nom de ligne). Sans ça, il disparaîtrait du CSV en F1.
classement = parties.groupby("pseudo").agg(
    points=("score", "sum"),
    parties=("score", "count"),
    meilleur=("score", "max"),
)
classement = classement.sort_values("points", ascending=False).reset_index()
print("E4 :")
print(classement)
# Réponse : pas forcément. Zoé a beaucoup de points parce qu'elle a joué
# 10 parties, deux fois plus que Lina. Pour comparer à égalité, il faudrait
# le score moyen par partie : moyenne=("score", "mean").

# E5. Taux de réussite par affaire.
# La colonne "bon_coupable" contient True/False.
# La moyenne d'une colonne True/False = la part de True
# (ex. 2 True sur 3 parties -> 0.67). On multiplie par 100 pour avoir
# un pourcentage, et on arrondit.
taux = parties.groupby("affaire")["bon_coupable"].mean() * 100
print("E5 :")
print(taux.round(0).sort_values())   # de 33 % (sono) à 100 % (nain de jardin)

# E6. Les parties de Lina, de la plus récente à la plus ancienne.
# Les dates sont écrites 2026-11-12T12:38:00 : dans ce format, l'ordre
# alphabétique est aussi l'ordre chronologique, donc on peut trier
# directement, en décroissant pour avoir la plus récente en haut.
lina = parties[parties["pseudo"] == "Lina"].sort_values("date", ascending=False)
print("E6 :")
print(lina[["date", "affaire", "score"]])   # 5 parties, la 1re du 12/11 avec 42


# =====================================================================
# Partie F — Enregistrer
# =====================================================================

# F1. Enregistrer le classement dans un nouveau CSV.
# Même séparateur et même encodage qu'à la lecture, pour pouvoir le relire.
# index=False : n'écrit pas les numéros de ligne (0, 1, 2...) de pandas,
# sinon une colonne sans nom apparaît à gauche dans le tableur.
classement.to_csv("data/classement.csv", sep=";", encoding="utf-8-sig", index=False)

# F2. Ajouter une partie à la fin d'un fichier sans l'effacer.
fichier = Path("data/mes_parties.csv")
# On crée un mini-tableau d'une seule ligne : une liste qui contient
# un dictionnaire (clé = nom de colonne, valeur = contenu de la case).
ma_partie = pd.DataFrame([{"pseudo": "Moi", "affaire_id": 1, "score": 95}])
# - mode="a" ("append" = ajouter) : on écrit à la fin du fichier au lieu
#   de le remplacer.
# - header=not fichier.exists() : on écrit la ligne d'en-tête seulement
#   si le fichier n'existe pas encore (donc au tout premier lancement).
ma_partie.to_csv(fichier, mode="a", header=not fichier.exists(),
                 index=False, sep=";", encoding="utf-8-sig")
print("F2 :")
print(pd.read_csv(fichier, sep=";", encoding="utf-8-sig"))
# Réponses :
# - mode="a" sert à ajouter à la suite. Sans lui, chaque lancement
#   effacerait le fichier et il ne resterait qu'une seule partie.
# - Sans header=not fichier.exists(), l'en-tête "pseudo;affaire_id;score"
#   serait réécrit à chaque lancement, au milieu des données.


# =====================================================================
# Défi
# =====================================================================

# Une fonction qui reçoit un numéro d'affaire et renvoie le meilleur
# score de chaque joueur sur cette affaire, du plus fort au moins fort.
# 1. On garde seulement les parties de cette affaire (filtre comme en B3).
# 2. On regroupe par joueur et on prend son score maximum (comme en E4).
# 3. On trie en décroissant.
# "return" renvoie le résultat à celui qui appelle la fonction.
def classement_de(affaire_id):
    parties_affaire = parties[parties["affaire_id"] == affaire_id]
    meilleurs = parties_affaire.groupby("pseudo")["score"].max()
    return meilleurs.sort_values(ascending=False)


print("Défi - classement_de(1) :")
print(classement_de(1))   # Karim 98, Lina 96, Sarah 94, Tom 93, Enzo 50, Zoé 48