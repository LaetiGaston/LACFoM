from individus import Individus

class Foetus(Individus):
    """ Function exclusive to foetus
    """

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