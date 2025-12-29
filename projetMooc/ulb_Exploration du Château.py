"""
Projet Château - Niveaux 1 à 4 (MOOC)
Auteur: Costa Dos Santos Lima, WALDYR
Date: 03/09/2025

Description: Jeu d'exploration dans un château avec gestion des déplacements,
             collecte d'objets et résolution d'énigmes pour ouvrir les portes.

Fonctionnalités :
- Lecture des 3 fichiers de données : plan, objets, portes
- Affichage turtle : bandeau d'annonces, zone plan, colonne inventaire
- Déplacements clavier (flèches) avec gestion des murs/bords
- Sortie (victoire), objets à ramasser (inventaire), portes (Q/R)

Fichiers requis dans le même dossier :
- plan_chateau.txt
- dico_objets.txt
- dico_portes.txt

Convention des cases de la matrice du plan :
0 = vide (blanc), 1 = mur (gris), 2 = sortie (jaune), 3 = porte (orange), 4 = objet (vert)

Position de départ (conforme à l'énoncé) : (0, 1)
"""

import turtle
import os
from CONFIGS import *


# =============================================================================
# VARIABLES GLOBALES
# =============================================================================
matrice = None
objets = {}
inventaire = []
portes = {}
portes_ouvertes = set()
position = POSITION_DEPART
pas = 0
message_jeu = "Bienvenue dans le jeu! Utilisez les flèches pour vous déplacer."

t_annonce = turtle.Turtle()
t_annonce.hideturtle()
t_annonce.up()

t_inventaire = turtle.Turtle()
t_inventaire.hideturtle()
t_inventaire.up()

# =============================================================================
# FONCTIONS DE LECTURE DES FICHIERS (niveau 1)
# =============================================================================

def lire_matrice(fichier: str):
    """
    Lit un fichier contenant un plan de château et retourne une matrice.
    Args:
        fichier (str): Nom du fichier contenant le plan
    Returns:
        list: Matrice représentant le plan du château
    """
    try:
        with open(fichier, 'r', encoding='utf-8') as file:
            lignes = file.readlines()
            matrice = [list(map(int, ligne.strip().split())) for ligne in lignes]
        return matrice
    except FileNotFoundError:
        print(f"Erreur: Le fichier {fichier} n'a pas été trouvé.")
        return None
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {fichier}: {e}")
        return None

def creer_dictionnaire_des_objets(fichier_des_objets: str):
    """
    Crée un dictionnaire des objets à partir d'un fichier.
    Args:
        fichier_des_objets (str): Nom du fichier contenant les objets
    Returns:
        dict: Dictionnaire avec les positions comme clés et les objets comme valeurs
    """
    objets_dict = {}
    try:
        with open(fichier_des_objets, encoding="utf-8") as f:
            for ligne in f:
                if ligne.strip():
                    coords, nom = eval(ligne.strip())
                    objets_dict[coords] = nom
    except FileNotFoundError:
        pass
    return objets_dict

def creer_dictionnaire_des_portes(fichier_des_portes: str):
    """
    Crée un dictionnaire des portes et questions à partir d'un fichier.
    Args:
        fichier_des_portes (str): Nom du fichier contenant les portes et questions   
    Returns:
        dict: Dictionnaire avec les positions comme clés et les questions/réponses comme valeurs
    """
    portes_dict = {}
    try:
        with open(fichier_des_portes, encoding="utf-8") as f:
            for ligne in f:
                if ligne.strip():
                    coords, qr = eval(ligne.strip())
                    portes_dict[coords] = qr
    except FileNotFoundError:
        pass
    return portes_dict

# =============================================================================
# FONCTIONS D'AFFICHAGE DU PLAN (niveau 1)
# =============================================================================

def calculer_pas(matrice: list):
    """
    Calcule la dimension des cases pour que le plan tienne dans la fenêtre.
    Args:
        matrice (list): Matrice représentant le plan du château   
    Returns:
        int: Taille d'un côté de case en pixels
    """
    row = len(matrice)
    col = len(matrice[0])

    width = ZONE_PLAN_MAXI[0] - ZONE_PLAN_MINI[0]
    height = ZONE_PLAN_MAXI[1] - ZONE_PLAN_MINI[1]

    pitch_width = width // col
    pitch_height = height // row

    return min(pitch_width, pitch_height)

def coordonnees(case: tuple, pas: int):
    """
    Calcule les coordonnées turtle du coin inférieur gauche d'une case.
    Args:
        case (tuple): Coordonnées (ligne, colonne) de la case
        pas (int): Taille d'un côté de case en pixels   
    Returns:
        tuple: Coordonnées (x, y) du coin inférieur gauche de la case
    """
    row, col = case
    x = ZONE_PLAN_MINI[0] + col * pas
    y = ZONE_PLAN_MAXI[1] - (row + 1) * pas
    return x, y

def tracer_carre(dimension: int):
    """
    Trace un carré de la dimension spécifiée.
    Args:
        dimension (int): Longueur d'un côté du carré en pixels
    """
    turtle.begin_fill()
    for _ in range(4):
        turtle.forward(dimension)
        turtle.left(90)
    turtle.end_fill()

def tracer_case(case: tuple, couleur: str, pas: int):
    """
    Trace une case de la couleur spécifiée.
    Args:
        case (tuple): Coordonnées (ligne, colonne) de la case
        couleur (str): Couleur de la case
        pas (int): Taille d'un côté de case en pixels
    """
    x, y = coordonnees(case, pas)
    turtle.up()
    turtle.goto(x, y)
    turtle.down()
    turtle.fillcolor(couleur)
    tracer_carre(pas)
    turtle.up()

def afficher_plan(matrice: list):
    """
    Affiche le plan complet du château.
    Args:
        matrice (list): Matrice représentant le plan du château
    """
    if matrice is None:
        print("Matrice vide - impossible d'afficher le plan")
        return 
    
    # Configuration turtle
    turtle.speed(0)
    turtle.hideturtle()
    
    # Parcourir toutes les cases de la matrice
    for i in range(len(matrice)):
        for j in range(len(matrice[i])):
            valeur = matrice[i][j]
            # Utiliser le tableau COULEURS pour obtenir la couleur correspondante
            if 0 <= valeur < len(COULEURS):
                couleur = COULEURS[valeur]
            else:
                couleur = COULEUR_COULOIR  # Couleur par défaut
                
            tracer_case((i, j), couleur, pas)

# =============================================================================
# FONCTIONS D'INTERFACE UTILISATEUR
# =============================================================================

def effacer_zone_annonces():
    """Efface la zone d'annonces."""
    x, y = POINT_AFFICHAGE_ANNONCES
    turtle.up()
    turtle.goto(x, y)
    turtle.down()
    turtle.fillcolor("white")
    turtle.begin_fill()
    # Dessiner un rectangle qui couvre toute la largeur de la zone d'annonces
    turtle.forward(480)  # Largeur totale de la fenêtre (-240 à 240)
    turtle.right(90)
    turtle.forward(40)   # Hauteur du bandeau d'annonces
    turtle.right(90)
    turtle.forward(480)
    turtle.right(90)
    turtle.forward(40)
    turtle.right(90)
    turtle.end_fill()
    turtle.up()

def afficher_message(texte):
    """Affiche un message dans le bandeau d'annonces."""
    t_annonce.clear()  # efface uniquement l’ancien texte du bandeau
    t_annonce.goto(POINT_AFFICHAGE_ANNONCES)
    t_annonce.write(texte, font=("Arial", 12, "normal"))

def afficher_inventaire():
    """Affiche l'inventaire à droite."""
    global inventaire
    t_inventaire.clear()  # efface uniquement l’ancien inventaire
    x, y = POINT_AFFICHAGE_INVENTAIRE
    t_inventaire.goto(x, y)
    t_inventaire.write("Inventaire :", font=("Arial", 14, "bold"))
    y_ligne = y - 24
    if not inventaire:
        t_inventaire.goto(x, y_ligne)
        t_inventaire.write("— (vide) —", font=("Arial", 12, "normal"))
    else:
        for obj in inventaire:
            t_inventaire.goto(x, y_ligne)
            t_inventaire.write(f"• {obj}", font=("Arial", 12, "normal"))
            y_ligne -= 20
# ===========================================================================
# GESTION DU PERSONNAGE
# ============================================================================

def dessiner_joueur(position, pas):
    """
    Dessine le joueur à sa position actuelle.
    Args:
        position (tuple): Position (ligne, colonne) du joueur
        pas (int): Taille d'un côté de case en pixels
    """
    x, y = coordonnees(position, pas)
    turtle.up()
    turtle.goto(x + pas // 2, y + pas // 2)
    turtle.dot(pas * RATIO_PERSONNAGE, COULEUR_PERSONNAGE)

def effacer_joueur():
    """Efface le joueur en redessinant la case sous lui."""
    global position, matrice, pas
    
    ligne, colonne = position
    valeur = matrice[ligne][colonne]
    
    # Redessine la case avec la couleur d'origine
    if 0 <= valeur < len(COULEURS):
        couleur = COULEURS[valeur]
    else:
        couleur = COULEUR_COULOIR
        
    tracer_case(position, couleur, pas)

# =============================================================================
# FONCTIONS AUXILIAIRES (niveaux 3 et 4)
# =============================================================================

def ramasser_objet(position):
    """
    Ramasse un objet à la position spécifiée.
    Args:
        position (tuple): Position de l'objet (ligne, colonne)
    """
    global objets, inventaire, matrice, pas
    if position in objets:
        objet = objets[position]
        inventaire.append(objet)
        # Efface l'objet de la matrice (devient case vide)
        i, j = position
        matrice[i][j] = 0
        tracer_case(position, COULEURS[0], pas)
        dessiner_joueur(position, pas)
        turtle.update()
        afficher_message(f"Vous avez trouvé: {objet}")
        afficher_inventaire()

def gerer_porte(position_porte):
    """
    Gère l'interaction avec une porte.
    Args:
        position_porte (tuple): Position de la porte (ligne, colonne)
    Returns:
        bool: True si la porte s'ouvre, False sinon
    """
    global portes, portes_ouvertes, matrice, pas
    
    if position_porte not in portes:
        afficher_message("Cette porte est fermée.")
        return False
    
    question, reponse = portes[position_porte]
    afficher_message("Cette porte est fermée.")
    
    # Poser la question
    saisie = turtle.textinput("Question", question)
    turtle.listen()  # IMPORTANT : relance l'écoute clavier
    
    if saisie is None:
        afficher_message("Vous n'avez pas répondu. La porte reste fermée.")
        return False
    
    if saisie.strip().lower() == reponse.strip().lower():
        # Ouvrir la porte
        portes_ouvertes.add(position_porte)
        i, j = position_porte
        matrice[i][j] = 0  # Transforme la porte en case vide
        tracer_case(position_porte, COULEURS[0], pas)
        afficher_message("Bonne réponse ! La porte s'ouvre.")
        return True
    else:
        afficher_message("Mauvaise réponse. La porte reste fermée.")
        return False

# =============================================================================
# FONCTIONS DE DÉPLACEMENT (GESTION DES ÉVÉNEMENTS CLAVIER) (niveau 2)
# =============================================================================

def deplacer(mouvement):
    """
    Déplace le personnage dans la direction spécifiée.
    Args:
        mouvement (tuple): Mouvement à effectuer (dligne, dcolonne)
    """
    global matrice, position, pas, objets, portes, portes_ouvertes

    ligne, colonne = position
    dligne, dcolonne = mouvement
    new_ligne = ligne + dligne
    new_colonne = colonne + dcolonne

    # Vérification des limites
    if not (0 <= new_ligne < len(matrice) and 0 <= new_colonne < len(matrice[0])):
        afficher_message("Vous ne pouvez pas sortir du château!")
        return

    # Vérification des murs
    if matrice[new_ligne][new_colonne] == 1:
        afficher_message("Il y a un mur ici!")
        return

    # Vérification des portes fermées
    if (matrice[new_ligne][new_colonne] == 3 and 
        (new_ligne, new_colonne) not in portes_ouvertes):
        if not gerer_porte((new_ligne, new_colonne)):
            return  # La porte reste fermée, on ne peut pas avancer

    # Déplacement valide
    effacer_joueur()
    
    # Vérifier si le joueur a trouvé un objet
    if matrice[new_ligne][new_colonne] == 4 and (new_ligne, new_colonne) in objets:
        ramasser_objet((new_ligne, new_colonne))
    
    position = (new_ligne, new_colonne)
    dessiner_joueur(position, pas)
    turtle.update()
    
    # Vérifier si le joueur a atteint la sortie
    if matrice[new_ligne][new_colonne] == 2:
        afficher_message("Félicitations! Vous avez trouvé la sortie!")
        turtle.title("Victoire ! Vous avez trouvé la sortie 🎉")

def deplacer_haut():
    """Gère le déplacement vers le haut"""
    turtle.onkeypress(None, "Up")   
    deplacer((-1, 0))
    turtle.onkeypress(deplacer_haut, "Up") 

def deplacer_bas():
    """Gère le déplacement vers le bas"""
    turtle.onkeypress(None, "Down")
    deplacer((1, 0))
    turtle.onkeypress(deplacer_bas, "Down")

def deplacer_gauche():
    """Gère le déplacement vers la gauche"""
    turtle.onkeypress(None, "Left")   
    deplacer((0, -1))
    turtle.onkeypress(deplacer_gauche, "Left")  

def deplacer_droite():
    """Gère le déplacement vers la droite"""
    turtle.onkeypress(None, "Right")
    deplacer((0, 1))
    turtle.onkeypress(deplacer_droite, "Right")

# =============================================================================
# FONCTIONS UTILITAIRES
# =============================================================================

def creer_fichiers_exemple():
    """Crée les fichiers de données d'exemple s'ils n'existent pas"""
    if not os.path.exists(fichier_plan):
        with open(fichier_plan, "w") as f:
            f.write("1 1 1 1 1 1 1 1 1 1\n")
            f.write("1 0 0 0 0 0 0 0 0 1\n")
            f.write("1 0 1 1 1 1 1 1 0 1\n")
            f.write("1 0 1 0 0 0 0 1 0 1\n")
            f.write("1 0 1 0 1 1 0 1 0 1\n")
            f.write("1 0 1 0 1 4 0 1 0 1\n")
            f.write("1 0 1 0 1 1 0 1 0 1\n")
            f.write("1 0 1 0 0 0 0 1 0 1\n")
            f.write("1 0 1 1 1 1 1 1 3 1\n")  # Porte en (8, 8)
            f.write("1 0 0 0 0 0 0 0 2 1\n")  # Sortie en (9, 8)
            f.write("1 1 1 1 1 1 1 1 1 1\n")
    
    if not os.path.exists(fichier_objets):
        with open(fichier_objets, "w", encoding='utf-8') as f:
            f.write('(5, 5), "Clé en or"\n')
    
    if not os.path.exists(fichier_questions):
        with open(fichier_questions, "w", encoding='utf-8') as f:
            f.write('(8, 8), ("Capitale de la Belgique ?", "Bruxelles")\n')

def quitter():
    """Quitte le jeu"""
    turtle.bye()

# =============================================================================
# PROGRAMME PRINCIPAL
# =============================================================================
if __name__ == '__main__':
    # Configuration de la fenêtre turtle
    turtle.setup(800, 600)
    turtle.title("Escape Game - Château Mystère")
    turtle.bgcolor("white")
    turtle.tracer(0)  # Désactive l'animation automatique
    turtle.hideturtle()

    creer_fichiers_exemple()

    # Initialisation des variables globales
    matrice = lire_matrice(fichier_plan)
    objets = creer_dictionnaire_des_objets(fichier_objets)
    portes = creer_dictionnaire_des_portes(fichier_questions)
    
    if matrice:
        pas = calculer_pas(matrice)
        
        # Affichage du plan
        afficher_plan(matrice)
        
        # Dessin du joueur
        dessiner_joueur(position, pas)
        turtle.update()
        
        # Configuration des touches
        turtle.listen()
        turtle.onkeypress(deplacer_gauche, "Left")
        turtle.onkeypress(deplacer_droite, "Right")
        turtle.onkeypress(deplacer_haut, "Up")
        turtle.onkeypress(deplacer_bas, "Down")
        turtle.onkeypress(quitter, "Escape")
        
        # Message initial
        afficher_message("Utilisez les flèches pour vous déplacer")
        afficher_inventaire()
        
        turtle.mainloop()
    else:
        print("Échec du chargement du plan.")