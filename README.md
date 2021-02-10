# LACFoM

Pour rendre exécutable:

La version exécutable qui sera obtenue ne sera fonctionnelle que sur le système exploitation où la manipulation aura été effectuée.
PyInstaller est utilisé pour créer l'exécutable.

--------------------------------------Création du fichier spec--------------------------------------------------------

Regrouper l'ensemble des scripts python (pas le .kv, voir par la suite) ainsi que logo.ico dans un dossier. (Exemple ici V_demo_6)

Commande bash dans ce nouveau dossier créé:

    python -m PyInstaller --name LACFoM --icon C:\Users\laeti\Documents\2020\LACFoM\VersionOptimise\logo.ico main_gui.py

(remplacer chemin du logo)

Un fichier spec est créé dans le dossier suite à cette commande. Avant de modifier ce fichier spec, créer un dossier "data" dans le dossier contenant le fichier spec qui comportera le script my.kv et les images : croix.png, logo.png, loco_CHU.png, croos.png, check.png

---------------------------------------Modification du fichier spec----------------------------------------------------

Les modifications du fichier spec se basent sur la partie "Packaging a simple app" de la page suivante: https://kivy.org/doc/stable/guide/packaging-windows.html

1)Dans le fichier spec, en première ligne copier/coller la ligne suivante :

from kivy.deps import sdl2, glew

2)Ensuite, remplacer la partie coll par le copier/coller suivant :

coll = COLLECT(exe, Tree('examples-path\demo\touchtracer\'),

           a.binaries,
           
           a.zipfiles,
           
           a.datas,
           
           *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
           
           strip=False,
           
           upx=True,
           
           name='LACFoM')

Dans cette partie coll, spécifier le chemin du dossier "data" à la ligne : coll = COLLECT(exe, Tree('examples-path\demo\touchtracer\'),

3)Toujours dans le fichier spec, dans la partie "a = Analysis", à la ligne hiddenimports il faut écrire :

hiddenimports = ['win32timezone']

4)Dans la partie exe du fichier spec, remplacer : console=True par console=False

-------------------------------------------Création du exe------------------------------------------------------------

Commande bash dans le dossier contenant le fichier spec :

    python -m PyInstaller LACFoM.spec

La version exe se trouvera dans le dossier "dist" qui sera créé à la suite de cette commande.



python -m PyInstaller --name LACFoM --icon C:\Users\laeti\Documents\2020\LACFoM\VersionOptimiseTest\logo.ico main_gui.py
