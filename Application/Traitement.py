import pandas as pd
import numpy as np
import logging
from datetime import datetime
from time import strftime
import re

heure = datetime.now()
heure_vrai = heure.strftime("%d-%m-%Y_%Hh_%Mm")
logging.basicConfig(filename='log_' + heure_vrai + '.txt', filemode='w', format='%(name)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


class Echantillon:
    """ Parameters used to analyze one fetal sample

    Attributes:
        date : date sample
        liste_lignes (list) : extracted from txt file, lines corresponding to fetus
        sexe (str) : fetus sex
        concordance (str) : DNAs match between mother and fetus
        seuil_nbre_marqueurs (int) : marker number which have to be contaminated to declare sample as contaminated
        seuil_hauteur (int) : spike height to check
        conclusion (int) : contaminated sample (1) or not (0)
    """

    def __init__(self, date, name, liste_lignes, sexe=None, concordance_mere_foet=None, concordance_pere_foet=None,
                 seuil_nbre_marqueurs=2, seuil_hauteur=1 / 3, conclusion=None):
        """ The constructor for Echantillon class

        Parameters:
            date : date sample
            liste_lignes (list) : extracted from txt file, lines corresponding to fetus
            sexe (str) : fetus sex
            concordance (str) : DNAs match between mother and fetus
            seuil_nbre_marqueurs (int) : marker number which have to be contaminated to declare sample as contaminated
            seuil_hauteur (int) : spike height to check
            conclusion (int) : contaminated sample (1) or not (0)

        """
        self.date = date
        self.name = name
        self.liste_lignes = liste_lignes
        self.seuil_nbre_marqueurs = seuil_nbre_marqueurs
        self.conclusion = conclusion
        self.seuil_hauteur = seuil_hauteur
        self.sexe = sexe
        self.concordance_mere_foet = concordance_mere_foet
        self.concordance_pere_foet = concordance_pere_foet

    def get_date(self):
        return self.date

    def get_name(self):
        return self.name

    def get_seuil_nbre_marqueurs(self):
        """ Return seuil_nbre_marqueurs
        """
        return self.seuil_nbre_marqueurs

    def get_seuil_hauteur(self):
        """ Return seuil_hauteur
        """
        return self.seuil_hauteur

    def get_conclusion(self):
        """ Return conclusion
        """
        return self.conclusion

    def get_sexe(self):
        """ Return sex
        """
        return self.sexe

    def get_concordance_mere_foet(self):
        """ Return concordance
        """
        return self.concordance_mere_foet

    def get_concordance_pere_foet(self):
        """ Return concordance
        """
        return self.concordance_pere_foet

    def set_seuil_nbre_marqueurs(self, nb):
        """ Set seuil_nbre_marqueurs
        """
        self.seuil_nbre_marqueurs = nb

    def set_seuil_hauteur(self, hauteur):
        """ Set seuil_hauteur
        """
        self.seuil_hauteur = hauteur

    def set_sexe(self, sexe):
        """ Set sex
        """
        self.sexe = sexe

    def set_concordance_mere_foet(self, concordance_mere_foet):
        """ Set concordance
        """
        self.concordance_mere_foet = concordance_mere_foet

    def set_concordance_pere_foet(self, concordance_pere_foet):
        """ Set concordance
        """
        self.concordance_pere_foet = concordance_pere_foet

    def set_conclusion(self, conclusion):
        """ Set conclusion
        """
        self.conclusion = conclusion

    def analyse_donnees(self, mere, foetus, pere):
        """ Analyze data
            Concordance between mere/foetus and pere/foetus is done.
            For one couple lignes mere/foetus, informative character and conclusion is set.

            Parameters :
                mere (list) : lines extracted from txt file corresponding to mother
                foetus (list) : lines extracted from txt file corresponding to fetus
                pere (list) : lines extracted from txt file corresponding to father

            Return two dataframes :
                - first one containing information about Name, Conclusion and Details for each marker
                - second one containing global information about sample (Number of informative markers, contaminated markers and free contaminated markers )
            """
        logger.info("Analyse des données")
        logger.info("Vérification concordance ADN")
        concordance_mf = 0
        concordance_pf = None
        try:
            if len(pere) != 0:
                logger.info("Père détecté")
                logger.info("Vérification concordance des ADNs entre père et foetus")
                concordance_pf = 0
                for alleles in range(len(foetus)):
                    for allele_foetus in range(3):
                        if foetus[alleles].allele[allele_foetus] in pere[alleles].allele:
                            if foetus[alleles].allele[allele_foetus] != 0.0:
                                pere[alleles].concordance_pere_foetus = "OUI"
                                concordance_pf = concordance_pf + 1
                                break
                        else:
                            pere[alleles].concordance_pere_foetus = "NON"
            logger.info("Vérification concordance des ADNs entre mère et foetus")
            for alleles in range(len(foetus)):
                for allele_foetus in range(3):
                    if foetus[alleles].allele[allele_foetus] in mere[alleles].allele:
                        if foetus[alleles].allele[allele_foetus] != 0.0:
                            foetus[alleles].concordance_mere_foetus = "OUI"
                            concordance_mf = concordance_mf + 1
                            break
                    else:
                        foetus[alleles].concordance_mere_foetus = "NON"
        except Exception as e:
            logger.error("Vérification concordance ADN impossible", exc_info=True)

        logger.info("Vérification concordance des ADNs terminée")
        if concordance_mf != len(foetus):
            resultats, conclusion = self.resultat(concordance_mf, concordance_pf, foetus, mere, pere)
            return resultats, conclusion
        else:
            try:
                logger.info("Traitements des marqueurs\n")
                for nbre_lignes in range(1, len(mere)):
                    logger.info("Traitement du marqueur : " + str(foetus[nbre_lignes].marqueur))
                    pic = foetus[nbre_lignes].foetus_pics()
                    logger.info("Calcul du nombre d'allèles pour le foetus")
                    logger.info("Nombre d'allèles pour le foetus : " + str(pic))
                    logger.info("Vérification de l'homozygotie de la mère")
                    mere[nbre_lignes].homozygotie()
                    logger.info("Mère homozygote : " + str(mere[nbre_lignes].homozygote))
                    logger.info("Vérification si mère et foetus possèdent les mêmes allèles")
                    foetus[nbre_lignes].allele_semblable(mere[nbre_lignes])
                    logger.info("Code informatif vérification mêmes allèles que la mère : " + str(
                        foetus[nbre_lignes].informatif))
                    logger.info("Initialisation du taux de contamination pour calcul à venir")
                    logger.info("Taux initialisé")
                    foetus[nbre_lignes].taux = 0.0
                    logger.info(
                        "Si code informatif vérification mêmes allèles que la mère différent de 2, vérification écho")
                    logger.info("Si écho, affection de la valeur 3 pour code informatif")
                    if foetus[nbre_lignes].informatif != 2:
                        logger.info("Vérification si écho")
                        mere[nbre_lignes].echo(foetus[nbre_lignes])
                        logger.info(
                            "Code informatif pour vérification écho retourné : " + str(foetus[nbre_lignes].informatif))
                    logger.info("Début chaîne de traitement")
                    if pic == 3:
                        logger.info("Trois allèles détectés")
                        foetus[nbre_lignes].contamination_heterozygote(mere[nbre_lignes], self.get_seuil_hauteur())
                        logger.info("Marqueur informatif, affectation de la valeur 1 pour code contamination")
                        logger.info("Calcul taux de contamination du marqueur")
                        logger.info("Calcul terminé")
                    elif mere[nbre_lignes].homozygote:
                        logger.info("Mère homozygote détectée")
                        logger.info("Marqueur non informatif, affection de la valeur 0 pour code informatif")
                        foetus[nbre_lignes].informatif = 0
                    elif pic == 2:
                        logger.info("Deux allèles détectés")
                        if foetus[nbre_lignes].informatif == 2:
                            logger.info("Mêmes allèles entre mère et foetus, vérification si homozygote contaminé")
                            foetus[nbre_lignes].contamination_homozygote(self.get_seuil_hauteur())
                            if foetus[nbre_lignes].contamination == 1:
                                logger.info("Homozygote contaminé identifié")
                                logger.info("Calcul du taux de contamination")
                                logger.info("Calcul du taux de contamination effectué")
                            else:
                                logger.info(
                                    "Marqueur non contaminé, affectation de la valeur 0 pour code contamination")
                        else:
                            if foetus[nbre_lignes].informatif != 3:
                                logger.info("Code informatif différent de 3, pas d'écho")
                                logger.info("Marqueur informatif, affectation de la valeur 1 pour code informatif")
                                foetus[nbre_lignes].informatif = 1
                                logger.info(
                                    "Marqueur non contaminé, affectation de la valeur 0 pour code contamination")
                                foetus[nbre_lignes].contamination = 0
                    else:
                        logger.info("Un seul allèle détecté")
                        if foetus[nbre_lignes].informatif != 3:
                            logger.info("Code informatif différent de 3, pas d'écho")
                            logger.info("Marqueur informatif, affectation de la valeur 1 pour code informatif")
                            foetus[nbre_lignes].informatif = 1
                            logger.info(
                                "Marqueur non contaminé, affectation de la valeur 0 pour code contamination\n\n")
                            foetus[nbre_lignes].contamination = 0
                    logger.info("Marqueur suivant\n")
                logger.info("Détermination contamination pour échantillon")
                logger.info(
                    "Echantillon contaminé si plus de " + str(self.seuil_nbre_marqueurs) + "marqueurs contaminés")
                self.conclusion_echantillon(foetus)
                logger.info("Détermination contamination pour échantillon terminée")
                logger.info("Fin de traitement")
                logger.info("Stockage des conclusions")
                resultats, conclusion = self.resultat(concordance_mf, concordance_pf, foetus, mere, pere)
                return resultats, conclusion
            except Exception as e:
                logger.error("Traitement des marqueurs impossible", exc_info=True)

    def resultat(self, concordance_mf, concordance_pf, liste_F, liste_M, liste_P):
        """ Set informative character and conclusion for each marker using code tables
                Code tables are :

                Informative code :
                    0 : Homozygous mother
                    1 : Informative marker
                    2 : Same alleles between mother and fetus
                    3 : Stutter

                Contamination code :
                    0 : No contamination
                    1 : Homozygous marker contaminated
                    2 : Heterozygous marker contaminated
                    3 : High level of contamination

                Sample conclusion code :
                    0 : not contaminated
                    1 : contaminated

            Parameters :
                - concordance (int) : DNAs matching markers between mother and fetus
                - list_F (list) : contains fetus lines from txt file
                - liste_M (list): contains mother lines from txt file
                - liste_P (list) : contains father lines from txt file

            Return two dataframes :
                - first one containing information about Name, Conclusion and Details for each marker
                - second one containing global information about sample (Number of informative markers, contaminated markers and free contaminated markers)

        """
        resultat = {"Marqueur": [], "Conclusion": [], "Concordance Mere/Foetus": [], "Détails M/F": [],
                    "Concordance Pere/Foetus": [], "Détails P/F": []}
        marqueurs_conta = 0
        marqueurs_conta_majeur = 0
        marqueurs_non_conta = 0
        somme_conta = 0
        logger.info("Détermination du sexe")
        try:
            if liste_F[0].allele[1] == 0.0:
                self.set_sexe("F")
            else:
                self.set_sexe("M")
        except Exception as e:
            logger.error("Détermination du sexe impossible", exc_info=True)

        try:
            if concordance_mf != len(liste_F) and concordance_pf != len(liste_F) or concordance_mf != len(
                    liste_F) and concordance_pf == None:
                del resultat["Conclusion"]
                self.set_concordance_mere_foet("NON")
                self.set_concordance_pere_foet("NON")
                if concordance_pf == None:
                    logger.warning("Concordance ADNs mère/foetus négative")
                    logger.warning("Père absent")
                    self.set_concordance_pere_foet("ABS")
                    del resultat["Concordance Pere/Foetus"]
                    del resultat["Détails P/F"]
                    logger.info("Concordance mère/foetus : " + str(self.get_concordance_mere_foet()))
                    logger.info("Concordance père/foetus : " + str(self.get_concordance_pere_foet()))
                    logger.info("Répertoriation des marqueurs non concordants")
                    for nbres in range(1, len(liste_F)):
                        resultat["Marqueur"].append(str(liste_F[nbres].marqueur))
                        resultat["Concordance Mere/Foetus"].append(liste_F[nbres].concordance_mere_foetus)
                        if liste_F[nbres].concordance_mere_foetus == "NON":
                            resultat["Détails M/F"].append(
                                "M : " + str(liste_M[nbres].normalisation(liste_M[nbres].allele)) + " F: " + str(
                                    liste_F[nbres].normalisation(liste_F[nbres].allele)))
                        else:
                            resultat["Détails M/F"].append("")
                    conclusion = pd.DataFrame({"1": ["Non calculé", "Non calculé", "Non calculé", self.get_date()]},
                                              index=["Nombre de marqueurs informatifs non contaminés",
                                                     "Nombre de marqueurs informatifs contaminés",
                                                     "Moyenne du pourcentage de contamination", "Date"])
                    resultats = pd.DataFrame(resultat, columns=["Marqueur", "Concordance Mere/Foetus", "Détails M/F"])
                    logger.info("Répertoriation terminée")
                    logger.info("Analyse des données terminée")
                    logger.info("Résultats renvoyés et prêts pour affichage")
                    return resultats, conclusion
                else:
                    logger.info("Concordance mère/foetus : " + str(self.get_concordance_mere_foet()))
                    logger.info("Concordance père/foetus : " + str(self.get_concordance_pere_foet()))
                    logger.info("Répertoration des marqueurs non concordants")
                    for nbres in range(1, len(liste_F)):
                        resultat["Marqueur"].append(str(liste_F[nbres].marqueur))
                        resultat["Concordance Mere/Foetus"].append(liste_F[nbres].concordance_mere_foetus)
                        resultat["Concordance Pere/Foetus"].append(liste_P[nbres].concordance_pere_foetus)
                        if liste_F[nbres].concordance_mere_foetus == "NON" and liste_P[
                            nbres].concordance_pere_foetus == "NON":
                            resultat["Détails M/F"].append(
                                "M : " + str(liste_M[nbres].normalisation(liste_M[nbres].allele)) + " F: " + str(
                                    liste_F[nbres].normalisation(liste_F[nbres].allele)))
                            resultat["Détails P/F"].append(
                                "P : " + str(liste_P[nbres].normalisation(liste_P[nbres].allele)) + " F : " + str(
                                    liste_F[nbres].normalisation(liste_F[nbres].allele)))
                        elif liste_F[nbres].concordance_mere_foetus == "NON":
                            resultat["Détails M/F"].append(
                                "M: " + str(liste_M[nbres].normalisation(liste_M[nbres].allele)) + " F : " + str(
                                    liste_F[nbres].normalisation(liste_F[nbres].allele)))
                            resultat["Détails P/F"].append("")
                        elif liste_P[nbres].concordance_pere_foetus == "NON":
                            resultat["Détails P/F"].append(
                                "P: " + str(liste_P[nbres].normalisation(liste_P[nbres].allele)) + " F: " + str(
                                    liste_F[nbres].normalisation(liste_F[nbres].allele)))
                            resultat["Détails M/F"].append("")
                        else:
                            resultat["Détails M/F"].append("")
                            resultat["Détails P/F"].append("")
                        conclusion = pd.DataFrame({"1": ["Non calculé", "Non calculé", "Non calculé", self.get_date()]},
                                                  index=["Nombre de marqueurs informatifs non contaminés",
                                                         "Nombre de marqueurs informatifs contaminés",
                                                         "Moyenne du pourcentage de contamination", "Date"])
                        resultats = pd.DataFrame(resultat,
                                                 columns=["Marqueur", "Concordance Mere/Foetus", "Détails M/F",
                                                          "Concordance Pere/Foetus", "Détails P/F"])
                    logger.info("Répertoriation terminée")
                    logger.info("Analyse des données terminée")
                    logger.info("Résultats renvoyés et prêts pour l'affichage")
                    return resultats, conclusion
            elif concordance_mf != len(liste_F) and concordance_pf == len(liste_F) or concordance_mf != len(
                    liste_F) and concordance_pf == None:
                self.set_concordance_mere_foet("NON")
                self.set_concordance_pere_foet("OUI")
                if concordance_pf == None:
                    self.set_concordance_pere_foet("ABS")
                logger.info("Concordance mère/foetus : " + str(self.get_concordance_mere_foet()))
                logger.info("Concordance père/foetus : " + str(self.get_concordance_pere_foet()))
                logger.info("Répertoration des marqueurs non concordants")
                del resultat["Conclusion"]
                del resultat["Concordance Pere/Foetus"]
                del resultat["Détails P/F"]
                for nbres in range(1, len(liste_F)):
                    resultat["Marqueur"].append(str(liste_F[nbres].marqueur))
                    resultat["Concordance Mere/Foetus"].append(liste_F[nbres].concordance_mere_foetus)
                    if liste_F[nbres].concordance_mere_foetus == "NON":
                        resultat["Détails M/F"].append(
                            "M: " + str(liste_M[nbres].normalisation(liste_M[nbres].allele)) + " F: " + str(
                                liste_F[nbres].normalisation(liste_F[nbres].allele)))
                    else:
                        resultat["Détails M/F"].append("")
                    conclusion = pd.DataFrame({"1": ["Non calculé", "Non calculé", "Non calculé", self.get_date()]},
                                              index=["Nombre de marqueurs informatifs non contaminés",
                                                     "Nombre de marqueurs informatifs contaminés",
                                                     "Moyenne du pourcentage de contamination", "Date"])
                    resultats = pd.DataFrame(resultat, columns=["Marqueur", "Concordance Mere/Foetus", "Détails M/F"])
                    logger.info("Répertoriation terminée")
                    logger.info("Analyse des données terminée")
                    logger.info("Résultats renvoyés et prêts pour l'affichage")
                return resultats, conclusion
            elif concordance_mf == len(liste_F) and concordance_pf == len(liste_F) or concordance_mf == len(
                    liste_F) and concordance_pf == None:
                self.set_concordance_mere_foet("OUI")
                self.set_concordance_pere_foet("OUI")
                if concordance_pf == None:
                    self.set_concordance_pere_foet("ABS")
                del resultat["Concordance Mere/Foetus"]
                del resultat["Concordance Pere/Foetus"]
                del resultat["Détails P/F"]
                for nbres in range(1, len(liste_F)):
                    resultat["Marqueur"].append(str(liste_F[nbres].marqueur))
                    if liste_F[nbres].informatif == 0:
                        resultat["Conclusion"].append("Non informatif")
                        resultat["Détails M/F"].append("Mère homozygote")
                    elif liste_F[nbres].informatif == 1:
                        if liste_F[nbres].contamination == 0:
                            marqueurs_non_conta += 1
                            resultat["Conclusion"].append("Non contaminé")
                            resultat["Détails M/F"].append("")
                        elif liste_F[nbres].contamination == 1:
                            marqueurs_conta += 1
                            somme_conta = somme_conta + liste_F[nbres].taux
                            resultat["Conclusion"].append("Contaminé")
                            resultat["Détails M/F"].append(str(liste_F[nbres].taux) + "%")
                        elif liste_F[nbres].contamination == 2:
                            marqueurs_conta += 1
                            somme_conta = somme_conta + liste_F[nbres].taux
                            resultat["Conclusion"].append("Contaminé")
                            resultat["Détails M/F"].append(str(liste_F[nbres].taux) + "%")
                        else:
                            marqueurs_conta_majeur += 1
                            resultat["Conclusion"].append("Contaminé")
                            resultat["Détails M/F"].append(
                                str(liste_F[nbres].taux[0]) + "% / " + str(liste_F[nbres].taux[1]) + "%")
                    elif liste_F[nbres].informatif == 2:
                        resultat["Conclusion"].append("Non informatif")
                        resultat["Détails M/F"].append("Mêmes allèles que la mère")
                    else:
                        resultat["Conclusion"].append("Non informatif")
                        resultat["Détails M/F"].append("Echo")
                resultats = pd.DataFrame(resultat, columns=["Marqueur", "Conclusion", "Détails M/F"])
                try:
                    moyenne_conta = somme_conta / marqueurs_conta
                except ZeroDivisionError:
                    moyenne_conta = 0
                if marqueurs_conta_majeur >= 1:
                    conclusion = pd.DataFrame(
                        {"1": [int(marqueurs_non_conta), int(marqueurs_conta + marqueurs_conta_majeur), "MAJEURE",
                               self.get_date()]},
                        index=["Nombre de marqueurs informatifs non contaminés",
                               "Nombre de marqueurs informatifs contaminés",
                               "Moyenne du pourcentage de contamination", "Date"])
                else:
                    conclusion = pd.DataFrame(
                        {"1": [int(marqueurs_non_conta), int(marqueurs_conta + marqueurs_conta_majeur),
                               round(moyenne_conta, 2), self.get_date()]},
                        index=["Nombre de marqueurs informatifs non contaminés",
                               "Nombre de marqueurs informatifs contaminés",
                               "Moyenne du pourcentage de contamination", "Date"])
                return resultats, conclusion
            elif concordance_mf == len(liste_F) and concordance_pf != len(liste_F):
                self.set_concordance_mere_foet("OUI")
                self.set_concordance_pere_foet("NON")
                del resultat["Concordance Mere/Foetus"]
                for nbres in range(1, len(liste_F)):
                    resultat["Concordance Pere/Foetus"].append(liste_P[nbres].concordance_pere_foetus)
                    if liste_P[nbres].concordance_pere_foetus == "NON":
                        resultat["Détails P/F"].append(
                            "P: " + str(liste_P[nbres].normalisation(liste_P[nbres].allele)) + " F: " + str(
                                liste_F[nbres].normalisation(liste_F[nbres].allele)))
                    else:
                        resultat["Détails P/F"].append("")
                for nbres in range(1, len(liste_F)):
                    resultat["Marqueur"].append(str(liste_F[nbres].marqueur))
                    if liste_F[nbres].informatif == 0:
                        resultat["Conclusion"].append("Non informatif")
                        resultat["Détails M/F"].append("Mère homozygote")
                    elif liste_F[nbres].informatif == 1:
                        if liste_F[nbres].contamination == 0:
                            marqueurs_non_conta += 1
                            resultat["Conclusion"].append("Non contaminé")
                            resultat["Détails M/F"].append("")
                        elif liste_F[nbres].contamination == 1:
                            marqueurs_conta += 1
                            somme_conta = somme_conta + liste_F[nbres].taux
                            resultat["Conclusion"].append("Contaminé")
                            resultat["Détails M/F"].append(str(liste_F[nbres].taux) + "%")
                        elif liste_F[nbres].contamination == 2:
                            marqueurs_conta += 1
                            somme_conta = somme_conta + liste_F[nbres].taux
                            resultat["Conclusion"].append("Contaminé")
                            resultat["Détails M/F"].append(str(liste_F[nbres].taux) + "%")
                        else:
                            marqueurs_conta_majeur += 1
                            resultat["Conclusion"].append("Contaminé")
                            resultat["Détails M/F"].append(
                                str(liste_F[nbres].taux[0]) + "% / " + str(liste_F[nbres].taux[1]) + "%")
                    elif liste_F[nbres].informatif == 2:
                        resultat["Conclusion"].append("Non informatif")
                        resultat["Détails M/F"].append("Mêmes allèles que la mère")
                    else:
                        resultat["Conclusion"].append("Non informatif")
                        resultat["Détails M/F"].append("Echo")
                resultats = pd.DataFrame(resultat,
                                         columns=["Marqueur", "Conclusion", "Détails M/F", "Concordance Pere/Foetus",
                                                  "Détails P/F"])
            try:
                moyenne_conta = somme_conta / marqueurs_conta
            except ZeroDivisionError:
                moyenne_conta = 0
            if marqueurs_conta_majeur >= 1:
                conclusion = pd.DataFrame(
                    {"1": [int(marqueurs_non_conta), int(marqueurs_conta + marqueurs_conta_majeur), "MAJEURE",
                           self.get_date()]},
                    index=["Nombre de marqueurs informatifs non contaminés",
                           "Nombre de marqueurs informatifs contaminés",
                           "Moyenne du pourcentage de contamination", "Date"])
            else:
                conclusion = pd.DataFrame(
                    {"1": [int(marqueurs_non_conta), int(marqueurs_conta + marqueurs_conta_majeur),
                           round(moyenne_conta, 2), self.get_date()]},
                    index=["Nombre de marqueurs informatifs non contaminés",
                           "Nombre de marqueurs informatifs contaminés",
                           "Moyenne du pourcentage de contamination", "Date"])
            return resultats, conclusion
            logger.info("Analyse des données terminée")
            logger.info("Résultats renvoyés et prêts pour l'affichage")
        except Exception as e:
            logger.error("Stockage des données impossible", exc_info=True)

    def conclusion_echantillon(self, liste_foetus):
        """ This concludes about sample contamination.

            If the number of contaminated marker is higher than seuil_nbre_marqueurs -> sample is contaminated
            Else -> sample is not contaminated

            Parameters :
                liste_foetus (list) : contains fetus lines from txt file
        """
        compteur = 0
        for lignes in range(1, len(liste_foetus)):
            if liste_foetus[lignes].informatif == 1 and liste_foetus[lignes].contamination != 0:
                compteur = compteur + 1
        if compteur > self.seuil_nbre_marqueurs:
            self.conclusion = 1
        else:
            self.conclusion = 0


class Patient:
    """ Common informations between mother and fetus

        Attributes :
            marqueur (list) : markers list
            allele (list) : alleles list
            hauteur (list) : alleles height list
            informatif (int) : informatif character of marker
    """

    def __init__(self, num, marqueur, allele, hauteur, informatif):
        """ The constructor for Patient class

            Parameters :
            num (str) : name
            marqueur (list) : markers list
            allele (list) : alleles list
            hauteur (list) : alleles height list
            informatif (int) : informatif character of marker
        """
        self.num = num
        self.marqueur = marqueur
        self.allele = allele
        self.hauteur = hauteur
        self.informatif = informatif

    def get_name(self):
        return self.num

    def allele_semblable(self, mere):
        """ Check for each marker if fetus and mother have the same alleles list.
            Because homozygous marker from mother is always non-informative character, we only check similarity for heterozygous marker.

            Parameters :
                - mere (list) : mere class object

            If Similarite is equal to two, informative code is set to 2.
        """
        Similarite = 0
        for Allele in range(3):
            if self.allele[Allele] in mere.allele and self.allele[Allele] != 0.0:
                Similarite = Similarite + 1
        if Similarite == 2:
            self.informatif = 2

    def echo(self, foetus):
        """ Allow to detect stutter.
            Stutter : Fetus alleles are 12 and 8, Mother alleles are 11 and 10. 11 is a stutter because is n-1 (12-1) from fetus alleles

            Parameters :
                - foetus (list) : list of fetus object corresponding to each line of the fetus extracted from the txt file

            If a stutter is detected, fetus informative code is set to 3.

        """
        Allele_semblable = 0
        for Allele in range(3):
            if self.allele[Allele] in foetus.allele and self.allele[Allele] != 0.0:
                Allele_semblable = Allele
        if Allele_semblable == 0:
            Allele_Echo = self.allele[Allele_semblable + 1]
            for Alleles_foetus in range(3):
                if foetus.allele[Alleles_foetus] - 1 == Allele_Echo:
                    foetus.informatif = 3
        elif Allele_semblable == 1:
            Allele_Echo = self.allele[Allele_semblable - 1]
            for Alleles_foetus in range(3):
                if foetus.allele[Alleles_foetus] - 1 == Allele_Echo:
                    foetus.informatif = 3

    def normalisation(self, liste_alleles):
        liste_alleles2 = []
        for alleles in range(len(liste_alleles)):
            if liste_alleles[alleles] != 0.0:
                liste_alleles2.append(liste_alleles[alleles])
        return liste_alleles2


class Mere(Patient):
    """ Exclusive informations about the mother. Mere class inherits from Patient.

        Attributes :
            homozygote (boolean) : set to True if the mother is homozygous for the marker studied
    """

    def __init__(self, num, marqueur, allele, hauteur, informatif, homozygote):
        """ The constructor for Mere class

            Parameters :
                - homozygote (boolean) : set to True if the mother is homozygous for the marker studied
        """

        super().__init__(num, marqueur, allele, hauteur, informatif)
        self.homozygote = homozygote

    def homozygotie(self):
        """ Detect if the mother is homozygous for the marker stutied.
            If it's true, homozygote is set to True
        """
        if self.allele[1] == 0.0:
            self.homozygote = True


class Foetus(Patient):
    """ Exclusive informations about the fetus. Mere class inherits from Patient.

        Attributes :
            - contamination (int) : 0 if the marker is not contaminated. 1 if it is.
            - taux (int) : value corresponding to the contamination
    """

    def __init__(self, num, marqueur, allele, hauteur, concordance_mere_foetus, informatif, contamination, taux):
        """ The constructor for Mere class

            Parameters :
                - contamination (int) : 0 if the marker is not contaminated. 1 if it is.
                - taux (int) : value corresponding to the contamination
        """

        super().__init__(num, marqueur, allele, hauteur, informatif)
        self.contamination = contamination
        self.taux = taux
        self.concordance_mere_foetus = concordance_mere_foetus

    def foetus_pics(self):
        """ Count spikes number (alleles number)

            Return :
                Spikes number
        """
        pic = 0
        if 0.0 not in self.allele:
            self.contamination = 2
            pic = 3
        elif 0.0 == self.allele[1]:
            pic = 1
        else:
            pic = 2
        return pic

    def contamination_heterozygote(self, mere, seuil):
        """ Compute contamination value for heterozygous contamination.

            Parameters :
                - mere (list) : list of Mere object corresponding to each line of the mother extracted from the txt file

            Set taux attribute to value computed.
        """
        for alleles in range(3):
            if self.allele[alleles] not in mere.allele:
                self.allele.pop(alleles)
                pic_pere = self.hauteur.pop(alleles)
                break
        if self.hauteur[0] < self.hauteur[1] * seuil or self.hauteur[1] < self.hauteur[0] * seuil:
            self.contamination = 2
            self.informatif = 1
            if self.hauteur[1] < self.hauteur[0] * seuil:
                allele_contaminant = 1
                taux = ((self.hauteur[allele_contaminant]) / (
                        self.hauteur[allele_contaminant] + pic_pere)) * 100
            else:
                allele_contaminant = 0
                taux = ((self.hauteur[allele_contaminant]) / (
                        self.hauteur[allele_contaminant] + pic_pere)) * 100
            self.taux = round(taux, 2)
        else:
            taux1 = ((self.hauteur[1]) / (
                    self.hauteur[1] + pic_pere)) * 100
            taux2 = ((self.hauteur[0]) / (
                    self.hauteur[0] + pic_pere)) * 100
            self.contamination = 3
            self.informatif = 1
            self.taux = [round(taux1, 2), round(taux2, 2)]

    def contamination_homozygote(self, seuil):
        """ Check if the marker is homozygous contaminated.
            Contamination is computed if is.

            Parameters :
            - Seuil : Value to discriminate homozygous contamination

            If the marker is contaminated, contamination code is set to 1 and informative code is set to 1 too.
            Set taux attribute to value computed.
        """
        if self.hauteur[0] < self.hauteur[1] * seuil or self.hauteur[1] < self.hauteur[0] * seuil:
            self.contamination = 1
            self.informatif = 1
            if self.hauteur[1] < self.hauteur[0] * seuil:
                allele_contaminant = 1
                taux = ((2 * self.hauteur[allele_contaminant]) / (
                        self.hauteur[allele_contaminant] + self.hauteur[0])) * 100
            else:
                allele_contaminant = 0
                taux = ((2 * self.hauteur[allele_contaminant]) / (
                        self.hauteur[allele_contaminant] + self.hauteur[1])) * 100
            self.taux = round(taux, 2)
        else:
            self.taux = 0.0


class Pere(Patient):
    """ Exclusive informations about the father. Pere class inherits from Patient.

        Did not implement because mother and fetus are enough to conclude.
    """

    def __init__(self, num, marqueur, allele, hauteur, informatif, concordance_pere_foetus):
        super().__init__(num, marqueur, allele, hauteur, informatif)
        self.concordance_pere_foetus = concordance_pere_foetus


def lecture_fichier(path_data_frame):
    """ Read file corresponding to path_data_frame.
        For each line, Mere, Foetus or Pere object are created.
        At the end, one Echantillon object is created.

        Parameters :
        - path_data_frame (file)

        Return :
        Donnees_Mere (list) : list of Mere object corresponding to each line of the mother extracted from the txt file
        Donnees_Foetus (list) : list of Foetus object corresponding to each line of the fetus extracted from the txt file
        Donnees_Pere (list) : list of Pere object corresponding to each line of the father extracted from the txt file
        Echantillon_F : Echantillon object to summerize the file
    """
    iterateur = 2
    donnees_mere = []
    donnees_foetus = []
    donnees_pere = []
    logger.info("Ouverture du fichier")
    try:
        donnees_na = pd.read_csv(path_data_frame, sep='\t', header=0)
        donnees = donnees_na.replace(np.nan, 0.0, regex=True)
    except Exception as e:
        logger.error("Ouverture impossible", exc_info=True)

    logger.info("Chargement des données")
    try:
        if (donnees.shape[0] > 32):
            iterateur = 3
            num_pere = re.search("\w-(\w*)", donnees["Sample Name"].values[2]).group(1)
        allele_na = donnees[["Allele 1", "Allele 2", "Allele 3"]].values
        hauteur_na = donnees[["Height 1", "Height 2", "Height 3"]].values
        date_echantillon = re.search("(\d{4}-\d{2}-\d{2})", donnees["Sample File"].values[0]).group()
        nom_echantillon = re.search("\w-([\w,\W]*)", donnees["Sample Name"].values[1]).group(1)
        num_mere = re.search("\w-(\w*)", donnees["Sample Name"].values[0]).group(1)
        allele, hauteur = homogeneite_type(allele_na, hauteur_na)
        for ligne in range(0, donnees.shape[0] - 1, iterateur):
            m = Mere(num_mere, donnees["Marker"][ligne], allele[ligne],
                     hauteur[ligne], None, False)
            f = Foetus(nom_echantillon, donnees["Marker"][ligne], allele[ligne + 1],
                       hauteur[ligne + 1], None, None, None, None)
            if (iterateur == 3):
                p = Pere(num_pere, donnees["Marker"][ligne],
                         allele[ligne + 2], hauteur[ligne + 2], None, None)
                donnees_pere.append(p)
            donnees_mere.append(m)
            donnees_foetus.append(f)
        echantillon_f = Echantillon(date_echantillon, nom_echantillon, f)
    except Exception as e:
        logger.error("Chargement données impossible", exc_info=True)

    return donnees_mere, donnees_foetus, donnees_pere, echantillon_f


def homogeneite_type(list_allele, list_hauteur):
    """ Allow to convert string into float for Alleles and Height values in order to compute contamination.

        Parameters :
            - list_allele (list) : alleles list
            - list_height (list) : height list

        Return :
            - Allele (list) : converted values
            - Hauteur (list) : converted values
    """
    try:
        logger.info("Homogénéisation des données")
        iteration = 2
        allele = []
        hauteur = []
        allele.append(list_allele[0])
        allele.append(list_allele[1])
        hauteur.append(list_hauteur[0])
        hauteur.append(list_hauteur[1])
        if len(list_allele) > 32:
            iteration = 3
            allele.append(list_allele[2])
            hauteur.append(list_hauteur[2])
        for i in range(iteration, len(list_allele)):
            al = []
            ht = []
            for j in range(3):
                al.append(float(list_allele[i][j]))
                ht.append(float(list_hauteur[i][j]))
            allele.append(al)
            hauteur.append(ht)
        return allele, hauteur
    except Exception as e:
        logger.error("Homogénéisation impossible", exc_info=True)


if __name__ == "__main__":
    M, F, P, Echantillon_F = lecture_fichier('non_conco_M_PM.txt')
    resultats, conclusion = Echantillon_F.analyse_donnees(M, F, P)
    print(Echantillon_F.concordance_pere_foet)
    print(resultats)
    print(conclusion)

    
#Application mise au point par :
#Mirna Marie-Joseph
#Théo Gauvrit
#Kévin Merchadou

