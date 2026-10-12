# GENDARMERIE DESK — édition SQLite

Application Streamlit de démonstration pour organiser des dossiers administratifs, activités, échéances, documents et rapports. **Aucune connexion Supabase n'est utilisée.** La base SQLite est créée automatiquement.

## 1. Prérequis
- Python 3.10 ou supérieur
- Connexion Internet uniquement pour installer les dépendances

## 2. Installation sous Windows
1. Décompressez le ZIP dans un dossier de votre choix.
2. Ouvrez PowerShell ou l'invite de commandes dans ce dossier.
3. Créez un environnement virtuel (recommandé) :
   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
4. Installez les dépendances :
   ```powershell
   python -m pip install -r requirements.txt
   ```
5. Lancez l'application :
   ```powershell
   python -m streamlit run app.py
   ```
6. Au premier lancement, créez votre nom d'utilisateur et un mot de passe d'au moins 12 caractères.

## 3. Installation sous Linux/macOS
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

## 4. Stockage
La base est créée ici : `data/gendesk.sqlite3`.
Les pièces jointes sont stockées dans `data/documents/`.
Les sauvegardes sont stockées dans `data/backups/`.

Vous pouvez définir un autre emplacement de données avec la variable d'environnement `GENDARMERIE_DESK_DATA`.

## 5. Utilisation sur téléphone
Par défaut, l'application est locale sur l'ordinateur. Pour un test sur le même réseau Wi-Fi, lancez :
```bash
python -m streamlit run app.py --server.address 0.0.0.0
```
Puis, depuis le téléphone connecté au même réseau, ouvrez l'adresse IP locale de l'ordinateur suivie du port `:8501`. Le pare-feu et le réseau doivent autoriser cet accès. Ne redirigez pas ce port directement vers Internet.

## 6. Important sur GitHub public et Streamlit Community Cloud
- Ne poussez jamais le dossier `data/`, des fichiers SQLite, pièces jointes, mots de passe ou secrets vers un dépôt public.
- SQLite et les fichiers locaux peuvent être effacés lors d'un redéploiement ou ne pas être partagés durablement sur un hébergement cloud éphémère. Cette version est destinée d'abord à un usage local/test.
- Pour un accès à distance persistant depuis différents réseaux, il faudra une infrastructure approuvée avec stockage persistant et protections adaptées. Ne mettez pas de données judiciaires, personnelles sensibles ou opérationnelles sur un hébergement public sans autorisation explicite du service compétent.

## 7. Fonctions incluses
- Connexion utilisateur individuel, création du mot de passe au premier lancement et changement de mot de passe.
- Tableau de bord et indicateurs automatiques.
- Modules de dossiers/enquêtes administratives, auditions, activités de service, agenda, consignes, encadrement, matériel, formation et rapports.
- Registre des personnes et gestion documentaire avec pièces jointes locales.
- Recherche, création, modification, suppression et journal d'audit.
- Exports CSV, Excel et PDF.
- Sauvegarde SQLite et restauration depuis une sauvegarde compatible.

## 8. Limites et usage responsable
Cette application est un prototype administratif générique. Elle ne remplace pas les logiciels officiels, les procédures ou les modèles de procès-verbaux approuvés. Ne saisissez que des données que vous êtes autorisé à traiter et stockez-les dans un environnement validé par l'autorité compétente. Un mot de passe unique ne suffit pas à sécuriser un service exposé sur Internet.
