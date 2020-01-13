from individus import Individus

class Temoin(Individus):
    """ Common informations between mother, fetus and father

        Attributes :
            data (dict) : markers, alleles, heights and informatif character
    """

    def __init__(self, ID, data, genre):
        """ The constructor for Patient class

            Parameters :
            ID (str) : name
            genre (str) ["pos", "neg"] : type of 
            data (dict)
        """
        super().__init__(ID, data)
        self.genre = genre
        self.TPOS = {"AMEL":["X","Y"], "CSF1PO":[12],"D13S317":[9,11],"D16S539":[9,13], "D18S51":[16,18], "D21S11":[29,31.2], "D3S1358":[17,18], "D5S818":[12],"D7S820":[8,11], "D8S1179":[14,15], "FGA":[20,23], "Penta_D":[12,13], "Penta_E":[7,14], "TH01":[6,9.3], "TPOX":[11], "vWA":[16,19]} #2800M

    def check(self):
        listeFalse = []
        for marqueur in self.TPOS.keys():
            if (self.genre == "pos" and self.data[marqueur] != self.TPOS[marqueur]) or (self.genre == "neg" and self.data[marqueur] != []) :
                listFalse.append(marqueur)
            elif self.genre not in ["pos", "neg"]:
                sys.out.write("Error: name %s unknown")
                return ["error"]
    
        return listeFalse