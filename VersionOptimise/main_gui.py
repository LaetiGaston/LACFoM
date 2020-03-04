# coding: utf-8

# version application 1.0


import copy
import logging
import sys
import os
import time
from os.path import sep, expanduser, dirname, join

import kivy
from kivy.animation import Animation
from kivy.app import App
from kivy.config import Config
from kivy.core.window import Window
from kivy.factory import Factory
from kivy.garden.filebrowser import FileBrowser
from kivy.properties import *
from kivy.properties import ListProperty
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.uix.tabbedpanel import TabbedPanelHeader
from kivy.uix.checkbox import CheckBox
from kivy.utils import platform
from functools import partial

from datetime import datetime
from time import strftime
import pandas as pd
import traitement
import echantillon
import individus
import foetus
import mere
import pere
import temoin
import pdf_feuille_resultat

kivy.require('1.10.1')
Window.clearcolor = (0.949, 0.945, 0.945, 1)
Window.size = (1300, 790)

# Window.fullscreen = "auto"
Window.minimum_width = 1200
Window.minimum_height = 730

heure = datetime.now()
heure_vrai = heure.strftime("%d-%m-%Y_%Hh_%Mm")
log_filename = "log/log_" + heure_vrai + '.txt'
logging.basicConfig(filename=log_filename, filemode='w', format='%(name)s - %(levelname)s: %(message)s',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ScreenManagement(ScreenManager):
    pass


class EcranPremier(Screen):
    def show_load(self, nom_utilisateur):
        try:
            self.manager.get_screen('ecran_principale').ids.ecranMethod.show_load()
            self.manager.get_screen('ecran_principale').ids.ecranMethod.InfoParametre["nom_utilisateur"] = str(
                nom_utilisateur)
        except Exception as e:
            logger.error("Chargement écran échoué", exc_info=True)
            return

        logger.info("Changment d'écran réussi")


class EcranFct(Screen):
    pass


class TableOnglets(TabbedPanel):
    # override tab switching method to animate on tab switch
    def switch_to(self, header, **kwargs):
        anim = Animation(opacity=0, d=.24, t='in_out_quad')

        def start_anim(_anim, child, in_complete, *lt):
            _anim.start(child)

        def _on_complete(*lt):
            if header.content:
                header.content.opacity = 0
                anim = Animation(opacity=1, d=.20, t='in_out_quad')
                start_anim(anim, header.content, True)
            super(TableOnglets, self).switch_to(header)

        anim.bind(on_complete=_on_complete)
        if self.current_tab.content:
            start_anim(anim, self.current_tab.content, False)
        else:
            _on_complete()


class CloseableHeader(TabbedPanelHeader):
    panel = ObjectProperty(None)
    text1 = ObjectProperty(None)
    supr_onglets = ObjectProperty(None)


class LeaveDialog(BoxLayout):
    quitter = ObjectProperty(None)
    cancel = ObjectProperty(None)


class EcraserDialog(BoxLayout):
    save = path = ObjectProperty(None)
    path = ObjectProperty(None)
    filename = ObjectProperty(None)
    cancel = ObjectProperty(None)


class LoadDialog(FloatLayout):
    load = ObjectProperty(None)
    cancel = ObjectProperty(None)
    retour = ObjectProperty(None)
    ecran = ObjectProperty(None)
    path = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(LoadDialog, self).__init__(**kwargs)
        self.ids.drives_list.adapter.bind(on_selection_change=self.drive_selection_changed)

    def get_win_drives(self):
        if platform == 'win':
            import win32api

            drives = win32api.GetLogicalDriveStrings()
            drives = drives.split('\000')[:-1]

            return drives
        else:
            return []

    def drive_selection_changed(self, *args):
        selected_item = args[0].selection[0].text
        self.ids.file_chooser.path = selected_item


class ParametreDialog(FloatLayout):
    save_parametres = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)
    hauteur = ObjectProperty(None)
    nb = ObjectProperty(None)
    emetteur = ObjectProperty(None)
    entite = ObjectProperty(None)
    reinit_para = ObjectProperty(None)


class InfosConclusion(BoxLayout):
    TLigneInfo1 = ObjectProperty(None)
    TLigneInfo2 = ObjectProperty(None)
    TLigneInfo3 = ObjectProperty(None)


class ColSupp(BoxLayout):
    color = ObjectProperty(None)
    t_col = ObjectProperty(None)


class ConcordanceEtSexe(BoxLayout):
    info_sexe = ObjectProperty(None)
    conco_M = ObjectProperty(None)
    conco_P = ObjectProperty(None)
    colorconcoM = ListProperty((256, 256, 256, 1))
    colorconcoP = ListProperty((256, 256, 256, 1))
    image_pos=ObjectProperty(None)
    image_neg=ObjectProperty(None)


class LigneTableau(BoxLayout):
    t_col1 = ObjectProperty(None)
    t_col2 = ObjectProperty(None)
    t_col3 = ObjectProperty(None)
    color_mode = ObjectProperty(None)
    color_text = ListProperty((256, 256, 256, 1))
    color_text2 = ListProperty((256, 256, 256, 1))
    large = ObjectProperty(None)


class ResAnalyse(BoxLayout):
    save = path = ObjectProperty(None)
    path = ObjectProperty(None)
    nfoetus = ObjectProperty(None)
    nmere = ObjectProperty(None)
    npere = ObjectProperty(None)
    titre = ObjectProperty(None)
    NvGroupe = ObjectProperty(None)
    show_save = ObjectProperty(None)
    colorconcoM = (256, 256, 256, 1)
    colorconcoP = (256, 256, 256, 1)
    SaveLog = ObjectProperty(None)
    down_button = ObjectProperty(None)
    InfoParametre = {}
    filename = ""
    path = ""
    H = ObjectProperty(None)
    N = ObjectProperty(None)

    def attribut(self, InfoParametre):
        self.InfoParametre = copy.copy(InfoParametre)

    def remplissage(self, Echantillon):

        tableau_df = self.InfoParametre["df_conclusion"]
        
        conclusion = self.InfoParametre["df_detail"]
        
        try:
            #check des temoins
            #TODO : gestion exception
            if len(Echantillon.tpos.check()) > 0:
                final_decision_pos = "cross.png"
                self.InfoParametre["temoin_positif"]=0
            else:
                final_decision_pos = "check.png"
                self.InfoParametre["temoin_positif"]=1
            if len(Echantillon.tneg.check()) > 0:
                final_decision_neg = "cross.png"
                self.InfoParametre["temoin_negatif"]=0
            else:
                final_decision_neg = "check.png"
                self.InfoParametre["temoin_negatif"]=1
            
            

            #####Concordance#######
            if(Echantillon.concordance_pere_foet):
                concordance_pere="OUI"
            elif( Echantillon.concordance_pere_foet==False):
                concordance_pere="NON"
                self.colorconcoP = (241 / 256, 31 / 256, 82 / 256, 1)
            else:
                concordance_pere="ABS"
                self.colorconcoP = ( 256, 256,256, 1)
            if(Echantillon.concordance_mere_foet):
                concordance_mere="OUI"
            else:
                concordance_mere="NON"
                self.colorconcoM = (241 / 256, 31 / 256, 82 / 256, 1)
            
            BoxConcordance = ConcordanceEtSexe(info_sexe="Sexe foetus : " + Echantillon.foetus.get_sexe(),
                                               conco_M=concordance_mere,
                                               conco_P=concordance_pere,
                                               colorconcoM=self.colorconcoM,
                                               colorconcoP=self.colorconcoP,
                                               image_pos = final_decision_pos,
                                               image_neg = final_decision_neg)
            self.ids.TitreEtConco.add_widget(BoxConcordance)

            if Echantillon.concordance_mere_foet:
                entete = LigneTableau(t_col1='[b]' + "Marqueurs" + '[/b]',
                                      t_col2='[b]' + "Conclusions" + '[/b]',
                                      t_col3='[b]' + "Détails" + '[/b]',
                                      color_mode=(75 / 255, 127 / 255, 209 / 255, 1),
                                      color_text=(0.949, 0.945, 0.945, 1),
                                      color_text2=(0.949, 0.945, 0.945, 1))
                if Echantillon.get_contamine():
                    self.ids.TButtonContamine.state = 'down'

                else:
                    self.ids.TButtonNonContamine.state = 'down'
                self.ids.le_tableau.add_widget(entete)

                parti_conclu = InfosConclusion(
                    TLigneInfo1="Nombre de marqueurs informatifs non contaminés: " + str(conclusion[0]),
                    TLigneInfo2="Nombre de marqueurs informatifs contaminés: " + str(conclusion[1]),
                    TLigneInfo3="Moyenne du pourcentage de contamination: " + str(conclusion[2])
                )
                self.ids.ensemble_info.add_widget(parti_conclu)

                for i in range(len(tableau_df.index)):
                    colortext = (256, 256, 256, 1)
                    colmode = (49 / 255, 140 / 255, 231 / 255, 0.2)
                    t_col2 = tableau_df["Conclusion"][i]
                    if tableau_df["Conclusion"][i] == 'Non contaminé':
                        colortext = (23 / 256, 116 / 256, 10 / 256, 1)
                    if tableau_df["Conclusion"][i] == 'Contaminé':
                        t_col2 = '[b]' + tableau_df["Conclusion"][i] + '[/b]'
                        colortext = (241 / 256, 31 / 256, 82 / 256, 1)
                    if tableau_df["Conclusion"][i] == "Non informatif":
                        colmode = (0.949, 0.945, 0.945, 0.2)
                    ligne = LigneTableau(t_col1=tableau_df["Marqueur"][i],
                                         t_col2=t_col2,
                                         t_col3=tableau_df["Détails M/F"][i],
                                         color_mode=colmode,
                                         color_text2=colortext)
                    self.ids.le_tableau.add_widget(ligne)
            else:
                if Echantillon.concordance_pere_foet or Echantillon.concordance_pere_foet == None:
                    entete = LigneTableau(t_col1="Marqueurs",
                                          t_col2="Concordance Mere/Foetus",
                                          t_col3="Détails",
                                          color_mode=(75 / 255, 127 / 255, 209 / 255, 1),
                                          color_text=(0.949, 0.945, 0.945, 1),
                                          color_text2=(0.949, 0.945, 0.945, 1)
                                          )
                    self.ids.le_tableau.add_widget(entete)

                    self.ids.togglebutonEtLabel.clear_widgets()
                    new_label = Label(text="Analyse non réalisée", color=(241 / 256, 31 / 256, 82 / 256, 1),
                                      font_size=30)
                    self.ids.togglebutonEtLabel.add_widget(new_label)
                    self.ids.labelPrelev.font_size = 30
                    self.ids.labelPrelev.color = (241 / 256, 31 / 256, 82 / 256, 1)

                    for i in range(len(tableau_df.index)):
                        colortext = (256, 256, 256, 1)
                        colmode = (49 / 255, 140 / 255, 231 / 255, 0.2)
                        if tableau_df["Concordance Mere/Foetus"][i] == 'NON':
                            colortext = (241 / 256, 31 / 256, 82 / 256, 1)
                        ligne = LigneTableau(t_col1=tableau_df["Marqueur"][i],
                                             t_col2=tableau_df["Concordance Mere/Foetus"][i],
                                             t_col3=tableau_df["Détails M/F"][i],
                                             color_mode=colmode,
                                             color_text2=colortext)
                        self.ids.le_tableau.add_widget(ligne)


                else:
                    entete = LigneTableau(t_col1="Marqueurs",
                                          t_col2="Concordance Mere/Foetus",
                                          t_col3="Détails M/F", color_mode=(75 / 255, 127 / 255, 209 / 255, 1),
                                          color_text=(0.949, 0.945, 0.945, 1),
                                          color_text2=(0.949, 0.945, 0.945, 1),
                                          large=0.20)

                    col4 = Label(text="Concordance Pere/Foetus", color=(0.949, 0.945, 0.945, 1))
                    col5 = Label(text="Détails P/F", color=(0.949, 0.945, 0.945, 1))
                    entete.add_widget(col4)
                    entete.add_widget(col5)
                    self.ids.le_tableau.add_widget(entete)
                    self.ids.togglebutonEtLabel.clear_widgets()
                    new_label = Label(text="Analyse non réalisée", color=(241 / 256, 31 / 256, 82 / 256, 1),
                                      font_size=30)
                    self.ids.togglebutonEtLabel.add_widget(new_label)

                    self.ids.labelPrelev.color = (241 / 256, 31 / 256, 82 / 256, 1)

                    for i in range(len(tableau_df.index)):
                        if tableau_df["Concordance Mere/Foetus"][i] == 'NON':
                            for i in range(len(tableau_df.index)):
                                colortext = (256, 256, 256, 1)
                                colmode = (49 / 255, 140 / 255, 231 / 255, 0.2)
                                if tableau_df["Concordance Mere/Foetus"][i] == 'NON':
                                    colortext = (241 / 256, 31 / 256, 82 / 256, 1)
                                else:
                                    colmode = (0.949, 0.945, 0.945, 0.2)
                                if tableau_df["Concordance Pere/Foetus"][i] == 'NON':
                                    col4 = ColSupp(t_col=tableau_df["Concordance Pere/Foetus"][i],
                                                   color=(241 / 256, 31 / 256, 82 / 256, 1))
                                else:
                                    col4 = ColSupp(t_col=tableau_df["Concordance Pere/Foetus"][i],
                                                   color=(256, 256, 256, 1))
                                    colmode = (0.949, 0.945, 0.945, 0.2)
                                ligne = LigneTableau(t_col1=tableau_df["Marqueur"][i],
                                                     t_col2=tableau_df["Concordance Mere/Foetus"][i],
                                                     t_col3=tableau_df["Détails M/F"][i],
                                                     color_mode=colmode,
                                                     color_text2=colortext)

                                col5 = Label(text=tableau_df["Détails P/F"][i], color=(256, 256, 256, 1),
                                             text_size=(self.width, None))
                                col5a = ColSupp(t_col=tableau_df["Détails P/F"][i], color=(256, 256, 256, 1))
                                ligne.add_widget(col4)
                                ligne.add_widget(col5a)

                                self.ids.le_tableau.add_widget(ligne)


        except Exception as e:
            logger.error("Remplissage de la page échouée", exc_info=True)
        logger.info("Remplissage de la page réussi")

    def CouleurBouton(self, id):

        if id == 0:
            self.ids.TButtonNonContamine.background_color = (23 / 256, 116 / 256, 10 / 256, 1)
            self.ids.TButtonNonContamine.color = [0.949, 0.945, 0.945, 1]
            self.ids.TButtonContamine.background_color = (220 / 255, 220 / 255, 220 / 255, 1)
            self.ids.TButtonContamine.color = [130 / 256, 130 / 256, 130 / 256, 1]
        else:
            self.ids.TButtonContamine.background_color = (241 / 256, 31 / 256, 82 / 256, 1)
            self.ids.TButtonContamine.color = [0.949, 0.945, 0.945, 1]
            self.ids.TButtonNonContamine.background_color = (220 / 256, 220 / 256, 220 / 256, 1)
            self.ids.TButtonNonContamine.color = [130 / 256, 130 / 256, 130 / 256, 1]


class getInput(Popup):
    def __init__(self, data, **kwargs):
            Popup.__init__(self, **kwargs)
            self.data = data
            self.GridLayout = GridLayout(cols=5, rows=5)

            self.checkBox_a = CheckBox(group="mother")
            self.checkBox_a2 = CheckBox(group="mother")
            self.checkBox_a3 = CheckBox(group = "mother")

            self.checkBox_b = CheckBox(group="foetus")
            self.checkBox_b2 = CheckBox(group="foetus")
            self.checkBox_b3 = CheckBox(group = "foetus")

            self.checkBox_c = CheckBox(group="pere")
            self.checkBox_c2 = CheckBox(group="pere")
            self.checkBox_c3 = CheckBox(group="pere")

            self.LabelEmpty = Label(text="")
            self.GridLayout.add_widget(self.LabelEmpty)

            self.LabelMother = Label(text="Mère")
            self.GridLayout.add_widget(self.LabelMother)

            self.LabelFoetus = Label(text="Foetus")
            self.GridLayout.add_widget(self.LabelFoetus)

            self.LabelFather = Label(text="Père")
            self.GridLayout.add_widget(self.LabelFather)

            self.GridLayout.add_widget(Label(text=""))

            self.LabelID1 = Label(text=data[0])
            self.GridLayout.add_widget(self.LabelID1)
            
            self.GridLayout.add_widget(self.checkBox_a)

            self.GridLayout.add_widget(self.checkBox_a2)
            self.GridLayout.add_widget(self.checkBox_a3)
            self.GridLayout.add_widget(Label(text=""))
            
            self.LabelID2 = Label(text=data[1])
            self.GridLayout.add_widget(self.LabelID2)

            self.GridLayout.add_widget(self.checkBox_b)
            self.GridLayout.add_widget(self.checkBox_b2)
            self.GridLayout.add_widget(self.checkBox_b3)
            self.GridLayout.add_widget(Label(text=""))

            self.LabelID3 = Label(text=data[2])
            self.GridLayout.add_widget(self.LabelID3)

            self.GridLayout.add_widget(self.checkBox_c)
            self.GridLayout.add_widget(self.checkBox_c2)
            self.GridLayout.add_widget(self.checkBox_c3)
            self.GridLayout.add_widget(Label(text=""))
            self.GridLayout.add_widget(Label(text=""))
            self.GridLayout.add_widget(Label(text=""))
            self.GridLayout.add_widget(Label(text=""))
            self.GridLayout.add_widget(Label(text=""))
            
            self.cancelButton = Button()
            self.cancelButton.text = 'Cancel'
            self.cancelButton.size_hint = (0.2,0.2)

            self.okButton = Button()
            self.okButton.text="OK"
            self.okButton.size_hint=(0.20,0.20)

            self.GridLayout.add_widget(self.okButton)

            self.title="Identification des individus"
            self.content = self.GridLayout
            self.size_hint=(0.9, 0.9)
            self.auto_dismiss=False
            
            self.cancelButton.bind(on_press = self.cancelButtonPress)
            self.okButton.bind(on_press = self.okButtonPress)

            self.samples = {}

            self.notDone = True


    def getResult(self):
        print("in get results du popup")
        #self.open()
        while True:
            print("waiting for chackbox selection")
        print("after open popup")

    def onClose(self):
            return

    def okButtonPress(self, instance):
        print(" ****************** okButtonPressed ***************************")
        ID1 = [self.checkBox_a.active, self.checkBox_b.active, self.checkBox_c.active]
        ID2 = [self.checkBox_a2.active, self.checkBox_b2.active, self.checkBox_c2.active]
        ID3 = [self.checkBox_a3.active, self.checkBox_b3.active, self.checkBox_c3.active]
        print(ID1)
        print(ID2)
        print(ID3)
        if ID1.count(True) == 2 or ID2.count(True) == 2 or ID3.count(True) == 2:
            print("Deux echantillons meme origine")
            self._popupEr = Popup(title="Erreur", content=Label(text="Deux échantillons ne peuvent avoir la même origine"),
                            size_hint=(0.3, 0.3))
            self._popupEr.open()
        elif ID1.count(True) == 0 or ID2.count(True) == 0 or ID3.count(True) == 0:
            print("Un echantillon n'a pas été attribué")
            self._popupEr = Popup(title="Erreur", content=Label(text="Un échantillon n'a pas été attribué"),
                            size_hint=(0.3, 0.3))
            self._popupEr.open()
        else:
            self.samples["mother"] = self.data[ID1.index(True)]
            self.samples["foetus"] = self.data[ID2.index(True)]
            self.samples["father"] = self.data[ID3.index(True)]
            print(self.samples)
            print("Quit fonction okButton Pressed")
            self.notDone = False
            self.dismiss()
        return

    def getSamples(self):
        self.notDone = True
        self.open()          
        self.rootWindow = self.get_root_window()
        
        while self.notDone :
            #sys.stdout.write("Sleeping\n")
            time.sleep(0.01)
            self.rootWindow._mainloop()
        
        if self.samples == {}:
            return ""
        else:    
            return self.samples

    def cancelButtonPress(self):
        sys.stdout.write('Cancel button was pressed \n')
        self.dismiss()
        self.notDone = False
        return

class EcranFctMethod(GridLayout):
    loadfile = ObjectProperty(None)
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)
    hauteur = "1/3"
    conta = 5
    nb = 2
    InfoParametre = {}
    onglets = {}
    nb_header = 0
    choix = 0
    retour = False
    cpt = 0
    InfoParametre["choix"] = None
    emetteur = "PBP-P2A-GEN"
    entite = "PBP-PTBM"
    memory_path = join(expanduser('~'), 'Desktop')

    def dismiss_popup(self):
        self._popup.dismiss()

    def dismiss_load(self, instance):
        self._popup.dismiss()

    def dismiss_popups(self):
        self.popup2.dismiss()
        self._popup.dismiss()

    def show_load(self):
        """  Display a pop up windows with the FileChooser for loading purpose
                        """

        self.hauteur = "1/3"
        self.nb = 2

        if platform == 'win':
            user_path = dirname(expanduser('~')) + sep + 'Documents'
        else:
            user_path = expanduser('~') + sep + 'Documents'

        browser = FileBrowser(select_string='Sélectionner',
                              path=self.memory_path,
                              favorites=[(user_path, 'Documents')],
                              filters=["*.txt"],
                              dirselect=True)
        browser.bind(
            on_success=self._fbrowser_success,
            on_submit=self._fbrowser_submit,
            on_canceled=self.dismiss_load)

        self._popup = Popup(title='Ouvrir un fichier', content=browser, size_hint=(0.9, 0.9))
        self._popup.open()
        if self.retour:
            return True

    def _fbrowser_success(self, instance):
        print("sucess")
        if self.load(instance.path, instance.selection):
            if self.compute():
                self.panel.manager.current = "ecran_principale"
                self.memory_path = instance.path

    def _fbrowser_submit(self, instance):
        print("submit")
        if self.load(instance.path, instance.selection):
            if self.compute():
                self.panel.manager.current = "ecran_principale"
                self.memory_path = instance.path

    def retour_conclusion(self, retour):
        self.retour = retour

    def cpt_onglets(self, titre):
        if titre in self.onglets:
            final_titre = titre + "(" + str(self.onglets[titre]) + ")"
            self.onglets[titre] += 1
            return final_titre
        else:

            self.onglets[titre] = 1
            return titre

    def load(self, path, filename):
        """ Call the functions and methods from Traitement2 with default parameters, path and filename
                chose by user. Gather result from them and put it in attributes of an instance of ResAnalyse
                """
        try:
            # lecture du fichier et traitement
            data = traitement.lecture_fichier(os.path.join(path, filename[0]))
            if not isinstance(data, list):
                self._popupEr = Popup(title="Erreur", content=Label(text=Echantillon),
                            size_hint=(0.3, 0.3))
                self._popupEr.open()
                return

            myPopupLoad = getInput(data[0])
            #myPopupLoad.bind(on_dismiss=self.compute())
            #myPopupLoad.open()
            self.dictsamples = myPopupLoad.getSamples()
            print("Get samples: ")
            print(self.dictsamples)
            self.data = data[1]
            self.instance_path = path
            self.filename = filename
        except Exception as e:

            logger.error("Chargement données impossible", exc_info=True)

            return False
        logger.info("Chargement des données réussi")
        #self.compute()
        return True
            

    def compute(self):
        try:
            Echantillon = traitement.computedata(self.dictsamples, self.data)
            self.InfoParametre["Echantillon"]=Echantillon
            if not isinstance(Echantillon, traitement.Echantillon):
                self._popupEr = Popup(title="Erreur", content=Label(text=Echantillon),
                            size_hint=(0.3, 0.3))
                self._popupEr.open()
                return
            code = traitement.concordance_ADN(Echantillon)
            if code:
                self._popupEr = Popup(title="Erreur", content=Label(text=code),
                            size_hint=(0.3, 0.3))
                self._popupEr.open()
            logger.info("fonction lecture fichier réussi")
            Echantillon.set_seuil_hauteur(eval(self.hauteur))
            Echantillon.set_seuil_nbre_marqueurs(float(self.nb))
            logger.info("Attribution des taux réussi")
            Echantillon.analyse_marqueur()
            logger.info("Fonction analyse_données réussi")
            # récupération et attribution de données
            self.titre = self.cpt_onglets(Echantillon.get_id())
            nv_onglets = CloseableHeader(text1=self.titre + "  ", panel=self.ids.les_onglets,
                                         supr_onglets=self.supr_onglets)

            self.InfoParametre["Sexe"] = Echantillon.foetus.get_sexe()
            self.InfoParametre["df_conclusion"] = pd.DataFrame.from_dict(Echantillon.get_resultats())
            self.InfoParametre["df_detail"] = Echantillon.get_conclusion()
            self.InfoParametre["code_conclu"] = Echantillon.get_contamine()
            self.InfoParametre["nom_projet"] = Echantillon.get_id()
            self.InfoParametre["nom_mere"] = Echantillon.mere.ID
            self.InfoParametre["Emetteur"] = self.emetteur
            self.InfoParametre["Entite_appli"] = self.entite
            self.InfoParametre["nom_pdf"] = self.titre + "_" + self.InfoParametre["nom_utilisateur"]
            self.InfoParametre["Version"] = str(version)
            logger.info("Récupération des données réussi")
            if Echantillon.concordance_pere_foet == None:
                self.InfoParametre["num_pere"] = "ABS"
                self.InfoParametre["pres_pere"] = "ABS"
            else:
                self.InfoParametre["num_pere"] = Echantillon.pere.ID
                self.InfoParametre["pres_pere"] = "OUI"
            self.InfoParametre["num_foetus"] = Echantillon.foetus.ID
            self.InfoParametre["filename"] = self.filename
            self.InfoParametre["path"] = self.instance_path
            self.InfoParametre["nb"] = str(self.nb)
            self.InfoParametre["hauteur"] = self.hauteur
            contenu_res = ResAnalyse(
                titre=self.titre,
                nfoetus=self.InfoParametre["num_foetus"],
                npere=self.InfoParametre["num_pere"],
                nmere=self.InfoParametre["nom_mere"],
                NvGroupe=len(self.ids.les_onglets.tab_list),
                save=self.save,
                down_button=self.down_button,
                H=self.hauteur,
                N=str(self.nb))
            contenu_res.attribut(self.InfoParametre)
            contenu_res.remplissage(Echantillon)
            self.content = contenu_res
            nv_onglets.content = self.content

            self.ids.les_onglets.add_widget(nv_onglets)
            self.ids.les_onglets.switch_to(nv_onglets, )
            self.dismiss_popup()
            self.cpt = self.cpt + 1

        except Exception as e:
            
            logger.error("Traitement des données impossible", exc_info=True)

            return False
        logger.info("Traitement des données réussi")

        return True

    def change_onglets(self):
        if len(self.ids.les_onglets.get_tab_list()) != 0:
            self.ids.les_onglets.switch_to(self.ids.les_onglets.get_tab_list()[0], )
        else:
            self.panel.manager.current = "EcranAccueil"
            self.retour = False

    def supr_onglets(self, id):

        self.ids.les_onglets.remove_widget(id)
        self.change_onglets()

    def save(self):
        """Call function for creating pdf and test if the automatic conclusion have been changed"""

        filename = self.ids.les_onglets.current_tab.content.InfoParametre["nom_pdf"]
        self.instance_path = os.path.join("temp_pdf")
        try:
            if (self.ids.les_onglets.current_tab.content.InfoParametre["choix"] == 0 and
                    self.ids.les_onglets.current_tab.content.InfoParametre["code_conclu"] == 0):
                conclu = 0
            elif (self.ids.les_onglets.current_tab.content.InfoParametre["choix"] == 1 and
                  self.ids.les_onglets.current_tab.content.InfoParametre["code_conclu"] == 1):
                conclu = 1
            elif (self.ids.les_onglets.current_tab.content.InfoParametre["choix"] == 0 and
                  self.ids.les_onglets.current_tab.content.InfoParametre["code_conclu"] == 1):
                conclu = 2
            elif (self.ids.les_onglets.current_tab.content.InfoParametre["choix"] == 1 and
                  self.ids.les_onglets.current_tab.content.InfoParametre["code_conclu"] == 0):
                conclu = 3
            else:
                conclu = self.ids.les_onglets.current_tab.content.InfoParametre["code_conclu"]
        except Exception as e:
            logger.error("Echec atribution varaible conclu", exc_info=True)
            return
        while True:
            try:
                pdf_feuille_resultat.creation_PDF(os.path.join("temp_pdf"),
                                                  self.InfoParametre["Echantillon"],
                                                  self.InfoParametre["nom_pdf"],
                                                  conclu,
                                                  self.InfoParametre["nom_utilisateur"],
                                                  self.ids.les_onglets.current_tab.content.InfoParametre["hauteur"],
                                                  self.ids.les_onglets.current_tab.content.InfoParametre["nb"],
                                                  None,
                                                  self.ids.les_onglets.current_tab.content.InfoParametre["temoin_positif"],
                                                  self.ids.les_onglets.current_tab.content.InfoParametre["temoin_negatif"],
                                                  self.ids.les_onglets.current_tab.content.InfoParametre[
                                                      "Entite_appli"],
                                                  self.ids.les_onglets.current_tab.content.InfoParametre["Emetteur"],
                                                  self.ids.les_onglets.current_tab.content.InfoParametre["Version"])
                self.dismiss_popup()
                break
            except OSError as e:
                self.ids.les_onglets.current_tab.content.InfoParametre["nom_projet"] += "I"
                filename += "I"

                logger.error("Echec lancement créaton pdf", exc_info=True)
                continue
        logger.info("Création pdf réussi")
        if platform == 'linux':
            os.system("xdg-open " + os.path.join("temp_pdf",filename ) + ".pdf")
        else:
            os.system('start ' + os.path.join("temp_pdf") + "\\" + filename + ".pdf")

    def down_button(self, num):

        self.ids.les_onglets.current_tab.content.InfoParametre["choix"] = num

    def ouverture_manuel(self):
        logger.info("Ouverture manuel pdf réussi")
        if platform == 'linux':
            os.system("xdg-open " + os.path.join("Manuel_utilisateur") + ".pdf")
        else:
            os.system('start ' + os.path.join("Manuel_utilisateur") + ".pdf")

    def ouverture_parametres(self):
        """  Display a pop up windows with the parameters
                                        """
        try:
            content = ParametreDialog(hauteur=str(self.ids.les_onglets.current_tab.content.InfoParametre["hauteur"]),
                                      nb=str(self.ids.les_onglets.current_tab.content.InfoParametre["nb"]),
                                      save_parametres=self.save_parametres,
                                      emetteur=self.ids.les_onglets.current_tab.content.InfoParametre["Emetteur"],
                                      entite=self.ids.les_onglets.current_tab.content.InfoParametre["Entite_appli"],
                                      cancel=self.dismiss_popup)
            self._popup = Popup(title="Modifier des paramètres",
                                content=content,
                                size_hint=(0.9, 0.9))
            self._popup.open()
        except Exception as e:
            logger.error("Ouverture paramètre impossible", exc_info=True)
            return
        logger.info("Ouverture paramètre réussi")

    def save_parametres(self, p1, p3, p4, p5):
        """  The new parameters of the analysis are put in temp attributes(EcranFctmethod's attributes)
                and a new analysis is started(load method)
                                        """
        try:
            self.nb = p1
            self.hauteur = p3
            self.emetteur = p4
            self.entite = p5
            #self.load(self.ids.les_onglets.current_tab.content.InfoParametre["path"],
            #          self.ids.les_onglets.current_tab.content.InfoParametre["filename"])
            self.compute()
            self.dismiss_popup()
        except Exception as e:
            logger.error("Changement paramètres échoué nb(attendu)=entier,nb(indiqué)= " + str(
                p1) + ", hauteur(attendu)=entier ou fraction,hauteur(indiqué)=" + str(p3), exc_info=True)
            return
        logger.info("Changement paramètres réussi")

    def quitter(self):
        content = LeaveDialog(cancel=self.dismiss_popup, quitter=self.leaving_application)

        self._popup = Popup(title="Quitter", content=content,
                            size_hint=(0.4, 0.4))
        self._popup.open()


class MyApp(App):
    """It's the main Class application, kivy detect kv file automatically with a name in lowercase
        which is before the word App in the name of this class
        , example: MyApp will detect a the kv file my.kv or TestApp
        will detect the kv file test.kv
                                """

    Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

    title = 'LACFoM'

    def build(self):
        self.icon = 'logo.png'
        Window.bind(on_request_close=self.on_request_close)

    def on_request_close(self, *args):
        content = LeaveDialog(cancel=self.dismiss_popup, quitter=self.quitter)

        self.popup3 = Popup(title="Quitter", content=content,
                            size_hint=(0.4, 0.4))
        self.popup3.open()

        return True

    def quitter(self):
        for f in os.listdir("temp_pdf"):
            os.remove(os.path.join("temp_pdf", f))

        self.stop()

    def dismiss_popup(self):
        self.popup3.dismiss()


"""Factory register is for communicating name's Classes to the kv file
                                """

Factory.register('ResAnalyse', cls=ResAnalyse)
Factory.register('EcranPremier', cls=EcranPremier)
Factory.register('EcranFct', cls=EcranFct)
Factory.register('EcranFctMethod', cls=EcranFctMethod)
Factory.register('LoadDialog', cls=LoadDialog)
Factory.register('ParametreDialog', cls=ParametreDialog)
Factory.register('LigneTableau', cls=LigneTableau)
Factory.register('InfosConclusion', cls=InfosConclusion)
Factory.register('ConcordanceEtSexe', cls=ConcordanceEtSexe)
Factory.register('CloseableHeader', cls=CloseableHeader)
Factory.register('LeaveDialog', cls=LeaveDialog)
Factory.register('col_supp', cls=ColSupp)
if __name__ == '__main__':
    version = 1.0
    app = MyApp()
    app.run()
