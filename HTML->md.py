import os
from markitdown import MarkItDown
from bs4 import BeautifulSoup , Comment
import chardet
import re
from lxml import etree, html
from html import unescape


def converti (source_file) :
    md = MarkItDown()
    result = md.convert(source_file)
    # Générer le chemin de sortie avec extension .md
    output_file = os.path.splitext(source_file)[0] + ".md"
    # Sauvegarder au même emplacement
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result.text_content)
    print(f"Fichier Markdown sauvegardé : {output_file}")

romains = {
    "I": 1, "II": 2, "III": 3, "IV": 4,
    "V": 5, "VI": 6, "VII": 7, "VIII": 8
}

def tri_personnalise(nom):
    """Combiner tri numérique et traitement des chiffres romains."""
    # Extraire les numéros romains
    nom_sans_espace = nom.replace(" ", "")
    numero_roman = romains.get(nom_sans_espace.split("_")[-1].replace(".html", ""), float('inf'))
    # Extraire les autres parties numériques
    numeric_parts = [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', nom)]
    return numeric_parts, numero_roman


def pre (lines,new_soup) :
    for line in lines:
        line = line.strip()  # Nettoyer les espaces en début/fin de ligne
        if not line:
            continue  # Ignorer les lignes vides
        if line.isupper():  # Si la ligne est un titre (tout en majuscules)
            if line.startswith('LIVRE'):
                new_tag = new_soup.new_tag("h1")
            else:
                new_tag = new_soup.new_tag("h2")
            new_tag.string = line
            new_soup.append(new_tag)
        elif line.startswith('Can'):  # Si la ligne commence par "Can"
            # Si la ligne contient un "§", séparer la partie Can de la partie §
            if '§' in line:
                # Séparer avant et après le "§"
                can_part, section_part = line.split('§', 1)

                # Ajouter la partie "Can" dans un <h3>
                can_tag = new_soup.new_tag("h3")
                can_tag.string = can_part.strip()
                new_soup.append(can_tag)

                # Traiter la partie après "§" et séparer avant et après le point
                section_part = section_part.strip()
                split_section = section_part.split(". ", 1)  # Séparer avant et après le point
                if len(split_section) > 1:
                    reference = "§ " + split_section[0] + ". "  # La référence canonique avec le § et le numéro
                    rest_of_line = split_section[1]  # Le texte restant après le point

                    # Ajouter la référence canonique dans un <h4>
                    ref_tag = new_soup.new_tag("h4")
                    ref_tag.string = reference
                    new_soup.append(ref_tag)

                    # Ajouter le reste du texte dans un <p>
                    para_tag = new_soup.new_tag("p")
                    para_tag.string = rest_of_line
                    new_soup.append(para_tag)
                else:
                    # Si la ligne ne contient pas de texte après le point
                    ref_tag = new_soup.new_tag("h4")
                    ref_tag.string = "§ " + split_section[0]

            else:
                split_line = line.split(" - ", 1)  # Sépare avant et après le tiret
                if len(split_line) > 1:
                    reference = split_line[0] + " - "  # La référence (avant le tiret)
                    rest_of_line = split_line[1]  # Le texte restant après le tiret

                    # Ajouter la référence canonique dans <h3>
                    ref_tag = new_soup.new_tag("h3")
                    ref_tag.string = reference
                    new_soup.append(ref_tag)

                    # Ajouter le reste du texte dans un <p>
                    para_tag = new_soup.new_tag("p")
                    para_tag.string = rest_of_line
                    new_soup.append(para_tag)
                else:
                    new_tag = new_soup.new_tag("h3")
                    new_tag.string = line
                    new_soup.append(new_tag)
        elif '§' in line:  # Si la ligne contient un "§" mais ne commence pas par "Can"
            # Séparer avant et après le premier "§"
            split_line = line.split(". ", 1)
            if len(split_line) > 1:
                reference = split_line[0] + ". "  # La référence (avant le tiret)
                rest_of_line = split_line[1]  # Le texte restant après le tiret

                # Ajouter la référence canonique dans <h3>
                ref_tag = new_soup.new_tag("h4")
                ref_tag.string = reference
                new_soup.append(ref_tag)

                # Ajouter le reste du texte dans un <p>
                para_tag = new_soup.new_tag("p")
                para_tag.string = rest_of_line
                new_soup.append(para_tag)
        else:  # Sinon, c'est un paragraphe
            new_tag = new_soup.new_tag("p")
            new_tag.string = line
            new_soup.append(new_tag)

    soup = new_soup

    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        suivant = tag.find_next()
        while suivant and suivant.name == tag.name:
            # Concaténer le texte de la balise suivante dans la balise actuelle
            tag.string = (tag.string or '') + ' ' + (suivant.get_text() or '')
            # Supprimer la balise suivante
            suivant.decompose()
            suivant = tag.find_next()

    for tag in soup.find_all('p'):
        suivant = tag.find_next_sibling()
        while suivant and suivant.name == 'p':
            # Fusionner le contenu
            tag.string = (tag.get_text(strip=True) + ' ' + suivant.get_text(strip=True)).strip()
            # Supprimer la balise suivante
            suivant.decompose()
            suivant = tag.find_next_sibling()
    return soup

def trouver_fichiers_html(racine):
    """ Recherche tous les fichiers HTML dans le dossier racine et ses sous-dossiers,
    les nettoie et les concatène en un seul fichier `concatene.html` dans le dossier racine puis le converti"""
    contenu_total = ""
    for chemin, sous_dossiers, fichiers in os.walk(racine):
        sous_dossiers.sort(key = tri_personnalise)
        fichiers.sort(key = tri_personnalise)
        print("Fichiers triés :", fichiers)
        for fichier in fichiers:
            if fichier.endswith('.html') :
                chemin_complet = os.path.join(chemin, fichier)
                contenu_total+= nettoyer_html(chemin_complet)
                #chemin_nettoye = os.path.splitext(chemin_complet)[0] + "_nettoye.html"

    contenu_total = "<html>\n<body>" + contenu_total + "</body>\n</html>"
    with open(racine + "/concatene.html", 'w', encoding='utf-8') as f:
        f.write(contenu_total)

    converti(racine + "/concatene.html")

def trouver_dossier_html(racine):
    """ Parcourt chaque dossier dans le dossier racine, cherche les fichiers HTML qu'il contient,
    les nettoie et les concatène en un fichier `concatene.html` dans chaque dossier, et les convertis. """
    for chemin, sous_dossiers, fichiers in os.walk(racine):
        contenu_total = ""
        sous_dossiers.sort(key = tri_personnalise)
        fichiers.sort(key = tri_personnalise)
        print("Fichiers triés :", fichiers)
        for fichier in fichiers:

            if fichier.endswith('.html') :
                chemin_complet = os.path.join(chemin, fichier)
                contenu_total+= nettoyer_html(chemin_complet)
                #chemin_nettoye = os.path.splitext(chemin_complet)[0] + "_nettoye.html"
        contenu_total = "<html>\n<body>" + contenu_total + "</body>\n</html>"
        #print(racine+"/"+chemin)
        #print("dossier : ",chemin)
        with open(chemin + "/concatene.html", 'w', encoding='utf-8') as f:
            f.write(contenu_total)

        converti(chemin + "/concatene.html")

italian_keywords = [
    "Initium", "secundum", "In principio", "Verbum", "Deus", "quæ",
    "venientem", "mundum", "In diebus illis", "Venerunt", "mulieres", "Salomonem",
    "obsecro", "hæc", "cubiculo", "peperi", "simul", "nullusque"
]

def nettoyer_html(fichier_entree):
    """Fait toutes les opérations pour nettoyer les fichiers html"""
    with open(fichier_entree, 'r', encoding='windows-1252') as f:
        contenu = f.read()

    contenu = unescape(contenu)
    contenu = re.sub(r'\u2019', "'", contenu)
    contenu = re.sub(r'\u00A0', ' ', contenu)
    parser = html.HTMLParser(recover=True)
    tree = html.fromstring(contenu, parser=parser)

    contenu = html.tostring(tree, encoding="unicode", pretty_print=True)

    soup = BeautifulSoup(contenu, 'html.parser')

    for span in soup.find_all('span', class_='Apple-converted-space'):
        span.decompose()

    for span in soup.find_all('p',class_ ='MsoNormal'):
        text = span.get_text(strip=True)
        a_tag = span.find('a', href="#_top")
        if not text :
            span.decompose()
        elif span.find('span', lang=True):
            span.decompose()
        elif a_tag:
            span.decompose()
        elif len(text) <= 20 and (text.isupper() or text.isdigit()):
            if text.isupper():
                new_tag = soup.new_tag('h3')
            else :
                new_tag = soup.new_tag('h4')
            new_tag.string = text
            span.replace_with(new_tag)

        else:
            pass

    for span in soup.find_all('span', lang=True):
        span.decompose()

    # Identifier et transformer les titres
    for span in soup.find_all('span', class_=lambda x: x and x.startswith('font')):
        text = span.get_text(strip=True)
        # Vérifier si c'est un titre (exemple : court et tout en majuscules ou chiffres romains)
        if len(text) <= 40 and text.isupper():
            # Remplacer par une balise <h3> ou <h2> selon vos besoins
            new_tag = soup.new_tag('h2')
            new_tag.string = text
            span.replace_with(new_tag)
        else:
            # Laisser tel quel si ce n'est pas un titre
            pass

    for p in soup.find_all('p', class_='MsoNormal'):
        text = p.get_text(strip=True)

        # Si le paragraphe contient des mots italiens/latins, le supprimer
        if any(keyword in text for keyword in italian_keywords) or re.search(r'\b(in|ad)\b', text, re.IGNORECASE):
            p.decompose()

    # Supprimer les balises <style>, <script>, et les commentaires
    for tag in soup(['table', 'tr', 'td','span','head','meta','div','body','big','font','strong','spanstyle']):
        tag.unwrap()  # Retire la balise mais conserve le contenu

    for tag in soup(['style', 'script', 'img','nobr','link','xml']):
        tag.decompose()
    for tag in soup.find_all():
        if tag.name and tag.name.startswith(('o:', 'st1')):
            tag.decompose()

    for tag in soup.find_all('p'):
        text = tag.get_text(strip=True)

        align_value = tag.attrs.get('align')  # Accéder à l'attribut `align` en minuscules
        if align_value  :
            align_value = align_value.upper()  # Convertir en majuscules pour comparaison
            if align_value.startswith("JUSTIFY") and text.startswith(("I.", "II.", "III.", "IV.", "V.")):
                new_tag = soup.new_tag('h3')
                new_tag.string = text
                tag.replace_with(new_tag)
            elif align_value.startswith("CENTER") and tag.get_text(strip=True):
                new_tag = soup.new_tag('h2')
                new_tag.string = text
                tag.replace_with(new_tag)

    for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    for tag in soup.find_all(True):
        tag.attrs = {key: value for key, value in tag.attrs.items() if key in ['href', 'src', 'alt']}



    for tag in soup.find_all('p'):
        if tag.find('a') and len(tag.contents) == 1:  # Vérifie si <p> contient uniquement <a>
            tag.decompose()


    for tag in soup('a'):
        tag.unwrap()  # Retire la balise mais conserve le contenu


    for tag in soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
        suivant = tag.find_next()
        while suivant and suivant.name == tag.name:
            # Concaténer le texte de la balise suivante dans la balise actuelle
            tag.string = (tag.string or '') + ' ' + (suivant.get_text() or '')
            # Supprimer la balise suivante
            suivant.decompose()
            suivant = tag.find_next()


#retire le contenu entre 2 balises h1 pareilles
    textes_h1 = set()
    for tag in soup.find_all('h1'):
        texte = re.sub(r'\s+', ' ', tag.get_text().strip())
        if texte in textes_h1:  # Si un duplicata est trouvé
            precedent = tag.find_previous_sibling()  # Trouver l'élément précédent
            print(precedent)
            while precedent and precedent.name != 'h1':  # Supprimer tout entre les deux
                a_supprimer = precedent
                precedent = a_supprimer.find_previous_sibling()
                a_supprimer.decompose()
                parent = tag.parent
                for sibling in list(parent.children):
                    if sibling.name != 'h1' and sibling.string and sibling.string.strip() == "":
                        sibling.extract()

            tag.decompose()
        else:
            textes_h1.add(texte)


    if soup.title:
        soup.title.decompose()
    #    soup.title.name = "h2"

    for tag in soup.find_all('b'):
        if tag.find(('h2','h3','h4','h1')) and len([child for child in tag.contents if not str(child).strip() == ""]) == 1:
            tag.unwrap()

    pre_tag = soup.find('pre')
    if pre_tag:
        pre_content = pre_tag.get_text()

        # Diviser le texte brut en lignes
        lines = pre_content.splitlines()

        new_soup = BeautifulSoup("", "html.parser")
        soup = pre(lines, new_soup)

    contenu = str(soup)
    contenu = re.sub(r'=', '', contenu)

    contenu = re.sub(r'<\?if .*?\?>*', '', contenu)
    contenu = re.sub(r'<\?endif\?>*', '', contenu)


    contenu = re.sub(r'<html>', '', contenu)
    contenu = re.sub(r'</html>', '', contenu)


    fichier_sortie = os.path.splitext(fichier_entree)[0] + "_nettoye.html"

    print("fichier nettoyé : ", fichier_sortie )
    return contenu

dossier_racine = "/Users/nathan/Downloads/site_biblio/bibliotheque/bibliotheque/vorbourg"
#nettoyer_html(dossier_racine+'/treizieme.html')

trouver_fichiers_html(dossier_racine)
#trouver_dossier_html(dossier_racine)