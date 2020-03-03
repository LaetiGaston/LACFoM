# -*- coding: utf-8 -*-

import sys
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from time import strftime
import re
from echantillon import *


heure = datetime.now()
heure_vrai = heure.strftime("%d-%m-%Y_%Hh_%Mm")
logging.basicConfig(filename='log_' + heure_vrai + '.txt', filemode='w', format='%(name)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


def lecture_fichier(path_data_frame):
    data = []
    logger.info("Ouverture du fichier")

    try:
        #file_ = open(path_data_frame, "r")
        #for line in file_.readlines():
        #    print(line, line.split('\t'), len(line.split('\t')))
        #file_.close()
        donnees = pd.read_csv(path_data_frame, sep='\t', header=0, keep_default_na=False)
        # cast Allele and Height data as float
        #tmp = donnees.columns.tolist()[6:] #TODO: optimiser car nom Allele et Height
        #donnees = donnees.astype(dict(zip(tmp, [float]*len(tmp))))
    except Exception as e:
        logger.error("Ouverture impossible", exc_info=True)
        # 1: ouverture impossible
        return "Ouverture impossible.\n Vérifiez le format du fichier"

    logger.info("Chargement des données")
    # Check the presence of TPOS and TNEG
    if donnees[donnees["Sample Name"].str.contains(r'T.*POS|T\+|[Tt]?emoin( )?\+|[Tt]?emoin( )?(POS|positif)', regex=True) == True].shape[0] == 0:
        logger.error("Temoin positif absent", exc_info=True)
        # 2: T POS absent
        return "Témoin positif absent"
    elif donnees[donnees["Sample Name"].str.contains(r'T.*NEG|T\-|[Tt]?emoin( )?\-|[Tt]?emoin( )?(NEG|negatif)|BLANC|BLC|Blanc', regex=True) == True].shape[0] == 0:
        logger.error("Temoin negatif absent", exc_info=True)
        # 3: T NEG absent
        return "Témoin négatif absent"
    # Check the presence of the father
    elif donnees.shape[0]%5 == 0 or donnees.shape[0]%4 == 0:
        logger.error("Presence ou Absence des données du pere", exc_info=True)
        iterateur = donnees["Sample Name"].nunique()
    else:
        # 4: Nombre de lignes incorrect
        logger.error("Nombre de lignes incompatible", exc_info=True)
        return "Nombre de lignes incorrect"

    # Normalisation TPOS and TNEG name
    donnees.loc[donnees["Sample Name"].str.contains(r'T.*POS|T\+|[Tt]?emoin( )?\+|[Tt]?emoin( )?(POS|positif)', regex=True) == True, "Sample Name"] = "TPOS"
    donnees.loc[donnees["Sample Name"].str.contains(r'T.*NEG|T\-|[Tt]?emoin( )?\-|[Tt]?emoin( )?(NEG|negatif)|BLANC|BLC|Blanc', regex=True)== True, "Sample Name"] = "TNEG"

    # Get sample names to associate
    #allsamples = pd.unique(df["Sample Name"]).tolist()

    # Get data
    date_echantillon = re.search("(\d{4}-\d{2}-\d{2})", donnees["Sample File"].values[0]).group()
    for i in range(iterateur):
        data.append([re.search("(\w-)?(\w*)", donnees["Sample Name"].values[i]).group(2), {}])

    for ligne in range(0, donnees.shape[0], iterateur): #TODO: Pourquoi -1
        for i in range(iterateur):
            data[i][1][donnees["Marker"][ligne + i]] = {}
            data[i][1][donnees["Marker"][ligne + i]]["Allele"] = getdata(donnees.loc[ligne + i], "Allele")
            data[i][1][donnees["Marker"][ligne + i]]["Hauteur"] = getdata(donnees.loc[ligne + i], "Height")
            if len(data[i][1][donnees["Marker"][ligne + i]]["Allele"]) != len(data[i][1][donnees["Marker"][ligne + i]]["Hauteur"]):
                # Le marqueur "dans le log" n'a pas le meme nombre d'alleles que de hauteurs
                logger.info(donnees["Marker"][ligne + i])
                return "                      Le marqueur "+donnees["Marker"][ligne + i]+" \n n'a pas le même nombre d'allèles que de hauteurs"
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
        return "Erreur: la mère est de sexe masculin "
    logger.info("Check father sex")
    if echantillon.pere and not echantillon.pere.check_sex():
        # Le pere est de sexe feminin
        return "Erreur: le père est de sexe féminin "
    logger.info("Vérification de la concordance des ADNs")
    try:
        echantillon.concordance_ADN()
    except AttributeError:
        logger.info("Concordance ADN failed")

if __name__ == "__main__":
    file_path = sys.argv[1]
    print(file_path)
    echantillon = lecture_fichier(file_path)
    # Check temoins
    checktpos = echantillon.tpos.check()
    checktneg = echantillon.tneg.check()
    if checktpos == []:
        print("Temoin positif : validé")
    else:
        print("Témoin positif : NON VALIDE", checktpos)
    if checktneg == []:
        print("Temoin négatif : validé")
    else:
        print("Témoin négatif : NON VALIDE", checktneg)
    # Check concordance
    val = concordance_ADN(echantillon)
    print(echantillon.concordance_pere_foet)
    print(echantillon.concordance_mere_foet)
    # Do analyse
    echantillon.analyse_marqueur()
    for indice in range (len(echantillon.get_resultats()['Marqueur'])):
        print(echantillon.get_resultats()['Marqueur'][indice], ": ", echantillon.get_resultats()['Détails M/F'][indice])
    print(echantillon.get_contamine())
    print(echantillon.get_conclusion())