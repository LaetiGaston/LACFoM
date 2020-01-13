from individus import Individus

class Mere(Individus):
    """ Exclusive informations about the mother. Mere class inherits from Patient.
    """

    def __init__(self, ID, data):
        """ """
        # On appelle explicitement le constructeur de Personne :
        Individus.__init__(self, ID, data)
        

    
    def check_sex(self):
        for marqueur in self.data.keys():
            if 'Y' in self.data[marqueur]['Allele']:
                return False
        return True
        

    def homozygotie(self,allele_list):
        """ Detect if the mother is homozygous for the marker stutied.
            If it's true, homozygote is set to True
        """
        if self.allele[1] == 0.0:
            self.homozygote = True
