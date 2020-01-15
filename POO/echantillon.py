from mere import *
from foetus import *
from pere import *
from temoin import *


class Echantillon:

    """ Parameters used to analyze one fetal sample

    Attributes:
        date : date sample
        concordance (str) : DNAs match between mother and fetus
        seuil_nbre_marqueurs (int) : marker number which have to be contaminated to declare sample as contaminated
        seuil_hauteur (int) : spike height to check
        mere (object) : information about mother
        foetus (object) : information about fetus
        pere (object) : information about father
        tpos (object) : informations about tpos
        tneg (object) : informations about tneg
        ?? conclusion (int) : contaminated sample (1) or not (0)
    """

    def __init__(self, date, mere, foetus, tpos, tneg, pere = None, seuil_nbre_marqueurs=2, seuil_hauteur=1 / 3):
        """ The constructor for Echantillon class

        Parameters:
            date : date sample
            concordance (str) : DNAs match between mother and fetus
            seuil_nbre_marqueurs (int) : marker number which have to be contaminated to declare sample as contaminated
            seuil_hauteur (int) : spike height to check
            conclusion (int) : contaminated sample (1) or not (0)

        """
        self.date = date
        self.mere = Mere(*mere)
        self.foetus = Foetus(*foetus)
        self.tpos = Temoin(*tpos)
        self.tneg = Temoin(*tneg)
        if pere:
            self.pere = Pere(*pere)
        else:
            self.pere = pere
        self.seuil_nbre_marqueurs = seuil_nbre_marqueurs
        self.seuil_hauteur = seuil_hauteur
        self.concordance_mere_foet = None
        self.concordance_pere_foet = None

    def set_seuil_nbre_marqueurs(self, nb):
        """ Set seuil_nbre_marqueurs
        """
        self.seuil_nbre_marqueurs = nb

    def set_seuil_hauteur(self, hauteur):
        """ Set seuil_hauteur
        """
        self.seuil_hauteur = hauteur

    def concordance_ADN(self, number_mere=1, number_pere=1):
        concordance_mere_foet = 0
        concordance_pere_foet = 0
        for key in self.mere.data.keys():
            self.foetus.data[key]["concordance"] = ["OUI", "OUI"]
            if not common_element(self.mere.data[key]['Allele'], self.foetus.data[key]['Allele']):
                self.foetus.data[keys]["concordance"][0] = "NON"
                concordance_mere_foet += 1
                try:
                    concordance_pere_foet = 0
                    if not common_element(self.pere.data[key]['Allele'], self.foetus.data[key]['Allele']):
                        self.foetus.data[keys]["concordance"][1] = "NON"
                        concordance_pere_foet += 1
                except Exception as e:
                    pass
        
        # Check concordance
        self.concordance_mere_foet = True
        if concordance_mere_foet >= number_mere:
            self.concordance_mere_foet = False
        if self.pere and concordance_pere_foet >= number_pere:
            self.concordance_pere_foet = False
        elif self.pere:
            self.concordance_pere_foet = True

    def analyse_marqueur(self):
        """
        """
        marqueurs = list(self.foetus.data)
        marqueurs.remove('AMEL')
        for marqueur in marqueurs:
            # check if the mother is homozygote
            if len(self.mere.data[marqueur]["Allele"]) == 1:
                print(self.mere.data[marqueur]["Allele"])
                self.foetus.data[marqueur]["détails"] = "Mere homozygote"
                self.foetus.data[marqueur]["conclusion"] = "Non informatif"
            # check meme alleles que la mere
            elif sorted(self.foetus.data[marqueur]["Allele"]) == sorted(self.mere.data[marqueur]["Allele"]) :
                self.compute_homozygote_contamination(marqueur)
            # check allele dans echo a -1 de la mere
            elif common_element([ x-1 for x in self.foetus.data[marqueur]["Allele"] ], self.mere.data[marqueur]["Allele"]):
                # allele du foetus dans l'echo de la mere
                self.foetus.data[marqueur]["détails"] = "Echo"
                self.foetus.data[marqueur]["conclusion"] = "Non informatif"
            else:
                if len(self.foetus.data[marqueur]["Allele"]) == 3:
                    self.foetus.data[marqueur]["conclusion"] = "Contaminé"
                    self.compute_heterozygote_contamination(marqueur)
                elif len(self.foetus.data[marqueur]["Allele"]) == 1:
                    self.foetus.data[marqueur]["conclusion"] = "Non contaminé"
                    self.foetus.data[marqueur]["détails"] = ""
                elif len(self.foetus.data[marqueur]["Allele"]) == 2:
                    # Foetus htz non conta
                    self.foetus.data[marqueur]["conclusion"] = "Non contaminé"
                    self.foetus.data[marqueur]["détails"] = ""
                else:
                       self.foetus.data[marqueur]["conclusion"] = "Cas non envisagé"
                       self.foetus.data[marqueur]["détails"] = "Foetus: %s, Mere: %s"%(", ".join(map(str, self.foetus.data[marqueur]["Allele"])), ", ".join(map(str, self.mere.data[marqueur]["Allele"])))

        # Compute conclusion
        contamajeur = False
        conta = 0
        nonconta = 0
        valconta = 0
        # Nb de marqueurs informatifs non contamines
        for marqueur in marqueurs:
            if self.foetus.data[marqueur]["conclusion"] == "Non contaminé":
                nonconta += 1
            elif self.foetus.data[marqueur]["conclusion"] == "Contaminé":
                conta += 1
                if type(self.foetus.data[marqueur]["détails"]) == list:
                    contamajeur = True
                else:
                    valconta += self.foetus.data[marqueur]["détails"]
        if contamajeur:
            self.conclusion = [nonconta, conta, "MAJEUR"]
        elif conta == 0:
            self.conclusion = [nonconta, conta, 0]
        else:
            self.conclusion = [nonconta, conta, round(valconta/conta, 2)]
        
        if conta > self.seuil_nbre_marqueurs:
            self.contamine = True
        else:
            self.contamine = False


    def compute_heterozygote_contamination(self, marqueur):
        pic_pere = set(self.foetus.data[marqueur]["Allele"]) -set(self.mere.data[marqueur]["Allele"])

        pic1 = self.foetus.data[marqueur]["Hauteur"][self.foetus.data[marqueur]["Allele"].index(self.mere.data[marqueur]["Allele"][0])]
        pic2 = self.foetus.data[marqueur]["Hauteur"][self.foetus.data[marqueur]["Allele"].index(self.mere.data[marqueur]["Allele"][1])] = min(self.foetus.data[marqueur]["Hauteur"])

        if abs(pic1 - pic2) > (1 - self.seuil_hauteur) * max(pic1,pic2) :
            contaminant = min(pic1, pic2)
            self.foetus.data[marqueur]["détails"] = round((contaminant / (contaminant + pic_pere)) * 100, 2)
        else :
            self.foetus.data[marqueur]["détails"] = [round((pic1 / (pic1 + pic_pere)) * 100,2), round((pic2 / (pic2 + pic_pere)) * 100, 2)]
        
    def compute_homozygote_contamination(self, marqueur):
        if abs(self.foetus.data[marqueur]["Hauteur"][0] - self.foetus.data[marqueur]["Hauteur"][1]) > (1 - self.seuil_hauteur) * max(*self.foetus.data[marqueur]['Hauteur']) :
            contaminant = min(self.foetus.data[marqueur]["Hauteur"])
            autre = max(self.foetus.data[marqueur]["Hauteur"])
            self.foetus.data[marqueur]["détails"] = round(((2 * contaminant) / (contaminant + autre)) * 100, 2)
            self.foetus.data[marqueur]["conclusion"] = "Contaminé"
        else:
            self.foetus.data[marqueur]["conclusion"] = "Non informatif"
            self.foetus.data[marqueur]["détails"] = "Même allèles que la mère"

    def get_resultats(self):
        """
        Dictionnary  of all results
        """
       
        marqueurs = list(self.foetus.data)
        marqueurs.remove("AMEL")
        if self.concordance_mere_foet:
            resultat = {"Marqueur": marqueurs, "Conclusion": [ self.foetus.data[marqueur]["conclusion"] for marqueur in marqueurs ], "Détails M/F": [ self.foetus.data[marqueur]["détails"] for marqueur in marqueurs ]}
        else:
            if self.pere:
                if self.concordance_pere_foet:
                    resultat = {"Marqueur": marqueurs, "Concordance Mere/Foetus": [ self.foetus.data[marqueur]["concordance"][0] for marqueur in marqueurs ], "Détails M/F": self.get_notconcordant(0)}
                else:
                    resultat = {"Marqueur": [ marqueurs ], "Concordance Mere/Foetus": [ self.foetus.data[marqueur]["concordance"][0] for marqueur in marqueurs ], "Détails M/F": self.get_notconcordant(0), "Concordance Pere/Foetus": [ self.foetus.data[marqueur]["concordance"][1] for marqueur in marqueurs ], "Détails P/F": self.get_notconcordant(1)}
        return resultat

    def get_id(self):
        return self.mere.ID

    def get_contamine(self):
        return self.contamine
        
    def get_conclusion(self):
        return self.conclusion
        
    
    def get_notconcordant(self, parent):
        """
        return the list of not concordant alleles
        parent: 0 for mother and 1 for father
        """
        list_alleles = []
        for marqueur in self.foetus.data.keys():
            if self.foetus.data[marqueur]["concordance"][parent] == "NON":
                list_alleles.append("M: " + str(self.mere.data[marqueur]["Allele"]) + " F: " + str(self.foetus.data[marqueur]["Allele"]))
            else:
                list_alleles.append("")
        return list_alleles

def common_element(list1,list2):
    list1_set = set(list1)
    list2_set = set(list2)
    if len(list1_set.intersection(list2_set)) > 0:
        return True
    return False
