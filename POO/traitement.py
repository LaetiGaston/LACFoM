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
    echantillon = lecture_fichier('181985_xfra_ja_200618_PP16.txt')
    echantillon2 = lecture_fichier('PP16_XFra_F_290119_PP16.txt')
    concordance_ADN(echantillon)
    print(echantillon.concordance_pere_foet)
    print(echantillon.concordance_mere_foet)
