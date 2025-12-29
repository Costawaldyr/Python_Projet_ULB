#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from random import randint, seed

def lire_carte(fichier: str) -> dict :
    """
    Lit le fichier carte.txt et retourne un dictionnaire avec les données
    """
    donnees = {'taile':0 ,'montres':{}}
    try:
        #?ouvrir le fichier
        # file = open(fichier, 'rb')
        # row = file.readline()
        # file.close()

        with open (fichier, 'r') as file:
            rows = file.readline()

    except:
        print("Erreur avec le fichier carte.txt")
        return None
    return donnees

def grille_string(grille) -> str :
    """Initialise une grille vide de taille NxN"""
    pass

def afficher_grille(grille, vie: int, tresors_restants: int) -> None :
    """Affiche la grille et les informations du joueur"""
    pass

def  deplacer_personnage(direction, position_personnage, grille, vie) -> tuple :
    """Vérifie si le déplacement est possible"""
    pass


if __name__ == '__main__':
    seed(10)
    case_vide = "*"
    jouer = "P"
    tresor = "T"
    soin ="+"
    monstre = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
    montres = tuple("ABCDEFGHIJ") 

    print("### Nouvelle partie inittiée ! ###")
    print("Bienvenue dans l'exploration de Donjon !")

    niveau = -1
    while niveau < 0 or niveau > 2:
        try:
            niveau = int(input("Choisissez la difficulté (0: Facile, 1: Moyen, 2: Difficile) : "))
            if niveau < 0 or niveau > 2:
                print("Choix invalide. Entrez 0, 1 ou 2.")
        except:
            print("Veuillez entrer un nombre valide.")

    difficulte = niveau
    print("Difficulté choisie :", difficulte)


    