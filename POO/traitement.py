import pandas as pd
import numpy as np
import logging
from datetime import datetime
from time import strftime
import re
from echantillon import *
from individus import *
from mere import *
from foetus import *
from pere import *


heure = datetime.now()
heure_vrai = heure.strftime("%d-%m-%Y_%Hh_%Mm")
logging.basicConfig(filename='log_' + heure_vrai + '.txt', filemode='w', format='%(name)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)

def lecture_fichier(path_data_frame):
    donnees_mere = []
    donnees_foetus = []
    donnees_pere = []
    donnees_pos = []
    donnees_neg = []
    logger.info("Ouverture du fichier")
    try:
        donnees = pd.read_csv(path_data_frame, sep='\t', header=0, keep_default_na=False)
        # cast Allele and Height data as float
        tmp = donnees.columns.tolist()[3:]: #TODO: optimiser car nom Allele et Height
        donnees = donnees.astype(dict(tmp, [float]*len(tmp)))
    except Exception as e:
        logger.error("Ouverture impossible", exc_info=True)
        # 1: ouverture impossible
        return 1

    logger.info("Chargement des données")
    try:
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
        if donnees.shape[0]%4 == 0:
            logger.error("Absence des données du pere", exc_info=True)
            iterateur = 4
            donnees_pere = None

        elif donnees.shape[0]%5 == 0:
            logger.error("Presence des données du pere", exc_info=True)
            iterateur = 5
        else:
            # 4: Nombre de ligne incorrect
            logger.error("Nombre de lignes incompatible", exc_info=True)
            return 4
        
        # Get data
        num_pere = re.search("(\w-)?(\w*)", donnees["Sample Name"].values[2]).group(2)
        date_echantillon = re.search("(\d{4}-\d{2}-\d{2})", donnees["Sample File"].values[0]).group()
        num_mere = re.search("(\w-)?(\w*)", donnees["Sample Name"].values[1]).group(2)
        for ligne in range(0, donnees.shape[0] - 1, iterateur): #TODO: Pourquoi -1
            # Mere
            donnees_mere[donnees["Marker"][ligne]]["Allele"] = getdata(donnees[ligne], "Allele")
            donnees_mere[donnees["Marker"][ligne]]["Hauteur"] = getdata(donnees[ligne], "Height")
            # Foetus
            donnees_foetus[donnees["Marker"][ligne]]["Allele"] = getdata(donnees[ligne], "Allele")
            donnees_foetus[donnees["Marker"][ligne]]["Hauteur"] = getdata(donnees[ligne], "Height")
            # Pere
            if iterateur == 5:
                donnees_pere[donnees["Marker"][ligne]]["Allele"] = getdata(donnees[ligne], "Allele")
                donnees_pere[donnees["Marker"][ligne]]["Hauteur"] = getdata(donnees[ligne], "Height")
            # Tpos
            donnees_pos[donnees["Marker"][ligne]]["Allele"] = getdata(donnees[ligne], "Allele")
            donnees_pos[donnees["Marker"][ligne]]["Hauteur"] = getdata(donnees[ligne], "Height")
            # Tneg
            donnees_neg[donnees["Marker"][ligne]]["Allele"] = getdata(donnees[ligne], "Allele")
            donnees_neg[donnees["Marker"][ligne]]["Hauteur"] = getdata(donnees[ligne], "Height")

        echantillon_f = Echantillon(date_echantillon, donnees_mere, donnees_foetus, donnees_pos, donnees_neg, donnees_pere) #date, mere, foetus, tpos, tneg, pere = None, seuil_nbre_marqueurs=2, seuil_hauteur=1 / 3

    except Exception as e:
        logger.error("Chargement données impossible", exc_info=True)
        return 5
    return echantillon_f

    #MODULO A ADAPTER
    def str_to_float(dataframe, modulo):
        try:
            logger.info("Homogénéisation des données")
            for i in range(1,4):
                if modulo != 0:
                    dataframe['Allele ' + str(i)][2:] = dataframe['Allele ' + str(i)][2:].astype(float)
                    dataframe['Height ' + str(i)] = dataframe['Height ' + str(i)].astype(float)
                else:
                    dataframe['Allele ' + str(i)][3:] = dataframe['Allele ' + str(i)][3:].astype(float)
                    dataframe['Height ' + str(i)] = dataframe['Height ' + str(i)].astype(float)
            return dataframe
        except Exception as e:
            logger.error("Homogénéisation impossible", exc_info=True)

    def nan_cleaner(liste, val):
        if val != 0.0:
            liste.append(val)
        return liste
    logger.info("Ouverture du fichier")
    try:
        donnees_na = pd.read_csv(path_data_frame, sep='\t', header=0)
        donnees_na_filled = donnees_na.fillna(0)
        donnees = str_to_float(donnees_na_filled,len(donnees_na_filled.Marker.values)%3)
    except Exception as e:
        logger.error("Ouverture impossible", exc_info=True)
    
    logger.info("Chargement des données")
    try:
        date_echantillon = re.search("(\d{4}-\d{2}-\d{2})", donnees.loc[0]["Sample File"]).group()
        ID_echantillon = re.search("\w-([\w,\W]*)", donnees.loc[0]["Sample Name"]).group(1)
        mere = {}
        foetus = {}
        pere = {}
        ID_mere = re.search("\w-(\w*)", donnees.loc[0]["Sample Name"]).group(1)
        ID_foetus = re.search("\w-(\w*)", donnees.loc[1]["Sample Name"]).group(1)

        if len(donnees.Marker.values)%3 != 0: #changer ici le modulo et les indices si ils changent
            for indice_taille in range(0,len(donnees.Marker.values),2):
                mere[donnees.loc[indice_taille].Marker] = {'Allele' : nan_cleaner([],donnees.loc[indice_taille]['Allele 1']) +
                nan_cleaner([],donnees.loc[indice_taille]['Allele 2']) +
                nan_cleaner([],donnees.loc[indice_taille]['Allele 3']),
                'Hauteur': nan_cleaner([],donnees.loc[indice_taille]['Height 1']) +
                nan_cleaner([],donnees.loc[indice_taille]['Height 2']) +
                nan_cleaner([],donnees.loc[indice_taille]['Height 3'])}

                foetus[donnees.loc[indice_taille+1].Marker] = {'Allele' : nan_cleaner([],donnees.loc[indice_taille+1]['Allele 1']) +
                nan_cleaner([],donnees.loc[indice_taille+1]['Allele 2']) +
                nan_cleaner([],donnees.loc[indice_taille+1]['Allele 3']),
                'Hauteur': nan_cleaner([],donnees.loc[indice_taille+1]['Height 1']) +
                nan_cleaner([],donnees.loc[indice_taille+1]['Height 2']) +
                nan_cleaner([],donnees.loc[indice_taille+1]['Height 3'])}
        else:
            ID_pere = re.search("\w-(\w*)", donnees.loc[2]["Sample Name"]).group(1)
            for indice_taille in range(0,len(donnees.Marker.values),3):
                    mere[donnees.loc[indice_taille].Marker] = {'Allele' : nan_cleaner([],donnees.loc[indice_taille]['Allele 1']) +
                    nan_cleaner([],donnees.loc[indice_taille]['Allele 2']) +
                    nan_cleaner([],donnees.loc[indice_taille]['Allele 3']),
                    'Hauteur': nan_cleaner([],donnees.loc[indice_taille]['Height 1']) +
                    nan_cleaner([],donnees.loc[indice_taille]['Height 2']) +
                    nan_cleaner([],donnees.loc[indice_taille]['Height 3'])}

                    foetus[donnees.loc[indice_taille+1].Marker] = {'Allele' : nan_cleaner([],donnees.loc[indice_taille+1]['Allele 1']) +
                    nan_cleaner([],donnees.loc[indice_taille+1]['Allele 2']) +
                    nan_cleaner([],donnees.loc[indice_taille+1]['Allele 3']),
                    'Hauteur': nan_cleaner([],donnees.loc[indice_taille+1]['Height 1']) +
                    nan_cleaner([],donnees.loc[indice_taille+1]['Height 2']) +
                    nan_cleaner([],donnees.loc[indice_taille+1]['Height 3'])}

                    pere[donnees.loc[indice_taille+2].Marker] = {'Allele' : nan_cleaner([],donnees.loc[indice_taille+2]['Allele 1']) +
                    nan_cleaner([],donnees.loc[indice_taille+2]['Allele 2']) +
                    nan_cleaner([],donnees.loc[indice_taille+2]['Allele 3']),
                    'Hauteur': nan_cleaner([],donnees.loc[indice_taille+2]['Height 1']) +
                    nan_cleaner([],donnees.loc[indice_taille+2]['Height 2']) +
                    nan_cleaner([],donnees.loc[indice_taille+2]['Height 3'])}
            pere = Pere(ID_pere,pere)
        mere = Mere(ID_mere,mere)
        foetus = Foetus(ID_foetus,foetus)
        echantillon = Echantillon(date_echantillon, ID_echantillon, mere, foetus, pere)
    except Exception as e:
        logger.error("Chargement données impossible", exc_info=True)

    logger.info("Chargement des données réussi")    
    return echantillon

def getdata(line, name):
    data = []
    for key in line.keys():
        if name in key and line[key] != "":
            data.append(line[key])

def concordance_ADN(echantillon):
    logger.info("Vérification de la concordance des ADNs")
    for key in echantillon.mere.data.keys():
        if echantillon.common_element(echantillon.mere.data[key]['Allele'],echantillon.foetus.data[key]['Allele']):
            echantillon.concordance_mere_foet = True
        else:
            echantillon.concordance_mere_foet = False
            break
    try:
        for key in echantillon.pere.data.keys():
            if echantillon.common_element(echantillon.pere.data[key]['Allele'],echantillon.foetus.data[key]['Allele']):
                echantillon.concordance_pere_foet = True
            else:
                echantillon.concordance_pere_foet = False
                break
    except AttributeError:
        logger.info("Père absent")
        echantillon.get_concordance_pere_foet = None

if __name__ == "__main__":
    echantillon = lecture_fichier('Cas_avec_4.txt')
    echantillon2 = lecture_fichier('Cas_avec_5.txt')
    concordance_ADN(echantillon)
    concordance_ADN(echantillon2)
    print(echantillon.concordance_pere_foet)
    print(echantillon.concordance_mere_foet)
    print(echantillon2.concordance_pere_foet)
    print(echantillon2.concordance_mere_foet)

