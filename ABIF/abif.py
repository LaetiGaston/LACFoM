from rpy2.robjects.packages import importr
from scipy import signal
import numpy as np
from numpy import mean
from numpy import median
from scipy.stats import linregress
import matplotlib.pyplot as plt

def lecture_fichier(file):
        #Permet d'ouvrir le fichier. J'ai identifié la position de chaque marqueur et je vais donc chercher les infos.
        #fl, joe, tmr et Marqueur_taille contiennent des valeurs de fluorescence
        seqinr = importr('seqinr')
        donnees = seqinr.read_abif(file)
        print(type(donnees))
        fl = donnees[2][39]
        joe = donnees[2][40]
        tmr = donnees[2][41]
        Marqueur_taille = donnees[2][42]
        return fl,joe,tmr,Marqueur_taille

def calibration(temps_migration,intensite_fluo):
        #Signal renvoie une liste avec les valeurs des pics mais également l'index dans la liste où on les cherche
        #Calibrage_x ce sont les valeurs du marqueur de taille qu'on utilise pour calibrer
        #C'est pour ça qu'il y a 3 pop, car on vire les pics de 500, 550 et 600
        position_pic = signal.find_peaks(x=intensite_fluo,height=0.55)
        calibrage_y = [100,120,140,160,180,200,225,250,275,300,325,350,375,400,425,450,475]
        calibrage_x = []
        for values in range(16,len(position_pic[0])):
                calibrage_x.append(position_pic[0][values])
        calibrage_x.pop()
        calibrage_x.pop()
        calibrage_x.pop()
        lr = linregress(calibrage_x,calibrage_y)
        return lr[0],lr[1]

def conversion_pb(temps,a,b):
        #Permet de convertir l'axe de temps en axe de pb
        pb = []
        for t in range(len(temps)):
                pb.append(a*temps[t] + b)
        return pb

        

def recuperation_points(donnees):
        values_x = []
        values_y = []
        for valu in range(len(donnees)):
                if donnees[valu]:
                        values_y.append(donnees[valu]/1000)
        for val in range(len(values_y)):
                values_x.append(val)
        return values_x, values_y

def echelle_allelique():
        #Les ranges dans lesquels on est censé avoir les marqueurs.
        #Retourne un dico ou chaque clé est un marqueur.
        #La clé permet d'accéder à une liste contenant deux listes.
        #La première liste correspond aux ranges alléliques (194,198,202,...)
        #La deuxième liste correspond au numéro d'allèle (11,12,13,...)
        csf1po = []
        d13s317 = []
        d16s539 = []
        d18s51 = []
        d21s11 = []
        d3s1358 = []
        d5s818 = []
        d7s820 = []
        d8s1179 = []
        fga = []
        penta_d = []
        penta_e = []
        th01 = []
        tpox = []
        vwa = []
        a_csf1po = []
        a_d13s317 = []
        a_d16s539 = []
        a_d18s51 = []
        a_d21s11 = []
        a_d3s1358 = []
        a_d5s818 = []
        a_d7s820 = []
        a_d8s1179 = []
        a_fga = []
        a_penta_d = []
        a_penta_e = []
        a_th01 = []
        a_tpox = []
        a_vwa = []
        for i in range(115,263,4):
                if i <= 147:
                        d3s1358.append(i)
                if i >= 119 and i <= 155:
                        d5s818.append(i)
                if i >= 123 and i <= 171:
                        vwa.append(i)
                if i >= 203 and i <= 259:
                        d21s11.append(i)
                if i >= 203 and i <= 247:
                        d8s1179.append(i)
                if i >= 215 and i <= 247:
                        d7s820.append(i)
        for i in range(156,308,4):
                if i <= 195:
                        th01.append(i)
                if i >= 176 and i <= 208:
                        d13s317.append(i)
                if i >= 264 and i <= 304:
                        d16s539.append(i)
        th01.append(195)
        th01.insert(6,179)
        th01.pop(9)
        th01.pop(9)
        for i in range(262,448,4):
                if i <= 290:
                        tpox.append(i)
                if i >= 290 and i <= 366:
                        d18s51.append(i)
                if i >= 322 and i <= 444:
                        fga.append(i)
        for i in range(321,361,4):
                csf1po.append(i)
        for i in range(374,454,5):
                penta_d.append(i)
        for i in range(379,478,5):
                penta_e.append(i)
        for i in range(len(d3s1358)):
                a_d3s1358.append(i+12)
        for i in range(len(d5s818)):
                a_d5s818.append(i+7)
        for i in range(len(vwa)):
                a_vwa.append(i+10)
        for i in range(len(d13s317)):
                a_d13s317.append(i+7)
        for i in range(len(d8s1179)):
                a_d8s1179.append(i+7)
        for i in range(len(d7s820)):
                a_d7s820.append(i+6)
        for i in range(len(tpox)):
                a_tpox.append(i+6)
        for i in range(len(d16s539)):
                a_d16s539.append(i+5)
        d16s539.pop(1)
        d16s539.pop(1)
        a_d16s539.pop(1)
        a_d16s539.pop(1)
        for i in range(len(csf1po)):
                a_csf1po.append(i+6)
        for i in range(len(penta_e)):
                a_penta_e.append(i+5)
        for i in range(6):
                a_th01.append(i+4)
        a_th01.append(9.3)
        a_th01.append(10)
        a_th01.append(11)
        a_th01.append(13.3)
        for i in range(len(d21s11)):
                a_d21s11.append(i+24)
        a_d21s11.insert(1,24.2)
        a_d21s11.insert(3,25.2)
        a_d21s11.insert(7,28.2)
        a_d21s11.insert(9,29.2)
        a_d21s11.insert(11,30.2)
        a_d21s11.insert(13,31.2)
        a_d21s11.insert(15,32.2)
        a_d21s11.insert(17,33.2)
        a_d21s11.insert(19,34.2)
        a_d21s11.insert(21,35.2)
        d21s11.insert(1,205)
        d21s11.insert(3,209)
        d21s11.insert(7,221)
        d21s11.insert(9,225)
        d21s11.insert(11,229)
        d21s11.insert(13,233)
        d21s11.insert(15,237)
        d21s11.insert(17,241)
        d21s11.insert(19,245)
        d21s11.insert(21,249)
        for i in range(len(d18s51)):
                a_d18s51.append(i+8)
        d18s51.insert(3,300)
        d18s51.insert(7,312)
        a_d18s51.insert(3,10.2)
        a_d18s51.insert(7,13.2)
        for i in range(len(fga)):
                a_fga.append(i+16)
        fga.insert(3,332)
        fga.insert(5,336)
        fga.insert(7,340)
        fga.insert(9,344)
        fga.insert(11,348)
        fga.insert(13,352)
        fga.insert(15,356)
        fga.insert(17,360)
        fga.insert(24,384)
        fga.insert(37,432)
        fga.insert(39,436)
        fga.insert(41,440)
        fga.insert(43,444)
        a_fga.insert(3,18.2)
        a_fga.insert(5,19.2)
        a_fga.insert(7,20.2)
        a_fga.insert(9,21.2)
        a_fga.insert(11,22.2)
        a_fga.insert(13,23.2)
        a_fga.insert(15,24.2)
        a_fga.insert(17,25.2)
        a_fga.insert(24,31.2)
        a_fga.insert(37,43.2)
        a_fga.insert(39,44.2)
        a_fga.insert(41,45.2)
        a_fga.insert(43,46.2)
        for i in range(len(penta_d)):
                a_penta_d.append(i+2)
        penta_d.insert(1,376)
        penta_d.insert(3,381)
        a_penta_d.insert(1,2.2)
        a_penta_d.insert(3,3.2)
        penta_d.pop(0)
        penta_d.pop(1)
        penta_d.pop(2)
        penta_d.pop(3)
        penta_d.pop(3)
        a_penta_d.pop(0)
        a_penta_d.pop(1)
        a_penta_d.pop(2)
        a_penta_d.pop(3)
        a_penta_d.pop(3)
        ech = {"D3S1358" : [d3s1358,a_d3s1358],
        "TH01" : [th01,a_th01], 
        "D21S11" : [d21s11,a_d21s11],
        "D18S51" : [d18s51,a_d18s51], 
        "Penta_E" : [penta_e,a_penta_e],
        "vWA" : [vwa,a_vwa],
        "D8S1179" : [d8s1179,a_d8s1179], 
        "TPOX" : [tpox,a_tpox],
        "FGA" : [fga,a_fga],
        "D5S818" : [d5s818,a_d5s818],
        "D13S317" : [d13s317,a_d13s317], 
        "D7S820" : [d7s820,a_d7s820], 
        "D16S539" : [d16s539,a_d16s539], 
        "CSF1PO" : [csf1po,a_csf1po], 
        "Penta_D" : [penta_d,a_penta_d]}
        return ech

def determination_allele(liste,valeur):
    #Recherche dichotomique
    #Retourne 100 si valeur n'est pas dans la liste.
    #Retourne la position du match dans la liste.
    #Pq la position ? Pcq le dico contient deux listes je rappelle pour chaque marqueur.
    #Une pour les ranges, une pour les numéros d'allèle.
    #Donc si en position 10 des ranges j'ai un match, je récupère 10 et je vais voir dans la liste des numéros d'allèle à la position 10 pour obtenir le numéro.
    #Ca part du principe que les deux listes sont forcément de même taille !
    moitie = len(liste) // 2
    entier = int(valeur)
    if entier < liste[0] or entier > liste[len(liste) - 1]:
        return 100
    if entier == liste[moitie]:
        return moitie
    elif entier > liste[moitie - 1] and entier < liste[moitie]:
        ecart1= valeur - liste[moitie - 1]
        ecart2 = valeur - liste[moitie]
        if abs(ecart1) < abs(ecart2):
            return moitie - 1
        else:
            return moitie
    elif entier > liste[moitie - 1]:
        return moitie + determination_allele(liste[moitie:],valeur)
    else:
        return determination_allele(liste[:moitie],valeur)

def determination_allele_fl(fluorescence,pb,echelle):
        #On récupère les pics pour le marqueur FL. Valeur seuil = 4 pour considérer un pic
        pics = signal.find_peaks(x=fluorescence,height=4)
        pics_en_pb = []
        infos = {}
        marqueur_FL = ["D3S1358","TH01","D21S11","D18S51","Penta_E"]
        for val in range(len(pics[0][12:])):
                pics_en_pb.append(pb[pics[0][12:][val]])
        #On parcourt les marqueurs. Premier marqueur : D3S1358
        #On parcourt la valeur de ces pics en paire de bases.
        #Ligne 286 : echelle[marqueur_FL[marqueur]][0] -> on prend dans le dico echelle, avec la clé correspondante, la liste des longueurs d'allèles ([0])
        #Ligne 287 : si différent de 100, il a donc trouvé, on ajoute donc dans la liste_alleles, le numéro d'allèle correspondant.
        # Avec [1] on obtient la liste des numéros d'allèles.
        #Avec [allele] on obtient la position à laquelle on a eu un match
        #On met tout ça où chaque clé est le nom d'un marqueur et cette clé permet d'accéder à une liste de numéro d'allèles
        for marqueur in range(len(marqueur_FL)):
                liste_alleles = []
                for pb in range(len(pics_en_pb)):
                        allele = determination_allele(echelle[marqueur_FL[marqueur]][0],pics_en_pb[pb])
                        if allele != 100:
                                liste_alleles.append(echelle[marqueur_FL[marqueur]][1][allele])
                                infos[marqueur_FL[marqueur]] = liste_alleles
        print(infos)


def determination_allele_tmr(fluorescence,pb,echelle):
        pics = signal.find_peaks(x=fluorescence,height=4)
        pics_en_pb = []
        infos = {}
        marqueur_TMR = ["vWA","D8S1179","TPOX","FGA"]
        for val in range(len(pics[0][22:])):
                pics_en_pb.append(pb[pics[0][22:][val]])
        for marqueur in range(len(marqueur_TMR)):
                liste_alleles = []
                for pb in range(len(pics_en_pb)):
                        allele = determination_allele(echelle[marqueur_TMR[marqueur]][0],pics_en_pb[pb])
                        if allele != 100:
                                liste_alleles.append(echelle[marqueur_TMR[marqueur]][1][allele])
                                infos[marqueur_TMR[marqueur]] = liste_alleles
        print(infos)

def determination_allele_joe(fluorescence,pb,echelle):
        pics = signal.find_peaks(x=fluorescence,height=4)
        pics_en_pb = []
        infos = {}
        marqueur_JOE = ["D5S818","D13S317","D7S820","D16S539","CSF1PO","Penta_D"]
        for val in range(len(pics[0][12:])):
                pics_en_pb.append(pb[pics[0][12:][val]])
        for marqueur in range(len(marqueur_JOE)):
                liste_alleles = []
                for pb in range(len(pics_en_pb)):
                        allele = determination_allele(echelle[marqueur_JOE[marqueur]][0],pics_en_pb[pb])
                        if allele != 100:
                                liste_alleles.append(echelle[marqueur_JOE[marqueur]][1][allele])
                                infos[marqueur_JOE[marqueur]] = liste_alleles
        print(infos)

if __name__ == "__main__":
        fl,joe,tmr,Marqueur_taille = lecture_fichier('12-XFRA181836_D11_2018-06-20-06-44-01.fsa')
        #fl,joe,tmr,Marqueur_taille = lecture_fichier('10-XFRA181848_B11_2018-06-20-06-44-01.fsa')
        xMarqueur,yMarqueur = recuperation_points(Marqueur_taille)
        xFl,yFl = recuperation_points(fl)
        xJoe,yJoe = recuperation_points(joe)
        xTmr,yTmr = recuperation_points(tmr)
        a,b = calibration(xMarqueur,yMarqueur)
        ech = echelle_allelique()
        xMarqueur_c = conversion_pb(xMarqueur,a,b)
        xFl_calibre = conversion_pb(xFl,a,b)
        xJoe_calibre = conversion_pb(xJoe,a,b)
        xTmr_calibre = conversion_pb(xTmr,a,b)
        determination_allele_fl(yFl,xFl_c,ech)
        determination_allele_tmr(yTmr,xTmr_c,ech)
        determination_allele_joe(yJoe,xJoe_c,ech)
