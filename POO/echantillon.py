class Echantillon:

    """ Parameters used to analyze one fetal sample

    Attributes:
        date : date sample
        concordance (str) : DNAs match between mother and fetus
        seuil_nbre_marqueurs (int) : marker number which have to be contaminated to declare sample as contaminated
        seuil_hauteur (int) : spike height to check
        mere : information about mother
        foetus : information about fetus
        pere : information about father
        ?? conclusion (int) : contaminated sample (1) or not (0)
    """

    def __init__(self, date, ID ,mere, foetus, pere, concordance_mere_foet=None, concordance_pere_foet=None,
                 seuil_nbre_marqueurs=2, seuil_hauteur=1 / 3, conclusion=None):
        """ The constructor for Echantillon class

        Parameters:
            date : date sample
            concordance (str) : DNAs match between mother and fetus
            seuil_nbre_marqueurs (int) : marker number which have to be contaminated to declare sample as contaminated
            seuil_hauteur (int) : spike height to check
            conclusion (int) : contaminated sample (1) or not (0)

        """
        self.date = date
        self.ID = ID
        self.mere = mere
        self.foetus = foetus
        self.pere = pere
        self.seuil_nbre_marqueurs = seuil_nbre_marqueurs
        self.conclusion = conclusion
        self.seuil_hauteur = seuil_hauteur
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
