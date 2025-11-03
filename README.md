Mini projet ETRS711 : Application de gestion d’une cave à vin
=================================

Description
------
Application web Flask permettant de gérer des caves à vin. 
Il s’agit d’un projet universitaire réalisé dans le cadre de la ressource ETRS711 en première année de Master TRI à l’Université Savoie Mont Blanc. Ce mini projet a pour objectif pédagogique d’apprendre et de pratiquer la programmation orientée objet. Le langage utilisé est Python avec le micro‑framework Flask pour le développement web.

Fonctionnalités clés
--------------------
- Authentification simple: inscription et connexion par nom, prénom et mot de passe.
- Gestion des caves personnelles: création de caves, gestion des étagères, ajout et suppression de bouteilles.
- Ajout de bouteilles: domaine, nom, type (Rouge/Blanc/Rosé/Champagne), année, région, prix (€), photo d’étiquette (png/jpg/jpeg), quantité.
- Archivage: retrait de la cave avec note sur 20 et commentaire; historisation accessible dans la section Avis.
- Avis communautaires: agrégation des archives avec moyenne des notes et nombre d’avis par vin, détail des avis par vin.
- Tri dans l’interface de cave: tri par colonne (domaine, nom, type, année, région, quantité, étagère).
- Téléversement d’images: stockage dans `Code/static/images` avec nom de fichier unique.

Structure du projet
-------------------
- `Code/app.py`: application Flask, routes, logique métier d’orchestration et gestion des formulaires/uploads.
- `Code/db.py`: classe `DB` centralisant la connexion MySQL (utilise `mysql.connector`).
- `Code/GestionCave.py`: modèles et accès aux données MySQL (classes `Utilisateur`, `Cave`, `Etagere`, `Bouteille`, `BouteilleCave`, `BouteilleArchivee`).
- `Code/init_db.py`: script d’initialisation de la base de données et création des tables nécessaires.
- `Code/templates/`: templates Jinja2 (`base.html`, `index.html`, `login.html`, `register.html`, `creer_cave.html`, `mes_caves.html`, `explorer_caves.html`, `detail_cave.html`, `avis.html`, `avis_detail.html`).
- `Code/static/images/`: répertoire de stockage des images d’étiquettes téléversées (et images d’exemple).

Prérequis
---------
- Python 3.8+ (version minimale assurant la compatibilité avec Flask et mysql-connector-python)
- MySQL (service démarré et accessible en local)
- Pip pour installer les dépendances

Dépendances Python (à installer)
--------------------------------
Installez les paquets suivants (environnement virtuel facultatif) :

```
pip install flask mysql-connector-python
```

Remarque: `werkzeug`, `jinja2` et autres dépendances indirectes sont installées automatiquement via `flask`. Aucune autre dépendance n’est requise par le code fourni.

Configuration base de données
-----------------------------
- Adaptez les paramètres de connexion MySQL selon votre environnement local (utilisateur/mot de passe/host). Les paramètres de connexion par défaut sont définis dans `Code/db.py` (host=`127.0.0.1`, user=`root`, password=`""`, database=`gestioncave`).
- Initialisation de la base de données: exécutez `Code/init_db.py` pour créer la base `gestioncave` et les tables si elles n’existent pas.
-> Si vous utilisez le script d’initialisation de la base de donnée, pensez également à paramétrer paramètres de connexion dans `Code/init_db.py`.

Schéma de données (tables principales)
-------------------------------------
- `utilisateur(id, nom, prenom, mot_de_passe)`
- `cave(id, nom, id_utilisateur)`
- `etagere(id, nom, capacite, id_cave)`
- `bouteille(id, domaine_viticole, nom, type ENUM('Rouge','Blanc','Rosé','Champagne'), annee INT, region, photo_etiquette, prix DECIMAL(6,2))`
- `bouteille_cave(id, id_bouteille, id_etagere, date_mise_en_cave DATE)`
- `bouteille_archivee(id, id_bouteille, id_utilisateur, date_archivage DATE, note FLOAT, commentaire TEXT)`

Lancement rapide de l'application
-------------------
1) Copier le dossier `Code` en local
   - Placez le dossier `Code` dans l’emplacement de votre choix sur votre machine.
   - Si vous souhaitez utiliser l’upload d’images d’étiquette, vérifiez que le dossier `Code/static/images` existe (créez-le si nécessaire).

2) Installer les dépendances
```
pip install flask mysql-connector-python
```

3) Configurer MySQL
- Assurez-vous que MySQL est démarré.
- Si besoin, modifiez `Code/db.py` pour utiliser les bons identifiants.

4) Initialiser la base de données (création de `gestioncave` et des tables)
```
python Code/init_db.py
```

5) Lancer l’application Flask
```
python Code/app.py
```

6) Ouvrir le navigateur
- Accédez à `http://127.0.0.1:5000`
- Si vous n’êtes pas connecté, vous serez redirigé vers la page de connexion/inscription.

Utilisation
-----------------------------
- Inscription: `Inscription` puis création d’un compte (nom, prénom, mot de passe).
- Connexion: `Connexion` avec les identifiants saisis.
- Créer une cave: via `Créer une cave` (nom de la cave).
- Ajouter des étagères: depuis la page de détail de la cave (nom, capacité).
- Ajouter des bouteilles: formulaire sur la page de la cave (métadonnées, quantité, étagère, image d’étiquette optionnelle, prix).
- Archiver / Supprimer: actions disponibles par groupe de bouteilles; l’archivage permet de laisser une note (/20) et un commentaire.
- Avis: consulter la moyenne et le nombre d’avis par vin, puis le détail des avis.

Comportements et validations notables
------------------------------------
- Types autorisés: uniquement `Rouge`, `Blanc`, `Rosé`, `Champagne`.
- Upload d’images: formats `png`, `jpg`, `jpeg`; taille max 16MB; fichiers enregistrés dans `Code/static/images` avec un nom unique.
- Capacité d’étagère: l’application refuse d’ajouter des bouteilles si la capacité serait dépassée.
- Droits: seules les actions de modification/suppression d’une cave sont permises à son propriétaire.
- Tri: le tableau des bouteilles est triable côté serveur via les en-têtes de colonnes.

Routes principales
------------------
- `/` Accueil (redirige vers login si non connecté)
- `/login` (GET/POST) Connexion
- `/register` (GET/POST) Inscription
- `/logout` Déconnexion
- `/caves/creer` (GET/POST) Créer une cave
- `/caves/mes` Mes caves (utilisateur connecté)
- `/caves/explorer` Explorer toutes les caves
- `/caves/<cave_id>` Détail d’une cave (tri, actions, ajout bouteilles)
- `/etagere/creer` (POST) Créer une étagère
- `/etagere/supprimer` (POST) Supprimer une étagère si vide
- `/bouteilles/ajouter` (POST) Ajouter des bouteilles
- `/bouteilles/archiver` (POST) Archiver des bouteilles (note/commentaire)
- `/bouteilles/supprimer` (POST) Supprimer des bouteilles (sans archivage)
- `/avis` Vue agrégée des avis
- `/avis/details` Détail des avis d’un vin

Limites actuelles
-----------------------------
- Clé de session: valeur de développement dans `app.py` (`app.secret_key = "dev-secret"`). À remplacer en production par une clé sécurisée via variable d’environnement.
- Mots de passe: stockés en clair dans la table `utilisateur` (pas de hachage). À ne pas utiliser en production; implémenter un hachage (ex: `werkzeug.security` ou `bcrypt`).
- Moteur MySQL: tables créées avec MyISAM (sans contraintes et sans transactions). Pour un usage sérieux, privilégier InnoDB avec clés étrangères.
- Téléversement de fichiers: aucune vérification de contenu (seulement l’extension). Renforcer si déploiement public.

Crédits
-----------------
Élève réalisateur : Louis ALEXANDRE
Professeur encadrant : David Telisson

État du projet
-------------------
Le projet est terminé d’un point de vue universitaire car il répond au cahier des charges demandé par le professeur. 
Il reste néanmoins évolutif et peut être enrichi selon les besoins.
