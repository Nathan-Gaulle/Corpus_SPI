import os
import shutil
import re


def supprimer_fichiers_non_html_pdf(racine):
    for chemin, sous_dossiers, fichiers in os.walk(racine):
        for fichier in fichiers:
            if fichier.startswith('concatene'):
                chemin_complet = os.path.join(chemin, fichier)
                print(f"Suppression du fichier : {chemin_complet}")
                os.remove(chemin_complet)  # Supprime le fichier
            elif not fichier.endswith(('.html', '.htm', '.pdf')):  # Garde seulement HTML et PDF
                chemin_complet = os.path.join(chemin, fichier)
                print(f"Suppression du fichier : {chemin_complet}")
                os.remove(chemin_complet)  # Supprime le fichier
            """elif fichier.startswith('index'):
                chemin_complet = os.path.join(chemin, fichier)
                print(f"Suppression du fichier : {chemin_complet}")
                os.remove(chemin_complet)  # Supprime le fichier
                """




def supprimer_dossiers_vti(racine):
    for chemin, sous_dossiers, fichiers in os.walk(racine, topdown=False):
        for dossier in sous_dossiers:
            chemin_dossier = os.path.join(chemin, dossier)
            if dossier.startswith("_vti_"):  # Vérifie si le dossier commence par "_vti_"
                print(f"Suppression du dossier _vti_ : {chemin_dossier}")
                shutil.rmtree(chemin_dossier)  # Supprime le dossier et son contenu
            elif not os.listdir(chemin_dossier):  # Vérifie si le dossier est vide
                print(f"Suppression du dossier vide : {chemin_dossier}")
                os.rmdir(chemin_dossier)  # Supprime le dossier vide

correspondance = {
    "premier": 1, "deuxieme": 2, "troisieme": 3, "quatrieme": 4,
    "cinquieme": 5, "sixieme": 6, "septieme": 7, "huitieme": 8,
    "neuvieme": 9, "dixieme": 10, "onzieme": 11, "douzieme": 12,
    "treizieme": 13, "quatorzieme": 14, "quinzieme": 15, "seizieme": 16,
    "dixseptieme": 17, "dixhuitieme": 18, "dixneuvieme": 19, "vingtieme": 20,
    "vingtetunieme": 21, "vingtdeuxieme": 22, "vingttroisieme": 23,
    "vingtquatrieme": 24, "vingtcinquieme": 25, "vingtsixieme": 26,
    "vingtseptieme": 27, "vingthuitieme": 28, "vingtneuvieme": 29,
    "trenttieme": 30
}


def convertir_en_nombre(nom):
    return correspondance.get(nom, -1)



def renommer_htm_en_html(racine):
    for chemin, sous_dossiers, fichiers in os.walk(racine):
        for fichier in fichiers:
            if fichier.endswith("_nettoye.html"):
                chemin_dossier = os.path.join(chemin, fichier)
                print(f"Suppression du fichier : {chemin_dossier}")
                os.remove(chemin_dossier)
            else :

                if fichier.endswith('.htm'):  # Si le fichier a l'extension .htm
                    chemin_complet = os.path.join(chemin, fichier)
                    nouveau_chemin = chemin_complet + "l"  # Ajoute un "l" à la fin pour .html
                    os.rename(chemin_complet, nouveau_chemin)
                    chemin_complet = nouveau_chemin
                    fichier += "l"
                    print(f"Renommé : {chemin_complet} -> {nouveau_chemin}")
                fichier_nombre = convertir_en_nombre(os.path.splitext(fichier)[0])
                if fichier_nombre != -1 :
                    fichier_nombre = "/"+(str(fichier_nombre) + ".html")
                    chemin_complet = os.path.join(chemin, fichier)
                    nouveau_chemin = chemin + fichier_nombre
                    print (chemin_complet, nouveau_chemin)
                    os.rename(chemin_complet, nouveau_chemin)



def deplacer_et_renommer_md(racine, destination):
    for chemin, sous_dossiers, fichiers in os.walk(racine):
        for fichier in fichiers:
            if fichier.endswith(".md"):
                chemin_fichier_source = os.path.join(chemin, fichier)
                dossier_parent = os.path.basename(chemin)
                nouveau_nom_fichier = f"{dossier_parent}.md"
                chemin_relatif = os.path.relpath(chemin, racine)
                dossier_parent_destination = os.path.join(destination, os.path.dirname(chemin_relatif))
                os.makedirs(dossier_parent_destination, exist_ok=True)
                chemin_fichier_destination = os.path.join(dossier_parent_destination, nouveau_nom_fichier)
                shutil.copy2(chemin_fichier_source, chemin_fichier_destination)
                try:
                    os.rmdir(dossier_parent_destination)
                except OSError:
                    print(f"Le dossier {dossier_parent_destination} n'est pas vide et n'a pas été supprimé.")

racine = "/Users/nathan/Downloads/site_biblio"
destination = "/Users/nathan/Downloads/bibliotheque_md copy"
deplacer_et_renommer_md(racine, destination)

dossier_racine = "/Users/nathan/Downloads/site_biblio/bibliotheque/bibliotheque/voragine"
#dossier_racine = "/Users/nathan/Downloads/biliotheque_md"