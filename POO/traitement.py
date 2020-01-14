#!/home/lbourgea/Documents/Projets/Exome/pipeline_annotation/venv/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import logging
from datetime import datetime
from time import strftime
import re
from echantillon import *
#from individus import *
#from mere import *
#from foetus import *
#from pere import *


heure = datetime.now()
heure_vrai = heure.strftime("%d-%m-%Y_%Hh_%Mm")
logging.basicConfig(filename='log_' + heure_vrai + '.txt', filemode='w', format='%(name)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def lecture_fichier(path_data_frame):
    data = []
    logger.info("Ouverture du fichier")

    try:
        donnees = pd.read_csv(path_data_frame, sep='\t', header=0, keep_default_na=False)
        # cast Allele and Height data as float
        #tmp = donnees.columns.tolist()[6:] #TODO: optimiser car nom Allele et Height
        #donnees = donnees.astype(dict(zip(tmp, [float]*len(tmp))))
    except Exception as e:
        logger.error("Ouverture impossible", exc_info=True)
        # 1: ouverture impossible
        return 1

    logger.info("Chargement des données")
    # Check the presence of TPOS and TNEG
    if donnees[donnees["Sample Name"].str.contains("T POS") == True].shape[0] == 0:
        logger.error("Temoin positif absent", exc_info=True)
        # 2: T POS absent
        return 2
    elif donnees[donnees["Sample Name"].str.contains("T NEG") == True].shape[0] == 0:
        logger.error("Temoin negatif absent", exc_info=True)
        # 3: T NEG absent
        return 3
    # Check the presence of the father
    elif donnees.shape[0]%5 == 0 or donnees.shape[0]%4 == 0:
        logger.error("Presence ou Absence des données du pere", exc_info=True)
        iterateur = donnees["Sample Name"].nunique()
    else:
        # 4: Nombre de lignes incorrect
        logger.error("Nombre de lignes incompatible", exc_info=True)
        return 4
      
    # Get data
    date_echantillon = re.search("(\d{4}-\d{2}-\d{2})", donnees["Sample File"].values[0]).group()
    for i in range(iterateur):
        data.append([re.search("(\w-)?(\w*)", donnees["Sample Name"].values[i]).group(2), {}])

    for ligne in range(0, donnees.shape[0], iterateur): #TODO: Pourquoi -1
        for i in range(iterateur):
            data[i][1][donnees["Marker"][ligne + i]] = {}
            data[i][1][donnees["Marker"][ligne + i]]["Allele"] = getdata(donnees.loc[ligne + i], "Allele")
            data[i][1][donnees["Marker"][ligne + i]]["Hauteur"] = getdata(donnees.loc[ligne + i], "Height")
    # Deal with father data
    if iterateur == 5:
        data.insert( len(data), data.pop(2) ) 
    echantillon = Echantillon(date_echantillon, *data) #date, mere, foetus, tpos, tneg, pere = None, seuil_nbre_marqueurs=2, seuil_hauteur=1 / 3
    logger.info("Chargement des données réussi")    
    return echantillon

def getdata(line, name):
    data = []
    for key in line.keys():
        if name in key and line[key] in ['X', 'Y', '?']:
            data.append(line[key])
        elif name in key and line[key] != "":
            data.append(float(line[key]))
    return data

def concordance_ADN(echantillon):
    logger.info("Check mother sex")
    if not echantillon.mere.check_sex():
        # La mere est de sexe masculin
        return 7
    logger.info("Check father sex")
    if echantillon.pere and not echantillon.pere.check_sex():
        # Le pere est de sexe feminin
        return 8
    logger.info("Vérification de la concordance des ADNs")
    try:
        echantillon.concordance_ADN()
    except AttributeError:
        logger.info("Concordance ADN failled")

if __name__ == "__main__":
    echantillon = lecture_fichier('Cas_avec_4.txt')
    echantillon2 = lecture_fichier('Cas_avec_5.txt')
    print("Cas 4")
    val = concordance_ADN(echantillon)
    print("Cas 5")
    val2 = concordance_ADN(echantillon2)
    print(echantillon.concordance_pere_foet)
    print(echantillon.concordance_mere_foet)
    print(echantillon2.concordance_pere_foet)
    print(echantillon2.concordance_mere_foet)
    echantillon.analyse_marqueur()
    echantillon2.analyse_marqueur()

