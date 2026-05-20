@echo off
cd /d "C:\Users\user\OneDrive - 365\Bureau\automatiser le travaille"
echo [1/2] Consolidation Stock Produits Finis...
python consolidation_stock.py
echo [2/2] Consolidation Matieres Premieres...
python consolidation_mp.py
echo [3/3] Upload vers GitHub...
"c:\progra~1\git\bin\git.exe" add resultat_consolide.csv resultat_mp.csv
"c:\progra~1\git\bin\git.exe" commit -m "mise a jour"
"c:\progra~1\git\bin\git.exe" push
echo Mise a jour terminee le %date% a %time%
pause
