import os
import re
import json
from nltk.tokenize import word_tokenize

titres_bibliques_bs = [
    "Màteò", "Markò", "Lukàs", "Yòhanɛ̀ss", "Mìnsɔn mi Ɓaomâ", "Romà",
    "1 Kɔ̀rintò", "2 Kɔ̀rintò", "Gàlatìà", "Èfesò", "Fìlipìs", "Kòlosè",
    "1 Tèsàlonīkà", "2 Tèsàlonīkà", "1 Tìmòteò", "2 Tìmòteò", "Titò",
    "Fìlemòn", "Lòk Hebɛ̀r", "Yàkobòs", "1 Petrò", "2 Petrò",
    "1 Yòhanɛ̀s", "2 Yòhanɛ̀s", "3 Yòhanɛ̀s", "Yudàs", "Màsɔ̀ɔ̀là"
]

titres_bibliques_fr =  [
    "MATTHIEU",
    "MARC",
    "LUC",
    "JEAN",
    "ACTES",
    "ROMAINS",
    "1 CORINTHIENS",
    "2 CORINTHIENS",
    "GALATES",
    "EPHESIENS",
    "PHILIPPIENS",
    "COLOSSIENS",
    "1 THESSALONICIEN",
    "2 THESSALONICIEN",
    "1 TIMOTHEE",
    "2 TIMOTHEE",
    "TITE",
    "PHILEMON",
    "HEBREUX",
    "JACQUES",
    "1 PIERRE",
    "2 PIERRE",
    "1 JEAN",
    "2 JEAN",
    "3 JEAN",
    "JUDE",
    "RÉVÉLATION"
]

#pattern_verset_const = re.compile(r'(\s*)(\d+)\s*')
pattern_verset_bs = re.compile(r'(\d+)\s*')
pattern_verset_fr =  re.compile(r'\s*(\d+)\.(\d+)\s*')

pattern_verset = pattern_verset_bs
titres_bibliques = titres_bibliques_bs
pattern_verset_const = pattern_verset_fr
title_pattern = r'\b(' + '|'.join(titres_bibliques) + r')\s+(\d+)'

def extraire_titres_chapitres_textes(texte, titres):
    # Convertir le texte en minuscules pour une comparaison insensible à la casse
    texte = texte.lower()

    # Créer un dictionnaire pour stocker les titres, chapitres et textes associés
    titres_chapitres_textes = {}

    # Vérifier chaque titre dans la liste des titres
    for index, titre in enumerate(titres):

        # Convertir le titre en minuscules pour la comparaison
        titre_lower = titre.lower()

        # Créer un motif regex pour trouver le titre suivi d'un numéro de chapitre
        motif = re.compile(rf'\b{titre_lower}\s*(\d+)\b')

        # Chercher tous les chapitres associés à ce titre
        chapitres = re.findall(motif, texte)

        if chapitres:
            # Si des chapitres sont trouvés, initialiser le dictionnaire pour ce titre
            titres_chapitres_textes[titre] = {}
            for chapitre in chapitres:
                titre_and_next = titre_lower

                if chapitre == chapitres[- 1] and index < len(titres)-1:
                    titre_and_next = titres[index + 1].lower()

                # Créer un motif pour extraire le texte du chapitre
                texte_chapitre_motif = re.compile(rf'\b{titre_lower}{chapitre}(.*?)(?=\b{titre_and_next}\d+|$)', re.DOTALL)
                #
                texte_chapitre = texte_chapitre_motif.search(texte)

                if texte_chapitre:
                    texte_chapitre_entier = texte_chapitre.group(1).strip()
                    texte_chapitre_entier = re.sub(pattern_verset_const, r'\2 ', texte_chapitre_entier)

                    clean_chapter=  (texte_chapitre_entier.replace('\n', ' '))
                                     #.replace('\r', ' ').replace('  ', ' '))

                    verset = extraire_versets_complexes(clean_chapter, pattern_verset_bs)

                    # Ajouter le texte du chapitre au dictionnaire
                    titres_chapitres_textes[titre][chapitre] =   verset

    return titres_chapitres_textes

def extraire_versets_complexes(texte,pattern_verset):

    versets = {}
    verset_en_cours = None
    texte_en_cours = ""

    # Split le texte en segments basés sur la localisation des nombres qui marquent les nouveaux versets
    segments = pattern_verset.split(texte)

    # Le premier élément ne contient généralement pas de texte utile car il précède le premier numéro de verset
    if len(segments) > 1:
        for i in range(1, len(segments), 2):
            numero_verset = segments[i].strip()
            texte_segment = segments[i + 1].strip()

            if verset_en_cours:
                versets[verset_en_cours] = " " + texte_en_cours.strip()

            verset_en_cours = numero_verset
            texte_en_cours = texte_segment

    # Assurez-vous de sauvegarder le dernier verset traité
    if verset_en_cours and texte_en_cours:
        versets[verset_en_cours] = texte_en_cours.strip()

    return versets

def tokenize(texte):

    tokens = word_tokenize(texte)
    cleaned_tokens = [re.sub(r'[^\w\s]', '', token) for token in tokens if re.sub(r'[^\w\s]', '', token)]
    return cleaned_tokens

def supprimer_caracteres_speciaux(texte):

    # Remplacer les sauts de ligne par un espace (ou supprimer en utilisant '')
    texte_sans_saut_de_ligne = texte.replace('\n', ' ')

    # Supprimer les espaces multiples résultant de la suppression
    texte_sans_espaces_multiples = re.sub(r'\s+', ' ', texte_sans_saut_de_ligne).strip()

    # Découper le texte en lignes
    texte_clean = re.sub(title_pattern, r'\1\2*', texte_sans_espaces_multiples)

    return texte_clean

def lire_fichier_et_extraire_structure(nom_fichier):
    # Lire le contenu du fichier
    with open(nom_fichier, 'r', encoding='utf-8') as fichier:
        texte = fichier.read()
        texte = supprimer_caracteres_speciaux(texte)
        structure_bible = extraire_titres_chapitres_textes(texte, titres_bibliques)
    return structure_bible

def safe_books_to_json_file(books,output_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    json_file_path = os.path.join(output_dir, 'bible.json')
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(books, file, ensure_ascii=False, indent=4)


# Nom du fichier contenant le texte en bloc
#nom_fichier = '/home/sga/project/nlp/francais/bible.txt'
#output_dir = '/home/sga/project/nlp/francais/contents'

# Nom du fichier contenant le texte en bloc
nom_fichier = '/home/sga/project/nlp/bassa/bible_raw'
output_dir = '/home/sga/project/nlp/bassa/contents'

# Lire le fichier et extraire la structure
bible_bs_json = lire_fichier_et_extraire_structure(nom_fichier)
safe_books_to_json_file(bible_bs_json,output_dir)

