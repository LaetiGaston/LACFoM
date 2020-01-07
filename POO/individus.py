class Individus:
    """ Common informations between mother, fetus and father

        Attributes :
            data (dict) : markers, alleles, heights and informatif character
    """

    def __init__(self, ID, data):
        """ The constructor for Patient class

            Parameters :
            ID (str) : name
            data (dict)
        """
        self.ID = ID
        self.data = data


    def get_ID(self):
        return self.ID

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
