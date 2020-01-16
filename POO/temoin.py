from individus import Individus

class Temoin(Individus):
    """ Common informations between mother, fetus and father

        Attributes :
            data (dict) : markers, alleles, heights and informatif character
    """

    def __init__(self, ID, data):
        """ The constructor for Patient class

            Parameters :
            ID (str) : name
            genre (str) ["pos", "neg"] : type of 
            data (dict)
        """
        super().__init__(ID, data)
        self.TPOS = {"AMEL":["X","Y"], "CSF1PO":[12],"D13S317":[9,11],"D16S539":[9,13], "D18S51":[16,18], "D21S11":[29,31.2], "D3S1358":[17,18], "D5S818":[12],"D7S820":[8,11], "D8S1179":[14,15], "FGA":[20,23], "Penta_D":[12,13], "Penta_E":[7,14], "TH01":[6,9.3], "TPOX":[11], "vWA":[16,19]} #2800M

    def check(self):
        listeFalse = []
        for marqueur in self.TPOS.keys():
            if (self.ID == "TPOS" and self.data[marqueur]["Allele"] != self.TPOS[marqueur]) or (self.ID == "TNEG" and self.data[marqueur]["Allele"] != []) :
                listeFalse.append(marqueur)
        return listeFalse
