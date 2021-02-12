import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4,landscape
from reportlab.platypus import Image, Table, TableStyle, Paragraph
from reportlab.lib.units import cm
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.styles import getSampleStyleSheet
import re

from echantillon import *

def head_page():
    """
    Define the head of the report and it's content
    """
    pass

def table_mother_not_concordant():
    """
    Define the table for not concordant data with the mother
    """
    pass

def table_father_not_concordant():
    """
    Define the table for not concordant dna with father and contamination analysis
    """
    pass

def table_analysis():
    """
    Define the table for the analysis
    """
    pass

def report(output_path, echantillon, conclusion, user, seuil_hauteur_pic, seuil_nb_marqueur, seuil_percent_conta_, tpos, tneg, entite, emetteur, version):
    """
    Define and create the pdf report for the analysis
    Input:
      path : path of the pdf
      echantillon (object): Echantillon object of the analysis
      conclusion (int) : Code value of the conclusion of the analysis
      user (str) : user name
      seuil_hauteur_pic (int) : Threshold used to decide if a signal should be considered as a contamination
      seuil_nb_marqueur (int) : Threshold used to decide the minimal number of contaminated marker needed to conclude on a contamination
      seuil_percent_conta (float) : Threshold for the minimal percentage to decide if a sample is contaminated as a whole
      tpos (bool) : indicates if the tpos is ok
      tneg (bool) : indicates if the tneg is ok
      entite (string) : sharepoint quality data
      emetteur (string) : sharepoint quality data
      version (string) : version of the software
    """
    head = head_page(entite, emetteur, version, echantillon.date)