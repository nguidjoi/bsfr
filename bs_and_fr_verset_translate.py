import json
import os
import numpy as np

import pandas as pd



def main(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            dictionary = json.load(file)
        return dictionary

titres_bibliques = [
    "Màteò", "Markò", "Lukàs", "Yòhanɛ̀ss", "Mìnsɔn mi Ɓaomâ", "Romà",
    "1 Kɔ̀rintò", "2 Kɔ̀rintò", "Gàlatìà", "Èfesò", "Fìlipìs", "Kòlosè",
    "1 Tèsàlonīkà", "2 Tèsàlonīkà", "1 Tìmòteò", "2 Tìmòteò", "Titò",
    "Fìlemòn", "Lòk Hebɛ̀r", "Yàkobòs", "1 Petrò", "2 Petrò",
    "1 Yòhanɛ̀s", "2 Yòhanɛ̀s", "3 Yòhanɛ̀s", "Yudàs", "Màsɔ̀ɔ̀là"
]

def aplatir_dictionnaire(d, parent_key='', sep='_'):
    items = {}
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        if isinstance(v, dict):
            items.update(aplatir_dictionnaire(v, new_key, sep=sep))
        else:
            items[new_key] = v
    return items

def parcourir_dictionnaires(dico1, dico2, cles=[], resultats=[]):
    for cle in dico1.keys():
        if cle in dico2:
            valeur1 = dico1[cle]
            valeur2 = dico2[cle]
            if isinstance(valeur1, dict) and isinstance(valeur2, dict):
                parcourir_dictionnaires(valeur1, valeur2, cles + [cle], resultats)
            else:
                entree = {
                    'livre': cles[0] if len(cles) > 0 else '',
                    'chapitre': cles[1] if len(cles) > 1 else '',
                    'verset': cle,
                    'texte_bassa': valeur1,
                    'texte_francais': valeur2
                }
                resultats.append(entree)
        else:
            print(f"Clé {cle}, {dico1[cle]} non trouvée dans le second dictionnaire")
    return resultats


def safe_books_to_json_file(dic,output_dir, fileName):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    json_file_path = os.path.join(output_dir, fileName)
    with open(json_file_path, 'w', encoding='utf-8') as file:
        json.dump(dic, file, ensure_ascii=False, indent=4)


# Exemple d'utilisation
if __name__ == "__main__":
    jsonBible_bs = main('/home/sga/project/nlp/bassa/contents/bible.json')
    jsonBible_fr = main('/home/sga/project/nlp/francais/contents/bible.json')

    dico_fr_titre_bs = {titres_bibliques[i]: valeur for i, (cle, valeur) in enumerate(jsonBible_fr.items())}
    dico_bs_titre_bs = {titres_bibliques[i]: valeur for i, (cle, valeur) in enumerate(jsonBible_bs.items())}

    resultats = parcourir_dictionnaires(dico_bs_titre_bs, dico_fr_titre_bs)

    safe_books_to_json_file(resultats,'/home/sga/project/nlp/contents','resultats.json')

    print('FIN')